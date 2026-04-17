import re

# -------------
# ANALYSE.HTML
# -------------
with open('analyse.html', 'r', encoding='utf-8') as f:
    text_a = f.read()

risk_old = r'<div style="text-align:center;padding:10px 0 16px">\s*<div style="font-size:10px;color:var\(--muted\);letter-spacing:2px;text-transform:uppercase;margin-bottom:6px">Profil de similarité biomécanique</div>\s*<div style="font-family:\'Barlow Condensed\',sans-serif;font-weight:900;font-size:40px;color:var\(--green\)">LOW</div>\s*<div style="font-family:\'JetBrains Mono\',monospace;font-size:11px;color:var\(--muted\);margin-bottom:10px">Score: 0\.18 / 1\.00</div>\s*<div style="height:5px;background:rgba\(255,255,255,\.06\);border-radius:3px"><div style="height:5px;width:18%;background:var\(--green\);border-radius:3px"></div></div>\s*<div style="display:flex;justify-content:space-between;font-size:9px;color:rgba\(255,255,255,\.2\);margin-top:4px"><span>0</span><span>0\.25</span><span>0\.5</span><span>0\.75</span><span>1\.0</span></div>\s*</div>'

risk_new = """<div style="text-align:center;padding:10px 0 16px;">
  <div style="font-size:10px;color:var(--muted);
  letter-spacing:2px;text-transform:uppercase;
  margin-bottom:6px;">
    Profil de similarité biomécanique
  </div>
  
  <!-- Badge LOW -->
  <div id="risk-low" style="display:block;">
    <div style="font-family:'Barlow Condensed',sans-serif;
    font-weight:900;font-size:40px;color:var(--green);">
      LOW
    </div>
    <div style="font-size:12px;color:var(--green);
    margin-top:4px;font-weight:600;">
      ✓ Profil biomécanique favorable
    </div>
    <div style="font-size:11px;color:var(--muted);
    margin-top:3px;line-height:1.5;">
      Faible similarité avec les profils à risque LCA.<br>
      Continuer le suivi préventif régulier.
    </div>
  </div>

  <!-- Badge MODERATE -->
  <div id="risk-moderate" style="display:none;">
    <div style="font-family:'Barlow Condensed',sans-serif;
    font-weight:900;font-size:40px;color:var(--amber);">
      MODERATE
    </div>
    <div style="font-size:12px;color:var(--amber);
    margin-top:4px;font-weight:600;">
      ⚠ Vigilance recommandée
    </div>
    <div style="font-size:11px;color:var(--muted);
    margin-top:3px;line-height:1.5;">
      Similarité modérée avec des profils à risque.<br>
      Consultation avec un kinésithérapeute conseillée.
    </div>
  </div>

  <!-- Badge HIGH -->
  <div id="risk-high" style="display:none;">
    <div style="font-family:'Barlow Condensed',sans-serif;
    font-weight:900;font-size:40px;color:#ef5350;">
      HIGH
    </div>
    <div style="font-size:12px;color:#ef5350;
    margin-top:4px;font-weight:600;">
      ⛔ Surveillance médicale recommandée
    </div>
    <div style="font-size:11px;color:var(--muted);
    margin-top:3px;line-height:1.5;">
      Profil biomécanique similaire aux cas à risque élevé.<br>
      Consultation urgente avec un médecin du sport requise.
    </div>
  </div>

  <div style="font-family:'JetBrains Mono',monospace;
  font-size:11px;color:var(--muted);margin:10px 0;">
    Score: 0.18 / 1.00
  </div>
  <div style="height:5px;background:rgba(255,255,255,.06);
  border-radius:3px;">
    <div style="height:5px;width:18%;background:var(--green);
    border-radius:3px;"></div>
  </div>
  <div style="display:flex;justify-content:space-between;
  font-size:9px;color:rgba(255,255,255,.2);margin-top:4px;">
    <span>0 — Profil favorable</span>
    <span>1.0 — Profil à risque</span>
  </div>

  <!-- Légende des niveaux -->
  <div style="margin-top:16px;display:grid;
  grid-template-columns:1fr 1fr 1fr;gap:6px;">
    <div style="background:rgba(0,230,118,0.08);
    border:1px solid rgba(0,230,118,0.2);
    padding:8px 6px;text-align:center;">
      <div style="font-size:11px;font-weight:700;
      color:var(--green);">LOW</div>
      <div style="font-size:9px;color:var(--muted);
      margin-top:2px;">Score &lt; 0.35</div>
      <div style="font-size:9px;color:var(--green);
      margin-top:2px;">✓ Favorable</div>
    </div>
    <div style="background:rgba(245,158,11,0.08);
    border:1px solid rgba(245,158,11,0.2);
    padding:8px 6px;text-align:center;">
      <div style="font-size:11px;font-weight:700;
      color:var(--amber);">MODERATE</div>
      <div style="font-size:9px;color:var(--muted);
      margin-top:2px;">Score 0.35–0.65</div>
      <div style="font-size:9px;color:var(--amber);
      margin-top:2px;">⚠ Vigilance</div>
    </div>
    <div style="background:rgba(239,83,80,0.08);
    border:1px solid rgba(239,83,80,0.2);
    padding:8px 6px;text-align:center;">
      <div style="font-size:11px;font-weight:700;
      color:#ef5350;">HIGH</div>
      <div style="font-size:9px;color:var(--muted);
      margin-top:2px;">Score &gt; 0.65</div>
      <div style="font-size:9px;color:#ef5350;
      margin-top:2px;">⛔ Surveillance</div>
    </div>
  </div>
</div>"""

res_a = re.sub(risk_old, risk_new, text_a, count=1)
with open('analyse.html', 'w', encoding='utf-8') as f:
    f.write(res_a)

# -------------
# DASHBOARD.HTML
# -------------
with open('dashboard.html', 'r', encoding='utf-8') as f:
    text_b = f.read()

# Part A / B - KPI IDs
text_b = text_b.replace('<div class="kpi-value cyan">24</div>', '<div class="kpi-value cyan" id="kpi-athletes">24</div>')
text_b = text_b.replace('<div class="kpi-value">142</div>', '<div class="kpi-value" id="kpi-analyses">142</div>')
text_b = text_b.replace('<div class="kpi-value green">18</div>', '<div class="kpi-value green" id="kpi-risk">18</div>')
text_b = text_b.replace('<div class="kpi-value red">3</div>', '<div class="kpi-value red" id="kpi-high">3</div>')

# Part C - Table body div
table_rows_match = re.search(r'(<div class="table-row">.*</div>\s*</div>)', text_b, re.DOTALL)
if table_rows_match:
    original_rows = table_rows_match.group(1)
    # The regex captured up to the closing div of table-box most likely.
    pass

# We will just insert `<div id="athletes-tbody">` right after `</div>` of `.table-header`
th_end = text_b.find('</div>\n\n    <div class="table-row">')
if th_end != -1:
    idx_insert = th_end + 6 # right after </div>
    idx_end = text_b.find('</div>\n\n</div>\n\n<script>')
    if idx_end == -1: idx_end = text_b.find('</div>\n\n</body>')
    # Let's cleanly inject it using replace
    old_tbox = re.search(r'(<div class="table-header">.*?</div>)\s*(<div class="table-row">.*?)(\s*</div>\s*<!-- \/CONTENT -->|\s*</div>\s*</div>\s*<script)', text_b, re.DOTALL)
    if old_tbox:
        new_tbox = old_tbox.group(1) + '\n<div id="athletes-tbody">\n' + old_tbox.group(2) + '\n</div>\n' + old_tbox.group(3)
        text_b = text_b.replace(old_tbox.group(0), new_tbox)
    else:
        # manual 
        pass
else:
    # safe replace
    text_b = re.sub(r'(<div class="table-header">.*?</div>)', r'\1\n<div id="athletes-tbody">', text_b, flags=re.DOTALL)
    # adding closing div before </body>
    # it's a bit dirty, so let's modify the user script directly to target a clear div
    pass

# Part D - Demo Banner
banner_old = r'<!-- BANNER DÉMO -->.*?</a>\s*</div>'
banner_new = """<!-- BANNER DÉMO -->
<div id="demo-banner" style="display:none;
background:rgba(245,158,11,0.06);
border:1px solid rgba(245,158,11,0.2);
padding:12px 24px;margin-bottom:20px;
align-items:center;justify-content:space-between;
flex-wrap:wrap;gap:10px;">
  <div style="font-size:12px;color:var(--muted);
  display:flex;align-items:center;gap:8px;">
    <span style="color:var(--amber);font-size:16px;">🎬</span>
    <span>Aucune donnée réelle disponible —
    <strong style="color:var(--amber);">
    mode démonstration</strong> avec données fictives</span>
  </div>
  <a href="analyse.html"
  style="background:var(--cyan);color:#03080f;
  padding:7px 18px;font-family:'Barlow',sans-serif;
  font-weight:800;font-size:11px;letter-spacing:2px;
  text-transform:uppercase;text-decoration:none;">
    Analyser un athlète →
  </a>
</div>"""

text_b = re.sub(banner_old, banner_new, text_b, flags=re.DOTALL)

# Add athletes-tbody id properly!
# Before: <div class="table-header">...</div> \n <div class="table-row">...</div> \n <div class="table-row">...</div> \n </div>
tb_head = '<div class="table-header">'
tb_head_idx = text_b.find('<div class="table-header">')
if tb_head_idx != -1:
    end_of_head = text_b.find('</div>', tb_head_idx) + 6
    text_b = text_b[:end_of_head] + '\n<div id="athletes-tbody">' + text_b[end_of_head:]
    end_of_table_box = text_b.find('</div>\n\n</div>\n\n<script>')
    if end_of_table_box == -1: 
        end_of_table_box = text_b.find('</div>\n</body>')
    # add closing div
    if end_of_table_box != -1:
        text_b = text_b[:end_of_table_box] + '</div>\n' + text_b[end_of_table_box:]

# Add script
js = """
<script>
var SUPABASE_URL = 'https://kygrhqgyqqrylsxnshny.supabase.co';
var SUPABASE_KEY = 'sb_publishable_xEGDhI4c53TSQZOYrygUuA_4YTRjlNf';

async function loadSupabaseData() {
  try {
    var headers = {
      'apikey': SUPABASE_KEY,
      'Authorization': 'Bearer ' + SUPABASE_KEY,
      'Content-Type': 'application/json'
    };

    // Charger les athlètes
    var resAthletes = await fetch(
      SUPABASE_URL + '/rest/v1/athletes?select=*&order=created_at.desc',
      { headers: headers }
    );
    var athletes = await resAthletes.json();

    // Charger les analyses
    var resAnalyses = await fetch(
      SUPABASE_URL + '/rest/v1/analyses?select=*&order=created_at.desc',
      { headers: headers }
    );
    var analyses = await resAnalyses.json();

    // Mettre à jour les KPI cards
    var totalAthletes = athletes.length;
    var totalAnalyses = analyses.length;
    
    var scores = analyses
      .filter(function(a) { return a.risk_score !== null; })
      .map(function(a) { return a.risk_score; });
    var avgRisk = scores.length > 0 
      ? (scores.reduce(function(a,b){return a+b;},0)/scores.length).toFixed(2)
      : '—';
    var highRisk = scores.filter(function(s){return s > 0.65;}).length;

    // Mettre à jour le DOM
    var kpiIds = ['kpi-athletes','kpi-analyses','kpi-risk','kpi-high'];
    var kpiVals = [totalAthletes, totalAnalyses, avgRisk, highRisk];
    kpiIds.forEach(function(id, i) {
      var el = document.getElementById(id);
      if(el) el.textContent = kpiVals[i];
    });

    // Mettre à jour le tableau athlètes
    if(athletes.length > 0) {
      updateAthletesTable(athletes, analyses);
      hideDemoBanner();
    } else {
      showDemoBanner();
    }

  } catch(err) {
    console.log('Supabase non disponible:', err);
    showDemoBanner();
  }
}

function updateAthletesTable(athletes, analyses) {
  var tbody = document.getElementById('athletes-tbody');
  if(!tbody) return;
  tbody.innerHTML = '';
  
  athletes.forEach(function(a) {
    var lastAnalyse = analyses.find(function(an) {
      return an.athlete_id === a.id;
    });
    var risk = lastAnalyse ? lastAnalyse.risk_label : '—';
    var score = lastAnalyse ? 
      (lastAnalyse.risk_score || 0).toFixed(2) : '—';
    var cmj = lastAnalyse ? 
      (lastAnalyse.cmj_height || '—') : '—';
    var fppa = lastAnalyse ?
      (lastAnalyse.fppa_gauche || '—') : '—';
    
    var riskColor = risk === 'LOW' ? 'var(--green)' : 
                    risk === 'HIGH' ? 'var(--red)' : 'var(--amber)';
    var badgeClass = risk === 'LOW' ? 'badge-low' : 
                     risk === 'HIGH' ? 'badge-high' : 'badge-warn';
    var riskLabel = risk === 'LOW' ? 'Faible' :
                    risk === 'HIGH' ? 'Élevé' :
                    risk === 'MODERATE' ? 'Modéré' : '—';

    // USING DIV GRID STRUCTURE INSTEAD OF TR/TD TO KEEP DESIGN INTACT
    var row = '<div class="table-row">' +
      '<div><div class="athlete-name">' + (a.nom||'') + ' ' + (a.prenom||'') + '</div><div class="athlete-club">' + (a.club||'—') + '</div></div>' +
      '<div class="td">' + cmj + ' cm</div>' +
      '<div class="td">' + fppa + '°</div>' +
      '<div class="td">' + score + '</div>' +
      '<div><span class="badge ' + badgeClass + '">' + riskLabel + '</span></div>' +
      '<div><a class="btn-sm" href="analyse.html">Analyser</a></div>' +
      '</div>';
    tbody.innerHTML += row;
  });
}

function showDemoBanner() {
  var b = document.getElementById('demo-banner');
  if(b) b.style.display = 'flex';
}

function hideDemoBanner() {
  var b = document.getElementById('demo-banner');
  if(b) b.style.display = 'none';
}

// Charger les données au démarrage
window.addEventListener('load', loadSupabaseData);
</script>
"""

# check if we already have script tags at the bottom
if "window.addEventListener('load', loadSupabaseData);" not in text_b:
    text_b = text_b.replace('</body>', js + '\n</body>')

with open('dashboard.html', 'w', encoding='utf-8') as f:
    f.write(text_b)

print("done inject dashboard and analyse risk logic")
