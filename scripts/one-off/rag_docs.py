import os, glob, requests, numpy as np
from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:11434/v1", api_key="local")

EMBED_URL = "http://127.0.0.1:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"
CHAT_MODEL = "qwen2.5:14b-instruct"

def embed(text: str):
    resp = requests.post(EMBED_URL, json={"model": EMBED_MODEL, "prompt": text})
    return np.array(resp.json()["embedding"], dtype=np.float32)

def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def chunk_text(text, size=500):
    words = text.split()
    for i in range(0, len(words), size):
        yield " ".join(words[i:i+size])

# --- load docs ---
docs_dir = "/Users/donkeyking/development/unified-donkey-betz/docs"
chunks, embeddings = [], []

for path in glob.glob(os.path.join(docs_dir, "**/*.md"), recursive=True) + \
             glob.glob(os.path.join(docs_dir, "**/*.txt"), recursive=True):
    with open(path, "r", errors="ignore") as f:
        text = f.read()
        for ch in chunk_text(text):
            vec = embed(ch)
            chunks.append(ch)
            embeddings.append(vec)

embeddings = np.vstack(embeddings)

def ask(question: str, k=5):
    qvec = embed(question)
    sims = [cosine_sim(qvec, v) for v in embeddings]
    top_idx = np.argsort(sims)[::-1][:k]
    context = "\n\n".join(chunks[i] for i in top_idx)

    msgs = [
        {"role": "system", "content": "Answer ONLY from the Context. If unsure, reply exactly: I don't know."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
    ]
    resp = client.chat.completions.create(model=CHAT_MODEL, messages=msgs, temperature=0.0, max_tokens=500)
    return resp.choices[0].message.content

if __name__ == "__main__":
    print("Chunks loaded:", len(chunks))
    print(ask("What is contained in /docs/"))