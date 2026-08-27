const fs = require('fs');
const { execFileSync } = require('child_process');

const MD = 'D:/workbuddy/赚钱日报/2026-08-18.md';
const NODE = 'C:/Users/石/.workbuddy/binaries/node/versions/22.22.2/node';
const RUNJS = 'C:/Users/石/AppData/Local/npm-cache/_npx/8f08eae71a6e4041/node_modules/@larksuite/cli/scripts/run.js';
const UID = 'ou_6f106634389ed5b9104c327b3019e16b';

let body = '';
try { body = fs.readFileSync(MD, 'utf8'); } catch (e) { console.error('READ_FAIL', e.message); process.exit(2); }

const header = `**🔥 赚钱日报 · 2026-08-18（周二）**

> 今天最该盯的 3 个信号（时间紧只看这里）：
> 1. **OPC「一人公司」政策进入"全要素赋能"成熟阶段**——山东发算力券/语料券/工位号注册、安徽 Token贷可质押+政府预付款≥40%、佛山桂城 1亿直投基金+人才卡子女入学，海外没有的"国家发AI创业装备"
> 2. **海外 Reddit 几万人实测：赚钱靠"垂直×包月"，最快路径是"复制+垂直化"**——Top3=SEO页$500-5K/chatbot$1K-3K/线索$2K-8K；反面 AI代写$5-10/篇、247h agent仅$4 MRR 证伪躺赚
> 3. **国内手机副业实测月增收 300–2500 元**——大厂众包零押金时薪25-50、闲鱼虚拟资料3.99起、云客服22-32、短剧推文~2000/月；社区"先给价值再软广"是零成本获客红利

---

`;

const msg = header + body +
  `\n\n> 完整版：D:\\workbuddy\\赚钱日报\\2026-08-18.md ；离线面板：D:\\workbuddy\\赚钱面板\\赚钱面板-成品.html（双击即用）`;

try {
  const out = execFileSync(NODE, [RUNJS, 'im', '+messages-send', '--as', 'bot', '--user-id', UID, '--markdown', msg], { encoding: 'utf8', timeout: 60000 });
  console.log('FEISHU_OK');
  console.log(out.slice(0, 600));
} catch (e) {
  console.error('FEISHU_FAIL');
  console.error((e.stdout || '').slice(0, 400));
  console.error((e.stderr || '').slice(0, 600));
  process.exit(1);
}
