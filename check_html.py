import re
with open('analyse.html', 'r', encoding='utf-8') as f:
    text = f.read()

print('--- loadDemo matches ---')
for m in re.finditer(r'function loadDemo\(', text):
    print(m.span())

print('--- loadDemoResults matches ---')
for m in re.finditer(r'function loadDemoResults', text):
    print(m.span())

print('--- HTML Demo Button matches ---')
for m in re.finditer(r'<button[^>]*onclick="loadDemo\(\)"[^>]*>.*?<\/button>', text, re.DOTALL):
    print(m.span(), m.group(0)[:50])

print('--- lbtn matches ---')
lbtn_m = re.search(r'<button[^>]*id="lbtn"[^>]*>', text)
if lbtn_m: print(lbtn_m.group(0))

print('--- results div ---')
res_m = re.search(r'<div[^>]*id="res"[^>]*>', text)
if res_m: print(res_m.group(0)[:100])

print('--- progress bar ---')
prog_m = re.search(r'<div[^>]*id="prog"[^>]*>', text)
if prog_m: print(prog_m.group(0)[:100])

print('--- CSS classes logic ---')
# Check classes
m_cmv = re.search(r'class="bign".*?class="v"', text, re.DOTALL)
m_bi = re.search(r'class="bi"', text)
m_risk = re.search(r'LOW|HIGH|MODERATE', text)

print('CMJ value classes:', 'class="bign" and class="v"' if m_cmv else 'NOT FOUND')
print('FPPA bars classes:', 'class="bi"' if m_bi else 'NOT FOUND')
print('Risk text classes:', 'div containing LOW/MODERATE/HIGH' if m_risk else 'NOT FOUND')
