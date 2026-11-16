
const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
// nav scroll state
const nav=document.querySelector('header.nav');
addEventListener('scroll',()=>nav.classList.toggle('stuck',scrollY>20),{passive:true});
// mobile menu
const burger=document.getElementById('burger'),mob=document.getElementById('mobile');
burger?.addEventListener('click',()=>{const o=mob.classList.toggle('open');burger.textContent=o?'✕':'☰';});
mob.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{mob.classList.remove('open');burger.textContent='☰';}));
// staggered reveal
const io=new IntersectionObserver((es)=>{es.forEach(e=>{if(e.isIntersecting){const sibs=[...e.target.parentElement.children].filter(c=>c.classList.contains('rv'));const k=sibs.indexOf(e.target);setTimeout(()=>e.target.classList.add('in'),Math.max(0,k)*80);io.unobserve(e.target);}});},{rootMargin:'0px 0px -8% 0px'});
document.querySelectorAll('.rv').forEach(el=>io.observe(el));
// accelerator bars
const bio=new IntersectionObserver((es)=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');bio.unobserve(e.target);}}),{threshold:.4});
document.querySelectorAll('.acard').forEach(el=>bio.observe(el));
// count-up
const cio=new IntersectionObserver((es)=>{es.forEach(e=>{if(e.isIntersecting){const el=e.target,to=+el.dataset.to;if(RM){el.textContent=to;cio.unobserve(el);return;}let s=null;requestAnimationFrame(function st(t){s=s||t;const p=Math.min(1,(t-s)/1200);el.textContent=Math.round(to*(1-Math.pow(1-p,3)));if(p<1)requestAnimationFrame(st);});cio.unobserve(el);}});},{threshold:.6});
document.querySelectorAll('.ct').forEach(el=>cio.observe(el));
// magnetic buttons
if(false) document.querySelectorAll('.btn,.navcta').forEach(b=>{b.addEventListener('mousemove',e=>{const r=b.getBoundingClientRect();b.style.transform=`translate(${(e.clientX-r.left-r.width/2)*.18}px,${(e.clientY-r.top-r.height/2)*.32}px)`;});b.addEventListener('mouseleave',()=>b.style.transform='');});
// custom cursor
const cur=document.querySelector('.cur'),ring=document.querySelector('.cur-r');
if(false && cur){
  let mx=innerWidth/2,my=innerHeight/2,rx=mx,ry=my;
  addEventListener('mousemove',e=>{mx=e.clientX;my=e.clientY;cur.style.transform=`translate(${mx}px,${my}px) translate(-50%,-50%)`;});
  (function loop(){rx+=(mx-rx)*.18;ry+=(my-ry)*.18;ring.style.transform=`translate(${rx}px,${ry}px) translate(-50%,-50%)`;requestAnimationFrame(loop);})();
  document.querySelectorAll('a,button,[data-cursor]').forEach(el=>{el.addEventListener('mouseenter',()=>ring.classList.add('big'));el.addEventListener('mouseleave',()=>ring.classList.remove('big'));});
}

// clickable cards
document.querySelectorAll('[data-href]').forEach(el=>el.addEventListener('click',e=>{if(e.target.closest('a'))return;location.href=el.dataset.href;}));

// theme — default is dark everywhere (set inline in <head>); this button toggles & persists the choice
(function(){
  function applyTheme(t){document.documentElement.setAttribute('data-theme',t);try{(matchMedia('(max-width:768px), (hover:none) and (pointer:coarse)').matches?sessionStorage:localStorage).setItem('uvTheme',t);}catch(e){}}  /* phones: dark by default every visit; toggle lasts for the session */
  function toggle(){applyTheme(document.documentElement.getAttribute('data-theme')==='light'?'dark':'light');}
  var row=document.querySelector('header.nav .row');
  if(row){
    var navcta=row.querySelector('.navcta'), burger=row.querySelector('.burger');
    var grp=document.createElement('div'); grp.className='navright';
    var tb=document.createElement('button'); tb.className='themebtn'; tb.type='button'; tb.setAttribute('aria-label','Toggle light or dark theme'); tb.title='Toggle theme';
    tb.innerHTML='<svg class="sun" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg><svg class="moon" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>';
    tb.addEventListener('click',toggle);
    grp.appendChild(tb);
    if(navcta) grp.appendChild(navcta);
    if(burger) grp.appendChild(burger);
    row.appendChild(grp);
  }
})();

// device-platform tabs
(function(){
  var tabs=[].slice.call(document.querySelectorAll('.tab[data-tab]'));
  if(!tabs.length)return;
  var panels=[].slice.call(document.querySelectorAll('.tpanel'));
  function activate(key){
    tabs.forEach(function(t){var on=t.dataset.tab===key;t.classList.toggle('active',on);t.setAttribute('aria-selected',on?'true':'false');});
    panels.forEach(function(p){var on=p.id===key;p.classList.toggle('active',on);if(on)p.querySelectorAll('.rv').forEach(function(e){e.classList.add('in');});});
  }
  tabs.forEach(function(t){t.addEventListener('click',function(){activate(t.dataset.tab);if(history.replaceState)history.replaceState(null,'','#'+t.dataset.tab);});});
  function fromHash(scroll){
    var hk=(location.hash||'').replace('#',''),el=hk&&document.getElementById(hk);
    if(!(el&&el.classList.contains('tpanel')))return;
    activate(hk);
    if(scroll){var bar=document.querySelector('.tabwrap');if(bar)setTimeout(function(){bar.scrollIntoView({behavior:'smooth',block:'start'});},30);}
  }
  fromHash(!!location.hash);
  window.addEventListener('hashchange',function(){fromHash(true);});
})();

// node-graph background — page-wide 3D force-graph look (no deps). A node "ball" with
// nearest-neighbour links, perspective projection, slow auto-rotation, subtle cursor
// parallax, and a gentle zoom-in driven by scroll position. Extremely faint.
(function(){
  if(RM) return;                                  // reduced-motion: leave it off
  var hosts=document.querySelectorAll('.ngbg'); if(!hosts.length) return;
  var STEEL=[110,168,255], PERI=[140,146,210];
  function rgba(c,a){return 'rgba('+c[0]+','+c[1]+','+c[2]+','+a+')';}
  hosts.forEach(function(host){
    var canvas=document.createElement('canvas'); host.appendChild(canvas);
    var ctx=canvas.getContext('2d'); if(!ctx) return;
    var W=0,H=0,dpr=1,P=[],E=[],R=200,CAM=480,cx=0,cy=0,raf=0;
    var SX=[],SY=[],SC=[],ORD=[];
    var autoY=0,TILT=0.28,pX=0,pY=0,mnx=0,mny=0,has=false,zoom=1,zoomT=1;
    function build(){
      var n=Math.max(150,Math.min(330,Math.round(W*H/2600)));
      R=Math.min(W,H)*0.46; CAM=2.4*R; cx=W/2; cy=H/2;
      P=[];
      for(var i=0;i<n;i++){
        var r=R*Math.pow(Math.random(),1/3), th=Math.random()*6.2832, ph=Math.acos(2*Math.random()-1), sp=Math.sin(ph);
        P.push({x:r*sp*Math.cos(th), y:r*sp*Math.sin(th), z:r*Math.cos(ph), s:(i%2)});
      }
      E=[]; var seen={};
      for(var i2=0;i2<n;i2++){
        var best=[];
        for(var j2=0;j2<n;j2++){ if(j2===i2)continue;
          var dx=P[i2].x-P[j2].x,dy=P[i2].y-P[j2].y,dz=P[i2].z-P[j2].z,dd=dx*dx+dy*dy+dz*dz;
          if(best.length<3){best.push([dd,j2]); best.sort(function(a,b){return a[0]-b[0];});}
          else if(dd<best[2][0]){best[2]=[dd,j2]; best.sort(function(a,b){return a[0]-b[0];});}
        }
        for(var b2=0;b2<best.length;b2++){var k=best[b2][1],lo=Math.min(i2,k),hi=Math.max(i2,k),key=lo+'-'+hi;
          if(!seen[key]){seen[key]=1; E.push([lo,hi]);}}
      }
      SX=new Array(n); SY=new Array(n); SC=new Array(n); ORD=[]; for(var o=0;o<n;o++)ORD.push(o);
    }
    function resize(){var r=host.getBoundingClientRect(); if(!r.width||!r.height)return;
      dpr=Math.min(window.devicePixelRatio||1,2); W=r.width; H=r.height;
      canvas.width=W*dpr; canvas.height=H*dpr; canvas.style.width=W+'px'; canvas.style.height=H+'px';
      ctx.setTransform(dpr,0,0,dpr,0,0); build();}
    function onScroll(){var max=(document.documentElement.scrollHeight-innerHeight)||1; var p=window.scrollY/max;
      if(p<0)p=0; if(p>1)p=1; zoomT=1+p*0.85;}
    function tick(){
      var n=P.length;
      if(W&&H&&n){
        autoY+=0.0012; zoom+=(zoomT-zoom)*0.05;
        pX+=((has?mnx*0.5:0)-pX)*0.04; pY+=((has?mny*0.4:0)-pY)*0.04;
        var aY=autoY+pX,aX=TILT+pY,cyy=Math.cos(aY),syy=Math.sin(aY),cxx=Math.cos(aX),sxx=Math.sin(aX),i,p,sc;
        for(i=0;i<n;i++){p=P[i];
          var x2=p.x*cyy+p.z*syy, z2=-p.x*syy+p.z*cyy, y2=p.y*cxx-z2*sxx, z3=p.y*sxx+z2*cxx;
          sc=CAM/(CAM-z3); SX[i]=cx+x2*sc*zoom; SY[i]=cy-y2*sc*zoom; SC[i]=sc;}
        ctx.clearRect(0,0,W,H); ctx.lineWidth=1;
        for(i=0;i<E.length;i++){var a=E[i][0],b=E[i][1],s=(SC[a]+SC[b])/2,al=(s-0.62)*0.16;
          if(al>0){ctx.strokeStyle=rgba(STEEL,al>0.11?0.11:al); ctx.beginPath(); ctx.moveTo(SX[a],SY[a]); ctx.lineTo(SX[b],SY[b]); ctx.stroke();}}
        ORD.sort(function(p,q){return SC[p]-SC[q];});
        for(var o=0;o<n;o++){i=ORD[o]; sc=SC[i]; var al=(sc-0.55)*0.28; if(al<0.035)al=0.035; if(al>0.22)al=0.22;
          var rr=(sc-0.5)*2.1*zoom; if(rr<0.5)rr=0.5;
          ctx.fillStyle=rgba(P[i].s?STEEL:PERI,al); ctx.beginPath(); ctx.arc(SX[i],SY[i],rr,0,6.2832); ctx.fill();}
      }
      raf=requestAnimationFrame(tick);
    }
    try{new ResizeObserver(resize).observe(host);}catch(e){addEventListener('resize',resize);}
    resize();
    addEventListener('scroll',onScroll,{passive:true}); onScroll();
    document.addEventListener('mousemove',function(e){if(e.clientX>=0&&e.clientX<=W&&e.clientY>=0&&e.clientY<=H){has=true; mnx=e.clientX/W-0.5; mny=e.clientY/H-0.5;}else{has=false;}},{passive:true});
    raf=requestAnimationFrame(tick);
  });
})();

/* ===== MOCK: hero live AgentMesh console ===== */
(function(){
  var root=document.querySelector('.meshviz'); if(!root) return;
  var PHONE=matchMedia('(max-width:768px)').matches;  /* phones run the live console too, with fewer dots per row */
  var PER=64, dots=[], byJob={};
  [].slice.call(root.querySelectorAll('.mv-row')).forEach(function(r){var box=r.querySelector('.mv-dots'), job=r.dataset.job; byJob[job]=[];
    for(var k=0;k<PER;k++){var d=document.createElement('i'); box.appendChild(d); dots.push(d); byJob[job].push(d);} });
  var N=dots.length;
  var cW=root.querySelector('.mv-c-watch'), cR=root.querySelector('.mv-c-retry'), cF=root.querySelector('.mv-c-flag'), cO=root.querySelector('.mv-c-off'), cD=root.querySelector('.mv-c-dec'), cL=root.querySelector('.mv-c-lat'), last=root.querySelector('.mv-last');
  /* channel budget — always sums to N (512): watching + retrying + flagged + offline */
  var OFFLINE=8, FLAGGED=15, R_MIN=4, R_MAX=23;   /* watching = 512-15-8-retrying = 466–485 */
  var RETRY=R_MIN+Math.floor(Math.random()*(R_MAX-R_MIN+1));
  function pick(arr){return arr.splice(Math.floor(Math.random()*arr.length),1)[0];}
  function of(c){return dots.filter(function(d){return d.className===c;});}
  function isFlag(d){return d.className==='f'||d.className==='d'||d.className==='a'||d.className==='b';}
  dots.forEach(function(d){d.className='w';});
  var offs=dots.slice(); for(var k=0;k<OFFLINE;k++) pick(offs).className='off';
  function balance(){
    var fl=dots.filter(isFlag).length, f=of('f'), w;
    while(fl>FLAGGED&&f.length){pick(f).className='w';fl--;}
    w=of('w'); while(fl<FLAGGED&&w.length){pick(w).className='f';fl++;}
    var rt=of('rt'); w=of('w');
    while(rt.length>RETRY){pick(rt).className='w'; rt=of('rt');}
    while(of('rt').length<RETRY&&w.length){pick(w).className='rt';}
  }
  function counts(){
    balance();
    var n={w:0,rt:0,fl:0,off:0}; dots.forEach(function(d){var c=d.className; if(c==='w')n.w++; else if(c==='rt')n.rt++; else if(c==='off')n.off++; else n.fl++;});
    cW.textContent=n.w; cR.textContent=n.rt; cF.textContent=n.fl; cO.textContent=n.off; cD.textContent=decisions.toLocaleString();
  }
  function say(txt){last.classList.add('fade'); setTimeout(function(){last.textContent=txt; last.classList.remove('fade');},250);}
  function ambient(){
    RETRY=Math.max(R_MIN,Math.min(R_MAX,RETRY+Math.round((Math.random()-.5)*6)));
    /* channels recover and others start retrying: swap a few, and move a few flags around */
    var rt=of('rt'), w=of('w'), f=of('f');
    for(var k=0;k<Math.min(5,rt.length,w.length);k++){pick(rt).className='w'; pick(w).className='rt';}
    w=of('w'); for(var k2=0;k2<Math.min(2,f.length,w.length);k2++){pick(f).className='w'; pick(w).className='f';}
    counts();
  }
  var tiles=[].slice.call(root.querySelectorAll('.mv-tile'));
  var EV={
    robot:[['a','Lane A · part diverted to rework','11.8 ms','drafting work order · joint 3'],['a','Lane A · cell slowed to safe speed band','10.9 ms','drafting gearbox inspection'],['b','Lane B · request: stop cell at end of cycle','13.1 ms','drafting WO · servo 4']],
    vision:[['a','Lane A · defect found · panel held','9.4 ms','drafting NCR · cell 6'],['a','Lane A · weld bead off-spec · part to rework','8.7 ms','adding image + signal to evidence'],['b','Lane B · lens contamination · request cleaning','12.2 ms','drafting maintenance note']],
    weld:[['a','Lane A · module diverted to rework','11.6 ms','drafting NCR-7714'],['a','Lane A · tab weld re-queued','10.2 ms','updating traceability record'],['b','Lane B · request: change protective glass','12.8 ms','drafting WO · head 5']],
    pump:[['b','Lane B · request: swap to standby at lot boundary','17.3 ms','drafting WO F-3318'],['b','Lane B · bearing tones rising · facilities notified','16.4 ms','checking supplier units'],['a','Lane A · tool idle hint to scheduler','14.9 ms','evidence pack updated']],
    test:[['b','Lane B · flag to test conductor','19.8 ms','drafting post-test report'],['b','Lane B · strain trend matches run 112','18.5 ms','attaching spectrogram to run record'],['a','Lane A · channel marked for review','15.0 ms','drafting test-data note']],
    net:[['b','Lane B · unusual write · OT team notified','14.2 ms','evidence pack updated'],['a','Lane A · unknown laptop quarantined (IT side)','9.8 ms','drafting incident record'],['b','Lane B · firmware change outside window','15.6 ms','drafting change review']],
    formation:[['a','Lane A · cell held for extended aging','12.4 ms','drafting grading note · F-12'],['b','Lane B · self-discharge cluster · request review','16.1 ms','drafting quality record'],['a','Lane A · cell re-binned to lower grade','11.0 ms','updating traceability record']],
    agv:[['a','Lane A · AGV 7 rerouted around aisle 4','8.9 ms','drafting wheel-motor WO'],['b','Lane B · battery temp high · request return to dock','13.7 ms','drafting battery health note'],['a','Lane A · AGV 3 speed capped in shared zone','9.6 ms','evidence pack updated']],
    layup:[['a','Lane A · ply wrinkle · panel held for review','10.4 ms','drafting NCR · layup L-1'],['b','Lane B · cure oven ramp off-profile · request hold','16.8 ms','attaching thermal trace to record'],['a','Lane A · fibre gap flagged · ply re-queued','9.9 ms','updating traceability record']],
    storage:[['b','Lane B · off-gas rising · alarm to fire panel','14.6 ms','drafting incident record · BS-9'],['b','Lane B · cell temp spread · request derate','15.2 ms','drafting inspection note'],['a','Lane A · string marked for next inspection','11.3 ms','evidence pack updated']],
    drone:[['a','Lane A · flight held · wind above limit','8.6 ms','logging decision to evidence'],['b','Lane B · motor 3 vibration · request inspection','13.9 ms','drafting WO · D-2'],['a','Lane A · battery swap queued before next flight','9.2 ms','drafting battery health note']],
    chiller:[['b','Lane B · request: stage backup chiller','18.2 ms','drafting WO · CH-2'],['a','Lane A · setpoint trim within approved band','12.7 ms','logging energy saving'],['b','Lane B · compressor current drift · facilities notified','17.6 ms','drafting inspection plan']]};
  var LBL={w:'watching',d:'deciding',a:'Lane A acted',b:'Lane B request',r:'drafting'};
  var decisions=1840+Math.floor(Math.random()*60), RMo=matchMedia('(prefers-reduced-motion: reduce)').matches;
  function setTile(t,st,w){t.setAttribute('data-s',st); t.querySelector('.mv-st').textContent=LBL[st]; t.querySelector('.mv-bar i').style.width=w+'%';}
  var busy={};
  function event(){
    var free=tiles.filter(function(t){return !busy[t.dataset.job];}); if(!free.length) return;
    var t=free[Math.floor(Math.random()*free.length)], job=t.dataset.job, opts=EV[job], ev=opts[Math.floor(Math.random()*opts.length)], name=t.querySelector('b').textContent;
    var row=(byJob[t.dataset.row||job]||dots).filter(function(x){return x.className==='w'||x.className==='f';}), d=row[Math.floor(Math.random()*row.length)]; if(!d) return; busy[job]=1;
    d.className='d'; setTile(t,'d',60); counts(); say(name+' · signal flagged · deciding…');
    setTimeout(function(){ var ms=(18+Math.random()*8).toFixed(1)+' ms'; d.className=ev[0]; setTile(t,ev[0],100); decisions++; if(cL) cL.textContent=ms; counts(); say(name+' → '+ev[1]+' · '+ms); },900);
    setTimeout(function(){ setTile(t,'r',75); d.className='w'; counts(); say(name+' · '+ev[3]); },2600);
    setTimeout(function(){ setTile(t,'w',20+Math.random()*30); busy[job]=0; counts(); },4400);
  }
  tiles.forEach(function(t){setTile(t,'w',20+Math.random()*40);});
  counts();
  if(RMo) return;
  setInterval(ambient,700); setInterval(event,1100); setTimeout(event,300); setTimeout(event,900);
})();

/* ===== MOCK: pilot form → mailto (no backend; nothing sent until the visitor presses send) ===== */
document.querySelectorAll('form.pilotform').forEach(function(f){
  f.addEventListener('submit',function(e){
    e.preventDefault();
    var seg=f.seg.value, stage=f.stage.value, what=(f.what.value||'').trim();
    var subj='Pilot on your line — '+seg;
    var body='Industry: '+seg+'\nWhere we are: '+stage+'\nWhat to watch first: '+(what||'(to discuss)')+'\n\nName:\nCompany:\nPhone:\n';
    location.href='mailto:'+unm(f.getAttribute('data-m'))+'?subject='+encodeURIComponent(subj)+'&body='+encodeURIComponent(body);
  });
});

/* ===== hero: drone ship starts just off the left edge of the screen ===== */
(function(){
  var sail=document.querySelector('.dv-sail'); if(!sail) return;
  var svg=sail.ownerSVGElement; var r=svg.getBoundingClientRect(); if(!r.width) return;
  var units=(r.left+r.width*0.30)/(r.width/330);     /* px from screen edge → viewBox units, plus the boat's own length */
  sail.style.setProperty('--dv-from',(-Math.round(units))+'px');
})();

/* ===== email: the address is never in the page source; decoded here for real visitors ===== */
function unm(t){ return t ? t.split('').reverse().join('').replace('|','@') : ''; }
document.querySelectorAll('[data-m]').forEach(function(el){
  if (el.tagName==='FORM') return;
  var a=unm(el.getAttribute('data-m'));
  if (el.tagName==='A'){ var sj=el.getAttribute('data-subject'); el.setAttribute('href','mailto:'+a+(sj?'?subject='+encodeURIComponent(sj):'')); }
  else { el.textContent=a; }
});
