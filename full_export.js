async function exportAnnotatedVideo() {
  var vid = document.getElementById('v-CMJ');
  var btn = document.getElementById('exportVidBtn');
  var prog = document.getElementById('exportProgress');
  var msg  = document.getElementById('exportMsg');
  var bar  = document.getElementById('exportBar');

  if (!vid || !vid.src || vid.src === window.location.href) {
    alert('Uploadez une vid├®o CMJ d\'abord.');
    return;
  }

  // V├®rifier support MediaRecorder
  if (!window.MediaRecorder) {
    alert('Votre navigateur ne supporte pas l\'export vid├®o. Utilisez Chrome.');
    return;
  }

  prog.style.display = 'block';
  msg.textContent = 'Chargement du mod├¿le IA...';
  bar.style.width = '5%';
  btn.disabled = true;
  btn.style.opacity = '0.6';

  // Initialiser d├®tecteur si pas encore fait
  if (!detector) {
    try {
      await initDetector();
    } catch(e) {
      msg.textContent = 'ÔÜá Erreur mod├¿le: ' + e.message;
      btn.disabled = false; btn.style.opacity = '1';
      return;
    }
  }

  // Canvas offscreen pour dessiner vid├®o + landmarks
  var offCv = document.createElement('canvas');
  var offCtx = offCv.getContext('2d');

  // Attendre m├®tadonn├®es vid├®o
  await new Promise(function(resolve) {
    if (vid.readyState >= 2) { resolve(); return; }
    vid.addEventListener('loadeddata', resolve, {once:true});
  });

  var W = vid.videoWidth  || vid.clientWidth  || 640;
  var H = vid.videoHeight || vid.clientHeight || 480;
  offCv.width = W; offCv.height = H;

  var duration = vid.duration;
  var fps = 25;
  var mimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp9')
    ? 'video/webm;codecs=vp9' : 'video/webm';

  var stream   = offCv.captureStream(fps);
  var recorder = new MediaRecorder(stream, {mimeType: mimeType, videoBitsPerSecond: 2500000});
  var chunks   = [];

  recorder.ondataavailable = function(e) { if (e.data.size > 0) chunks.push(e.data); };

  recorder.onstop = function() {
    var blob = new Blob(chunks, {type: mimeType});
    var url  = URL.createObjectURL(blob);
    var a    = document.createElement('a');
    a.href = url;
    a.download = 'VERTEXTRACK_' + cur + '_landmarks.webm';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    btn.disabled = false; btn.style.opacity = '1';
    msg.textContent = 'Ô£ô Vid├®o t├®l├®charg├®e avec succ├¿s !';
    bar.style.width = '100%'; bar.style.background = 'var(--green)';
    setTimeout(function() {
      prog.style.display = 'none';
      bar.style.background = 'var(--cyan)';
      bar.style.width = '0%';
    }, 4000);
  };

  // Mettre la vid├®o en pause et revenir au d├®but
  vid.pause();
  vid.currentTime = 0;
  await new Promise(function(r) {
    vid.onseeked = r;
    setTimeout(r, 500);
  });

  msg.textContent = 'Enregistrement en cours...';
  bar.style.width = '10%';
  recorder.start(100); // collecter des chunks toutes les 100ms

  var frameInterval = 1 / fps;
  var currentTime   = 0;

  // Boucle frame par frame
  while (currentTime <= duration) {
    // Aller ├á la frame
    vid.currentTime = currentTime;
    await new Promise(function(r) {
      vid.onseeked = r;
      setTimeout(r, 80); // max 80ms par frame
    });

    // Dessiner la frame vid├®o
    offCtx.clearRect(0, 0, W, H);
    offCtx.drawImage(vid, 0, 0, W, H);

    // D├®tecter pose et dessiner landmarks
    try {
      var poses = await detector.estimatePoses(offCv);
      if (poses && poses.length > 0) {
        drawPoseOnCanvas(offCtx, poses[0].keypoints, W, H);
      }
    } catch(e) {}

    // Mise ├á jour barre de progression
    var pct = Math.min(95, Math.round((currentTime / duration) * 90) + 10);
    bar.style.width = pct + '%';
    msg.textContent = 'Export... ' + Math.round(currentTime) + 's / ' + Math.round(duration) + 's  (' + pct + '%)';

    currentTime += frameInterval;

    // Laisser respirer le navigateur
    await new Promise(function(r) { setTimeout(r, 0); });
  }

  recorder.stop();
  msg.textContent = 'Finalisation...';
  bar.style.width = '98%';
}
// DRAG & DROP
window.addEventListener('load', function() {
  var dz = document.querySelector('#z-CMJ .upzone');
  var inp = document.getElementById('f-CMJ');
  if (dz && inp) {
    dz.addEventListener('dragover', function(e) { e.preventDefault(); dz.style.borderColor='var(--cyan)'; });
    dz.addEventListener('dragleave', function() { dz.style.borderColor='rgba(0,200,255,0.3)'; });
    dz.addEventListener('drop', function(e) {
      e.preventDefault(); dz.style.borderColor='rgba(0,200,255,0.3)';
      var f = e.dataTransfer.files[0];
      if (f && f.type.startsWith('video/')) {
        var dt = new DataTransfer(); dt.items.add(f); inp.files = dt.files;
        onFile({target:{files:inp.files}}, 'CMJ');
      }
    });
  }
});
</script>

</body>
</html>
