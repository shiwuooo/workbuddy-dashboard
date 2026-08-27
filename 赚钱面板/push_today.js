const fs = require('fs');
const { execFileSync } = require('child_process');

const MD = 'D:/workbuddy/赚钱日报/2026-08-17.md';
const NODE = 'C:/Users/石/.workbuddy/binaries/node/versions/22.22.2/node';
const RUNJS = 'C:/Users/石/AppData/Local/npm-cache/_npx/8f08eae71a6e4041/node_modules/@larksuite/cli/scripts/run.js';
const UID = 'ou_6f106634389ed5b9104c327b3019e16b';

let body = '';
try { body = fs.readFileSync(MD, 'utf8'); } catch (e) { console.error('READ_FAIL', e.message); process.exit(2); }

const header = `**🔥 赚钱日报 · 2026-08-17（周一）**

> 今天最该盯的 3 个信号（时间紧只看这里）：
> 1. **OPC「装备包」继续加码扩散**——重庆12条/安徽省级三年方案/佛山桂城街道级，真给钱：免费工位+算力券+Token贷+预付款40%+导师陪跑
> 2. **本地小商家 AI chatbot/代运营 国内外共识 No.1**——国内 500–1500/店/月、海外 $300–500 搭建 + $150–500/mo 包月，仍真能赚未卷
> 3. **海外「自动赚钱/被动收入」被实测打脸**——247h 自动 agent 仅 $4 MRR、AI 代写压到 $5–10/篇、dropshipping/POD 证伪；真相=垂直小众+持续执行

---

`;

const msg = header + body +
  `\n\n> 完整版：D:\\workbuddy\\赚钱日报\\2026-08-17.md ；离线面板：D:\\workbuddy\\赚钱面板\\赚钱面板-成品.html（双击即用）`;

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
