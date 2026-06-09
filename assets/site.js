
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

// node-graph background — very light force-directed canvas mesh (no deps).
// Charge repulsion + link springs settle an organic graph that drifts gently; dim by default.
(function(){
  if(RM) return;                                  // reduced-motion: leave the host empty
  var hosts=document.querySelectorAll('.ngbg'); if(!hosts.length) return;
  var STEEL=[110,168,255], PERI=[129,134,196];
  function rgba(c,a){return 'rgba('+c[0]+','+c[1]+','+c[2]+','+a+')';}
  hosts.forEach(function(host){
    var canvas=document.createElement('canvas'); host.appendChild(canvas);
    var ctx=canvas.getContext('2d'); if(!ctx) return;
    var W=0,H=0,dpr=1,N=[],E=[],REST=120,KR=9000,MAXV=6,mouse={x:-9999,y:-9999},raf=0;
    var KS=0.02,DAMP=0.88,PAD=12,JIT=0.04,HOVERD=190,BRIGHT=0.5,LBASE=0.2,NBASE=0.32;
    function step(settling){
      var i,j,a,b,dx,dy,d2,d,f,ux,uy;
      for(i=0;i<N.length;i++)for(j=i+1;j<N.length;j++){a=N[i];b=N[j];dx=a.x-b.x;dy=a.y-b.y;d2=dx*dx+dy*dy||0.01;d=Math.sqrt(d2);
        f=KR/d2;ux=dx/d;uy=dy/d;a.vx+=ux*f;a.vy+=uy*f;b.vx-=ux*f;b.vy-=uy*f;}
      for(i=0;i<E.length;i++){a=N[E[i][0]];b=N[E[i][1]];dx=b.x-a.x;dy=b.y-a.y;d=Math.hypot(dx,dy)||0.01;f=(d-REST)*KS;ux=dx/d;uy=dy/d;
        a.vx+=ux*f;a.vy+=uy*f;b.vx-=ux*f;b.vy-=uy*f;}
      for(i=0;i<N.length;i++){var nd=N[i];
        if(!settling){nd.vx+=(Math.random()-0.5)*JIT;nd.vy+=(Math.random()-0.5)*JIT;}
        nd.vx*=DAMP;nd.vy*=DAMP;
        if(nd.vx>MAXV)nd.vx=MAXV;if(nd.vx<-MAXV)nd.vx=-MAXV;if(nd.vy>MAXV)nd.vy=MAXV;if(nd.vy<-MAXV)nd.vy=-MAXV;
        nd.x+=nd.vx;nd.y+=nd.vy;
        if(nd.x<PAD){nd.x=PAD;nd.vx*=-0.5;} if(nd.x>W-PAD){nd.x=W-PAD;nd.vx*=-0.5;}
        if(nd.y<PAD){nd.y=PAD;nd.vy*=-0.5;} if(nd.y>H-PAD){nd.y=H-PAD;nd.vy*=-0.5;}}
    }
    function build(){
      var n=Math.max(16,Math.min(40,Math.round(W*H/18000)));
      var sp=Math.sqrt(W*H/n)*0.95; REST=sp; KR=sp*sp*0.85; MAXV=sp*0.05;
      N=[];E=[];
      for(var i=0;i<n;i++) N.push({x:Math.random()*W,y:Math.random()*H,vx:0,vy:0,z:0.6+Math.random()*0.6,s:(i%2)});
      for(var i2=1;i2<n;i2++) E.push([i2,(Math.random()*i2)|0]);
      var ex=Math.round(n*0.6);
      for(var k=0;k<ex;k++){var a=(Math.random()*n)|0,b=(Math.random()*n)|0; if(a!==b)E.push([a,b]);}
      for(var s=0;s<170;s++) step(true);            // pre-settle before first paint
    }
    function bri(px,py){if(mouse.x<-9000)return 0;var d=Math.hypot(mouse.x-px,mouse.y-py);if(d>=HOVERD)return 0;return (1-d/HOVERD)*BRIGHT;}
    function draw(){
      ctx.clearRect(0,0,W,H);ctx.lineWidth=1;var i,a,b;
      for(i=0;i<E.length;i++){a=N[E[i][0]];b=N[E[i][1]];var mb=bri((a.x+b.x)/2,(a.y+b.y)/2);
        ctx.strokeStyle=rgba(STEEL,Math.min(0.8,LBASE+mb));ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();}
      for(i=0;i<N.length;i++){var nd=N[i];var al=Math.min(0.9,(NBASE+bri(nd.x,nd.y))*nd.z);
        ctx.fillStyle=rgba(nd.s?STEEL:PERI,al);ctx.beginPath();ctx.arc(nd.x,nd.y,1.1+nd.z*1.5,0,6.2832);ctx.fill();}
    }
    function tick(){if(W&&H){step(false);draw();}raf=requestAnimationFrame(tick);}
    function resize(){var r=host.getBoundingClientRect();if(!r.width||!r.height)return;
      dpr=Math.min(window.devicePixelRatio||1,2);W=r.width;H=r.height;canvas.width=W*dpr;canvas.height=H*dpr;
      canvas.style.width=W+'px';canvas.style.height=H+'px';ctx.setTransform(dpr,0,0,dpr,0,0);build();}
    try{new ResizeObserver(resize).observe(host);}catch(e){addEventListener('resize',resize);}
    resize();
    document.addEventListener('mousemove',function(e){var r=host.getBoundingClientRect();var x=e.clientX-r.left,y=e.clientY-r.top;
      if(x>=0&&x<=W&&y>=0&&y<=H){mouse.x=x;mouse.y=y;}else{mouse.x=-9999;mouse.y=-9999;}},{passive:true});
    raf=requestAnimationFrame(tick);
  });
})();
