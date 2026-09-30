import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const project = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const url = 'http://127.0.0.1:4173/';
const isWorkbench = async () => {
  try { const response = await fetch(url); return response.ok && (await response.text()).includes('GinvAds · 广告工作台'); }
  catch { return false; }
};
function openBrowser() {
  if (process.platform === 'win32') spawn('cmd.exe', ['/c', 'start', '', url], { windowsHide: true, stdio: 'ignore' }).unref();
  else if (process.platform === 'darwin') spawn('open', [url], { stdio: 'ignore' }).unref();
  else spawn('xdg-open', [url], { stdio: 'ignore' }).unref();
  console.log(`请在浏览器打开：${url}`);
}
if (await isWorkbench()) {
  console.log('工作台已经启动。'); openBrowser();
} else {
  const server = spawn(process.execPath, [path.join(project, 'scripts/serve.mjs')], { cwd: project, windowsHide: true, stdio: 'inherit' });
  server.on('error', error => { console.error(error.message); process.exitCode = 1; });
  server.on('exit', code => { process.exitCode = code || 0; });
  for (let attempt = 0; attempt < 20; attempt++) {
    if (await isWorkbench()) { openBrowser(); break; }
    await new Promise(resolve => setTimeout(resolve, 250));
  }
}
