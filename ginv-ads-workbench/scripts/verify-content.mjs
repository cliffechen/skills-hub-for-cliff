import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { toolDefinitions } from '../workbench/dist/calculators.js';
const json = async filename => JSON.parse(await readFile(new URL('../' + filename, import.meta.url), 'utf8'));
const source = await json('public/data/source-content.json');
const shipped = await json('workbench/dist/data/source-content.json');
const coverage = await json('archive/coverage.json');
assert.deepEqual(shipped, source, '工作台数据必须与采集数据完全一致');
assert.equal(coverage.status, 'complete');
assert.equal(coverage.articleHtmlAndTitleParity, true);
assert.equal(coverage.articleIdsUnique, true);
assert.equal(coverage.conceptIdsUnique, true);
assert.equal(coverage.emptyArticleBodies, 0);
assert.ok(coverage.internalAnchors.every(anchor => anchor.targetExists));
for (const asset of coverage.assets) {
  assert.equal(asset.status, 200);
  const bytes = await readFile(new URL('../' + asset.path, import.meta.url));
  assert.equal(createHash('sha256').update(bytes).digest('hex'), asset.sha256, `资源哈希不一致：${asset.path}`);
}
for (const document of coverage.sourceDocuments) {
  const bytes = await readFile(new URL('../' + document.path, import.meta.url));
  assert.equal(createHash('sha256').update(bytes).digest('hex'), document.sha256, `来源快照哈希不一致：${document.path}`);
}
assert.deepEqual(source.counts, { topics: 13, articles: 54, concepts: 20, tools: 5 });
for (const key of ['topics', 'articles', 'concepts', 'tools']) {
  assert.equal(source[key].length, source.counts[key]);
  assert.equal(new Set(source[key].map(item => item.id)).size, source.counts[key], `${key} ID必须唯一`);
}
const linked = [];
for (const topic of source.topics) {
  assert.ok(topic.sopHtml && topic.decisionHtml && topic.tipsHtml, '每个主题完整保留流程、判断与提示');
  assert.deepEqual(topic.articleIds, source.articles.filter(article => article.topicId === topic.id).map(article => article.id));
  linked.push(...topic.articleIds);
}
assert.equal(new Set(linked).size, source.articles.length);
for (const article of source.articles) assert.ok(article.title && article.bodyHtml && article.bodyText && article.sections.length);
for (const concept of source.concepts) assert.ok(concept.title && concept.bodyHtml && concept.bodyText);
for (const tool of source.tools) {
  assert.ok(tool.inputs.length && tool.sourceCode && toolDefinitions[tool.id]);
  for (const input of tool.inputs) assert.ok(input.id && input.label && input.defaultValue !== undefined);
}
const files = ['index.html', 'styles.css', 'app.js', 'calculators.js', 'data/source-content.json'];
for (const file of files) assert.ok((await readFile(new URL('../workbench/dist/' + file, import.meta.url))).length);
const fingerprint = createHash('sha256').update(JSON.stringify(source)).digest('hex');
console.log(`内容检查通过：13主题 / 54文章 / 20概念 / 5工具；所有正文、关联与发布数据完全一致。\n数据SHA256：${fingerprint}`);
