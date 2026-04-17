import re

with open('analyse.html', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'<div style="text-align:center;padding:10px 0 16px;">.*?</div>\s*</div>\s*</div>', text, re.DOTALL)
if m:
    with open('risk_block.html', 'w', encoding='utf-8') as fw:
        fw.write(m.group(0))
    print("Found risk block, written to risk_block.html")
else:
    print("Not found")
