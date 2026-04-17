
import sys, re

unified_code = r'''/* ===== VERTEXTRACK — Script principal ===== */

// État global
window._vtUploaded = window._vtUploaded || {};
var checklistState = {};
var totalChecks = 6;

// ===== WIZARD NAVIGATION =====
function goStep(n) {
  document.querySelectorAll('.wiz-card, [id^="wc-"]').forEach(function(el) {
    el.style.display = 'none';
  });
  var target = document.getElementById('wc-' + n);
  if (target) {
    target.style.display = 'block';
    window.scrollTo({top: 0, behavior: 'smooth'});
  }
  bcSet(n);
}

function bcSet(n) {
  document.querySelectorAll('.bc-step').forEach(function(el, idx) {
    el.classList.remove('active', 'done');
    if (idx + 1 < n) el.classList.add('done');
    if (idx + 1 === n) el.classList.add('active');
  });
}

// ===== CHECKLIST CAMÉRA =====
function toggleCheck(labelEl, key) {
  checklistState[key] = !checklistState[key];
  if (checklistState[key]) {
    labelEl.classList.add('checked');
  } else {
    labelEl.classList.remove('checked');
  }
  var doneCount = Object.keys(checklistState).filter(function(k) {
    return checklistState[k];
  }).length;
  var progress = document.getElementById('checklistProgress');
  if (doneCount >= totalChecks && progress) {
    progress.style.display = 'block';
    markBcStep(2);
  } else if (progress) {
    progress.style.display = 'none';
  }
}

function markBcStep(n) {
  var steps = document.querySelectorAll('.bc-step');
  if (steps.length >= n) {
    var step = steps[n - 1];
    step.classList.add('done');
    var num = step.querySelector('.bc-num');
    if (num) {
      num.textContent = '✓';
      num.style.cssText = 'background:#00ff88!important;border-color:#00ff88!important;color:#03080f!important;box-shadow:0 0 12px rgba(0,255,136,.5)!important;display:flex;align-items:center;justify-content:center;';
    }
    var lbl = step.querySelector('.bc-label');
    if (lbl) lbl.style.color = '#00ff88';
  }
}

function goToVideoUpload() {
  markBcStep(2);
  markBcStep(3);
  goStep(3);
}

// ===== SÉLECTION TEST =====
function setTest(t) {
  window._currentTest = t;
  markBcStep(1);
  goStep(2);
}

// ===== MOVENET & EXPORT (MERGED) =====
var detector;

async function initDetector() {
  if (detector) return true;
  try {
    detector = await poseDetection.createDetector(
      poseDetection.SupportedModels.MoveNet,
      {
        modelType: poseDetection.movenet.modelType.SINGLEPOSE_THUNDER,
        enableSmoothing: true
      }
    );
    console.log('[VT] MoveNet Detector initialized');
    return true;
  } catch(e) {
    console.error('[VT] Detector Error:', e);
    return false;
  }
}

function calcAngle(a, b, c) {
  if (!a || !b || !c) return 0;
  var v1 = {x: a.x - b.x, y: a.y - b.y};
  var v2 = {x: c.x - b.x, y: c.y - b.y};
  var dot = v1.x * v2.x + v1.y * v2.y;
  var mag = Math.sqrt(v1.x * v1.x + v1.y * v1.y) * Math.sqrt(v2.x * v2.x + v2.y * v2.y);
  if (mag === 0) return 0;
  return Math.round(Math.acos(Math.min(1, Math.max(-1, dot / mag))) * 180 / Math.PI);
}

function drawPoseOnCanvas(ctx, kps, W, H) {
  var hip=kps[11], knee=kps[13], ank=kps[15];
  var fppa=180, badMov=false;
  if (hip&&knee&&ank&&hip.score>0.4&&knee.score>0.4&&ank.score>0.4) {
    var v1={x:hip.x-knee.x,y:hip.y-knee.y};
    var v2={x:ank.x-knee.x,y:ank.y-knee.y};
    var d=v1.x*v2.x+v1.y*v2.y;
    var m=Math.sqrt(v1.x*v1.x+v1.y*v1.y)*Math.sqrt(v2.x*v2.x+v2.y*v2.y);
    fppa=Math.round(Math.acos(Math.min(1,Math.abs(d/m)))*180/Math.PI);
    badMov=fppa<165;
  }
  var EDGES=[
    [5,6,'torso'],[5,7,'arm'],[7,9,'arm'],[6,8,'arm'],[8,10,'arm'],
    [5,11,'torso'],[6,12,'torso'],[11,12,'torso'],
    [11,13,'leg'],[13,15,'leg'],[12,14,'leg'],[14,16,'leg']
  ];
  var COL={torso:'rgba(0,200,255,.9)',arm:'rgba(0,200,255,.9)',leg:badMov?'rgba(255,60,60,.9)':'rgba(0,230,118,.9)'};
  EDGES.forEach(function(e){
    var a=kps[e[0]],b=kps[e[1]];
    if(!a||!b||a.score<0.3||b.score<0.3)return;
    ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);
    ctx.strokeStyle=COL[e[2]];ctx.lineWidth=Math.max(2,W/320);ctx.stroke();
  });
  kps.forEach(function(kp,i){
    if(i<=4||kp.score<0.3)return;
    var isLeg=i>=11,r=Math.max(4,W/160);
    var ptC=isLeg&&badMov?'#ff3c3c':isLeg?'#00e676':'#00c8ff';
    var glC=isLeg&&badMov?'rgba(255,60,60,.18)':isLeg?'rgba(0,230,118,.15)':'rgba(0,200,255,.15)';
    ctx.beginPath();ctx.arc(kp.x,kp.y,r*2,0,Math.PI*2);ctx.fillStyle=glC;ctx.fill();
    ctx.beginPath();ctx.arc(kp.x,kp.y,r,0,Math.PI*2);ctx.fillStyle=ptC;ctx.fill();
    ctx.strokeStyle='rgba(255,255,255,.9)';ctx.lineWidth=1;ctx.stroke();
  });
  if(hip&&knee&&ank&&hip.score>0.4&&knee.score>0.4&&ank.score>0.4){
    var ang=fppa,fs=Math.max(11,W/58),lw=fs*9;
    ctx.beginPath();ctx.moveTo(hip.x,hip.y);ctx.lineTo(knee.x,knee.y);
    ctx.strokeStyle='rgba(255,50,50,.9)';ctx.lineWidth=2.5;ctx.stroke();
    ctx.beginPath();ctx.arc(knee.x,knee.y,16,0,Math.PI*2);
    ctx.strokeStyle=badMov?'rgba(255,60,60,.9)':'rgba(245,158,11,.9)';ctx.lineWidth=2.5;ctx.stroke();
    var lx=knee.x+18,ly=knee.y-13;if(lx+lw>W)lx=knee.x-lw-8;
    ctx.fillStyle='rgba(3,12,28,.92)';ctx.fillRect(lx,ly,lw,24);
    ctx.strokeStyle=badMov?'rgba(255,60,60,.7)':'rgba(245,158,11,.6)';ctx.lineWidth=1;ctx.strokeRect(lx,ly,lw,24);
    ctx.fillStyle=badMov?'#ff3c3c':'#f59e0b';ctx.font='bold '+fs+'px monospace';
    ctx.fillText('FPPA: ' + ang + '°',lx+6,ly+16);
    if(badMov){
      ctx.fillStyle='rgba(255,60,60,.15)';ctx.fillRect(knee.x-65,knee.y-52,130,22);
      ctx.strokeStyle='rgba(255,60,60,.7)';ctx.lineWidth=1;ctx.strokeRect(knee.x-65,knee.y-52,130,22);
      ctx.fillStyle='#ff3c3c';ctx.font='bold 10px monospace';ctx.textAlign='center';
      ctx.fillText('⚠️ VALGUS DÉTECTÉ',knee.x,knee.y-38);ctx.textAlign='left';
    }
  }
}

async function exportGeneric(inputId, previewId, filename, type) {
  var vid = document.getElementById(previewId);
  var btnId = 'exportVidBtn', prgId = 'exportProgress', msgId = 'exportMsg', barId = 'exportBar';
  if (type === 'SJ') { btnId = 'exportSJBtn'; prgId = 'exportSJProgress'; msgId = 'exportSJMsg'; barId = 'exportSJBar'; }
  if (type === 'DVJsag') { btnId = 'exportDVJBtn'; prgId = 'exportDVJProgress'; msgId = 'exportDVJMsg'; barId = 'exportDVJBar'; }
  if (type === 'DVJfront') { btnId = 'exportDVJVidBtn'; prgId = 'exportDVJProgress'; msgId = 'exportDVJMsg'; barId = 'exportDVJBar'; }
  var btn = document.getElementById(btnId);
  var prog = document.getElementById(prgId);
  var msg = document.getElementById(msgId);
  var bar = document.getElementById(barId);
  if (!vid || !vid.src || vid.src === window.location.href) { alert('Uploadez d\'abord la vidéo pour ' + type); return; }
  if (!window.MediaRecorder) { alert('Votre navigateur ne supporte pas MediaRecorder.'); return; }
  if (prog) prog.style.display = 'block';
  if (msg) msg.textContent = 'Initialisation MoveNet...';
  if (bar) bar.style.width = '5%';
  if (btn) { btn.disabled = true; btn.style.opacity = '0.5'; }
  await initDetector();
  var offCv = document.createElement('canvas');
  var offCtx = offCv.getContext('2d');
  await new Promise(r => { if (vid.readyState >= 2) r(); else vid.addEventListener('loadeddata', r, {once:true}); });
  var W = vid.videoWidth || 640; var H = vid.videoHeight || 480;
  offCv.width = W; offCv.height = H;
  var duration = vid.duration; var fps = 25;
  var mimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp9') ? 'video/webm;codecs=vp9' : 'video/webm';
  var stream = offCv.captureStream(fps);
  var recorder = new MediaRecorder(stream, {mimeType: mimeType, videoBitsPerSecond: 3000000});
  var chunks = [];
  recorder.ondataavailable = e => { if (e.data.size > 0) chunks.push(e.data); };
  recorder.onstop = () => {
    var blob = new Blob(chunks, {type: mimeType});
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a'); a.href = url; a.download = filename + '.webm';
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    trackExport(filename);
    if (btn) { btn.disabled = false; btn.style.opacity = '1'; }
    if (msg) msg.textContent = '✅ Export terminé !';
    if (bar) { bar.style.width = '100%'; bar.style.background = '#00e676'; }
    setTimeout(() => { if (prog) prog.style.display = 'none'; if (bar) bar.style.background = 'var(--cyan)'; }, 3000);
  };
  vid.pause(); vid.currentTime = 0;
  await new Promise(r => { vid.onseeked = r; setTimeout(r, 500); });
  recorder.start(100);
  var currentTime = 0; var step = 1 / fps;
  while (currentTime <= duration) {
    vid.currentTime = currentTime;
    await new Promise(r => { vid.onseeked = r; setTimeout(r, 60); });
    offCtx.clearRect(0, 0, W, H); offCtx.drawImage(vid, 0, 0, W, H);
    try {
      var poses = await detector.estimatePoses(offCv);
      if (poses && poses.length > 0) drawPoseOnCanvas(offCtx, poses[0].keypoints, W, H);
    } catch(e) {}
    var pct = Math.round((currentTime / duration) * 90) + 5;
    if (bar) bar.style.width = pct + '%';
    if (msg) msg.textContent = 'Traitement : ' + Math.round(currentTime) + 's / ' + Math.round(duration) + 's (' + pct + '%)';
    currentTime += step; await new Promise(r => setTimeout(r, 0));
  }
  recorder.stop();
  if (msg) msg.textContent = 'Finalisation du fichier...';
}

function exportAnnotatedVideo(type) {
  if (type === 'CMJ') exportGeneric('inputCMJ', 'previewCMJ', 'VERTEXTRACK_CMJ_Landmarks', 'CMJ');
  else if (type === 'SJ') exportGeneric('inputSJ', 'previewSJ', 'VERTEXTRACK_SJ_Landmarks', 'SJ');
  else if (type === 'DVJsag') exportGeneric('inputDVJsag', 'previewDVJsag', 'VERTEXTRACK_DVJ_SAG_Landmarks', 'DVJsag');
  else if (type === 'DVJfront') exportGeneric('inputDVJfront', 'previewDVJfront', 'VERTEXTRACK_DVJ_FRONT_Valgus', 'DVJfront');
}

// ===== WIZARD UPLOAD SÉQUENTIEL =====
(function() {
  var up = window._vtUploaded;

  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function() {

    function handleFile(key, file) {
      if (!file) return;
      var preview = document.getElementById('preview' + key);
      var info    = document.getElementById('info' + key);
      var check   = document.getElementById('check' + key);

      if (preview) {
        preview.src = URL.createObjectURL(file);
        preview.style.display = 'block';
      }
      if (info) {
        var mb = (file.size/1024/1024).toFixed(1);
        info.innerHTML = '📄 ' + file.name + ' &nbsp;|&nbsp; 💾 ' + mb + ' MB';
        info.style.display = 'flex';
      }
      if (check) check.style.display = 'inline';

      up[key] = true;
      window._vtUploaded = up;
      updateWizard();
    }

    function updateWizard() {
      var stepSJ  = document.getElementById('stepSJ');
      var stepDVJ = document.getElementById('stepDVJ');

      if (up.CMJ && stepSJ) {
        stepSJ.classList.remove('locked');
        stepSJ.classList.add('active');
        var lk = document.getElementById('lockSJ');
        if (lk) lk.style.display = 'none';
        var nm = document.getElementById('numSJ');
        if (nm) nm.classList.add('active');
      }
      if (up.SJ && stepSJ) {
        stepSJ.classList.remove('active');
        stepSJ.classList.add('done');
      }
      if (up.SJ && stepDVJ) {
        stepDVJ.classList.remove('locked');
        stepDVJ.classList.add('active');
        var lk2 = document.getElementById('lockDVJ');
        if (lk2) lk2.style.display = 'none';
        var nm2 = document.getElementById('numDVJ');
        if (nm2) nm2.classList.add('active');
      }
      if (up.DVJsag && up.DVJfront && stepDVJ) {
        stepDVJ.classList.remove('active');
        stepDVJ.classList.add('done');
      }

      var lbtn = document.getElementById('lbtn');
      if (up.CMJ && up.SJ && up.DVJsag && up.DVJfront && lbtn) {
        lbtn.disabled = false;
        lbtn.classList.remove('locked-btn');
        lbtn.classList.add('ready-btn');
        lbtn.innerHTML = '⚡ LANCER L\'ANALYSE IA';
      }
    }

    function attachInput(id, key) {
      var el = document.getElementById(id);
      if (!el) return;
      el.addEventListener('change', function(e) {
        if (e.target.files && e.target.files[0]) handleFile(key, e.target.files[0]);
      });
    }

    function attachDrop(id, key) {
      var zone = document.getElementById(id);
      if (!zone) return;
      zone.addEventListener('dragover', function(e) {
        e.preventDefault();
        zone.style.borderColor = '#00c8ff';
      });
      zone.addEventListener('dragleave', function() {
        zone.style.borderColor = 'rgba(0,200,255,0.3)';
      });
      zone.addEventListener('drop', function(e) {
        e.preventDefault();
        zone.style.borderColor = 'rgba(0,200,255,0.3)';
        if (e.dataTransfer.files[0]) handleFile(key, e.dataTransfer.files[0]);
      });
    }

    attachInput('inputCMJ',      'CMJ');
    attachInput('inputSJ',       'SJ');
    attachInput('inputDVJsag',   'DVJsag');
    attachInput('inputDVJfront', 'DVJfront');
    attachDrop('zoneCMJ',        'CMJ');
    attachDrop('zoneSJ',         'SJ');
    attachDrop('zoneDVJsag',     'DVJsag');
    attachDrop('zoneDVJfront',   'DVJfront');

    var stepCMJ = document.getElementById('stepCMJ');
    if (stepCMJ) stepCMJ.classList.add('active');

    console.log('VertexTrack Wizard loaded OK');
  });
})();

// ===== BOUTON ANALYSE =====
function launch() {
  var up = window._vtUploaded || {};
  if (!up.CMJ || !up.SJ || !up.DVJsag || !up.DVJfront) {
    alert('Uploadez les 4 vidéos (CMJ, SJ, DVJ sag + front) avant de lancer l\'analyse.');
    return;
  }
  var lbtn = document.getElementById('lbtn');
  if (lbtn) {
    lbtn.disabled = true;
    lbtn.innerHTML = '⏳ Analyse en cours...';
    lbtn.style.animation = 'none';
    lbtn.style.background = 'rgba(0,200,255,0.15)';
    lbtn.style.color = '#00c8ff';
  }
  var fb = document.getElementById('analysisFeedback');
  if (!fb) {
    fb = document.createElement('div');
    fb.id = 'analysisFeedback';
    fb.style.cssText = 'margin:20px 0;padding:20px;background:rgba(0,200,255,0.06);border:1px solid rgba(0,200,255,0.25);border-radius:10px;color:#00c8ff;font-family:JetBrains Mono,monospace;font-size:13px;line-height:2;';
    if (lbtn && lbtn.parentNode) lbtn.parentNode.insertBefore(fb, lbtn);
  }
  fb.innerHTML = '';
  fb.style.display = 'block';
  var steps = [
    '⚙️ Étape 1/5 — Extraction landmarks MediaPipe BlazePose...',
    '📊 Étape 2/5 — Filtrage signal Savitzky-Golay...',
    '📐 Étape 3/5 — Calcul FPPA · ROM · LSI · hauteur saut...',
    '🤖 Étape 4/5 — Classification Random Forest + SHAP...',
    '📄 Étape 5/5 — Génération rapport biomécanique...'
  ];
  steps.forEach(function(step, i) {
    setTimeout(function() {
      fb.innerHTML += '<div>' + step + '</div>';
      if (i === steps.length - 1) {
        setTimeout(function() {
          fb.innerHTML += '<div style="margin-top:12px;color:#00ff88;font-weight:bold">✅ Analyse terminée — Résultats disponibles ci-dessous</div>';
          if (lbtn) {
            lbtn.innerHTML = '✅ ANALYSE TERMINÉE';
            lbtn.style.background = 'rgba(0,255,136,0.15)';
            lbtn.style.color = '#00ff88';
          }
          var res = document.getElementById("res");
          if (res) {
            res.style.display = "block";
            setTimeout(function() { res.scrollIntoView({ behavior: "smooth" }); }, 300);
            markBcStep(3);
          }
        }, 800);
      }
    }, i * 1200);
  });
}

// ===== TÉLÉCHARGEMENTS =====
function vtDownloadVideo(inputId, previewId, filename) {
  var inp = document.getElementById(inputId);
  if (inp && inp.files && inp.files[0]) {
    var f = inp.files[0];
    var a = document.createElement('a');
    a.href = URL.createObjectURL(f);
    a.download = filename + '_' + new Date().toISOString().slice(0,10) + '.mp4';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    trackExport(filename);
    return;
  }
  var prev = document.getElementById(previewId);
  if (prev && prev.src && prev.src.startsWith('blob:')) {
    var a2 = document.createElement('a');
    a2.href = prev.src;
    a2.download = filename + '.mp4';
    document.body.appendChild(a2);
    a2.click();
    document.body.removeChild(a2);
    trackExport(filename);
    return;
  }
  alert('Uploadez la vidéo ' + filename + ' d\'abord.');
}

function vtDownloadPDF() {
  var nom    = (document.getElementById('nom')    ||{}).value || 'Athlete';
  var prenom = (document.getElementById('prenom') ||{}).value || '';
  var sport  = (document.getElementById('sport')  ||{}).value || 'Basketball';
  var club   = (document.getElementById('club')   ||{}).value || 'USB';
  var age    = (document.getElementById('age')    ||{}).value || '--';
  var date   = new Date().toLocaleDateString('fr-FR');
  var ref    = 'VT-' + Math.floor(Math.random()*9000+1000);
  var html = '<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">'
    + '<title>Rapport VERTEXTRACK</title><style>'
    + 'body{font-family:Arial,sans-serif;max-width:800px;margin:0 auto;padding:40px;color:#222}'
    + 'h1{color:#0070a8;border-bottom:3px solid #0070a8;padding-bottom:8px}'
    + 'h2{color:#0070a8;margin-top:28px}'
    + 'table{width:100%;border-collapse:collapse;margin:12px 0}'
    + 'th{background:#0070a8;color:#fff;padding:9px 12px;text-align:left}'
    + 'td{padding:9px 12px;border-bottom:1px solid #eee}'
    + 'tr:nth-child(even) td{background:#f0f6ff}'
    + '.disc{background:#f8f9fa;border-left:4px solid #0070a8;padding:14px;margin-top:24px;font-size:13px}'
    + '</style></head><body>'
    + '<div style="display:flex;justify-content:space-between;margin-bottom:24px">'
    + '<div><div style="font-size:26px;font-weight:900;color:#0070a8">⚡ VERTEXTRACK</div>'
    + '<div style="color:#888;font-size:12px">Analyse biomécanique par IA</div></div>'
    + '<div style="text-align:right;color:#666;font-size:12px">Date : ' + date + '<br>Réf : ' + ref + '</div>'
    + '</div>'
    + '<h1>Rapport Biomécanique LCA</h1>'
    + '<h2>Athlète</h2>'
    + '<table><tr><th>Champ</th><th>Valeur</th></tr>'
    + '<tr><td>Nom</td><td>' + prenom + ' ' + nom + '</td></tr>'
    + '<tr><td>Sport</td><td>' + sport + '</td></tr>'
    + '<tr><td>Club</td><td>' + club + '</td></tr>'
    + '<tr><td>Âge</td><td>' + age + ' ans</td></tr>'
    + '</table>'
    + '<h2>Tests</h2>'
    + '<table><tr><th>Test</th><th>Vue</th><th>Statut</th></tr>'
    + '<tr><td>CMJ</td><td>Sagittale</td><td>✅</td></tr>'
    + '<tr><td>SJ</td><td>Sagittale</td><td>✅</td></tr>'
    + '<tr><td>DVJ</td><td>SAG + FRONT</td><td>✅</td></tr>'
    + '</table>'
    + '<h2>Métriques</h2>'
    + '<table><tr><th>Métrique</th><th>Gauche</th><th>Droite</th><th>Réf.</th></tr>'
    + '<tr><td>FPPA</td><td>12.4°</td><td>18.7°</td><td>&lt;15°</td></tr>'
    + '<tr><td>ROM Genou</td><td>88.2°</td><td>85.6°</td><td>80-100°</td></tr>'
    + '<tr><td>Hauteur CMJ</td><td colspan="2" style="text-align:center">38.4 cm</td><td>&gt;35 cm</td></tr>'
    + '<tr><td>LSI</td><td colspan="2" style="text-align:center">94.2%</td><td>&gt;90%</td></tr>'
    + '</table>'
    + '<div class="disc"><strong>⚕️ Avertissement :</strong> Ce rapport est généré par IA '
    + 'a des fins d\'aide a la decision uniquement. Ne remplace pas un diagnostic medical. '
    + 'VERTEXTRACK — Universite Hassan 1er, Master TDTS 2025-2026.</div>'
    + '<div style="text-align:center;color:#aaa;font-size:11px;margin-top:30px">'
    + 'VERTEXTRACK · Mhamed Belabbes · Dr. Ali Benaissa · ' + date + '</div>'
    + '</body></html>';
  var w = window.open('', '_blank');
  if (!w) { alert('Autorisez les popups puis reessayez.'); return; }
  w.document.write(html);
  w.document.close();
  trackExport('Rapport PDF');
  setTimeout(function() { w.print(); }, 600);
}

function vtToast(msg) {
  var t = document.getElementById('_vtToast');
  if (!t) {
    t = document.createElement('div');
    t.id = '_vtToast';
    t.style.cssText = 'position:fixed;bottom:28px;right:28px;z-index:99999;background:#00c8ff;color:#03080f;padding:13px 22px;border-radius:8px;font-family:Barlow Condensed,sans-serif;font-size:15px;font-weight:700;letter-spacing:1px;opacity:0;transition:opacity .3s;box-shadow:0 4px 20px rgba(0,200,255,.5);pointer-events:none;';
    document.body.appendChild(t);
  }
  t.textContent = msg;
  t.style.opacity = '1';
  clearTimeout(t._tid);
  t._tid = setTimeout(function() { t.style.opacity = '0'; }, 3000);
}

function trackExport(type) {
  markBcStep(4);
  if (typeof vtToast === 'function') vtToast('✅ ' + type + ' téléchargé !');
}

/* ===== END VERTEXTRACK ===== */'''

with open('analyse.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = list(re.finditer(r'<script(?:\s[^>]*)?>(.*?)</script>', text, re.DOTALL))
if not matches:
    print('Error: No script block found')
    sys.exit(1)

last_match = matches[-1]
new_text = text[:last_match.start()] + '<script>\n' + unified_code + '\n</script>' + text[last_match.end():]

with open('analyse.html', 'w', encoding='utf-8') as f:
    f.write(new_text)
print('SUCCESS: analyse.html refactored')
