with open("scratch/s44d2_debug.md", "r", encoding="utf-8") as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'\*\*\.', text)]
print("Matches for **.:", matches)
for pos in matches:
    print(f"Context: {text[pos-20:pos+20]}")

matches_nl = [m.start() for m in re.finditer(r'\*\*\n', text)]
print("Matches for **\\n:", matches_nl)
for pos in matches_nl:
    print(f"Context: {text[pos-20:pos+20]}")
