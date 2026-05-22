import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = path.read_bytes()
m = re.search(rb"\(15,'([^']+)'\)", data)
if not m:
    print("nao encontrou Pará no dump")
    sys.exit(1)
value = m.group(1)
print("valor:", value.decode("utf-8"))
print("hex:", value.hex())
print("ok" if value.hex() == "506172c3a1" else "corrompido")
