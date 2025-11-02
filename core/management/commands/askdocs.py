from django.core.management.base import BaseCommand
from core.rag import build_docs_context
import requests
import json

OLLAMA_URL = "http://127.0.0.1:11434/v1/chat/completions"
MODEL = "qwen2.5:14b-instruct"   # change if you want another model

class Command(BaseCommand):
    help = "Ask a question using the /docs RAG system"

    def add_arguments(self, parser):
        parser.add_argument("question", type=str)

    def handle(self, *args, **options):
        question = options["question"]

        # 1) Build retrieval context from /docs
        ctx = build_docs_context(question, k=8, max_chars=8000)

        # 2) Compose system + user messages
        system_prompt = (
            "You are an assistant that answers ONLY using the provided Context. "
            "If facts are missing, say 'I don't know'. "
            "Format:\n"
            "- 3–7 short bullet points\n"
            "- No navigation advice\n"
            "- Inline citations with [file#chunk]"
        )

        messages = [
            {"role": "system", "content": system_prompt + "\n\nContext:\n" + ctx},
            {"role": "user", "content": question},
        ]

        # 3) Call Ollama locally
        payload = {
            "model": MODEL,
            "messages": messages,
            "options": {"num_ctx": 8192},
        }

        resp = requests.post(
            OLLAMA_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=120,
        )
        resp.raise_for_status()

        data = resp.json()
        answer = data["choices"][0]["message"]["content"].strip()

        # 4) Print result
        print("\n=== ANSWER ===")
        print(answer)
        print("\n=== RAW CONTEXT ===")
        print(ctx[:1000] + ("..." if len(ctx) > 1000 else ""))
    
    
    