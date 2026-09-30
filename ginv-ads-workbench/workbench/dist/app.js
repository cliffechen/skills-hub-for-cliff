import { calculateTool, toolDefinitions } from './calculators.js';

const root = document.querySelector('#app');
let data;
let query = '';
let searchFilter = 'all';
let conceptFilter = 'all';
let calculatorResults = new Map();
let calculatorValues = new Map();
let toastTimer;
let activeRoute;
let composingSearch = false;

const iconPaths = {
  home: '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>',
  book: '<path d="M12 6C9 3 5 3 3 4v15c3-1 6-1 9 2 3-3 6-3 9-2V4c-2-1-6-1-9 2Z"/><path d="M12 6v15"/>',
  cards: '<rect x="7" y="3" width="14" height="17" rx="1"/><path d="M3 7v14h14M11 8h6M11 12h6M11 16h3"/>',
  calc: '<rect x="5" y="2" width="14" height="20" rx="1"/><path d="M8 6h8M8 11h1M12 11h1M16 11h1M8 15h1M12 15h1M16 15h1M8 19h1M12 19h1M16 19h1"/>',
  search: '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
  external: '<path d="M14 3h7v7M21 3l-9 9M10 3H3v18h18v-7"/>',
  back: '<path d="m14 5-7 7 7 7"/>',
  close: '<path d="m5 5 14 14M19 5 5 19"/>',
  copy: '<rect x="8" y="8" width="13" height="13" rx="1"/><path d="M16 4V3H3v13h1"/>',
  print: '<path d="M6 8V3h12v5M6 16H3V8h18v8h-3M6 13h12v8H6zM17 11h1"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7v1"/>',
};
function icon(name, size = 19) { return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${iconPaths[name] || iconPaths.book}</svg>`; }
function esc(value = '') { return String(value).replace(/[&<>"']/g, value => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[value])); }
function cleanHtml(html = '') {
  const template = document.createElement('template');
  template.innerHTML = html;
  const allowed = new Set(['DIV', 'SPAN', 'P', 'UL', 'OL', 'LI', 'STRONG', 'B', 'EM', 'I', 'BR', 'H2', 'H3', 'H4', 'H5', 'TABLE', 'THEAD', 'TBODY', 'TR', 'TH', 'TD', 'BLOCKQUOTE', 'PRE', 'CODE', 'A', 'IMG', 'HR', 'SUB', 'SUP']);
  const remove = new Set(['SCRIPT', 'STYLE', 'IFRAME', 'OBJECT', 'EMBED', 'FORM', 'INPUT', 'BUTTON', 'LINK', 'META']);
  for (const element of [...template.content.querySelectorAll('*')]) {
    if (remove.has(element.tagName) || (element.tagName === 'I' && element.className.includes('fa-'))) { element.remove(); continue; }
    if (!allowed.has(element.tagName)) { element.replaceWith(...element.childNodes); continue; }
    for (const attr of [...element.attributes]) {
      if (!['class', 'href', 'src', 'alt', 'colspan', 'rowspan', 'title'].includes(attr.name)) element.removeAttribute(attr.name);
    }
    if (element.tagName === 'A') {
      const url = element.getAttribute('href') || '';
      if (!/^(https?:\/\/|#|\.\/)/i.test(url)) element.removeAttribute('href');
      else if (/^https?:/i.test(url)) { element.setAttribute('target', '_blank'); element.setAttribute('rel', 'noopener noreferrer'); }
    }
    if (element.tagName === 'IMG') {
      const src = element.getAttribute('src') || '';
      if (!/^(https?:\/\/|\.\/|data:image\/)/i.test(src)) element.removeAttribute('src');
      element.setAttribute('loading', 'lazy');
    }
  }
  return template.innerHTML;
}

function route() {
  const segments = location.hash.replace(/^#\/?/, '').split('/').map(value => { try { return decodeURIComponent(value); } catch { return ''; } });
  return { view: segments[0] || 'overview', id: segments[1] || '', articleId: segments[2] || '' };
}
function go(view, id = '', articleId = '') {
  const next = `#${view}${id ? '/' + encodeURIComponent(id) : ''}${articleId ? '/' + encodeURIComponent(articleId) : ''}`;
  if (location.hash === next) render(); else location.hash = next;
}
function sectionFor(view) { return ({ topic: 'library', article: 'library', concept: 'concepts', tool: 'tools' })[view] || view; }
function topicArticles(topic) { return data.articles.filter(article => article.topicId === topic.id); }
function methodCount(topic) { return topic.articleIds.length; }
function short(value, length = 100) { return value.length > length ? value.slice(0, length) + '…' : value; }
function dateLabel() { return new Intl.DateTimeFormat('zh-CN', { timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date(data.capturedAt)).replaceAll('/', '.'); }

function searchBox(value = '', placeholder = '搜索问题、关键词或广告指标') {
  return `<label class="search-box">${icon('search', 17)}<input id="global-search" type="search" value="${esc(value)}" placeholder="${esc(placeholder)}" aria-label="搜索全部知识与工具" autocomplete="off"><span class="key-label">/</span></label>`;
}
function heading(title, subtitle, number = '') {
  return `<div class="page-heading"><div><h1>${esc(title)}</h1>${subtitle ? `<p>${esc(subtitle)}</p>` : ''}</div>${number ? `<span class="minor-number">${esc(number)}</span>` : ''}</div>`;
}
function breadcrumb(parts = []) { return `<div class="breadcrumb"><button data-view="overview">工作台</button>${parts.map(part => `<span>/</span><span>${esc(part)}</span>`).join('')}</div>`; }
function footer() { return `<footer class="footer"><span>GinvAds · ${data.counts.articles} 篇方法论 / ${data.counts.concepts} 张概念卡 / ${data.counts.tools} 个工具</span><a href="${esc(data.source.url)}" target="_blank" rel="noopener noreferrer">来源：Ginv-Ads 广告智库</a></footer>`; }
function sourceNote(url = data.source.url) { return `<p class="source-note">内容保留原站表述，采集于 ${dateLabel()}。<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">查看原始来源</a></p>`; }
function toolDescription(tool) { return ({ t2: '由目标 ACoS、转化率和客单价，反推允许的平均 CPC。', t3: '按平均转化率和 CPC，估算约一单点击量的预算。' })[tool.id] || tool.description; }
function toolCard(tool) { return `<button class="tool-card" data-view="tool" data-id="${esc(tool.id)}"><span class="tool-top">${icon('calc', 21)}<span class="tool-num">0${tool.order}</span></span><h3>${esc(tool.title)}</h3><p>${esc(short(toolDescription(tool), 70))}</p></button>`; }
function topicItem(topic) {
  return `<button class="topic-item" data-view="topic" data-id="${esc(topic.id)}"><span class="topic-index">${String(topic.order).padStart(2, '0')}</span><span class="topic-info"><span class="topic-name">${esc(topic.title)}</span><span class="topic-desc">${esc(short(topic.tipsText || topic.sopText, 66))}</span></span><span class="topic-count">${methodCount(topic)} 篇</span><span class="topic-indicator"></span></button>`;
}

function overview() {
  return `${breadcrumb(['知识总览'])}${heading('广告知识工作台', '从投放问题，到方法、指标与计算。', 'AMAZON PPC')}<div class="search-area">${searchBox(query)}<span class="small-label">全文检索</span></div><section class="stats" aria-label="知识库完整收录统计"><div class="stat"><div class="number">${data.counts.topics}<small>TOPICS</small></div><div class="label">专题方法论</div><div class="sub">${data.counts.articles} 篇完整内容</div></div><div class="stat"><div class="number">${data.counts.concepts}<small>CONCEPTS</small></div><div class="label">广告概念卡</div><div class="sub">定义 · 公式 · 应用</div></div><div class="stat"><div class="number">${String(data.counts.tools).padStart(2, '0')}<small>TOOLS</small></div><div class="label">计算工具</div><div class="sub">参数输入 · 结果解读</div></div></section><section><div class="section-heading"><h2>专题目录</h2><span>${data.counts.topics} 个主题 · ${data.counts.articles} 篇方法论</span></div><div class="topic-grid">${data.topics.map(topicItem).join('')}</div></section><section><div class="section-heading"><h2>投放计算工具</h2><button class="text-link" data-view="tools">全部工具</button></div><div class="tool-grid">${data.tools.map(toolCard).join('')}</div></section>${footer()}`;
}
function library() { return `${breadcrumb(['主题库'])}${heading('主题方法论', '完整保留核心流程、快速判断与每篇方法论。', `${data.counts.articles} ARTICLES`)}<div class="search-area">${searchBox(query, '搜索方法、投放问题或关键词')}</div><div class="topic-grid">${data.topics.map(topicItem).join('')}</div>${footer()}`; }
function topicView(current) {
  const topic = data.topics.find(item => item.id === current.id);
  if (!topic) return empty('找不到此主题', '返回主题库重新选择。', 'library');
  const articles = topicArticles(topic);
  const article = current.articleId ? articles.find(item => item.id === current.articleId) : undefined;
  if (current.articleId && !article) return empty('找不到此篇方法论', '返回本主题重新选择。', 'topic', topic.id);
  const visible = article ? [article] : articles;
  return `${breadcrumb(['主题库', topic.title])}<div class="reader-header"><div><h1>${esc(topic.title)}</h1><div class="reader-meta">${articles.length} 篇方法论 · ${article ? '单篇阅读' : '完整主题'} · 来源 GinvAds</div></div><div class="reader-controls"><button class="outline-button" data-action="print" title="打印当前阅读内容">${icon('print', 16)}<span>打印</span></button></div></div><nav class="chapter-nav" aria-label="主题章节"><button data-view="topic" data-id="${esc(topic.id)}" class="${!article ? 'active' : ''}">完整主题</button>${articles.map((item, index) => `<button data-view="topic" data-id="${esc(topic.id)}" data-article="${esc(item.id)}" class="${article?.id === item.id ? 'active' : ''}" title="${esc(item.title)}">${String(index + 1).padStart(2, '0')} · ${esc(short(item.title, 25))}</button>`).join('')}</nav><div class="content-detail">${!article ? `<section class="topic-overview prose"><div class="topic-sop">${cleanHtml(topic.sopHtml)}</div><div class="topic-decision">${cleanHtml(topic.decisionHtml)}</div><div class="topic-tip">${cleanHtml(topic.tipsHtml)}</div></section>` : ''}${visible.map(item => `<article class="article-section" id="article-${esc(item.id)}" data-article-id="${esc(item.id)}"><div class="article-number">方法论 ${String(item.order).padStart(2, '0')} / ${String(articles.length).padStart(2, '0')}</div><h2 class="article-title">${esc(item.title)}</h2><div class="prose">${cleanHtml(item.bodyHtml)}</div></article>`).join('')}</div>${sourceNote(topic.sourceUrl)}${footer()}`;
}
function conceptCard(concept) { return `<button class="concept-card" data-view="concept" data-id="${esc(concept.id)}"><span class="concept-code">CONCEPT ${String(concept.order).padStart(2, '0')}</span><h3>${esc(concept.title)}</h3><p>${esc(short(concept.meaning, 98))}</p><span class="concept-more">查看定义与应用</span></button>`; }
function concepts() {
  const list = conceptFilter === 'formula' ? data.concepts.filter(item => item.formula) : data.concepts;
  return `${breadcrumb(['概念卡'])}${heading('广告概念卡', '定义、公式、含义与使用场景。', `${data.counts.concepts} CONCEPTS`)}<div class="search-area">${searchBox(query, '搜索 ACoS、EV、匹配方式…')}</div><div class="view-tabs" aria-label="概念卡筛选"><button class="${conceptFilter === 'all' ? 'active' : ''}" data-concept-filter="all">全部概念<span>${data.concepts.length}</span></button><button class="${conceptFilter === 'formula' ? 'active' : ''}" data-concept-filter="formula">包含公式<span>${data.concepts.filter(item => item.formula).length}</span></button></div><div class="concept-grid">${list.map(conceptCard).join('')}</div>${footer()}`;
}
function conceptView(current) {
  const concept = data.concepts.find(item => item.id === current.id);
  if (!concept) return empty('找不到此概念', '返回概念卡重新选择。', 'concepts');
  return `${breadcrumb(['概念卡', concept.title])}${heading(concept.title, concept.subtitle, `CONCEPT ${String(concept.order).padStart(2, '0')}`)}<div class="content-detail"><div class="prose concept-detail">${cleanHtml(concept.bodyHtml)}</div></div>${sourceNote(concept.sourceUrl)}<div style="margin:24px 0"><button class="outline-button" data-view="concepts">${icon('back', 15)}返回概念卡</button></div>${footer()}`;
}
function toolsView() { return `${breadcrumb(['计算工具'])}${heading('投放计算工具', '从实际参数出发，核算点击成本、广告效率与预算。', `${data.counts.tools} TOOLS`)}<div class="tool-grid tools-catalog">${data.tools.map(toolCard).join('')}</div><div class="formula-section"><h2>计算口径</h2><p>五个工具沿用原站计算公式。转化率与 ACoS 输入百分数，金额统一使用美元；结果旁会显示公式、取整方式和使用说明。</p><p>“反推保本 CPC”实际求目标 ACoS 下允许的点击成本；“保底日预算”是按平均转化率估算的参考值。</p></div>${sourceNote()}${footer()}`; }
function fieldInput(input, tool) {
  const saved = calculatorValues.get(tool.id) || {};
  const value = saved[input.id] ?? input.defaultValue;
  const currency = /USD/.test(input.label);
  const percentage = /%/.test(input.label);
  const label = input.label.replace(/\s*\((USD|%)\)/g, '');
  const cvr = percentage && !/ACoS/.test(input.label);
  const positive = (tool.id === 't1' && input.id === 't1p') || (tool.id === 't2' && input.id === 't2p') || ((tool.id === 't3' || tool.id === 't4') && cvr);
  const signed = /m$/.test(input.id);
  return `<div class="form-field"><label for="${esc(input.id)}">${esc(label)}</label><div class="input-with-unit"><input id="${esc(input.id)}" name="${esc(input.id)}" type="number" inputmode="decimal" step="any" ${signed ? '' : `min="${positive ? '0.000001' : '0'}"`} ${cvr ? 'max="100"' : ''} value="${esc(value)}" required aria-describedby="help-${esc(input.id)}"><span>${currency ? 'USD' : '%'}</span></div><div class="field-help" id="help-${esc(input.id)}">${esc(toolDefinitions[tool.id].help[input.id] || '')}</div></div>`;
}
function toolView(current) {
  const tool = data.tools.find(item => item.id === current.id);
  if (!tool) return empty('找不到此工具', '返回计算工具重新选择。', 'tools');
  const definition = toolDefinitions[tool.id];
  return `${breadcrumb(['计算工具', tool.title])}${heading(tool.title, toolDescription(tool), `TOOL ${String(tool.order).padStart(2, '0')}`)}<nav class="chapter-nav" aria-label="工具切换">${data.tools.map(item => `<button class="${tool.id === item.id ? 'active' : ''}" data-view="tool" data-id="${esc(item.id)}">${esc(item.title)}</button>`).join('')}</nav><form id="calculator-form" class="calc-layout" data-tool="${esc(tool.id)}" novalidate><div class="form-grid">${tool.inputs.map(item => fieldInput(item, tool)).join('')}</div><div class="form-actions"><button type="submit" class="primary-button">${icon('calc', 17)}计算结果</button><button type="button" class="secondary-button" data-action="reset-calculator">恢复默认值</button></div><div id="calculator-error" role="alert"></div></form><div class="formula-section"><h2>计算公式</h2><div class="formula-box">${esc(definition.formula)}</div><p>${esc(definition.note)}</p></div><details class="source-details"><summary>原站工具说明</summary><div class="prose"><p>${esc(tool.description)}</p><p>${tool.inputs.map(item => esc(item.label) + '：默认 ' + esc(item.defaultValue)).join('；')}</p></div></details>${sourceNote(tool.sourceUrl)}${footer()}`;
}
function searchMatches() {
  const terms = query.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
  if (!terms.length) return [];
  const source = [
    ...data.topics.map(topic => ({ type: 'topic', title: topic.title, text: `${topic.sopText}\n${topic.decisionText}\n${topic.tipsText}`, topic: topic.title, id: topic.id, order: topic.order, subtitle: '专题核心流程', view: 'topic' })),
    ...data.articles.map(article => ({ type: 'article', title: article.title, text: article.bodyText, topic: data.topics.find(topic => topic.id === article.topicId)?.title || '', id: article.topicId, articleId: article.id, order: article.order, view: 'topic' })),
    ...data.concepts.map(concept => ({ type: 'concept', title: concept.title, text: concept.bodyText, topic: concept.subtitle, id: concept.id, order: concept.order, view: 'concept' })),
    ...data.tools.map(tool => ({ type: 'tool', title: tool.title, text: tool.bodyText + '\n' + toolDefinitions[tool.id].note + '\n' + toolDefinitions[tool.id].formula, topic: '计算工具', id: tool.id, order: tool.order, view: 'tool' })),
  ];
  return source.filter(item => terms.every(term => `${item.title}\n${item.text}`.toLocaleLowerCase().includes(term))).map(item => ({ ...item, score: terms.reduce((score, term) => score + (item.title.toLocaleLowerCase().includes(term) ? 10 : 1), 0) })).sort((a, b) => b.score - a.score);
}
function highlight(text) {
  let escaped = esc(text);
  const terms = query.trim().split(/\s+/).filter(Boolean).sort((a, b) => b.length - a.length);
  if (!terms.length) return escaped;
  const expression = terms.map(term => esc(term).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|');
  return escaped.replace(new RegExp(expression, 'gi'), match => `<mark>${match}</mark>`);
}
function snippet(text) {
  const terms = query.trim().toLocaleLowerCase().split(/\s+/);
  const normalized = text.replace(/\s+/g, ' ');
  const positions = terms.map(term => normalized.toLocaleLowerCase().indexOf(term)).filter(position => position >= 0);
  const at = positions.length ? Math.min(...positions) : 0;
  const start = Math.max(0, at - 25);
  return `${start ? '…' : ''}${normalized.slice(start, start + 160)}${normalized.length > start + 160 ? '…' : ''}`;
}
function searchView() {
  const results = searchMatches();
  const visible = searchFilter === 'all' ? results : results.filter(item => item.type === searchFilter);
  const filters = [['all', '全部'], ['topic', '主题'], ['article', '方法论'], ['concept', '概念'], ['tool', '工具']];
  return `${breadcrumb(['全文搜索'])}${heading('搜索知识库', query ? `“${query}” · 找到 ${results.length} 条相关内容` : '输入关键词，搜索所有正文、概念和工具。')}<div class="search-area">${searchBox(query)}</div><div class="view-tabs">${filters.map(([id, label]) => `<button class="${searchFilter === id ? 'active' : ''}" data-search-filter="${id}">${label}<span>${id === 'all' ? results.length : results.filter(item => item.type === id).length}</span></button>`).join('')}</div>${visible.length ? `<div class="search-results">${visible.map(item => `<button class="search-result" data-view="${item.view}" data-id="${esc(item.id)}" ${item.articleId ? `data-article="${esc(item.articleId)}"` : ''}><span class="result-type">${esc(({ topic: '主题', article: '方法论', concept: '概念卡', tool: '工具' })[item.type])}<span>${esc(item.topic)}</span></span><h3>${highlight(item.title)}</h3><p>${highlight(snippet(item.text))}</p></button>`).join('')}</div>` : `<div class="empty-state">${query ? '没有找到相关内容' : '搜索整个广告知识库'}<p>${query ? '可以换一个关键词，或减少搜索词。' : '试试：ACoS、断货、否词、转化率。'}</p></div>`}${footer()}`;
}
function empty(title, message, view = 'overview', id = '') { return `<div class="empty-state">${esc(title)}<p>${esc(message)}</p><button class="outline-button" data-view="${view}" data-id="${esc(id)}" style="margin-top:20px">返回</button></div>`; }

function panelLabel(label) { return `<div class="panel-label"><span class="square"></span>${label}</div>`; }
function panelFoot() { return `<div class="panel-foot"><span>SOURCE / ${dateLabel()}</span><a href="${esc(data.source.url)}" target="_blank" rel="noopener noreferrer">Ginv-Ads 广告智库 ${icon('external', 13)}</a></div>`; }
function overviewPanel() {
  return `${panelLabel('KNOWLEDGE INDEX')}<h2>把问题，<br>变成下一步。</h2><p>选择一个主题，找到对应的操作流程和判断标准。</p><div class="panel-number">${data.counts.articles}<small>篇</small></div><div class="panel-number-label">完整方法论 · 已收录</div><div class="panel-dot-grid" aria-hidden="true">${Array.from({ length: data.counts.articles }, () => '<i></i>').join('')}</div><div class="panel-line"></div><div class="panel-label">常用主题</div><div class="panel-links">${['new_product', 'bid_budget', 'negative', 'report'].map(id => { const topic = data.topics.find(item => item.id === id); return topic ? `<button data-view="topic" data-id="${esc(id)}">${esc(topic.title)}<small>${methodCount(topic)} 篇</small></button>` : ''; }).join('')}</div><div class="panel-mini-stats"><div><strong>${data.counts.concepts}</strong><span>概念卡</span></div><div><strong>${data.counts.tools}</strong><span>计算工具</span></div></div>${panelFoot()}`;
}
function toolResultPanel(toolId) {
  const result = calculatorResults.get(toolId);
  const tool = data.tools.find(item => item.id === toolId);
  return `${panelLabel('CALCULATION')}<h2>计算结果</h2>${result ? `<div id="calculation-results" aria-live="polite">${result.metrics.map((item, index) => `<div class="result-item ${index === 0 ? 'main-result' : ''}"><div class="result-label">${esc(item.label)}</div><div class="result-value" data-metric="${index}">${item.unit === 'USD' ? '$' : ''}${Number(item.value).toFixed(item.precision)}<small>${item.unit === 'USD' ? '' : esc(item.unit)}</small></div>${item.note ? `<div class="result-note">${esc(item.note)}</div>` : ''}</div>`).join('')}<p>${esc(result.summary)}</p><button class="panel-copy" data-action="copy-result">${icon('copy', 15)}复制结果</button></div>` : '<div class="result-empty">填写参数后点击「计算结果」。<br>结果和说明会显示在这里。</div>'}<div class="panel-line"></div><div class="panel-label">相关概念</div><div class="panel-links">${(toolDefinitions[toolId]?.conceptIds || []).map(id => data.concepts.find(item => item.id === id)).filter(Boolean).map(concept => `<button data-view="concept" data-id="${esc(concept.id)}">${esc(concept.title)}</button>`).join('')}</div><p class="result-disclaimer">${esc(toolDefinitions[toolId]?.note || tool?.description || '')}</p>${panelFoot()}`;
}
function topicPanel(current) {
  const topic = data.topics.find(item => item.id === current.id);
  if (!topic) return overviewPanel();
  const articles = topicArticles(topic);
  return `${panelLabel('READING DESK')}<h2>${esc(topic.title)}</h2><p>${esc(topic.tipsText)}</p><div class="panel-number">${String(articles.length).padStart(2, '0')}<small>篇</small></div><div class="panel-number-label">当前主题方法论</div><div class="panel-line"></div><div class="panel-label">章节目录</div><div class="panel-links"><button data-view="topic" data-id="${esc(topic.id)}">核心流程与快速判断</button>${articles.map(article => `<button data-view="topic" data-id="${esc(topic.id)}" data-article="${esc(article.id)}"><span>${esc(short(article.title, 46))}</span><small>${String(article.order).padStart(2, '0')}</small></button>`).join('')}</div><div class="panel-line"></div><div class="panel-label">计算工具</div><div class="panel-links">${data.tools.slice(0, 3).map(tool => `<button data-view="tool" data-id="${esc(tool.id)}">${esc(tool.title)}</button>`).join('')}</div>${panelFoot()}`;
}
function conceptsPanel(current) {
  const concept = data.concepts.find(item => item.id === current.id);
  return `${panelLabel('CONCEPT LIBRARY')}<h2>${concept ? esc(concept.title) : '理解指标，<br>再判断表现。'}</h2>${concept ? `<p>${esc(concept.meaning)}</p>${concept.formula ? `<div class="panel-line"></div><div class="panel-formula">${esc(concept.formula)}</div>` : ''}` : `<div class="panel-number">${data.counts.concepts}<small>张</small></div><p>从 ACoS、CVR 到匹配方式与广告位，把常见概念放在手边。</p>`}<div class="panel-line"></div><div class="panel-label">常用指标</div><div class="panel-links">${data.concepts.filter(item => ['acos', 'cpc', 'cvr', 'ev', 'tacos'].includes(item.id)).map(item => `<button data-view="concept" data-id="${esc(item.id)}">${esc(item.title)}<small>定义 / 应用</small></button>`).join('')}</div>${panelFoot()}`;
}
function panel(current) {
  if (current.view === 'tool' && toolDefinitions[current.id]) return toolResultPanel(current.id);
  if (current.view === 'topic') return topicPanel(current);
  if (current.view === 'concept' || current.view === 'concepts') return conceptsPanel(current);
  if (current.view === 'tools') return `${panelLabel('ADVERTISING TOOLS')}<h2>先核算，<br>再调整投放。</h2><p>使用同一口径的真实参数，计算每次点击的价值与可承受成本。</p><div class="panel-number">05<small>个</small></div><div class="panel-number-label">原站计算工具 · 完整保留</div><div class="panel-line"></div><div class="panel-label">选择工具</div><div class="panel-links">${data.tools.map(tool => `<button data-view="tool" data-id="${esc(tool.id)}">${esc(tool.title)}<small>0${tool.order}</small></button>`).join('')}</div>${panelFoot()}`;
  if (current.view === 'search') return `${panelLabel('FULL TEXT SEARCH')}<h2>搜索所有内容</h2><p>支持专题核心流程、54 篇完整正文、概念卡和工具说明。</p><div class="panel-line"></div><div class="panel-label">可以这样搜</div><div class="panel-links">${['ACoS', '断货', '否词', '转化率', 'SKAG'].map(term => `<button data-search="${term}">${term}</button>`).join('')}</div>${panelFoot()}`;
  return overviewPanel();
}

function render() {
  if (!data) return;
  const current = route();
  activeRoute = current;
  const selected = sectionFor(current.view);
  const nav = [['overview', '工作台', 'home'], ['library', '主题库', 'book'], ['concepts', '概念卡', 'cards'], ['tools', '计算工具', 'calc']];
  const body = current.view === 'overview' ? overview() : current.view === 'library' ? library() : current.view === 'topic' ? topicView(current) : current.view === 'concepts' ? concepts() : current.view === 'concept' ? conceptView(current) : current.view === 'tools' ? toolsView() : current.view === 'tool' ? toolView(current) : current.view === 'search' ? searchView() : empty('页面不存在', '请从左侧导航选择内容。');
  root.innerHTML = `<div class="shell"><aside class="rail" aria-label="主导航"><button class="rail-logo" data-view="overview" aria-label="GinvAds 工作台"><span class="logo-box">G</span></button><nav class="rail-nav">${nav.map(([view, label, name]) => `<button class="rail-button ${selected === view ? 'active' : ''}" data-view="${view}" aria-label="${label}" ${selected === view ? 'aria-current="page"' : ''}>${icon(name, 20)}<span class="tooltip">${label}</span></button>`).join('')}<button class="rail-button ${selected === 'search' ? 'active' : ''}" data-view="search" aria-label="全文搜索">${icon('search', 20)}<span class="tooltip">全文搜索</span></button></nav><a class="rail-bottom" href="${esc(data.source.url)}" target="_blank" rel="noopener noreferrer" aria-label="打开原站">${icon('external', 18)}</a></aside><header class="topbar"><button class="wordmark" data-view="overview">GinvAds<span>广告智库</span></button><nav class="topnav" aria-label="工作区">${nav.map(([view, label]) => `<button data-view="${view}" class="${selected === view ? 'active' : ''}" ${selected === view ? 'aria-current="page"' : ''}>${label}</button>`).join('')}</nav><div class="topbar-end"><span class="local-badge">知识库快照 · ${dateLabel()}</span><button class="header-source" data-view="search" aria-label="搜索">${icon('search', 18)}</button><a class="header-source" href="${esc(data.source.url)}" target="_blank" rel="noopener noreferrer" aria-label="打开原站">${icon('external', 17)}</a></div></header><nav class="mobile-nav" aria-label="移动导航">${nav.map(([view, label]) => `<button data-view="${view}" class="${selected === view ? 'active' : ''}" ${selected === view ? 'aria-current="page"' : ''}>${label}</button>`).join('')}</nav><div class="body-layout"><main id="main" class="main">${body}</main><aside id="blue-panel" class="blue-panel" aria-label="${current.view === 'tool' ? '计算结果与相关概念' : '相关知识与导航'}">${panel(current)}</aside></div></div><div id="toast" class="toast" role="status" hidden></div>`;
  document.title = `${current.view === 'topic' ? data.topics.find(item => item.id === current.id)?.title || '主题库' : current.view === 'tool' ? data.tools.find(item => item.id === current.id)?.title || '计算工具' : current.view === 'concept' ? data.concepts.find(item => item.id === current.id)?.title || '概念卡' : ({ overview: '广告工作台', library: '主题库', concepts: '概念卡', tools: '计算工具', search: '全文搜索' })[current.view] || '广告工作台'} · GinvAds`;
  if (current.view === 'tool' && toolDefinitions[current.id]) runCalculator(false);
}

function showToast(message) {
  const target = document.querySelector('#toast');
  target.textContent = message; target.hidden = false;
  clearTimeout(toastTimer); toastTimer = setTimeout(() => { target.hidden = true; }, 2400);
}
function readForm() {
  const form = document.querySelector('#calculator-form');
  return form ? Object.fromEntries(new FormData(form)) : null;
}
function runCalculator(announce = true) {
  const form = document.querySelector('#calculator-form');
  if (!form) return;
  const values = readForm();
  calculatorValues.set(form.dataset.tool, values);
  const error = document.querySelector('#calculator-error');
  try {
    const result = calculateTool(form.dataset.tool, values);
    calculatorResults.set(form.dataset.tool, result);
    error.innerHTML = '';
    document.querySelector('#blue-panel').innerHTML = toolResultPanel(form.dataset.tool);
    if (announce) { showToast('计算完成'); if (window.innerWidth <= 740) document.querySelector('#blue-panel').scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  } catch (issue) {
    calculatorResults.delete(form.dataset.tool);
    error.innerHTML = `<p class="error-message">${esc(issue.message)}</p>`;
    document.querySelector('#blue-panel').innerHTML = toolResultPanel(form.dataset.tool);
  }
}

root.addEventListener('click', async event => {
  const target = event.target.closest('button,[data-view]');
  if (!target) return;
  if (target.dataset.view) { clearTimeout(searchTimer); go(target.dataset.view, target.dataset.id, target.dataset.article); return; }
  if (target.dataset.search) { query = target.dataset.search; searchFilter = 'all'; go('search'); return; }
  if (target.dataset.searchFilter) { searchFilter = target.dataset.searchFilter; render(); return; }
  if (target.dataset.conceptFilter) { conceptFilter = target.dataset.conceptFilter; render(); return; }
  if (target.dataset.action === 'print') window.print();
  if (target.dataset.action === 'reset-calculator') { calculatorValues.delete(activeRoute.id); calculatorResults.delete(activeRoute.id); render(); showToast('已恢复默认参数'); }
  if (target.dataset.action === 'copy-result') {
    const result = calculatorResults.get(activeRoute.id);
    const tool = data.tools.find(item => item.id === activeRoute.id);
    if (!result || !tool) return;
    const content = `${tool.title}\n${result.metrics.map(item => `${item.label}：${item.unit === 'USD' ? '$' : ''}${item.value.toFixed(item.precision)} ${item.unit === 'USD' ? '' : item.unit}`).join('\n')}\n${result.summary}\n${result.note}`;
    try { await navigator.clipboard.writeText(content); showToast('结果已复制'); } catch { showToast('浏览器未允许复制，请选中结果文字复制。'); }
  }
});
let searchTimer;
function scheduleSearch(input) {
  query = input.value;
  clearTimeout(searchTimer);
  const start = input.selectionStart;
  const end = input.selectionEnd;
  searchTimer = setTimeout(() => {
    if (route().view !== 'search') history.replaceState(null, '', '#search');
    searchFilter = 'all'; render();
    const search = document.querySelector('#global-search');
    search.focus();
    try { search.setSelectionRange(start, end); } catch { /* Some browser variants omit selection support. */ }
  }, 180);
}
root.addEventListener('compositionstart', event => { if (event.target.id === 'global-search') { composingSearch = true; clearTimeout(searchTimer); } });
root.addEventListener('compositionend', event => { if (event.target.id === 'global-search') { composingSearch = false; scheduleSearch(event.target); } });
root.addEventListener('input', event => {
  if (event.target.id === 'global-search') {
    if (!composingSearch && !event.isComposing) scheduleSearch(event.target);
  } else if (event.target.closest('#calculator-form')) {
    calculatorValues.set(activeRoute.id, readForm());
    calculatorResults.delete(activeRoute.id);
    document.querySelector('#calculator-error').innerHTML = '';
    document.querySelector('#blue-panel').innerHTML = toolResultPanel(activeRoute.id);
  }
});
root.addEventListener('submit', event => { if (event.target.id === 'calculator-form') { event.preventDefault(); runCalculator(); } });
window.addEventListener('hashchange', () => { clearTimeout(searchTimer); render(); window.scrollTo({ top: 0, behavior: 'instant' }); });
document.querySelector('.skip-link').addEventListener('click', event => {
  event.preventDefault();
  const main = document.querySelector('#main');
  if (main) { main.tabIndex = -1; main.focus(); main.scrollIntoView({ block: 'start' }); }
});
document.addEventListener('keydown', event => {
  if (event.key === '/' && !event.ctrlKey && !event.metaKey && !['INPUT', 'TEXTAREA', 'SELECT'].includes(event.target.tagName)) {
    event.preventDefault(); if (!document.querySelector('#global-search')) { go('search'); setTimeout(() => document.querySelector('#global-search')?.focus(), 0); } else document.querySelector('#global-search').focus();
  }
});

try {
  const response = await fetch('./data/source-content.json');
  if (!response.ok) throw new Error(`知识数据读取失败（${response.status}）。`);
  data = await response.json();
  if (![data.topics, data.articles, data.concepts, data.tools].every(Array.isArray)) throw new Error('知识库文件格式不完整。');
  render();
  registerWorkbenchTools();
} catch (error) {
  root.innerHTML = `<div class="loading-page"><div><h1 style="font-size:24px">知识库暂时无法载入</h1><p style="margin-top:14px">${esc(error.message)}</p><p style="margin-top:10px">请通过本地启动命令或工作台网站打开，避免直接双击 HTML 文件。</p><button class="outline-button" style="margin-top:20px" onclick="location.reload()">重新载入</button></div></div>`;
}

function registerWorkbenchTools() {
  const context = document.modelContext;
  if (!context?.registerTool) return;
  const lifecycle = new AbortController();
  window.addEventListener('pagehide', () => lifecycle.abort(), { once: true });
  const register = tool => {
    try { Promise.resolve(context.registerTool(tool, { signal: lifecycle.signal })).catch(error => console.warn('工作台工具注册失败：', error.message)); }
    catch (error) { console.warn('工作台工具注册失败：', error.message); }
  };
  register({
    name: 'search_advertising_knowledge',
    title: '搜索广告知识库',
    description: '搜索已收录的主题、54篇方法论、20张概念卡及5个工具，并在工作台显示搜索结果。',
    annotations: { readOnlyHint: false, untrustedContentHint: true },
    inputSchema: { type: 'object', properties: { query: { type: 'string', minLength: 1, description: '搜索词，例如ACoS、断货或否词。' } }, required: ['query'], additionalProperties: false },
    execute(input) {
      if (!input || typeof input.query !== 'string' || !input.query.trim()) throw new Error('请提供非空搜索词。');
      query = input.query.trim(); searchFilter = 'all';
      clearTimeout(searchTimer);
      history.replaceState(null, '', '#search'); render();
      const matches = searchMatches();
      return { query, count: matches.length, results: matches.slice(0, 10).map(item => ({ type: item.type, title: item.title, id: item.articleId || item.id, excerpt: snippet(item.text) })) };
    },
  });
  register({
    name: 'calculate_advertising_tool',
    title: '计算广告指标',
    description: '用工作台原站公式计算广告参数，并更新对应工具页面和可见结果。t1=盈亏平衡ACoS，t0=单点击EV，t2=目标ACoS允许CPC，t3=预算参考，t4=高点击阈值。',
    annotations: { readOnlyHint: false, untrustedContentHint: false },
    inputSchema: { type: 'object', properties: { toolId: { type: 'string', enum: ['t1', 't0', 't2', 't3', 't4'] }, values: { type: 'object', description: '输入ID到数字的映射，与界面输入一一对应。例如t1:{t1p:40,t1m:12}。', properties: Object.fromEntries(data.tools.flatMap(tool => tool.inputs.map(input => [input.id, { type: 'number', description: input.label }]))), additionalProperties: false } }, required: ['toolId', 'values'], additionalProperties: false },
    execute(input) {
      const tool = data.tools.find(item => item.id === input?.toolId);
      if (!tool || !input.values || typeof input.values !== 'object' || Array.isArray(input.values)) throw new Error('请提供有效工具ID与参数。');
      const allowed = tool.inputs.map(item => item.id);
      if (Object.keys(input.values).some(key => !allowed.includes(key))) throw new Error('参数ID与选定工具不一致。');
      const result = calculateTool(tool.id, input.values);
      clearTimeout(searchTimer);
      calculatorValues.set(tool.id, { ...input.values }); calculatorResults.set(tool.id, result);
      history.replaceState(null, '', `#tool/${tool.id}`); render();
      return { toolId: tool.id, title: tool.title, metrics: result.metrics, summary: result.summary, note: result.note };
    },
  });
}
