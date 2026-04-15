import os
import re
import pickle
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError

# Minimal deps only
import numpy as np
from core.services.openai_client_factory import get_openai_client

DOCS_DIR = Path(os.getenv("RAG_DOCS_DIR", "./docs"))
CACHE_PATH = Path(os.getenv("RAG_CACHE_PATH", ".rag_cache.pkl"))

EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
CHAT_MODEL  = os.getenv("LLM_MODEL",   "qwen2.5:14b-instruct")

BASE_URL = os.environ.get("LLM_BASE_URL", "http://127.0.0.1:11434/v1")
API_KEY  = os.environ.get("LLM_API_KEY",  "local")

CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "1200"))   # chars
CHUNK_OVER = int(os.getenv("RAG_CHUNK_OVER", "200"))    # overlap chars
TOP_K      = int(os.getenv("RAG_TOP_K", "5"))

def clean_text(t: str) -> str:
    t = re.sub(r"<[^>]+>", " ", t)  # strip simple HTML tags
    t = re.sub(r"\s+", " ", t).strip()
    return t

def iter_docs(root: Path):
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".md", ".txt", ".rst", ".html"}:
            try:
                yield p, clean_text(p.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                continue

def chunk_text(text: str, size=CHUNK_SIZE, over=CHUNK_OVER):
    if len(text) <= size: 
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start = end - over
        if start <= 0: start = end
    return chunks

def cosine_sim(a, b):
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1e-9
    return float(np.dot(a, b) / denom)

class Command(BaseCommand):
    help = "Local RAG test using Ollama via OpenAI-compatible API (no GPT-5-minis touched)."

    def add_arguments(self, parser):
        parser.add_argument("question", type=str, help="Your question")
        parser.add_argument("--docs", type=str, default=str(DOCS_DIR), help="Docs directory")
        parser.add_argument("--k", type=int, default=TOP_K, help="Top K passages")
        parser.add_argument("--fresh", action="store_true", help="Ignore cache and re-embed")
        parser.add_argument("--debug", action="store_true", help="Print top matches and scores")

    def handle(self, *args, **opts):
        question = opts["question"]
        docs_dir = Path(opts["docs"])
        k = opts["k"]
        fresh = opts["fresh"]

        if not docs_dir.exists():
            raise CommandError(f"Docs dir not found: {docs_dir}")

        client = get_openai_client(api_key=API_KEY, base_url=BASE_URL)

        # 1) load or build corpus
        corpus = []
        for path, txt in iter_docs(docs_dir):
            for i, ch in enumerate(chunk_text(txt)):
                corpus.append({
                    "file": str(path.relative_to(docs_dir)),
                    "chunk_id": i,
                    "text": ch
                })
        if not corpus:
            raise CommandError(f"No docs found under {docs_dir}")

        # 2) load or compute embeddings
        if CACHE_PATH.exists() and not fresh:
            with CACHE_PATH.open("rb") as f:
                cached = pickle.load(f)
            # basic cache key: file count + embed model
            if cached.get("embed_model") == EMBED_MODEL and cached.get("corpus_count") == len(corpus):
                embeddings = cached["embeddings"]
            else:
                embeddings = None
        else:
            embeddings = None

        if embeddings is None:
            self.stdout.write(self.style.WARNING("Embedding corpus (first run or cache miss)…"))
            texts = [c["text"] for c in corpus]
            embeddings = []
            B = 64
            for i in range(0, len(texts), B):
                batch = texts[i:i+B]
                resp = client.embeddings.create(model=EMBED_MODEL, input=batch)
                # Ollama returns {"data":[{"embedding":[...]}...]}
                for item in resp.data:
                    embeddings.append(np.array(item.embedding, dtype=np.float32))
            CACHE_PATH.write_bytes(pickle.dumps({
                "embed_model": EMBED_MODEL,
                "corpus_count": len(corpus),
                "embeddings": embeddings,
            }))
            self.stdout.write(self.style.SUCCESS(f"Cached {len(corpus)} embeddings → {CACHE_PATH}"))

        # 3) embed query
        qresp = client.embeddings.create(model=EMBED_MODEL, input=[question])
        qvec = np.array(qresp.data[0].embedding, dtype=np.float32)

        sims = [cosine_sim(qvec, v) for v in embeddings]
        top_idx = np.argsort(sims)[::-1][:k]
        if opts.get("debug"):
            print("\n--- DEBUG TOP MATCHES ---")
            for j, idx in enumerate(top_idx[:10]):
                print(f"{j+1:>2}. score={sims[int(idx)]:.4f}  file={corpus[int(idx)]['file']}  chunk={corpus[int(idx)]['chunk_id']}")
                preview = corpus[int(idx)]['text'][:200].replace('\n',' ')
                print("    ", preview, "...\n")
        contexts = []
        for idx in top_idx:
            c = corpus[int(idx)]
            contexts.append(f"[{c['file']}#{c['chunk_id']}]\n{c['text']}")

        context_blob = "\n\n---\n\n".join(contexts)

        # 4) ask the chat model using ONLY context
        messages = [
    {"role":"system","content":(
        "You answer ONLY using the provided Context. "
        "Do NOT give navigation advice or instructions on how to search the docs. "
        "If facts are missing, say 'I don't know' for those parts. "
        "Produce a direct answer with short bullet points, and cite support inline using "
        "[file#chunk] labels that appear in the Context."
    )},
    {"role":"user","content":f"Context:\n{context_blob}\n\nQuestion: {question}\n\n"
                             "Output format:\n"
                             "- 3–7 short bullet points\n"
                             "- No navigation advice\n"
                             "- Include inline citations like [file#chunk]\n"}
]
        resp = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            temperature=0.0,
            max_tokens=500
        )
        answer = resp.choices[0].message.content.strip()

        print("\n=== ANSWER ===\n" + answer)
        print("\n=== SOURCES ===")
        for idx in top_idx:
            c = corpus[int(idx)]
            print(f"- {c['file']} (chunk {c['chunk_id']})")

