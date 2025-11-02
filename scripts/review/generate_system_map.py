import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
OUTPUT = ROOT / "SYSTEM_MAP.md"

def list_files(dir_path, prefix=""):
    entries = []
    for p in sorted(Path(dir_path).iterdir()):
        if p.is_dir():
            entries.append(f"{prefix}📂 {p.name}/")
            entries.extend(list_files(p, prefix + "  "))
        else:
            entries.append(f"{prefix}📄 {p.name}")
    return entries

def main():
    with open(OUTPUT, "w") as f:
        f.write("# 🗺️ Unified Donkey Betz — System Map\n\n")
        f.write("## 📂 Directory Structure\n")
        f.write("```\n")
        for line in list_files(ROOT):
            f.write(line + "\n")
        f.write("```\n\n")

        f.write("## 📚 Docs Index\n")
        for doc in sorted(DOCS.glob("*.md")):
            f.write(f"- {doc.name}\n")
        f.write("\n")

        f.write("## 🚦 Current Priorities (from README)\n")
        f.write("- Register 2 missing spiders\n")
        f.write("- Load 11 orphaned agents\n")
        f.write("- Connect revenue attribution\n")
        f.write("- Verify learning bridges\n")
        f.write("- Consolidate orchestration\n\n")

        f.write("## 🤖 Ollama Integration TODOs\n")
        f.write("- Confirm `OPENAI_BASE_URL` env setup for Ollama\n")
        f.write("- Run repo review with `qwen2.5:14b-instruct`\n")
        f.write("- Write adapter layer for `ollama_chat`\n")
        f.write("- Validate local completions on repo files\n")

    print(f"✅ System Map written to {OUTPUT}")

if __name__ == "__main__":
    main()