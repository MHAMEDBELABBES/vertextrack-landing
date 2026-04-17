function drawPoseOnCanvas(ctx, kps, W, H) {
  var hip=kps[11], knee=kps[13], ank=kps[15];
  var fppa=180, badMov=false;
  if (hip&&knee&&ank&&hip.score>0.4&&knee.score>0.4&&ank.score>0.4) {
    var v1={x:hip.x-knee.x,y:hip.y-knee.y};
    var v2={x:ank.x-knee.x,y:ank.y-knee.y};
    var d=v1.x*v2.x+v1.y*v2.y;
    var m=Math.sqrt(v1.x*v1.x+v1.y*v1.y)*Math.sqrt(v2.x*v2.x+v2.y*v2.y);
    fppa=Math.round(Math.acos(Math.min(1,Math.abs(d/m)))*180/Math.PI);
    badMov=fppa<160;
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
    ctx.fillText('FPPA: '+ang+'??',lx+6,ly+16);
    if(badMov){
      ctx.fillStyle='rgba(255,60,60,.15)';ctx.fillRect(knee.x-65,knee.y-52,130,22);
      ctx.strokeStyle='rgba(255,60,60,.7)';ctx.lineWidth=1;ctx.strokeRect(knee.x-65,knee.y-52,130,22);
      ctx.fillStyle='#ff3c3c';ctx.font='bold 10px monospace';ctx.textAlign='center';
      ctx.fillText('??? VALGUS GENOU',knee.x,knee.y-38);ctx.textAlign='left';
    }
  }
}
