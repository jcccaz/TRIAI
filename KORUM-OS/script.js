// Simple interactivity: clock + start menu
function updateClock(){
  const el=document.getElementById('clock');
  if(!el) return;
  const now=new Date();
  const hh=String(now.getHours()).padStart(2,'0');
  const mm=String(now.getMinutes()).padStart(2,'0');
  el.textContent=`${hh}:${mm}`;
}
setInterval(updateClock,1000);
updateClock();

const startBtn=document.getElementById('startBtn');
const startMenu=document.getElementById('startMenu');
const openStart=document.getElementById('openStart');
const openWelcome=document.getElementById('openWelcome');
const welcomeWindow=document.getElementById('welcome');

function toggleStart(open){
  const isOpen = typeof open === 'boolean' ? open : startMenu.getAttribute('aria-hidden')==='true';
  startMenu.setAttribute('aria-hidden', String(!isOpen));
  startBtn.setAttribute('aria-expanded', String(isOpen));
}

startBtn?.addEventListener('click', ()=> toggleStart());
openStart?.addEventListener('click', ()=> toggleStart(true));
openWelcome?.addEventListener('click', ()=>{
  welcomeWindow?.scrollIntoView({behavior:'smooth',block:'center'});
  toggleStart(false);
});

document.getElementById('showAlert')?.addEventListener('click', ()=>{
  alert('KORUM OS — demo action');
  toggleStart(false);
});

// close start menu on Escape or outside click
document.addEventListener('keydown', e=>{ if(e.key==='Escape') toggleStart(false); });
document.addEventListener('click', e=>{
  if(!startMenu || !startBtn) return;
  if(startMenu.contains(e.target) || startBtn.contains(e.target)) return;
  toggleStart(false);
});

// Click-to-zoom portal and redirect to /council (user-provided behavior)
document.body.addEventListener("click", () => {
  const portal = document.getElementById("portal");
  if (!portal) return;
  portal.classList.add("zoom");
  setTimeout(() => {
    window.location.href = "/council";
  }, 1600);
});

// Sigil-specific click: zoom portal then redirect (user-provided behavior)
document.getElementById("sigil").addEventListener("click", () => {
  const portal = document.getElementById("portal");

  portal.classList.add("zoom");

  setTimeout(() => {
    window.location.href = "/council";
  }, 800);
});

// Core overlay: open with `o`, close on click or Escape
const coreOverlay = document.getElementById('coreOverlay');
function openCore(){ coreOverlay?.classList.add('active'); coreOverlay?.setAttribute('aria-hidden','false'); }
function closeCore(){ coreOverlay?.classList.remove('active'); coreOverlay?.setAttribute('aria-hidden','true'); }

document.addEventListener('keydown', (e)=>{
  if(e.key === 'o') openCore();
  if(e.key === 'Escape') closeCore();
});

coreOverlay?.addEventListener('click', ()=> closeCore());

/* Cinematic reveal: particles + emblem/wordmark entrance */
const canvas = document.getElementById('particles');
let ctx, W, H, particles=[];
function resizeCanvas(){ if(!canvas) return; canvas.width = window.innerWidth; canvas.height = window.innerHeight; W=canvas.width; H=canvas.height; }

function initParticles(){ if(!canvas) return; ctx=canvas.getContext('2d'); resizeCanvas(); particles=[]; for(let i=0;i<70;i++){ particles.push({x:Math.random()*W,y:Math.random()*H*0.6+H*0.2, r:Math.random()*1.6+0.6, vx:(Math.random()-0.5)*0.3, vy:-0.1 - Math.random()*0.4, alpha:0.5+Math.random()*0.6}); } }

function drawParticles(){ if(!ctx) return; ctx.clearRect(0,0,W,H); for(let p of particles){ p.x += p.vx; p.y += p.vy; p.alpha *= 0.997; if(p.y< -30 || p.alpha<0.02){ p.x = Math.random()*W; p.y = H + 20; p.alpha = 0.5 + Math.random()*0.5; p.vx=(Math.random()-0.5)*0.3; p.vy=-0.1 - Math.random()*0.4; }
  ctx.beginPath(); ctx.fillStyle = 'rgba(255,200,120,'+ (p.alpha*0.45) +')'; ctx.arc(p.x,p.y,p.r,0,Math.PI*2); ctx.fill(); }
  requestAnimationFrame(drawParticles);
}

function startCinematic(){ document.documentElement.classList.add('intro'); initParticles(); drawParticles();
  // reveal wordmark letters with stagger
  const word = 'KORUM'; const container = document.getElementById('revealWordmark'); if(container){ container.innerHTML=''; for(let i=0;i<word.length;i++){ const span=document.createElement('span'); span.className='letter'; span.textContent=word[i]; span.style.animationDelay = (0.6 + i*0.12)+'s'; container.appendChild(span);} setTimeout(()=> container.parentElement?.classList?.add('reveal'),200); container.setAttribute('aria-hidden','false'); }
}

window.addEventListener('resize', resizeCanvas);
window.addEventListener('load', ()=>{ startCinematic(); });
