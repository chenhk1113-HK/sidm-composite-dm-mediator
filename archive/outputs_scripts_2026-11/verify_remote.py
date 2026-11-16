import urllib.request, json, base64, sys
req = urllib.request.Request(
    "https://api.github.com/repos/chenhk1113-HK/sidm-composite-dm-mediator/contents/README.md",
    headers={"Authorization": "token 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"}
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