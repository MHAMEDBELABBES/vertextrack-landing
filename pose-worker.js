/* VertexTrack Pose Worker */
/* Note: TF.js ne supporte pas les Web Workers dans tous les navigateurs.
   Ce worker gère la communication et le feedback de progression
   pendant que le traitement reste dans le thread principal
   mais de façon non-bloquante via chunks async */

self.onmessage = function(e) {
  var data = e.data;
  
  if (data.type === 'START') {
    self.postMessage({ 
      type: 'STATUS', 
      msg: 'Worker initialisé — traitement en cours...' 
    });
  }
  
  if (data.type === 'PROGRESS') {
    self.postMessage({
      type: 'PROGRESS',
      percent: data.percent,
      frame: data.frame,
      total: data.total
    });
  }
  
  if (data.type === 'COMPLETE') {
    self.postMessage({
      type: 'COMPLETE',
      filename: data.filename
    });
  }
};
