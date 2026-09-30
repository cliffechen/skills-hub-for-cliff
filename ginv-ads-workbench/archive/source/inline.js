
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "name": "GinvAds 广告智库 · 亚马逊 PPC 实战方法论",
  "description": "汇总亚马逊广告投放的13大实战方法论主题,含新品推广、竞价预算、否词精准化、数据报表分析等内容。",
  "url": "https://sellerhelp.top/projects/Ginv-Ads广告智库/",
  "inLanguage": "zh-CN"
}



const topics=Array.from(document.querySelectorAll('#zoneContent .topic'));
const search=document.getElementById('search');
const progress=document.getElementById('progress');
const navItems=Array.from(document.querySelectorAll('.nav-item'));
const tabs=Array.from(document.querySelectorAll('.tab'));
const panes=Array.from(document.querySelectorAll('.pane'));

// ---------- Tab 切换 ----------
let currentTab='content';
function switchTab(name){
  currentTab=name;
  tabs.forEach(t=>t.classList.toggle('active',t.dataset.tab===name));
  panes.forEach(p=>p.classList.toggle('active',p.dataset.pane===name));
  window.scrollTo({top:0,behavior:'smooth'});
}
tabs.forEach(t=>t.addEventListener('click',()=>switchTab(t.dataset.tab)));
document.querySelectorAll('[data-tabnav]').forEach(a=>a.addEventListener('click',e=>{
  e.preventDefault();
  switchTab(a.dataset.tabnav);
}));

// ---------- 主题切换（默认一次只看一个主题）----------
function showTopic(id){
  topics.forEach(function(s){s.classList.toggle('hidden',s.id!==id);});
  navItems.forEach(n=>n.classList.toggle('active',n.dataset.topic===id));
  if(currentTab!=='content')switchTab('content');
}
navItems.forEach(n=>{if(n.dataset.topic){n.addEventListener('click',function(e){e.preventDefault();showTopic(n.dataset.topic);});}});
showTopic(topics[0].id);

// 卡片展开/收起
window.toggleMethod=function(el){el.closest('.method-card').classList.toggle('open');};

// 搜索：命中主题全部同时展示，未命中隐藏
search.addEventListener('input',function(){
  const kw=search.value.trim().toLowerCase();
  if(!kw){showTopic(topics[0].id);return;}
  let first=null;
  topics.forEach(function(s){
    const ok=s.textContent.toLowerCase().includes(kw);
    s.classList.toggle('hidden',!ok);
    if(ok&&!first)first=s.id;
  });
  navItems.forEach(n=>n.classList.remove('active'));
  if(first){
    const nav=document.querySelector('.nav-item[data-topic="'+first+'"]');
    if(nav)nav.classList.add('active');
  }
});

// 顶部进度 + 返回顶部
window.addEventListener('scroll',()=>{
  const h=document.documentElement;
  const pct=h.scrollTop/(h.scrollHeight-h.clientHeight)*100;
  progress.style.width=pct+'%';
});

// 计算器
function num(id){return parseFloat(document.getElementById(id).value)||0;}
function calEv(){
  const cv=num('t0c')/100,m=num('t0m'),c=num('t0p');
  if(!cv||!m){document.getElementById('t0o').innerHTML='请填写参数';return;}
  const ev=cv*m;
  const diff=ev-c;
  document.getElementById('t0o').innerHTML='单点击期望价值 EV ≈ $'+ev.toFixed(2)+'；当前 CPC $'+c.toFixed(2)+' → '+(diff>=0?'正期望，值得投，每点击可赚约 $'+diff.toFixed(2):'负期望，每点击约亏 $'+Math.abs(diff).toFixed(2)+'，应降出价/换词/否定');
}
function calBeAc(){const p=num('t1p'),m=num('t1m');const v=(p>0?m/p:0)*100;document.getElementById('t1o').innerHTML='可承受最高 ACoS ≈ '+v.toFixed(1)+'%'+(v>0?'（即每个点击的保本 EV 上限占比）':'');}
function calCpc(){const ac=num('t2a')/100,cv=num('t2c')/100,p=num('t2p');const v=ac*cv*p;const ev=cv*p;document.getElementById('t2o').innerHTML=v>0?('保本 CPC ≈ $'+v.toFixed(2)+'；若目标 ACoS 设满即为盈亏平衡，实际出价应 ≤ 该值'):'请填写完整参数';}
function calBud(){const cv=num('t3c')/100,c=num('t3p');if(!cv||!c){document.getElementById('t3o').innerHTML='请填写参数';return;}const need=Math.ceil(1/cv);const ev=cv*1;document.getElementById('t3o').innerHTML='至少 '+need+' 次点击出 1 单 → 保底预算 ≈ $'+(need*c).toFixed(0)+(ev>0?'；若 CPC 超过单点 EV 则跑再多也是亏，优先降出价':'');}
function calHc(){const c=num('t4c')/100;if(!c){document.getElementById('t4o').innerHTML='请填写参数';return;}const avg=1/c;document.getElementById('t4o').innerHTML='平均 '+avg.toFixed(1)+' 点击出 1 单；超过 '+(avg*1.5).toFixed(0)+' 点击仍不出单 → 考虑降价 / 换词';}

// ---------- 访客 / 访问量统计 ----------
// 每次页面加载调用一次 /api/track：
// - 访问量(PV)：每次加载都 +1
// - 访客(UV)：同一 IP 同一天只计一次
(function(){
  const statUv=document.getElementById('statUv');
  const statPv=document.getElementById('statPv');
  fetch('/api/track',{cache:'no-store'})
    .then(r=>{if(!r.ok)throw new Error('track failed');return r.json();})
    .then(d=>{
      if(statUv&&typeof d.siteUv==='number')statUv.textContent=d.siteUv.toLocaleString('zh-CN');
      if(statPv&&typeof d.sitePv==='number')statPv.textContent=d.sitePv.toLocaleString('zh-CN');
    })
    .catch(()=>{
      // 接口不可用时（例如本地直接打开 HTML、KV 未绑定等）静默隐藏，不影响页面其余功能
      if(statUv)statUv.textContent='—';
      if(statPv)statPv.textContent='—';
    });
})();

