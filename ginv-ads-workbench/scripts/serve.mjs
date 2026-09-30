import http from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../workbench/dist');
const port = Number(process.env.PORT || 4173);
const types = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.woff2': 'font/woff2' };
const server = http.createServer(async (request, response) => {
  try {
    const url = new URL(request.url, `http://127.0.0.1:${port}`);
    const relative = decodeURIComponent(url.pathname).replace(/^\/+/, '') || 'index.html';
    const filename = path.resolve(root, relative);
    if (filename !== root && !filename.startsWith(root + path.sep)) {
      response.writeHead(403).end('Forbidden');
      return;
    }
    const info = await stat(filename);
    if (!info.isFile()) throw new Error('Not a file');
    response.writeHead(200, { 'Content-Type': types[path.extname(filename)] || 'application/octet-stream', 'Cache-Control': 'no-cache', 'X-Content-Type-Options': 'nosniff' });
    response.end(await readFile(filename));
  } catch {
    response.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' }).end('找不到此文件。');
  }
});
server.listen(port, '127.0.0.1', () => console.log(`GinvAds 工作台已启动：http://127.0.0.1:${port}`));
server.on('error', (error) => { console.error(error.code === 'EADDRINUSE' ? `端口 ${port} 已被占用。请关闭已有服务，或设置 PORT 后重试。` : error.message); process.exitCode = 1; });
