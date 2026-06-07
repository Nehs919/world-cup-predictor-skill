import { chromium } from "playwright";
import { mkdir } from "fs/promises";
import path from "path";
import { fileURLToPath } from "url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const outDir = path.join(root, "docs", "images");
await mkdir(outDir, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });

// 1) Web app screenshot
try {
  await page.goto("https://kengine.xx.kg", { waitUntil: "networkidle", timeout: 60000 });
  const freeTab = page.locator('button[data-mode="free"]');
  if (await freeTab.count()) {
    await freeTab.click();
    await page.waitForTimeout(1500);
  }
  await page.screenshot({
    path: path.join(outDir, "web-demo.png"),
    fullPage: false,
  });
  console.log("Saved web-demo.png");
} catch (err) {
  console.error("Web screenshot failed:", err.message);
}

// 2) Cursor-style chat mock
const cursorHtml = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #1e1e1e; color: #d4d4d4; height: 100vh; display: flex;
  }
  .sidebar {
    width: 220px; background: #181818; border-right: 1px solid #2a2a2a;
    padding: 16px 12px; font-size: 12px; color: #888;
  }
  .sidebar h2 { color: #ccc; font-size: 13px; margin-bottom: 12px; font-weight: 600; }
  .sidebar .item { padding: 8px 10px; border-radius: 6px; margin-bottom: 4px; }
  .sidebar .item.active { background: #2d2d2d; color: #fff; }
  .main { flex: 1; display: flex; flex-direction: column; }
  .topbar {
    height: 44px; border-bottom: 1px solid #2a2a2a; display: flex; align-items: center;
    padding: 0 16px; font-size: 12px; color: #888;
  }
  .chat { flex: 1; padding: 24px 32px; overflow: hidden; }
  .msg { max-width: 760px; margin-bottom: 20px; line-height: 1.55; font-size: 14px; }
  .user { color: #9cdcfe; }
  .user .label { font-size: 11px; color: #666; margin-bottom: 6px; }
  .agent .label { font-size: 11px; color: #666; margin-bottom: 6px; }
  .card {
    background: #252526; border: 1px solid #333; border-radius: 8px;
    padding: 16px 18px; margin-top: 8px;
  }
  .card h3 { font-size: 16px; margin-bottom: 10px; color: #fff; }
  .stats { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px; margin-bottom: 10px; }
  .highlight { color: #4ec9b0; font-weight: 600; }
  .muted { color: #888; font-size: 12px; }
  code { background: #2d2d2d; padding: 1px 6px; border-radius: 4px; font-size: 12px; }
</style>
</head>
<body>
  <div class="sidebar">
    <h2>Cursor Agent</h2>
    <div class="item active">wc-predictor 德国 vs 库拉索</div>
    <div class="item">项目 README 编辑</div>
    <div class="item">engine 调试</div>
  </div>
  <div class="main">
    <div class="topbar">Agent · wc-predictor skill loaded</div>
    <div class="chat">
      <div class="msg user">
        <div class="label">You</div>
        /wc-predictor 预测德国和库拉索的比赛结果
      </div>
      <div class="msg agent">
        <div class="label">Agent</div>
        要用 <strong>默认设定</strong> 直接预测，还是 <strong>自定义参数</strong>？
      </div>
      <div class="msg user">
        <div class="label">You</div>
        默认设定
      </div>
      <div class="msg agent">
        <div class="label">Agent</div>
        已运行 <code>predict.py --a ger --b cuw --format json</code>
        <div class="card">
          <h3>德国 vs 库拉索</h3>
          <div class="stats">
            <div>阵型 · 4-2-3-1 vs 4-4-2</div>
            <div>调整后实力 · 71.1 vs 52.7</div>
          </div>
          <div class="highlight">胜率：德国 82.3% · 库拉索 17.7%</div>
          <div class="muted" style="margin-top:8px">最可能比分：3:0 (8.3%) · 4:0 (8.3%) · 3:1 (7.1%)</div>
          <div class="muted" style="margin-top:8px">含双方首发 11 人 + 替补名单（不展示球员能力值）</div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>`;

await page.setViewportSize({ width: 960, height: 620 });
await page.setContent(cursorHtml, { waitUntil: "load" });
await page.screenshot({
  path: path.join(outDir, "cursor-skill-demo.png"),
  fullPage: false,
});
console.log("Saved cursor-skill-demo.png");

await browser.close();
