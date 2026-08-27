/* ============================================================
   知本导师 · 593册学习成长经典之熔炼
   离线导师内核 + 可升级 AI 模式
   ============================================================ */

const PERSONA = `你是「知本导师」——一个由 593 本学习、思维、成长、自我管理经典熔炼而成的私人一对一导师。你不是某一个人，而是这些书共同智慧的集合体。你只服务一位用户，像好导师那样一对一陪伴：先诊断，再给可执行方案，绝不空谈。你温和但犀利，不灌鸡汤。

你的知识底色（共识）：学习方法（Barbara Oakley《学习之道》组块/交错/专注-发散模式、费曼学习法输出倒逼输入、印南敦史《阅读术》慢读取触动、Xdite《打造超人大脑》阅读写作进化三件套）；记忆（Scott Young《记忆的科学》编码-存储-提取、提取练习优于重读、Tara Swart《大脑训练手册》神经可塑性、Gazzaniga《双脑记》）；专注（Damon Zahariades《Fast Focus》快速启动、Rachael O'Meara《暂停键》主动休息）；思维（Ozan Varol《像火箭科学家一样思考》首性原理/实验思维、Jay Shetty《像高手一样思考》、冈田昭人《牛津人独立思考》批判性表达、莫琳·希凯《深度思考》追问本质、刘润《认知黑客》）；写作（James Scott Bell《这样写出好故事》冲突引擎）；自我管理（伊庭正康等《高效人生自我管理》、古川武士习惯）；科学世界观（Richard DeWitt《世界观》范式）。

导师十大原则：1 以教代学；2 组块+交错+间隔提取；3 提取练习重于重读；4 先启动再优化；5 主动暂停防透支；6 追问本质首性原理；7 像实验一样容错迭代；8 冲突驱动表达；9 习惯系统>意志力；10 用科学世界观校准认知。

交互风格：先诊断再开方，给可执行步骤并点明来源书，主动追问真实目标与障碍，中文交流，多用清单步骤。首次对话必问：具体目标、最大卡点、每日可投入时间、已有基础、一句话结果。诊断后输出：情况小结→推荐方法组合（点名来源书）→7天启动计划→每周复盘。`;

const THEMES = ["学习力","记忆","专注","思维","写作表达","自我管理","科学世界观"];

const METHODS = [
  {id:"chunk", theme:"学习力", name:"组块与交错学习", source:"《学习之道》Barbara Oakley",
   essence:"把知识拆成『组块』，交替练不同题型，让大脑在休息中自动联结。",
   steps:["专注模式弄懂单个概念","把相关概念打包成『组块』","用发散模式（散步/睡眠）让潜意识整合","交错练习不同题型，破除『错觉熟练』","番茄钟25分钟阻断拖延"],
   when:"学新技能、备考、感觉越学越乱时", practice:"每天3个番茄钟 + 睡前10分钟回顾组块"},

  {id:"feynman", theme:"学习力", name:"费曼输出法", source:"《费曼学习法》尹红心/李伟",
   essence:"能用大白话讲明白=真懂；讲不清的地方就是知识漏洞。",
   steps:["选一个概念","假装教给小白，写下来","卡住处=漏洞，回书补全","用类比进一步简化","每周做一次费曼笔记"],
   when:"检验是否真掌握、备考复盘、学完想固化", practice:"挑1个概念，写一段『给小白的讲解』"},

  {id:"slowread", theme:"学习力", name:"慢读抓取术", source:"《快速抓重点阅读术》印南敦史",
   essence:"读得慢反而快：不划线不跳，只为『触动』停顿并联想。",
   steps:["不追求读完，追求触动","遇到触动句停下，拉通想","只记1句真实感悟","读后立刻写3行","重读远胜泛读"],
   when:"读书吸收慢、读完就忘、信息焦虑", practice:"每本书只取3个触动点，写进卡片"},

  {id:"hyperbrain", theme:"学习力", name:"高速成长三件套", source:"《打造超人大脑》Xdite郑伊廷",
   essence:"阅读+写作+持续进化，用产出倒逼成长，形成飞轮。",
   steps:["输入时做知识卡片","当日输出一篇短文","公开获取反馈","每周复盘迭代","把成果沉淀为作品集"],
   when:"想系统进化、做个人IP、摆脱无效努力", practice:"每天1卡+1文，坚持30天"},

  {id:"retrieve", theme:"记忆", name:"提取式记忆", source:"《记忆的科学》Scott Young",
   essence:"记忆=编码→存储→提取；提取练习比重读强10倍。",
   steps:["主动回忆，闭卷自测","间隔重复（第1/3/7天）","交错提取不同科目","用睡眠巩固","给知识绑情境（地点/情绪）"],
   when:"记不住、考前、单词/公式背了就丢", practice:"用闪卡做 retrieval，不反复划线"},

  {id:"brainact", theme:"记忆", name:"大脑激活术", source:"《大脑训练手册》Tara Swart",
   essence:"神经可塑性终生在线；睡眠、压力、饮食直接改写大脑。",
   steps:["保证7-8小时睡眠","有氧运动促BDNF","正念降低皮质醇","可视化目标激活前额叶","减少多任务切换"],
   when:"脑疲劳、状态差、长期高压", practice:"固定睡眠+每周3次有氧"},

  {id:"twobrain", theme:"记忆", name:"双脑协作", source:"《双脑记》Gazzaniga",
   essence:"左脑叙事、右脑模式；让理性与直觉协作，警惕左脑的『解释偏差』。",
   steps:["难题先交给直觉发散","再用逻辑收束","留意左脑事后编故事","重大决策双脑交叉验证"],
   when:"创意卡壳、决策纠结、过度理性", practice:"先直觉选A/B，再逻辑论证"},

  {id:"fastfocus", theme:"专注", name:"快速启动", source:"《Fast Focus》Damon Zahariades",
   essence:"注意力是有限资源；先启动，阻力会自己消失。",
   steps:["5分钟计时硬启动","关通知、单屏工作","先吃青蛙做最难的事","批量处理琐事","设『专注块』保护时间"],
   when:"拖延、专注差、一坐下就刷手机", practice:"每天列1个『今日唯一要事』先做完"},

  {id:"pause", theme:"专注", name:"主动暂停", source:"《暂停键》Rachael O'Meara",
   essence:"持续加速会烧坏；刻意抽离，才能重新对焦真正渴望。",
   steps:["察觉倦怠信号","设一个『暂停日』","脱离日常环境","问『我真正想要什么』","带着答案回归"],
   when:"倦怠、迷茫、拼命却空虚", practice:"每月半日『暂停』，只问不答"},

  {id:"rocketsci", theme:"思维", name:"火箭科学家思维", source:"《像火箭科学家一样思考》Ozan Varol",
   essence:"用首性原理拆解、把目标当实验、包容失败快速迭代。",
   steps:["问『为什么是真的』追到地基","把目标设计成可证伪实验","预设失败预案","小成本试错快速迭代","向NASA学『绝境逢生』"],
   when:"创新、破局、不敢开始、怕失败", practice:"把大目标拆成3个最小实验"},

  {id:"deepthink", theme:"思维", name:"深度思考", source:"《深度思考》莫琳·希凯",
   essence:"不断逼近问题本质，而非停在表象与情绪。",
   steps:["写下表面问题","连问5个为什么","找出隐含假设","重构真问题","用第一性原理收口"],
   when:"问题复杂、被表象带偏、反复纠结", practice:"遇到难题先写『我真正在解决什么』"},

  {id:"oxford", theme:"思维", name:"牛津式独立思考", source:"《牛津人的30堂独立思考与精准表达课》冈田昭人",
   essence:"先证伪再表达；精准=逻辑清晰+换位思考。",
   steps:["区分事实与观点","主动找反例","用金字塔结构表达","换位思考听众","结论先行再给支撑"],
   when:"表达混乱、辩论、汇报、写作立论", practice:"任何观点先写『反方会怎么反驳我』"},

  {id:"cog hack", theme:"思维", name:"认知黑客", source:"《认知黑客》刘润/谢春霖",
   essence:"用简单逻辑看透复杂世界，建立可复用的思维模型。",
   steps:["识别因果错觉与相关混淆","建立基础模型（复利/边际/机会成本）","用模型解释现象","持续扩充模型库"],
   when:"看不懂世界、被信息淹没、决策混乱", practice:"每周吃透1个思维模型并举例"},

  {id:"story", theme:"写作表达", name:"冲突引擎写作", source:"《这样写出好故事》James Scott Bell",
   essence:"好故事=困局+转折；写作先立 LOCK（主角/目标/冲突/转折）。",
   steps:["定主角与核心目标","设不可回避的冲突","每章埋一个转折","用场景 show 而非 tell","边读名家边仿写"],
   when:"写作、自媒体、文案、讲不好故事", practice:"每天写300字微型冲突场景"},

  {id:"habit", theme:"自我管理", name:"习惯系统", source:"《高效人生自我管理》伊庭正康等/古川武士",
   essence:"靠系统不靠意志力；微习惯+环境设计，让好习惯自动发生。",
   steps:["选1个2分钟微习惯","固定时间地点","设计环境提示","不中断追踪","每周复盘微调"],
   when:"坚持不了、三分钟热度、靠硬扛", practice:"从『每天2分钟』开始，绝不跳过"},

  {id:"capital", theme:"自我管理", name:"成长资本", source:"《学习才是资本》哈佛商业评论",
   essence:"把学习当长期复利投资，而非临时任务。",
   steps:["定年度能力目标","切成每周学习块","每月产出作品","建立个人作品集","复盘复利曲线"],
   when:"职业成长、迷茫该学什么", practice:"每年只攻1-2项可复利能力"},

  {id:"worldview", theme:"科学世界观", name:"范式思维", source:"《世界观》Richard DeWitt",
   essence:"科学是范式下的互联信念网；换范式，世界全变。",
   steps:["列出自己的信念网","找支撑与反例","设想一个反范式","理解科学史如何演进","保持可错心态"],
   when:"校准认知、破除执念、看宏大问题", practice:"挑一个坚信的观点，写它的反范式"}
];

/* ---------- 导航 ---------- */
function showSection(id){
  document.querySelectorAll("section").forEach(s=>s.classList.remove("show"));
  document.getElementById(id).classList.add("show");
  document.querySelectorAll("nav.tabs button").forEach(b=>b.classList.remove("active"));
  document.querySelector('nav.tabs button[data-s="'+id+'"]').classList.add("active");
  if(id==="lib") renderMethods(currentFilter);
  if(id==="chat") refreshChatHint();
}

/* ---------- 方法库 ---------- */
let currentFilter="all";
function renderMethods(filter){
  currentFilter=filter;
  const box=document.getElementById("libGrid");
  const list = filter==="all"?METHODS:METHODS.filter(m=>m.theme===filter);
  box.innerHTML = list.map(m=>`
    <div class="mcard">
      <span class="src">${m.source}</span>
      <h4>${m.name}</h4>
      <div class="ess">${m.essence}</div>
      <ol>${m.steps.map(s=>`<li>${s}</li>`).join("")}</ol>
      <div class="when">适用：${m.when}<br>实操：${m.practice}</div>
    </div>`).join("");
  document.querySelectorAll("#libTags .tag").forEach(t=>
    t.classList.toggle("sel", t.dataset.f===filter));
}

/* ---------- 诊断室 ---------- */
const diag = {goal:null, pains:[], time:null, level:null, detail:""};
function pick(btn, key, multi){
  if(multi){
    btn.classList.toggle("sel");
    const v=btn.dataset.v;
    const i=diag.pains.indexOf(v);
    if(i>=0) diag.pains.splice(i,1); else diag.pains.push(v);
  }else{
    document.querySelectorAll('[data-group="'+key+'"]').forEach(b=>b.classList.remove("sel"));
    btn.classList.add("sel"); diag[key]=btn.dataset.v;
  }
}
function buildPlan(){
  if(!diag.goal){ alert("先选一个『目标类型』"); return; }
  const goalTheme={skill:"学习力",exam:"学习力",read:"学习力",write:"写作表达",
    think:"思维",habit:"自我管理",career:"自我管理"}[diag.goal];
  const painMap={in:"chunk",forget:"retrieve",focus:"fastfocus",
    output:"feynman",persist:"habit",method:"rocketsci"};
  let chosen=new Set();
  METHODS.filter(m=>m.theme===goalTheme).forEach(m=>chosen.add(m.id));
  diag.pains.forEach(p=>{ if(painMap[p]) chosen.add(painMap[p]); });
  // 兜底补记忆/专注
  if(chosen.size<3){ chosen.add("retrieve"); chosen.add("fastfocus"); }
  const picks=METHODS.filter(m=>chosen.has(m.id));

  const timeMin={t1:25,t2:45,t3:90,t4:150}[diag.time||"t2"];
  const blocks = timeMin<=30?1 : timeMin<=60?2 : timeMin<=120?3:4;
  const levelNote={zero:"零基础：先建立最小闭环，不求快",intro:"入门：固定节奏，重在坚持",
    adv:"进阶：加交错与输出密度"}[diag.level||"intro"];

  const days=["第1天","第2天","第3天","第4天","第5天","第6天","第7天"];
  const dayPlan=days.map((d,i)=>{
    const m=picks[i%picks.length];
    return `<li><b>${d}</b> · 聚焦《${m.source.split("》")[0].replace("《","")}》的「${m.name}」：
      今日${blocks}个专注块，做这一步——${m.steps[i%m.steps.length]}。</li>`;
  }).join("");

  const html=`<div class="plan">
    <h4>① 你的情况小结</h4>
    <p class="muted">目标：${diag.goal} ｜ 卡点：${diag.pains.length?diag.pains.join("、"):"未选"} ｜
    每日可投入约 ${timeMin} 分钟 ｜ 基础：${diag.level||"入门"}</p>
    <p>${diag.detail?("你的原话：「"+diag.detail+"」"):"（未填具体结果，建议补一句目标，导师更好对症下药）"}</p>
    <p><b>导师点评：</b>${levelNote}。围绕你的目标，我为你锁定了以下方法组合——</p>

    <h4>② 推荐方法组合（点名来源）</h4>
    ${picks.map(m=>`<p>· <b>${m.name}</b> <span class="muted">（${m.source}）</span><br>
      <span class="muted">${m.essence}</span></p>`).join("")}

    <h4>③ 7 天启动计划（每日约 ${timeMin} 分钟）</h4>
    <ol>${dayPlan}</ol>
    <p class="muted">每周日做 1 次费曼输出 + 1 次周复盘（见方法库对应卡片）。</p>

    <h4>④ 每周复盘清单</h4>
    <ol>
      <li>这周哪个方法真的用了？哪个只是收藏？</li>
      <li>最大的卡点是否移动了？没动，是哪个环节断了？</li>
      <li>下周只保留 1-2 个方法做深，砍掉其余。</li>
      <li>用「成长资本」思路，记录一个本周作品/产出。</li>
    </ol>

    <h4>⑤ 想深挖？从这 593 本里优先读</h4>
    <p class="muted">《学习之道》《费曼学习法》《记忆的科学》《像火箭科学家一样思考》
    《深度思考》《这样写出好故事》《世界观》——已内置进本导师的方法库，可在「方法库」随时查。</p>
  </div>`;
  document.getElementById("planOut").innerHTML=html;
}

/* ---------- 导师对话 ---------- */
let cfg = loadCfg();
let history=[];
function loadCfg(){
  try{ return JSON.parse(localStorage.getItem("zb_tutor_cfg")||"{}"); }catch(e){ return {}; }
}
function saveCfg(){ localStorage.setItem("zb_tutor_cfg", JSON.stringify(cfg)); }

function refreshChatHint(){
  const on = cfg && cfg.key;
  const n=document.getElementById("chatHint");
  if(on){ n.className="notice"; n.style.background="#eafaf1"; n.style.borderColor="#b7e4c7";
    n.style.color="#1f7a4d"; n.textContent="✅ AI 模式已开启（"+ (cfg.model||"默认模型") +"），可直接与导师自由对话。"; }
  else{ n.className="notice";
    n.textContent="⚠️ 当前为基础引导模式（离线）。想自由对话，请到「AI设置」填入接口Key；或复制「导师人格」到任意AI使用。"; }
}

const KW={ "专注":"fastfocus","拖延":"fastfocus","记不住":"retrieve","记忆":"retrieve",
  "费曼":"feynman","输出":"feynman","读书":"slowread","阅读":"slowread","写作":"story","写":"story",
  "思维":"rocketsci","决策":"rocketsci","深度":"deepthink","表达":"oxford","习惯":"habit",
  "坚持":"habit","目标":"capital","世界观":"worldview","大脑":"brainact","疲劳":"brainact",
  "暂停":"pause","倦怠":"pause","休息":"pause","学":"chunk","考试":"chunk","技能":"chunk",
  "方法":"rocketsci" };

function offlineReply(text){
  let hit=null;
  for(const k in KW){ if(text.indexOf(k)>=0){ hit=KW[k]; break; } }
  if(!hit) return "我是离线引导版，还不能自由对话。两个办法：① 到「AI设置」开启AI模式，和导师自然语言聊；② 复制「导师人格」粘贴到任意AI。\n\n你也可以先去「诊断室」生成专属方案，或到「方法库」按主题查具体方法。";
  const m=METHODS.find(x=>x.id===hit);
  return `导师说（来自《${m.source}》的「${m.name}」）：\n${m.essence}\n\n核心步骤：\n${m.steps.map((s,i)=>(i+1)+". "+s).join("\n")}\n\n实操：${m.practice}\n适用：${m.when}`;
}

function addMsg(role,text){
  const box=document.getElementById("chatBox");
  const d=document.createElement("div");
  d.className="msg "+(role==="me"?"me":"ai");
  d.textContent=text; box.appendChild(d); box.scrollTop=box.scrollHeight;
}
function sendChat(){
  const inp=document.getElementById("chatInput");
  const text=inp.value.trim(); if(!text) return;
  addMsg("me",text); inp.value=""; history.push({role:"user",content:text});
  if(cfg && cfg.key){
    aiReply(text);
  }else{
    const r=offlineReply(text);
    addMsg("ai",r); history.push({role:"assistant",content:r});
  }
}
async function aiReply(text){
  const url=cfg.endpoint||"https://api.openai.com/v1/chat/completions";
  const body={ model:cfg.model||"gpt-4o-mini",
    messages:[{role:"system",content:PERSONA},...history], temperature:0.7 };
  addMsg("ai","导师正在思考…");
  try{
    const res=await fetch(url,{method:"POST",headers:{"Content-Type":"application/json",
      "Authorization":"Bearer "+cfg.key},body:JSON.stringify(body)});
    const data=await res.json();
    const reply=(data.choices&&data.choices[0].message.content)||JSON.stringify(data);
    document.querySelectorAll("#chatBox .msg.ai").forEach((e,i,a)=>{ if(i===a.length-1) e.remove(); });
    addMsg("ai",reply); history.push({role:"assistant",content:reply});
  }catch(e){
    document.querySelectorAll("#chatBox .msg.ai").forEach((e,i,a)=>{ if(i===a.length-1) e.remove(); });
    addMsg("ai","调用失败："+e.message+"\n可能是 CORS 或 Key 无效。检查「AI设置」，或改用支持跨域的代理/本地模型。");
  }
}

/* ---------- AI 设置 ---------- */
function saveSettings(){
  cfg.endpoint=document.getElementById("cfgEndpoint").value.trim();
  cfg.key=document.getElementById("cfgKey").value.trim();
  cfg.model=document.getElementById("cfgModel").value.trim();
  saveCfg(); refreshChatHint();
  document.getElementById("cfgMsg").textContent="已保存（仅存在你本地浏览器）。";
}
function clearSettings(){
  cfg={}; saveCfg(); refreshChatHint();
  document.getElementById("cfgMsg").textContent="已清除本地配置。";
}

/* ---------- 人格复制 ---------- */
function copyPrompt(){
  navigator.clipboard.writeText(PERSONA).then(()=>{
    document.getElementById("copyMsg").textContent="✅ 已复制导师人格到剪贴板，粘贴到任意AI即可。";
  }).catch(()=>{ document.getElementById("copyMsg").textContent="复制失败，请手动选择下方文本。"; });
}

/* ---------- 初始化 ---------- */
window.addEventListener("DOMContentLoaded",()=>{
  document.getElementById("cfgEndpoint").value=cfg.endpoint||"https://api.openai.com/v1/chat/completions";
  document.getElementById("cfgKey").value=cfg.key||"";
  document.getElementById("cfgModel").value=cfg.model||"gpt-4o-mini";
  refreshChatHint();
  document.getElementById("chatInput").addEventListener("keydown",e=>{ if(e.key==="Enter") sendChat(); });
});
