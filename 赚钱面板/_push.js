const fs = require('fs');
const { execFileSync } = require('child_process');

const MD = 'D:/workbuddy/赚钱日报/2026-08-16.md';
const NODE = 'C:/Users/石/.workbuddy/binaries/node/versions/22.22.2/node';
const RUNJS = 'C:/Users/石/AppData/Local/npm-cache/_npx/8f08eae71a6e4041/node_modules/@larksuite/cli/scripts/run.js';
const UID = 'ou_6f106634389ed5b9104c327b3019e16b';

let body = '';
try { body = fs.readFileSync(MD, 'utf8'); } catch (e) { console.error('READ_FAIL', e.message); process.exit(2); }

const header = `**🔥 赚钱日报 · 2026-08-16（周日）**

> 今天最该盯的 3 个信号（时间紧只看这里）：
> 1. **OPC「装备包」下沉到街道级**——政策从「补算力」升级为「给订单 + 预付款≥40% + Token 可抵押贷款」
> 2. **海外把本地商家 AI chatbot 做成可复制零代码 $7K/月模板**，国内仍一单一结 = 价差窗口
> 3. **信息差套利在国内升温**，但 AI 生成内容正快速贬值（亚马逊 AI 书总量涨 38 倍、收入仅涨 9 倍）

---

`;

const msg = header + body +
  `\n\n> 完整版：D:\\workbuddy\\赚钱日报\\2026-08-16.md ；离线面板：D:\\workbuddy\\赚钱面板\\赚钱面板-成品.html（双击即用）`;

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
