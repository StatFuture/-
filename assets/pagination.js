(() => {
 const data=JSON.parse(document.getElementById('cms-page-data').textContent),size=data.pageSize;
 for(const list of document.querySelectorAll('[data-cms-list]')){
  const key=list.dataset.cmsList,items=data.groups[key]||[],pages=Math.ceil(items.length/size);
  if(pages<=1)continue;
  const nav=document.createElement('nav');nav.className='cms-pager';nav.setAttribute('aria-label',({news:'新闻',members:'成员',papers:'论文',projects:'项目',patents:'专利',books:'教材',awards:'荣誉',resources:'资料'})[key]+'分页');
  const prev=document.createElement('button'),next=document.createElement('button'),label=document.createElement('span'),jump=document.createElement('input'),go=document.createElement('button');prev.textContent='上一页';next.textContent='下一页';go.textContent='跳转';label.setAttribute('aria-live','polite');jump.type='number';jump.min=1;jump.max=pages;jump.setAttribute('aria-label','跳到第几页');nav.append(prev,label,next,jump,go);list.after(nav);let current=1;
  function paint(page,focus=false){current=Math.min(pages,Math.max(1,Math.trunc(Number(page))||1));list.querySelectorAll('video').forEach(v=>v.pause());list.innerHTML=items.slice((current-1)*size,current*size).join('');label.textContent=`第 ${current} / ${pages} 页，共 ${items.length} 条`;prev.disabled=current===1;next.disabled=current===pages;jump.value=current;if(focus){list.tabIndex=-1;list.focus({preventScroll:true});if(list.getBoundingClientRect().top<0)list.scrollIntoView({block:'start'});}}
  prev.onclick=()=>paint(current-1,true);next.onclick=()=>paint(current+1,true);go.onclick=()=>paint(jump.value,true);jump.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();go.click()}};paint(1);
 }
 document.querySelectorAll('[role=tab]').forEach(t=>t.addEventListener('click',()=>{document.querySelectorAll('[role=tabpanel][hidden] video').forEach(v=>v.pause())}));
 const toggle=document.querySelector('.menu-toggle'),tabs=document.getElementById('tabs');if(toggle&&tabs)toggle.onclick=()=>{const open=tabs.classList.toggle('open');toggle.setAttribute('aria-expanded',String(open))};
 document.documentElement.dataset.cmsReady='true';
})();
