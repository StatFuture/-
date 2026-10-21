(() => {
 // The original hover-to-switch behavior is replaced with deliberate click/keyboard selection.
 const tabs=[...document.querySelectorAll('[role="tab"]')],panels=[...document.querySelectorAll('[role="tabpanel"]')];
 function select(id){const tab=tabs.find(t=>t.getAttribute('aria-controls')===id)||tabs[0];if(!tab)return;tabs.forEach(t=>{const active=t===tab;t.setAttribute('aria-selected',String(active));t.tabIndex=active?0:-1});panels.forEach(p=>p.hidden=p.id!==tab.getAttribute('aria-controls'));}
 for(const old of tabs){const fresh=old.cloneNode(true);old.replaceWith(fresh);} // Remove old hover listeners without touching labels or appearance.
 const cleanTabs=[...document.querySelectorAll('[role="tab"]')];tabs.splice(0,tabs.length,...cleanTabs);
 tabs.forEach((tab,i)=>{tab.onclick=()=>{const id=tab.getAttribute('aria-controls');select(id);if(location.protocol!=='about:'){try{history.pushState(null,'','#'+id)}catch{try{location.hash=id}catch{}}}const nav=document.getElementById('tabs'),menu=document.querySelector('.menu-toggle'),wasOpen=nav?.classList.contains('open');nav?.classList.remove('open');menu?.setAttribute('aria-expanded','false');if(wasOpen)menu?.focus({preventScroll:true});};tab.onkeydown=e=>{const next=({ArrowRight:(i+1)%tabs.length,ArrowLeft:(i+tabs.length-1)%tabs.length,Home:0,End:tabs.length-1})[e.key];if(next!==undefined){e.preventDefault();tabs[next].click();tabs[next].focus();}};});
 const requested=()=>{let id='';try{id=decodeURIComponent(location.hash.slice(1))}catch{}select(id)};addEventListener('popstate',requested);addEventListener('hashchange',requested);requested();document.documentElement.dataset.facultyReady='true';
})();
