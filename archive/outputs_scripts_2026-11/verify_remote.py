# Archived 2026-11-16 from the gitignored outputs/ tree.
# The GitHub token this script hardcoded was REDACTED on 2026-11-16 when the file entered
# tracked scope (finding F45): the token was never pushed to any remote, and the owner was
# told to rotate it. The script is kept as provenance of a one-off remote-README check.
import urllib.request, json, base64, sys
req = urllib.request.Request(
    "https://api.github.com/repos/chenhk1113-HK/sidm-composite-dm-mediator/contents/README.md",
    headers={"Authorization": "token REDACTED-2026-11-16"}
)
data = json.loads(urllib.request.urlopen(req).read())
b64 = data["content"]
content = base64.b64decode(b64).decode("utf-8")
print(f"Lines: {len(content.splitlines())}")
print(f"Count 'Relationship to other projects': {content.count('Relationship to other projects')}")
print(f"Count 'wimpy/bin/python': {content.count('wimpy/bin/python')}")
print(f"Count 'FUSE': {content.count('FUSE')}")
print()
print("=== Sections ===")
for line in content.splitlines():
    if line.startswith("## "):
        print(line)