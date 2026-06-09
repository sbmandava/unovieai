
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
if(!RM) document.querySelectorAll('.btn,.navcta').forEach(b=>{b.addEventListener('mousemove',e=>{const r=b.getBoundingClientRect();b.style.transform=`translate(${(e.clientX-r.left-r.width/2)*.18}px,${(e.clientY-r.top-r.height/2)*.32}px)`;});b.addEventListener('mouseleave',()=>b.style.transform='');});
// custom cursor
const cur=document.querySelector('.cur'),ring=document.querySelector('.cur-r');
if(cur && !RM && matchMedia('(hover:hover)').matches){
  let mx=innerWidth/2,my=innerHeight/2,rx=mx,ry=my;
  addEventListener('mousemove',e=>{mx=e.clientX;my=e.clientY;cur.style.transform=`translate(${mx}px,${my}px) translate(-50%,-50%)`;});
  (function loop(){rx+=(mx-rx)*.18;ry+=(my-ry)*.18;ring.style.transform=`translate(${rx}px,${ry}px) translate(-50%,-50%)`;requestAnimationFrame(loop);})();
  document.querySelectorAll('a,button,[data-cursor]').forEach(el=>{el.addEventListener('mouseenter',()=>ring.classList.add('big'));el.addEventListener('mouseleave',()=>ring.classList.remove('big'));});
}

// clickable cards
document.querySelectorAll('[data-href]').forEach(el=>el.addEventListener('click',e=>{if(e.target.closest('a'))return;location.href=el.dataset.href;}));

// theme — default is set inline in <head> (light on desktop, dark on mobile/touch); this button toggles & persists the choice
(function(){
  function applyTheme(t){document.documentElement.setAttribute('data-theme',t);try{localStorage.setItem('uvTheme',t);}catch(e){}}
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
  var hk=(location.hash||'').replace('#',''),el=hk&&document.getElementById(hk);
  if(el&&el.classList.contains('tpanel'))activate(hk);
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
