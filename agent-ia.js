(function() {

var GROQ_KEY = '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';
var GROQ_MODEL = 'llama-3.3-70b-versatile';
var GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions';

var VT_AGENT = {
  isOpen: false,
  messages: [],
  profile: null,
  role: 'athlete'
};

function buildSystemPrompt(profile, role) {
  var base = "Tu es Dr. VERTEX, expert en biomecanique sportive et prevention LCA integre dans VERTEXTRACK. Tu combines l expertise d un coach professionnel de haut niveau (basketball et football) et d un kinesitherapeute specialise LCA avec 15 ans d experience. Tu maitrises : Hewett 2005 AJSM (valgus dynamique et risque LCA), Kyritsis 2016 BJSM (criteres retour sport), Dingenen 2015 Knee (flexion genou optimale), Bosco 1983 (methode temps de vol CMJ), Ebben & Petushek 2010 (RSI modifie), Petersen 2011 AJSM (Nordic Hamstring), Soligard 2008 BMJ (FIFA 11+ efficacite -50% LCA), Myklebust 2003 BJSM (proprioception et LCA). Tu connais et appliques : PEP Program, FIFA 11+, protocole retour sport progressif Grindem 2016, RSI training, Neuromuscular Training (NMT).";

  var roleCtx = {
    athlete: "Tu parles a un athlete. Langage simple, direct et motivant. Pas de jargon medical. Tu donnes des exercices precis avec series x reps x frequence par semaine. Tu expliques pourquoi chaque exercice aide. Tu felicites les bons resultats. Ton : coach qui connait personnellement l athlete.",
    coach: "Tu parles a un coach sportif professionnel. Langage technique oriente performance. Tu proposes des exercices collectifs, parles de periodisation et charge d entrainement. Tu donnes des criteres objectifs de retour sport. Tu cites les references pour justifier tes recommandations. Ton : expert a expert, concis et factuel.",
    medecin: "Tu parles a un medecin du sport ou kinesitherapeute. Vocabulaire clinique complet et precis. Tu cites systematiquement les references scientifiques avec auteur+annee+journal. Tu analyses les mecanismes biocaniques en profondeur. Tu proposes des protocoles de reeducation progressifs avec criteres d evaluation. Tu mentionnes les contre-indications. Ton : collegue professionnel de sante."
  };

  var profileCtx = "";
  if (profile) {
    var fppaL = profile.fppa_left || profile.fppaLeft || 0;
    var fppaR = profile.fppa_right || profile.fppaRight || 0;
    var lsi   = profile.lsi_symmetry || profile.lsi || 1;
    var knee  = profile.knee_flexion_max || profile.kneeFlexion || 80;
    var h     = profile.jump_height_com || profile.jumpHeight || 0;
    var rsi   = profile.rsi_modified || 0;

    var alerts = [];
    var strengths = [];

    if (fppaL >= 15) alerts.push("FPPA gauche ELEVE " + fppaL.toFixed(1) + "deg => risque valgus significatif (Hewett 2005)");
    else if (fppaL >= 12) alerts.push("FPPA gauche MODERE " + fppaL.toFixed(1) + "deg => proche seuil critique 15deg");
    else strengths.push("FPPA gauche normal " + fppaL.toFixed(1) + "deg");

    if (lsi < 0.80) alerts.push("LSI SEVERE " + (lsi*100).toFixed(0) + "% => retour sport contre-indique (Kyritsis 2016)");
    else if (lsi < 0.90) alerts.push("LSI MODERE " + (lsi*100).toFixed(0) + "% => critere retour sport non atteint (<90%)");
    else strengths.push("LSI satisfaisant " + (lsi*100).toFixed(0) + "%");

    if (knee < 70) alerts.push("Flexion genou INSUFFISANTE " + knee.toFixed(0) + "deg => optimal 70-90deg (Dingenen 2015)");
    else if (knee >= 70 && knee <= 90) strengths.push("Flexion genou OPTIMALE " + knee.toFixed(0) + "deg");

    if (h >= 45) strengths.push("Hauteur saut EXCELLENTE " + h.toFixed(1) + "cm");
    else if (h >= 35) strengths.push("Hauteur saut correcte " + h.toFixed(1) + "cm");
    else if (h > 0) alerts.push("Hauteur saut FAIBLE " + h.toFixed(1) + "cm => objectif >= 38cm");

    if (rsi >= 0.9) strengths.push("RSI ELITE " + rsi.toFixed(3));
    else if (rsi >= 0.7) strengths.push("RSI BON " + rsi.toFixed(3));
    else if (rsi > 0) alerts.push("RSI FAIBLE " + rsi.toFixed(3) + " => travail pliometrique recommande");

    profileCtx = " | PROFIL ATHLETE: Hauteur CMJ=" + (h ? h.toFixed(1)+"cm" : "non mesure")
      + ", FPPA-G=" + (fppaL ? fppaL.toFixed(1)+"deg" : "?")
      + ", FPPA-D=" + (fppaR ? fppaR.toFixed(1)+"deg" : "?")
      + ", LSI=" + (lsi ? (lsi*100).toFixed(0)+"%" : "?")
      + ", Flexion genou=" + (knee ? knee.toFixed(0)+"deg" : "?")
      + ", RSI=" + (rsi ? rsi.toFixed(3) : "?")
      + " | ALERTES: " + (alerts.length ? alerts.join("; ") : "aucune alerte critique")
      + " | POINTS FORTS: " + (strengths.length ? strengths.join("; ") : "a evaluer");
  }

  return base
    + " | " + (roleCtx[role] || roleCtx.athlete)
    + profileCtx
    + " | REGLES ABSOLUES: Reponds TOUJOURS en francais. Maximum 5 phrases sauf si programme complet demande. Pour tout exercice donne: nom + series x reps + frequence/semaine. Cite auteur+annee pour toute reference scientifique. Reste dans ton domaine: biomecanique, saut vertical, LCA, performance sportive basketball/football.";
}

async function callGroq(userMessage) {
  VT_AGENT.messages.push({
    role: 'user',
    content: userMessage
  });

  var systemPrompt = buildSystemPrompt(
    VT_AGENT.profile, VT_AGENT.role);

  var body = {
    model: GROQ_MODEL,
    messages: [
      { role: 'system', content: systemPrompt }
    ].concat(VT_AGENT.messages.slice(-6)),
    max_tokens: 400,
    temperature: 0.7
  };

  try {
    var resp = await fetch(GROQ_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + GROQ_KEY
      },
      body: JSON.stringify(body)
    });

    if (!resp.ok) throw new Error('Groq error ' + resp.status);

    var data = await resp.json();
    var reply = data.choices[0].message.content;

    VT_AGENT.messages.push({
      role: 'assistant',
      content: reply
    });

    return reply;

  } catch(err) {
    console.error('[Agent IA Groq]', err);
    return 'Je rencontre une difficulte technique. Verifiez votre connexion et reessayez.';
  }
}

function getSuggestions(role, profile) {
  if (role === 'coach') return [
    'Programme equipe cette semaine',
    'Retour sport apres blessure ?',
    'Exercices collectifs LCA'
  ];
  if (role === 'medecin') return [
    'Protocole reeducation LCA',
    'Criteres retour sport',
    'Interpreter le score SHAP'
  ];
  var suggs = ['Explique mes resultats', 'Quels exercices ?', 'Mon risque LCA ?'];
  if (profile) {
    var fppaL = profile.fppa_left || profile.fppaLeft || 0;
    var lsi = profile.lsi_symmetry || profile.lsi || 1;
    if (fppaL >= 12) suggs[1] = 'Exercices pour mon genou';
    if (lsi < 0.90) suggs[2] = 'Ameliorer ma symetrie';
  }
  return suggs;
}

function getWelcome(role, profile) {
  if (role === 'medecin') {
    return 'Bonjour ! Je suis votre assistant clinique VERTEXTRACK. Je peux vous aider a interpreter les donnees biocaniques, suggerer des protocoles et repondre a vos questions cliniques.';
  }
  if (role === 'coach') {
    return 'Bonjour Coach ! Je peux vous aider a analyser les profils de vos joueurs, planifier les retours sport et adapter les programmes d\'entrainement.';
  }
  if (profile) {
    var fppaL = profile.fppa_left || profile.fppaLeft || 0;
    if (fppaL >= 12) {
      return 'Bonjour ! J\'ai analyse ton profil CMJ. Ton alignement du genou gauche merite attention (FPPA ' + fppaL.toFixed(1) + 'deg). Je suis la pour t\'aider !';
    }
  }
  return 'Bonjour ! Je suis ton assistant VERTEXTRACK. Je connais ton profil biometrique et je peux t\'aider a comprendre tes resultats et ameliorer tes performances.';
}

function createWidget() {
  var el = document.createElement('div');
  el.id = 'vt-agent-root';
  el.innerHTML = '\
<style>\
#vt-fab{position:fixed;bottom:24px;right:24px;width:54px;height:54px;\
border-radius:50%;background:linear-gradient(135deg,#00c8ff,#0088bb);\
border:none;cursor:pointer;z-index:9999;display:flex;align-items:center;\
justify-content:center;font-size:24px;box-shadow:0 4px 20px rgba(0,200,255,0.45);\
transition:transform .2s,box-shadow .2s;}\
#vt-fab:hover{transform:scale(1.1);box-shadow:0 6px 28px rgba(0,200,255,0.6);}\
#vt-fab-dot{position:absolute;top:-2px;right:-2px;width:12px;height:12px;\
background:#21c354;border-radius:50%;border:2px solid #03080f;\
animation:vtPulse 2s infinite;}\
@keyframes vtPulse{0%,100%{opacity:1;transform:scale(1);}\
50%{opacity:.5;transform:scale(1.4);}}\
#vt-chat{position:fixed;bottom:90px;right:24px;width:340px;height:470px;\
background:#060e1a;border:0.5px solid rgba(0,200,255,0.3);border-radius:14px;\
display:none;flex-direction:column;z-index:9999;\
box-shadow:0 8px 40px rgba(0,0,0,0.7);overflow:hidden;}\
#vt-chat.open{display:flex;}\
#vt-ch{background:rgba(0,200,255,0.08);border-bottom:0.5px solid\
 rgba(0,200,255,0.15);padding:12px 16px;display:flex;align-items:center;\
gap:10px;flex-shrink:0;}\
#vt-hav{width:32px;height:32px;border-radius:50%;background:rgba(0,200,255,0.2);\
border:1.5px solid rgba(0,200,255,0.5);display:flex;align-items:center;\
justify-content:center;font-size:15px;flex-shrink:0;}\
#vt-hinfo{flex:1;}\
#vt-hname{font-family:\'Barlow Condensed\',sans-serif;font-size:13px;\
font-weight:700;color:#fff;letter-spacing:.5px;}\
#vt-hstatus{font-size:10px;color:rgba(200,216,232,.45);\
display:flex;align-items:center;gap:4px;}\
#vt-sdot{width:6px;height:6px;background:#21c354;border-radius:50%;}\
#vt-cx{background:none;border:none;color:rgba(200,216,232,.4);\
cursor:pointer;font-size:20px;line-height:1;padding:0;}\
#vt-cx:hover{color:#c8d8e8;}\
#vt-msgs{flex:1;overflow-y:auto;padding:12px;display:flex;\
flex-direction:column;gap:8px;scrollbar-width:thin;\
scrollbar-color:rgba(0,200,255,.15) transparent;}\
.vm{max-width:88%;padding:9px 12px;border-radius:10px;\
font-size:12px;line-height:1.55;animation:vmIn .2s ease;}\
@keyframes vmIn{from{opacity:0;transform:translateY(5px);}\
to{opacity:1;transform:translateY(0);}}\
.vm-u{background:rgba(0,200,255,.1);border:0.5px solid rgba(0,200,255,.2);\
color:#c8d8e8;align-self:flex-end;border-bottom-right-radius:3px;}\
.vm-a{background:rgba(255,255,255,.04);border:0.5px solid rgba(255,255,255,.08);\
color:rgba(200,216,232,.85);align-self:flex-start;border-bottom-left-radius:3px;}\
.vm-t{background:rgba(255,255,255,.04);border:0.5px solid rgba(255,255,255,.08);\
align-self:flex-start;padding:10px 14px;border-radius:10px;}\
.vt-dots{display:flex;gap:4px;}\
.vt-dots span{width:6px;height:6px;background:rgba(0,200,255,.5);\
border-radius:50%;animation:vd 1.2s infinite;}\
.vt-dots span:nth-child(2){animation-delay:.2s;}\
.vt-dots span:nth-child(3){animation-delay:.4s;}\
@keyframes vd{0%,60%,100%{opacity:.2;transform:scale(.8);}\
30%{opacity:1;transform:scale(1);}}\
#vt-suggs{padding:8px 12px 0;display:flex;gap:5px;\
flex-wrap:wrap;flex-shrink:0;}\
.vs{font-size:10px;padding:4px 9px;border-radius:12px;\
border:0.5px solid rgba(0,200,255,.2);\
background:rgba(0,200,255,.05);color:rgba(0,200,255,.7);\
cursor:pointer;transition:all .15s;white-space:nowrap;}\
.vs:hover{background:rgba(0,200,255,.12);\
border-color:rgba(0,200,255,.4);color:#00c8ff;}\
#vt-ir{padding:10px 12px;border-top:0.5px solid rgba(0,200,255,.1);\
display:flex;gap:8px;align-items:flex-end;flex-shrink:0;}\
#vt-inp{flex:1;background:rgba(0,200,255,.04);\
border:0.5px solid rgba(0,200,255,.2);border-radius:8px;\
padding:8px 11px;font-size:12px;color:#c8d8e8;\
font-family:\'Barlow\',sans-serif;outline:none;resize:none;\
min-height:34px;max-height:72px;transition:border-color .15s;}\
#vt-inp:focus{border-color:rgba(0,200,255,.5);}\
#vt-inp::placeholder{color:rgba(200,216,232,.3);}\
#vt-snd{width:34px;height:34px;border-radius:8px;\
background:#00c8ff;border:none;cursor:pointer;\
display:flex;align-items:center;justify-content:center;\
flex-shrink:0;transition:opacity .15s;font-size:13px;\
color:#03080f;font-weight:700;}\
#vt-snd:hover{opacity:.85;}\
#vt-snd:disabled{opacity:.35;cursor:not-allowed;}\
#vt-disc{font-size:9px;color:rgba(200,216,232,.2);\
text-align:center;padding:4px 12px 8px;font-style:italic;flex-shrink:0;}\
</style>\
<button id="vt-fab" title="Assistant IA VERTEXTRACK">\
  \u{1F916}<div id="vt-fab-dot"></div>\
</button>\
<div id="vt-chat">\
  <div id="vt-ch">\
    <div id="vt-hav">\u{1F916}</div>\
    <div id="vt-hinfo">\
      <div id="vt-hname">Assistant VERTEXTRACK</div>\
      <div id="vt-hstatus">\
        <div id="vt-sdot"></div>\
        <span id="vt-hlbl">En ligne</span>\
      </div>\
    </div>\
    <button id="vt-cx">\u00D7</button>\
  </div>\
  <div id="vt-msgs"></div>\
  <div id="vt-suggs"></div>\
  <div id="vt-ir">\
    <textarea id="vt-inp"\
      placeholder="Pose ta question..." rows="1"></textarea>\
    <button id="vt-snd">\u27A4</button>\
  </div>\
  <div id="vt-disc">Assistant IA \u00B7 Ne remplace pas un avis m\u00E9dical</div>\
</div>';
  document.body.appendChild(el);

  // Récupérer profil et rôle
  VT_AGENT.role = localStorage.getItem('vt_user_role') || 'athlete';
  var stored = localStorage.getItem('vt_last_results');
  if (stored) try { VT_AGENT.profile = JSON.parse(stored); } catch(e){}
  if (!VT_AGENT.profile && window._lastAnalysisResults)
    VT_AGENT.profile = window._lastAnalysisResults;

  // Label rôle
  var rLabels = {athlete:'Mode Athl\u00E8te',coach:'Mode Coach',medecin:'Mode M\u00E9decin/Kin\u00E9'};
  document.getElementById('vt-hlbl').textContent =
    rLabels[VT_AGENT.role] || 'En ligne';

  // Suggestions
  var suggs = getSuggestions(VT_AGENT.role, VT_AGENT.profile);
  var suggEl = document.getElementById('vt-suggs');
  suggEl.innerHTML = suggs.map(function(s){
    return '<button class="vs">'+s+'</button>';
  }).join('');
  suggEl.querySelectorAll('.vs').forEach(function(b){
    b.addEventListener('click', function(){
      document.getElementById('vt-inp').value = this.textContent;
      send();
    });
  });

  // Events
  document.getElementById('vt-fab').addEventListener('click', function(){
    VT_AGENT.isOpen = !VT_AGENT.isOpen;
    var chat = document.getElementById('vt-chat');
    chat.classList.toggle('open', VT_AGENT.isOpen);
    if (VT_AGENT.isOpen &&
        document.getElementById('vt-msgs').children.length === 0) {
      addMsg('a', getWelcome(VT_AGENT.role, VT_AGENT.profile));
    }
    if (VT_AGENT.isOpen)
      document.getElementById('vt-inp').focus();
  });

  document.getElementById('vt-cx').addEventListener('click', function(){
    VT_AGENT.isOpen = false;
    document.getElementById('vt-chat').classList.remove('open');
  });

  document.getElementById('vt-snd').addEventListener('click', send);

  document.getElementById('vt-inp').addEventListener('keydown', function(e){
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  });

  document.getElementById('vt-inp').addEventListener('input', function(){
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 72) + 'px';
  });

  async function send() {
    var inp = document.getElementById('vt-inp');
    var txt = inp.value.trim();
    if (!txt) return;
    inp.value = '';
    inp.style.height = 'auto';
    var snd = document.getElementById('vt-snd');
    snd.disabled = true;
    addMsg('u', txt);
    var typing = addTyping();
    var reply = await callGroq(txt);
    typing.remove();
    addMsg('a', reply);
    snd.disabled = false;
    inp.focus();
  }

  function addMsg(role, text) {
    var d = document.createElement('div');
    d.className = 'vm vm-' + role;
    d.textContent = text;
    var msgs = document.getElementById('vt-msgs');
    msgs.appendChild(d);
    msgs.scrollTop = msgs.scrollHeight;
    return d;
  }

  function addTyping() {
    var d = document.createElement('div');
    d.className = 'vm vm-t';
    d.innerHTML = '<div class="vt-dots"><span></span><span></span><span></span></div>';
    var msgs = document.getElementById('vt-msgs');
    msgs.appendChild(d);
    msgs.scrollTop = msgs.scrollHeight;
    return d;
  }
}

document.addEventListener('DOMContentLoaded', createWidget);

})();
