
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
