import { copyFile, readFile } from 'node:fs/promises';
const source = new URL('../public/data/source-content.json', import.meta.url);
const data = JSON.parse(await readFile(source, 'utf8'));
if (data.coverage.status !== 'complete') throw new Error('采集尚未完成覆盖审计，请先完成采集审计。');
await copyFile(source, new URL('../workbench/dist/data/source-content.json', import.meta.url));
console.log(`数据已同步：${data.counts.topics} 主题 / ${data.counts.articles} 文章 / ${data.counts.concepts} 概念 / ${data.counts.tools} 工具。`);
