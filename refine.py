import sys
import re

try:
    with open('extracted_draw_utf8.js', 'r', encoding='utf-8') as f:
        content = f.read()

    # Update badMov threshold to 165 (15 deg)
    content = content.replace('badMov=fppa<160', 'badMov=fppa<165')

    # Fix the FPPA label
    # The old code might have text segments split or with ??
    # We want: ctx.fillText('FPPA: ' + ang + '°', lx + 6, ly + 16);
    content = re.sub(r"ctx\.fillText\('FPPA: '\s*\+\s*ang\s*\+\s*'.*?'", "ctx.fillText('FPPA: ' + ang + '°'", content)

    # Update alert text
    # Legacy: ctx.fillText('??? VALGUS GENOU', knee.x, knee.y - 38);
    # Target: ctx.fillText('⚠️ VALGUS DÉTECTÉ', knee.x, knee.y - 38);
    content = re.sub(r"ctx\.fillText\('.*?VALGUS GENOU'", "ctx.fillText('⚠️ VALGUS DÉTECTÉ'", content)

    # Some manual fixes for known patterns in that commit
    content = content.replace("ang+'??'", "ang+'°'")
    content = content.replace("'??? VALGUS GENOU'", "'⚠️ VALGUS DÉTECTÉ'")

    with open('final_replacement.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Success")
except Exception as e:
    print(f"Error: {e}")
