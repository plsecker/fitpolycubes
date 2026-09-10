from pathlib import Path
import re

ROOT = Path("/home/philip/Work/fitpolycubes")
SHIRAKAWA = ROOT / "shirakawa"

box_re = re.compile(r"^\d+x\d+x\d+$")

records = []

for path in sorted(SHIRAKAWA.glob("*.md")):
    section = None

    for line in path.read_text(errors="replace").splitlines():
        s = line.strip()

        if s == "3D":
            section = "3D"
            continue

        if s in {"4D", "5D", "*D", "3D 2-sided"}:
            section = None
            continue

        if section != "3D":
            continue

        fields = line.split("\t")
        if len(fields) < 4:
            continue

        box = fields[1].strip()
        status = fields[3].strip()

        if not box_re.fullmatch(box):
            continue

        dims = tuple(sorted(map(int, box.split("x"))))

        records.append({
            "piece": path.stem,
            "box": dims,
            "status": status,
            "source": fields[7].strip() if len(fields) > 7 else "",
            "year": fields[6].strip() if len(fields) > 6 else "",
        })

print(f"Files processed: {len(list(SHIRAKAWA.glob('*.md')))}")
print(f"Concrete 3D records: {len(records)}")
print(f"Status 0: {sum(r['status'] == '0' for r in records)}")
print(f"Status 1+: {sum(r['status'] == '1+' for r in records)}")
print("\nFirst 10 records:")

for r in records[:10]:
    print(r)
