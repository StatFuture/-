(() => {
 // Keep tab panels mounted, including their page controls and media state.
 const tabs=[...document.querySelectorAll('[role="tab"]')],panels=[...document.querySelectorAll('[role="tabpanel"]')];
 const positions=new Map();let activeId='',restoreTicket=0,hoverTimer;
 const menu=document.querySelector('.menu-toggle');
 const desktopHover=()=>matchMedia('(hover: hover) and (pointer: fine)').matches&&!menu?.getClientRects().length;
 function select(id){
  const tab=tabs.find(t=>t.getAttribute('aria-controls')===id)||tabs[0];if(!tab)return;
  const next=tab.getAttribute('aria-controls');
  if(next===activeId)return;
  if(activeId)positions.set(activeId,scrollY);
  activeId=next;const ticket=++restoreTicket,y=positions.get(next)||0;
  tabs.forEach(t=>{const active=t===tab;t.setAttribute('aria-selected',String(active));t.tabIndex=active?0:-1});
  panels.forEach(p=>p.hidden=p.id!==next);
  document.querySelectorAll('[role=tabpanel][hidden] video').forEach(v=>v.pause());
  document.dispatchEvent(new Event('faculty-tab-selected'));
  requestAnimationFrame(()=>{if(ticket!==restoreTicket)return;window.scrollTo({top:y,behavior:'instant'});requestAnimationFrame(()=>{if(ticket===restoreTicket)window.scrollTo({top:y,behavior:'instant'})});});
 }
 for(const old of tabs){const fresh=old.cloneNode(true);old.replaceWith(fresh);}
 tabs.splice(0,tabs.length,...document.querySelectorAll('[role="tab"]'));
 function cancelHover(){clearTimeout(hoverTimer);hoverTimer=null;}
 tabs.forEach((tab,i)=>{
  tab.onclick=()=>{
   cancelHover();const id=tab.getAttribute('aria-controls');select(id);
   if(location.protocol!=='about:'&&location.hash!=='#'+id){try{history.pushState(null,'','#'+id)}catch{try{location.hash=id}catch{}}}
   const nav=document.getElementById('tabs'),wasOpen=nav?.classList.contains('open');nav?.classList.remove('open');menu?.setAttribute('aria-expanded','false');if(wasOpen)menu?.focus({preventScroll:true});
  };
  tab.onkeydown=e=>{const next=({ArrowRight:(i+1)%tabs.length,ArrowLeft:(i+tabs.length-1)%tabs.length,Home:0,End:tabs.length-1})[e.key];if(next!==undefined){e.preventDefault();tabs[next].click();tabs[next].focus({preventScroll:true});}};
  tab.addEventListener('mouseenter',()=>{cancelHover();if(!desktopHover())return;hoverTimer=setTimeout(()=>{if(!desktopHover()||!tab.matches(':hover'))return;const id=tab.getAttribute('aria-controls');select(id);try{history.replaceState(null,'','#'+id)}catch{}},160)});
  tab.addEventListener('mouseleave',cancelHover);
 });
 const requested=()=>{cancelHover();let id='';try{id=decodeURIComponent(location.hash.slice(1))}catch{}select(id)};
 addEventListener('popstate',requested);addEventListener('hashchange',requested);addEventListener('blur',cancelHover);addEventListener('resize',cancelHover);
 requested();document.documentElement.dataset.facultyReady='true';
})();
