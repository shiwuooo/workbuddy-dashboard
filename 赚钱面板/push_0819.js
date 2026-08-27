const fs = require('fs');
const { execFileSync } = require('child_process');

const MD = 'D:/workbuddy/赚钱日报/2026-08-19.md';
const NODE = 'C:/Users/石/.workbuddy/binaries/node/versions/22.22.2/node';
const RUNJS = 'C:/Users/石/AppData/Local/npm-cache/_npx/8f08eae71a6e4041/node_modules/@larksuite/cli/scripts/run.js';
const UID = 'ou_6f106634389ed5b9104c327b3019e16b';

let body = '';
try { body = fs.readFileSync(MD, 'utf8'); } catch (e) { console.error('READ_FAIL', e.message); process.exit(2); }

const header = `**📰 赚钱日报 · 2026-08-19（周三）**

> 今天最该盯的 3 个信号（时间紧只看这里）：
> 1. **信息差套利——把「海外已验证 / 国内信息孤岛」双向搬**：海外模板/教程/产品翻译成中文上架小红书闲鱼（案例 Notion 模板 49.9 元首月 463 份）；国内供应链+玩法搬 TikTok 0 备货赚佣金（案例月入 10 万+）
> 2. **AI + 本地商家代运营 / OPC 政策继续下沉**：佛山桂城街道级（工位月补 180、1 亿基金）、重庆十二条（8000 补贴+600 万贷）、武汉 30 社区 1500 工位、济南 18 社区 550 家；海外 chatbot 包月 $1K–3K/mo = 价差窗口
> 3. **银发 / 低空 / 县域——政策托底现金流稳**：适老化改造补贴 2 万/户毛利 40%+、陪诊 6000–9000/月；持证飞手日薪 500–1000；返乡补贴 1–3 万+税费减免

---

`;

const msg = header + body +
  `\n\n> 完整版：D:\\workbuddy\\赚钱日报\\2026-08-19.md ；离线面板：D:\\workbuddy\\赚钱面板\\赚钱面板-成品.html（双击即用）`;

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
