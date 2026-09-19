import { PhonePreview } from './preview.js';

const $ = (id) => document.getElementById(id);
const state = { project: null, projects: [], selected: null, version: 0, savedVersion: 0,
  saving: null, saveTimer: null, saveError: null, importing: false, loading: false, fileIntent: null };
const uid = () => crypto.randomUUID();
const clone = (value) => structuredClone(value);
const esc = (value = '') => String(value).replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const imageTypes = new Set(['image/png', 'image/jpeg', 'image/webp']);
const assetURL = (id) => `/api/projects/${state.project.id}/assets/${id}`;
const targetJSON = (target) => esc(JSON.stringify(target));

function toast(message, isError = false) {
  $('toast').textContent = message;
  $('toast').classList.toggle('error', isError);
  $('toast').hidden = false;
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => { $('toast').hidden = true; }, isError ? 7000 : 3800);
}

async function request(path, options = {}) {
  let response;
  try { response = await fetch(path, { ...options, headers: { 'Content-Type': 'application/json', ...options.headers } }); }
  catch { throw new Error('无法连接本地服务。请确认启动窗口仍在运行，然后重试保存。'); }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(data.error || `操作失败（${response.status}）`);
    error.status = response.status;
    throw error;
  }
  return data;
}

function setSaveStatus() {
  const status = $('saveStatus');
  status.classList.toggle('save-error', !!state.saveError);
  status.textContent = state.saveError ? '未保存 · 请重试' : state.importing ? '正在导入素材…' :
    state.saving ? '正在保存…' : state.version !== state.savedVersion ? '等待保存…' : state.project ? '已保存在本机' : '本地私享 · 无需上传云端';
  status.title = state.saveError?.message || '';
  $('retrySave').hidden = !state.saveError;
  const busy = state.importing || state.loading;
  $('editorPanel').inert = busy;
  $('projectSelect').disabled = busy || !state.projects.length;
  $('newProject').disabled = busy;
  $('retrySave').disabled = busy;
  for (const id of ['renameProject', 'addImageModule', 'addCarouselModule', 'addVideoModule', 'viewportSelect', 'zoomSelect', 'shellToggle', 'toggleEditor']) $(id).disabled = busy || !state.project;
}

function markChanged({ preview = true, editor = false, delay = 650 } = {}) {
  if (!state.project) return;
  state.version++;
  if (preview) phone.update(state.project, { preservePosition: true });
  if (editor) renderEditor();
  clearTimeout(state.saveTimer);
  if (!state.saveError) state.saveTimer = setTimeout(saveNow, delay);
  setSaveStatus();
}

async function saveNow() {
  clearTimeout(state.saveTimer);
  if (state.project) {
    const actualView = phone.captureView();
    if (JSON.stringify(actualView) !== JSON.stringify(state.project.view)) {
      state.project.view = actualView;
      state.version++;
    }
  }
  if (!state.project || state.version === state.savedVersion) return true;
  if (state.saving) {
    const ok = await state.saving;
    return ok ? saveNow() : false;
  }
  const project = state.project;
  const version = state.version;
  const payload = clone(project);
  state.saveError = null;
  const pending = (async () => {
    try {
      const saved = await request(`/api/projects/${project.id}`, { method: 'PUT', body: JSON.stringify(payload) });
      if (state.project?.id === project.id) {
        state.project.revision = saved.revision;
        state.project.updatedAt = saved.updatedAt;
        state.savedVersion = version;
        const entry = state.projects.find((p) => p.id === project.id);
        if (entry) Object.assign(entry, { name: project.name, updatedAt: saved.updatedAt });
      }
      return true;
    } catch (error) {
      if (state.project?.id !== project.id) return false;
      state.saveError = error;
      if (error.status === 409) toast('项目已在另一个窗口更新。当前草稿仍在这里；点击“重试保存”可以另存为副本。', true);
      else toast(error.message, true);
      return false;
    } finally {
      state.saving = null;
      setSaveStatus();
    }
  })();
  state.saving = pending;
  setSaveStatus();
  const result = await pending;
  // Finish every edit made while this request was in flight before allowing a project switch.
  if (result && state.version !== state.savedVersion) return saveNow();
  return result;
}

const phone = new PhonePreview($('previewRoot'), {
  onViewChange(view) {
    if (!state.project || state.loading || state.importing || JSON.stringify(view) === JSON.stringify(state.project.view)) return;
    state.project.view = view;
    markChanged({ preview: false, delay: 1100 });
  },
  onSelectAsset(target) { selectTarget(target); },
  onError(message) { toast(typeof message === 'string' ? message : '视频暂时无法播放，请使用浏览器支持的 MP4。', true); },
});

function showNameDialog(title, initial = '') {
  return new Promise((resolve) => {
    const dialog = document.createElement('dialog');
    dialog.className = 'project-dialog';
    dialog.innerHTML = `<form method="dialog"><p class="dialog-eyebrow">LOCAL PROJECT</p><h2>${esc(title)}</h2><label class="field">产品 / 项目名称<input name="projectName" maxlength="100" required placeholder="例如：Urolithin A · 手机设计" value="${esc(initial)}"></label><div class="dialog-actions"><button class="button" value="cancel" formnovalidate>取消</button><button class="button primary" value="save">确定</button></div></form>`;
    document.body.append(dialog);
    dialog.addEventListener('close', () => { const value = dialog.returnValue === 'save' ? dialog.querySelector('input').value.trim() : null; dialog.remove(); resolve(value || null); }, { once: true });
    dialog.showModal();
    dialog.querySelector('input').focus();
    dialog.querySelector('input').select();
  });
}

function renderProjectList() {
  $('projectSelect').innerHTML = state.projects.length ? state.projects.map((p) => `<option value="${esc(p.id)}">${esc(p.name)}</option>`).join('') : '<option value="">选择或新建项目</option>';
  if (state.project) $('projectSelect').value = state.project.id;
  setSaveStatus();
}

async function openProject(id) {
  if (state.importing || state.loading) { renderProjectList(); return; }
  state.loading = true; setSaveStatus();
  try {
    if (state.project && !(await saveNow())) { renderProjectList(); return; }
    const project = await request(`/api/projects/${id}`);
    state.project = project;
    state.version = state.savedVersion = 0;
    state.saveError = null;
    state.selected = null;
    localStorage.setItem('amazon-preview.last-project', id);
    document.body.classList.remove('no-project');
    renderProjectList(); renderEditor(); applySettings();
    phone.update(project, { preservePosition: false });
  } catch (error) { toast(error.message, true); renderProjectList(); }
  finally { state.loading = false; setSaveStatus(); }
}

async function newProject() {
  if (state.importing || state.loading) return;
  const name = await showNameDialog('新建预览项目');
  if (!name) return;
  state.loading = true; setSaveStatus();
  try {
    if (!(await saveNow())) return;
    const project = await request('/api/projects', { method: 'POST', body: JSON.stringify({ name }) });
    state.projects.unshift({ id: project.id, name: project.name, updatedAt: project.updatedAt });
    state.loading = false;
    await openProject(project.id);
    toast('项目已创建。先放入主副图，或添加一个 A+ 模块。');
  } catch (error) { toast(error.message, true); }
  finally { state.loading = false; setSaveStatus(); }
}

async function retrySave() {
  if (state.importing || state.loading) return;
  if (state.saveError?.status !== 409) { await saveNow(); return; }
  const name = await showNameDialog('保留当前草稿，另存为副本', `${state.project.name} · 副本`);
  if (!name) return;
  const original = clone(state.project);
  state.importing = true; setSaveStatus();
  try {
    const project = await request('/api/projects', { method: 'POST', body: JSON.stringify({ name }) });
    const assetMap = new Map();
    for (const asset of Object.values(original.assets)) {
      const response = await fetch(`/api/projects/${original.id}/assets/${asset.id}`);
      if (!response.ok) throw new Error('素材复制失败，原草稿仍然保留。');
      const blob = await response.blob();
      const category = asset.category || (original.gallery.some((item) => item.assetId === asset.id) ? 'main' : 'aplus');
      const copied = await uploadAsset(project.id, blob, asset.name, asset, category);
      project.assets[copied.id] = copied; assetMap.set(asset.id, copied.id);
    }
    const remap = (value) => assetMap.get(value) || '';
    project.product = original.product; project.settings = original.settings; project.view = original.view;
    project.gallery = original.gallery.map((item) => ({ ...item, assetId: remap(item.assetId) }));
    project.modules = original.modules.map((mod) => ({ ...mod,
      ...(mod.type === 'image' ? { assetId: remap(mod.assetId) } : {}),
      ...(mod.type === 'carousel' ? { slides: mod.slides.map((s) => ({ ...s, assetId: remap(s.assetId) })) } : {}),
      ...(mod.type === 'video' ? { videoAssetId: remap(mod.videoAssetId), posterAssetId: remap(mod.posterAssetId) } : {}) }));
    const saved = await request(`/api/projects/${project.id}`, { method: 'PUT', body: JSON.stringify(project) });
    state.project = saved; state.saveError = null; state.version = state.savedVersion = 0;
    state.projects.unshift({ id: saved.id, name, updatedAt: saved.updatedAt });
    state.importing = false;
    await openProject(saved.id);
    toast('已将当前草稿和素材保存为独立副本。');
  } catch (error) { toast(error.message, true); }
  finally { state.importing = false; setSaveStatus(); }
}

function currentAsset(target) {
  if (!state.project || !target) return null;
  if (target.kind === 'gallery') return state.project.gallery.find((item) => item.id === target.itemId);
  const mod = state.project.modules.find((item) => item.id === target.moduleId);
  if (target.kind === 'slide') return mod?.slides?.find((item) => item.id === target.slideId);
  return mod;
}
function assetKey(target) { return target.kind === 'video' ? 'videoAssetId' : target.kind === 'poster' ? 'posterAssetId' : 'assetId'; }
function sameTarget(a, b) { return a && b && JSON.stringify(a) === JSON.stringify(b); }
function selectTarget(target, focus = true) {
  state.selected = target;
  document.querySelectorAll('[data-target]').forEach((el) => {
    const selected = sameTarget(JSON.parse(el.dataset.target), target);
    el.classList.toggle('selected', selected);
    el.setAttribute('aria-pressed', String(!!selected));
    if (selected && focus) el.focus({ preventScroll: true });
  });
}

function assetSlot(target, caption) {
  const item = currentAsset(target);
  const asset = state.project.assets[item?.[assetKey(target)]];
  const video = target.kind === 'video';
  let warning = '';
  if (asset && !video && ['image', 'slide'].includes(target.kind) && asset.width && asset.height && Math.abs(asset.width / asset.height - 4 / 3) > 0.025) warning = '比例与 4:3 预设不同，将完整显示';
  const media = asset ? (video ? '<span class="video-file-icon" aria-hidden="true">▶</span>' : `<img class="slot-thumb" src="${assetURL(asset.id)}" alt="" loading="lazy">`) : `<span class="slot-plus" aria-hidden="true">${video ? '▶' : '+'}</span>`;
  return `<div class="asset-cell"><button type="button" class="asset-slot ${asset ? '' : 'empty'} ${sameTarget(state.selected, target) ? 'selected' : ''}" data-target="${targetJSON(target)}" aria-pressed="${!!sameTarget(state.selected, target)}" title="点击选中后粘贴，双击选择文件；也可拖入文件">${media}<span class="slot-caption">${esc(asset?.name || caption)}</span><span class="slot-details">${asset ? esc(video ? `${asset.width || '—'}×${asset.height || '—'} · MP4` : `${asset.width}×${asset.height}`) : video ? '拖入 MP4 / 双击选择' : '选中后粘贴 / 拖入图片'}</span></button><div class="slot-actions"><button class="button compact" type="button" data-action="choose" data-target-ref="${targetJSON(target)}">${asset ? '替换' : '选择文件'}</button>${asset ? `<button class="icon-button" type="button" data-action="clear-asset" data-target-ref="${targetJSON(target)}" title="清空素材，保留位置" aria-label="清空素材">×</button>` : ''}</div>${warning ? `<p class="warning">${warning}</p>` : ''}</div>`;
}
function field(label, value, path, multiline = false, placeholder = '') {
  return `<label class="field">${label}${multiline ? `<textarea rows="2" data-field="${esc(path)}" placeholder="${esc(placeholder)}">${esc(value)}</textarea>` : `<input type="text" data-field="${esc(path)}" value="${esc(value)}" placeholder="${esc(placeholder)}">`}</label>`;
}
function sortButtons(kind, id, index, length, moduleId = '') {
  return `<span class="sort-buttons"><button class="icon-button drag-handle" draggable="true" data-sort-kind="${kind}" data-sort-id="${id}" data-module-id="${moduleId}" type="button" title="拖动排序" aria-label="拖动排序">⠿</button><button class="icon-button" data-action="move" data-kind="${kind}" data-id="${id}" data-module-id="${moduleId}" data-direction="-1" ${index === 0 ? 'disabled' : ''} type="button" title="向前移动" aria-label="向前移动">↑</button><button class="icon-button" data-action="move" data-kind="${kind}" data-id="${id}" data-module-id="${moduleId}" data-direction="1" ${index === length - 1 ? 'disabled' : ''} type="button" title="向后移动" aria-label="向后移动">↓</button><button class="icon-button danger" data-action="remove" data-kind="${kind}" data-id="${id}" data-module-id="${moduleId}" type="button" title="删除此项" aria-label="删除此项">×</button></span>`;
}

function renderEditor() {
  const p = state.project;
  const disabled = !p;
  for (const id of ['renameProject', 'addImageModule', 'addCarouselModule', 'addVideoModule', 'viewportSelect', 'zoomSelect', 'shellToggle', 'jumpGallery', 'jumpAplus']) $(id).disabled = disabled;
  if (!p) { $('productFields').innerHTML = ''; $('galleryEditor').innerHTML = ''; $('moduleList').innerHTML = ''; return; }
  $('productFields').innerHTML = field('品牌', p.product.brand, 'product.brand', false, '品牌名称（可留空）') + field('商品标题', p.product.title, 'product.title', true, '添加标题，感受主图在商品页里的效果') + field('价格', p.product.price, 'product.price', false, '例如 $39.99');
  $('galleryEditor').innerHTML = `<div class="asset-grid">${p.gallery.map((item, index) => `<div class="gallery-item" data-sort-drop="gallery" data-sort-id="${item.id}"><div class="slide-header"><span class="badge">${index === 0 ? '主图' : `副图 ${index}`}</span>${sortButtons('gallery', item.id, index, p.gallery.length)}</div>${assetSlot({ kind: 'gallery', itemId: item.id }, index === 0 ? '主图' : `副图 ${index}`)}</div>`).join('')}</div><button class="button full-width" data-action="add-gallery" type="button">＋ 添加主副图 · 可多选</button>${!p.gallery.length ? '<p class="hint">也可直接粘贴一张截图，开始预览。</p>' : ''}`;
  $('moduleList').innerHTML = p.modules.map((mod, index) => {
    const typeLabel = { image: '整张图片', carousel: '导航轮播', video: '全宽视频' }[mod.type];
    const english = { image: 'PREMIUM FULL IMAGE', carousel: 'PREMIUM NAVIGATION CAROUSEL', video: 'PREMIUM FULL VIDEO' }[mod.type];
    let content = '';
    if (mod.type === 'image') content = assetSlot({ kind: 'image', moduleId: mod.id }, '手机图片 · 4:3');
    if (mod.type === 'carousel') {
      content = `<p class="hint">每项单独导入手机图 · 4:3 · 官方基准 2–5 项，草稿不限</p>${mod.slides.map((slide, i) => `<div class="slide-editor" data-sort-drop="slide" data-sort-id="${slide.id}" data-module-id="${mod.id}"><div class="slide-header"><span class="badge">第 ${i + 1} 项</span>${sortButtons('slide', slide.id, i, mod.slides.length, mod.id)}</div>${field('导航标签', slide.label, `slide:${mod.id}:${slide.id}:label`, false, `标签 ${i + 1}`)}${assetSlot({ kind: 'slide', moduleId: mod.id, slideId: slide.id }, '轮播手机图 · 4:3')}<details class="optional-fields"><summary>图片外的标题与正文（可选）</summary>${field('标题', slide.title, `slide:${mod.id}:${slide.id}:title`)}${field('正文', slide.body, `slide:${mod.id}:${slide.id}:body`, true)}</details></div>`).join('')}<button class="button full-width" data-action="add-slide" data-module-id="${mod.id}" type="button">＋ 添加轮播项</button><button class="button full-width compact" data-action="batch-slides" data-module-id="${mod.id}" type="button">批量导入轮播图片</button>${mod.slides.length < 2 || mod.slides.length > 5 ? '<p class="warning">当前为草稿：该模块的官方基准为 2–5 项。</p>' : ''}`;
    }
    if (mod.type === 'video') content = `<div class="video-assets">${assetSlot({ kind: 'video', moduleId: mod.id }, '视频文件 · MP4')}${assetSlot({ kind: 'poster', moduleId: mod.id }, '独立封面 · 可选')}</div><p class="hint">视频按自身比例播放；封面与视频分别处理。</p>`;
    return `<section class="module-card" data-module-id="${mod.id}" data-sort-drop="module" data-sort-id="${mod.id}"><div class="module-head"><button type="button" class="module-title" data-action="reveal-module" data-module-id="${mod.id}" aria-label="定位 A+ 模块 ${index + 1}：${typeLabel}" title="点击定位右侧模块"><span class="module-number">${String(index + 1).padStart(2, '0')}</span><span><strong>${typeLabel}</strong><small>${english}</small></span></button>${sortButtons('module', mod.id, index, p.modules.length)}</div><div class="module-fields">${content}${mod.type !== 'carousel' ? `<details class="optional-fields"><summary>图片外的标题与正文（可选）</summary>${field('标题', mod.title, `module:${mod.id}:title`)}${field('正文', mod.body, `module:${mod.id}:body`, true)}</details>` : ''}</div></section>`;
  }).join('') || '<div class="section-empty"><strong>从一个模块开始</strong><p>选择下方模块，把你的 Canva 设计放进手机页面。</p></div>';
}

function addModule(type) {
  if (!state.project) { toast('请先新建一个产品项目。'); return; }
  const mod = { id: uid(), type, title: '', body: '' };
  if (type === 'image') mod.assetId = '';
  if (type === 'carousel') mod.slides = [{ id: uid(), assetId: '', label: '', title: '', body: '' }];
  if (type === 'video') Object.assign(mod, { videoAssetId: '', posterAssetId: '' });
  state.project.modules.push(mod);
  state.selected = type === 'image' ? { kind: 'image', moduleId: mod.id } : type === 'carousel' ? { kind: 'slide', moduleId: mod.id, slideId: mod.slides[0].id } : { kind: 'video', moduleId: mod.id };
  markChanged({ editor: true });
  $('moduleList').querySelector(`[data-module-id="${mod.id}"]`)?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  phone.jumpTo('aplus');
  selectTarget(state.selected);
}

function applySettings() {
  const s = state.project?.settings || { viewport: '390x844', zoom: 'fit', shell: true, editorCollapsed: false };
  $('viewportSelect').value = s.viewport;
  $('zoomSelect').value = s.zoom === 'fit' ? 'fit' : String(Math.round(Number(s.zoom) * 100));
  $('shellToggle').checked = s.shell;
  document.body.classList.toggle('is-collapsed', !!s.editorCollapsed);
  $('toggleEditor').setAttribute('aria-expanded', String(!s.editorCollapsed));
  $('toggleEditor').setAttribute('aria-label', s.editorCollapsed ? '展开编辑区' : '收起编辑区');
  $('toggleEditor').title = s.editorCollapsed ? '展开编辑区' : '收起编辑区';
  const label = $('toggleEditor').querySelector('[data-editor-label]');
  if (label) label.textContent = s.editorCollapsed ? '展开编辑' : '收起编辑';
  requestAnimationFrame(resizePhone);
}

function resizePhone() {
  const s = state.project?.settings || { viewport: '390x844', zoom: 'fit' };
  const [width, height] = s.viewport.split('x').map(Number);
  const stage = $('phoneStage');
  const style = getComputedStyle(stage);
  const availableWidth = stage.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight);
  const availableHeight = stage.clientHeight - parseFloat(style.paddingTop) - parseFloat(style.paddingBottom);
  const scale = s.zoom === 'fit' ? Math.max(0.2, Math.min(1, availableWidth / width, availableHeight / height)) : Number(s.zoom);
  Object.assign($('phoneViewport').style, { width: `${width}px`, height: `${height}px`, transform: `scale(${scale})`, transformOrigin: 'top left' });
  Object.assign($('phoneSizer').style, { width: `${width * scale}px`, height: `${height * scale}px` });
  const scaleLabel = $('scaleLabel');
  if (scaleLabel) scaleLabel.textContent = `${width} × ${height} · ${Math.round(scale * 100)}%`;
}

function openFiles(intent, video = false) {
  if (!state.project || state.importing || state.loading) return;
  state.fileIntent = intent;
  const input = video ? $('videoInput') : $('assetInput');
  input.value = ''; input.multiple = !video;
  input.click();
}

function mimeOf(file) {
  if (imageTypes.has(file.type) || file.type === 'video/mp4') return file.type;
  const ext = file.name?.split('.').pop().toLowerCase();
  return { png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', webp: 'image/webp', mp4: 'video/mp4' }[ext] || file.type;
}

async function readMedia(file, mime) {
  const url = URL.createObjectURL(file);
  try {
    if (mime !== 'video/mp4') {
      const img = new Image(); img.src = url;
      await img.decode();
      if (!img.naturalWidth || !img.naturalHeight) throw new Error();
      return { width: img.naturalWidth, height: img.naturalHeight };
    }
    return await new Promise((resolve, reject) => {
      const video = document.createElement('video');
      const finish = (fn, value) => { clearTimeout(timer); video.removeAttribute('src'); video.load(); fn(value); };
      const timer = setTimeout(() => finish(reject, new Error('无法读取视频。建议使用 H.264 编码的 MP4；此工具不自动转码。')), 12000);
      video.preload = 'metadata';
      video.onloadedmetadata = () => {
        video.onloadedmetadata = video.onerror = null;
        if (!video.videoWidth || !video.videoHeight || !Number.isFinite(video.duration)) { finish(reject, new Error('无法读取视频尺寸或时长。')); return; }
        finish(resolve, { width: video.videoWidth, height: video.videoHeight, duration: video.duration });
      };
      video.onerror = () => { video.onloadedmetadata = video.onerror = null; finish(reject, new Error('浏览器无法解码这个 MP4。请导出 H.264 视频后再试。')); };
      video.src = url;
    });
  } finally { URL.revokeObjectURL(url); }
}

async function uploadAsset(projectId, file, name, meta, category) {
  const params = new URLSearchParams({ name, width: meta.width || 0, height: meta.height || 0, category });
  if (meta.duration != null) params.set('duration', meta.duration);
  return request(`/api/projects/${projectId}/assets?${params}`, { method: 'POST', headers: { 'Content-Type': mimeOf(file) || meta.mime }, body: file });
}

function placeAsset(asset, intent, index) {
  const p = state.project;
  const makeSlide = () => ({ id: uid(), assetId: asset.id, label: '', title: '', body: '' });
  if (intent.mode === 'gallery') {
    const item = { id: uid(), assetId: asset.id }; p.gallery.push(item);
    return { kind: 'gallery', itemId: item.id };
  }
  if (intent.mode === 'slides') {
    const mod = p.modules.find((m) => m.id === intent.moduleId);
    if (!mod) throw new Error('轮播模块已删除，请重新导入。');
    const slide = makeSlide(); mod.slides.push(slide);
    return { kind: 'slide', moduleId: mod.id, slideId: slide.id };
  }
  const target = intent.target;
  if (index === 0 || ['video', 'poster'].includes(target.kind)) {
    const item = currentAsset(target);
    if (!item) throw new Error('选中的位置已删除，请重新选择。');
    item[assetKey(target)] = asset.id;
    return target;
  }
  if (target.kind === 'gallery') {
    const item = { id: uid(), assetId: asset.id };
    const at = p.gallery.findIndex((g) => g.id === target.itemId);
    p.gallery.splice(at + index, 0, item);
    return { kind: 'gallery', itemId: item.id };
  }
  if (target.kind === 'slide') {
    const mod = p.modules.find((m) => m.id === target.moduleId);
    if (!mod) throw new Error('轮播模块已删除，请重新导入。');
    const slide = makeSlide();
    const at = mod.slides.findIndex((s) => s.id === target.slideId);
    mod.slides.splice(at + index, 0, slide);
    return { kind: 'slide', moduleId: mod.id, slideId: slide.id };
  }
  const at = p.modules.findIndex((m) => m.id === target.moduleId);
  const mod = { id: uid(), type: 'image', title: '', body: '', assetId: asset.id };
  p.modules.splice(at + index, 0, mod);
  return { kind: 'image', moduleId: mod.id };
}

async function importFiles(files, intent) {
  if (state.loading) return;
  if (!state.project) { toast('先新建一个项目，再粘贴或拖入图片。'); return; }
  if (state.importing) { toast('正在导入上一批素材，请稍候。'); return; }
  const expectedVideo = intent?.target?.kind === 'video';
  const list = Array.from(files).filter((f) => expectedVideo ? mimeOf(f) === 'video/mp4' : imageTypes.has(mimeOf(f)));
  if (!list.length) { toast(expectedVideo ? '这个位置需要 MP4 视频。' : '这个位置支持 PNG、JPG 或 WebP 图片。', true); return; }
  if (expectedVideo || intent?.target?.kind === 'poster') list.splice(1);
  state.importing = true; setSaveStatus();
  let success = 0;
  const errors = [];
  let finalTarget = null;
  try {
    for (const file of list) {
      try {
        const mime = mimeOf(file);
        const meta = await readMedia(file, mime).catch((err) => { throw new Error(mime === 'video/mp4' ? err.message : `无法读取图片“${file.name || '截图'}”，原素材已保留。`); });
        const name = file.name || `截图-${new Date().toISOString().replace(/[:.]/g, '-')}.png`;
        const uploadFile = file.type === mime ? file : new File([file], name, { type: mime });
        const category = !intent || intent.mode === 'gallery' || intent.target?.kind === 'gallery' ? 'main' : 'aplus';
        const asset = await uploadAsset(state.project.id, uploadFile, name, meta, category);
        state.project.assets[asset.id] = asset;
        finalTarget = placeAsset(asset, intent || { mode: 'gallery' }, success);
        success++; markChanged({ editor: false });
      } catch (error) { errors.push(error.message); }
    }
  } finally {
    state.importing = false;
    if (finalTarget) state.selected = finalTarget;
    renderEditor(); setSaveStatus();
    if (success) {
      const saved = await saveNow();
      if (saved) toast(`已${intent?.mode === 'replace' ? '更新' : '导入'} ${success} 个素材${errors.length ? `；${errors.length} 个失败` : ''}。`);
      else toast(`已导入 ${success} 个素材，但项目尚未保存。请保留窗口并点击“重试保存”。`, true);
    }
    if (errors.length) toast(errors[0], true);
    if (state.selected) selectTarget(state.selected, false);
  }
}

function getList(kind, moduleId) {
  return kind === 'gallery' ? state.project.gallery : kind === 'module' ? state.project.modules : state.project.modules.find((m) => m.id === moduleId)?.slides;
}
function reorder(kind, id, destination, moduleId) {
  const list = getList(kind, moduleId);
  if (!list) return;
  const index = list.findIndex((item) => item.id === id);
  if (index < 0 || destination < 0 || destination >= list.length || index === destination) return;
  const [item] = list.splice(index, 1); list.splice(destination, 0, item);
  markChanged({ editor: true });
}

$('editorPanel').addEventListener('click', async (event) => {
  if (!state.project) return;
  const slot = event.target.closest('[data-target]');
  if (slot) {
    const target = JSON.parse(slot.dataset.target);
    selectTarget(target);
    phone.revealTarget(target);
    return;
  }
  const button = event.target.closest('[data-action]');
  if (!button) {
    if (event.target.closest('button, input, textarea, select, label, summary, a')) return;
    const slide = event.target.closest('.slide-editor');
    const card = event.target.closest('.module-card');
    const gallery = event.target.closest('.gallery-item');
    if (slide) phone.revealTarget({ kind: 'slide', moduleId: slide.dataset.moduleId, slideId: slide.dataset.sortId });
    else if (card) phone.revealTarget({ moduleId: card.dataset.moduleId });
    else if (gallery) phone.revealTarget({ kind: 'gallery', itemId: gallery.dataset.sortId });
    return;
  }
  const { action, moduleId, kind, id } = button.dataset;
  if (action === 'reveal-module') phone.revealTarget({ moduleId });
  if (action === 'choose') { const target = JSON.parse(button.dataset.targetRef); selectTarget(target, false); openFiles({ mode: 'replace', target }, target.kind === 'video'); }
  if (action === 'clear-asset') { const target = JSON.parse(button.dataset.targetRef); const item = currentAsset(target); if (item) item[assetKey(target)] = ''; markChanged({ editor: true }); }
  if (action === 'add-gallery') openFiles({ mode: 'gallery' });
  if (action === 'batch-slides') openFiles({ mode: 'slides', moduleId });
  if (action === 'add-slide') {
    const mod = state.project.modules.find((m) => m.id === moduleId);
    const slide = { id: uid(), assetId: '', label: '', title: '', body: '' };
    mod.slides.push(slide); state.selected = { kind: 'slide', moduleId, slideId: slide.id };
    markChanged({ editor: true }); selectTarget(state.selected);
  }
  if (action === 'move') { const list = getList(kind, moduleId); reorder(kind, id, list.findIndex((item) => item.id === id) + Number(button.dataset.direction), moduleId); }
  if (action === 'remove') {
    const list = getList(kind, moduleId); const at = list.findIndex((item) => item.id === id);
    if (at >= 0) list.splice(at, 1);
    if (state.selected && !currentAsset(state.selected)) state.selected = null;
    markChanged({ editor: true });
  }
});
$('editorPanel').addEventListener('dblclick', (event) => {
  const slot = event.target.closest('[data-target]');
  if (slot) { const target = JSON.parse(slot.dataset.target); openFiles({ mode: 'replace', target }, target.kind === 'video'); }
});
$('editorPanel').addEventListener('input', (event) => {
  const path = event.target.dataset.field;
  if (!path || !state.project) return;
  if (path.startsWith('product.')) state.project.product[path.split('.')[1]] = event.target.value;
  else {
    const [kind, moduleId, third, fourth] = path.split(':');
    const mod = state.project.modules.find((m) => m.id === moduleId);
    if (kind === 'module') mod[third] = event.target.value;
    else mod.slides.find((s) => s.id === third)[fourth] = event.target.value;
  }
  markChanged();
});

document.addEventListener('paste', (event) => {
  if (event.target.closest('input, textarea, [contenteditable="true"]')) return;
  const files = Array.from(event.clipboardData?.items || []).filter((item) => item.kind === 'file').map((item) => item.getAsFile()).filter(Boolean);
  if (!files.length) return;
  event.preventDefault();
  importFiles(files, state.selected ? { mode: 'replace', target: clone(state.selected) } : { mode: 'gallery' });
});
document.addEventListener('dragstart', (event) => {
  const handle = event.target.closest('[data-sort-kind]');
  if (!handle) return;
  event.dataTransfer.setData('application/x-preview-sort', JSON.stringify({ kind: handle.dataset.sortKind, id: handle.dataset.sortId, moduleId: handle.dataset.moduleId }));
  event.dataTransfer.effectAllowed = 'move';
});
document.addEventListener('dragover', (event) => {
  if (event.dataTransfer.types.includes('Files') || event.dataTransfer.types.includes('application/x-preview-sort')) {
    event.preventDefault(); event.dataTransfer.dropEffect = event.dataTransfer.types.includes('Files') ? 'copy' : 'move';
    event.target.closest('[data-target], [data-sort-drop]')?.classList.add('drag-over');
  }
});
document.addEventListener('dragleave', (event) => { event.target.closest?.('.drag-over')?.classList.remove('drag-over'); });
document.addEventListener('drop', (event) => {
  document.querySelectorAll('.drag-over').forEach((el) => el.classList.remove('drag-over'));
  if (event.dataTransfer.files.length) {
    event.preventDefault();
    const slot = event.target.closest('[data-target]');
    const target = slot ? JSON.parse(slot.dataset.target) : state.selected;
    importFiles(event.dataTransfer.files, target ? { mode: 'replace', target: clone(target) } : { mode: 'gallery' });
    return;
  }
  const raw = event.dataTransfer.getData('application/x-preview-sort');
  if (!raw || !state.project) return;
  event.preventDefault();
  try {
    const source = JSON.parse(raw);
    const dest = event.target.closest(`[data-sort-drop="${source.kind}"]`);
    if (!dest || (source.kind === 'slide' && dest.dataset.moduleId !== source.moduleId)) return;
    const list = getList(source.kind, source.moduleId);
    reorder(source.kind, source.id, list.findIndex((item) => item.id === dest.dataset.sortId), source.moduleId);
  } catch { /* Ignore unrelated drag payloads. */ }
});
for (const id of ['assetInput', 'videoInput']) $(id).addEventListener('change', (event) => { importFiles(event.target.files, state.fileIntent); });
$('newProject').addEventListener('click', newProject);
$('emptyState').addEventListener('click', (event) => { if (event.target.closest('button, [data-action="new-project"]')) newProject(); });
$('projectSelect').addEventListener('change', (event) => { openProject(event.target.value); });
$('renameProject').addEventListener('click', async () => {
  if (!state.project) return;
  const name = await showNameDialog('重命名项目', state.project.name);
  if (!name) return;
  state.project.name = name;
  const entry = state.projects.find((p) => p.id === state.project.id); if (entry) entry.name = name;
  renderProjectList(); markChanged({ preview: false });
});
$('retrySave').addEventListener('click', retrySave);
$('addImageModule').addEventListener('click', () => addModule('image'));
$('addCarouselModule').addEventListener('click', () => addModule('carousel'));
$('addVideoModule').addEventListener('click', () => addModule('video'));
$('toggleEditor').addEventListener('click', () => {
  if (state.project) { state.project.settings.editorCollapsed = !state.project.settings.editorCollapsed; applySettings(); markChanged({ preview: false }); }
});
$('viewportSelect').addEventListener('change', (event) => { state.project.settings.viewport = event.target.value; applySettings(); markChanged(); });
$('zoomSelect').addEventListener('change', (event) => { state.project.settings.zoom = event.target.value === 'fit' ? 'fit' : Number(event.target.value) / 100; applySettings(); markChanged({ preview: false }); });
$('shellToggle').addEventListener('change', (event) => { state.project.settings.shell = event.target.checked; markChanged(); });
$('jumpGallery').addEventListener('click', () => phone.jumpTo('gallery'));
$('jumpAplus').addEventListener('click', () => phone.jumpTo('aplus'));
document.addEventListener('keydown', (event) => { if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 's') { event.preventDefault(); if (!state.loading && !state.importing) saveNow(); } });
window.addEventListener('beforeunload', (event) => { if (state.importing || state.version !== state.savedVersion) { event.preventDefault(); event.returnValue = ''; } });
window.addEventListener('resize', resizePhone);
new ResizeObserver(resizePhone).observe($('phoneStage'));

async function init() {
  $('toast').hidden = true; $('retrySave').hidden = true;
  renderEditor(); applySettings();
  try {
    const data = await request('/api/projects'); state.projects = data.projects; renderProjectList();
    const last = localStorage.getItem('amazon-preview.last-project');
    const id = state.projects.find((p) => p.id === last)?.id || state.projects[0]?.id;
    if (id) await openProject(id);
  } catch (error) { toast(error.message, true); $('saveStatus').textContent = '本地服务未连接'; }
}
init();
