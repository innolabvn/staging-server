from pathlib import Path
import re

def split_llm_chunks(input_file="llm_chunks.txt", output_dir=Path("chunks")):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    chunks = re.split(r'# File: (.+?)\n', content)[1:]  # bỏ phần đầu
    for i in range(0, len(chunks), 2):
        file_path = chunks[i].strip()
        file_content = chunks[i + 1].strip()

        # Sanitize file name
        safe_name = re.sub(r'[\\/:*?"<>|]', '_', file_path)
        output_path = output_dir / f"{safe_name}.txt"

        with open(output_path, 'w', encoding='utf-8') as out_file:
            out_file.write(f"# File: {file_path}\n{file_content}\n")

    print(f"✅ Split {len(chunks)//2} chunks into '{output_dir}'")

if __name__ == "__main__":
    split_llm_chunks()
