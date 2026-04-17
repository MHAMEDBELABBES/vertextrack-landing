with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()
import re
m = re.search(r'<div class="stats-strip">.*?</section>', text, re.DOTALL)
if m: print(m.group(0)[:1000])
