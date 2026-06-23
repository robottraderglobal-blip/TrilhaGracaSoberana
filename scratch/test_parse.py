import re
from pathlib import Path

def main():
    file_path = Path("c:/Users/ryzen/Downloads/Antigravity/TrilhaGracaSoberana/novos/serie3-aconselhamento-biblico-21-devocionais.md")
    content = file_path.read_text(encoding="utf-8")
    
    # Split by "## Dia "
    parts = re.split(r'\n(## Dia \d+ —[^\n]*)', content)
    
    header = parts[0]
    days = []
    
    for i in range(1, len(parts), 2):
        day_title = parts[i].strip()
        day_content = parts[i+1] if i+1 < len(parts) else ""
        days.append((day_title, day_content))
        
    print(f"Total days found: {len(days)}")
    for title, body in days[:3]:
        print(f"\n--- {title} ---")
        lines = body.strip().splitlines()
        print("\n".join(lines[:6]))
        print("...")

if __name__ == "__main__":
    main()
