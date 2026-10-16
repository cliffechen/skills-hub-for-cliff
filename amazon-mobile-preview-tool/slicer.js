// Long-image slicer: cut a Canva long export (e.g. 1800×6750) into 4:3 tiles
// (default 1800×1350) for Amazon A+, then import them or save them locally.
// Everything runs in the browser; nothing leaves this computer until imported.

const esc = (value = '') => String(value).replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const imageTypes = new Set(['image/png', 'image/jpeg', 'image/webp']);

export function openSlicer({ onImport, canImport = true }) {
  const dialog = document.createElement('dialog');
  dialog.className = 'project-dialog slicer-dialog';
  dialog.innerHTML = `
    <div class="slicer-head"><div><p class="dialog-eyebrow">A+ LONG IMAGE SLICER</p><h2>切长图</h2></div><button class="icon-button" type="button" data-slicer="close" aria-label="关闭" title="关闭">×</button></div>
    <p class="hint">把 Canva 导出的长图按宽度等比缩放后，自动切成多张 A+ 图片。全部在本机浏览器处理。</p>
    <button class="slicer-drop" type="button" data-slicer="pick"><span>拖入长图、<b>点击选择</b>，或直接 Ctrl+V 粘贴</span><small>PNG / JPG / WebP</small></button>
    <input type="file" accept="image/png,image/jpeg,image/webp" hidden data-slicer="file">
    <div class="slicer-options">
      <label class="field">每张宽<input type="number" min="100" max="6000" value="1800" data-slicer="w"></label>
      <label class="field">每张高<input type="number" min="100" max="6000" value="1350" data-slicer="h"></label>
      <label class="field">格式<select data-slicer="fmt"><option value="image/jpeg">JPG</option><option value="image/png">PNG</option></select></label>
      <label class="field" data-slicer="q-wrap">JPG 质量<input type="number" min="50" max="100" value="92" data-slicer="q"></label>
    </div>
    <p class="slicer-info" data-slicer="info">还没有选择图片。</p>
    <div class="slicer-grid" data-slicer="grid"></div>
    <div class="slicer-actions">
      <div class="slicer-save"><button class="button compact" type="button" data-slicer="save-dir" disabled>保存到文件夹…</button><button class="button compact" type="button" data-slicer="download" disabled>逐张下载</button></div>
      <div class="slicer-import">${canImport ? '' : '<span class="slicer-note">先新建或打开项目，才能导入</span>'}<select data-slicer="as" aria-label="导入方式" ${canImport ? '' : 'disabled'}><option value="image">导入为：多个整张图片模块</option><option value="carousel">导入为：一个高级轮播模块</option></select><button class="button primary" type="button" data-slicer="import" disabled>导入当前项目</button></div>
    </div>`;
  document.body.append(dialog);
  const el = (name) => dialog.querySelector(`[data-slicer="${name}"]`);
  let img = null, imgURL = '', baseName = 'aplus', slices = [], run = 0;

  const resetSlices = () => { slices.forEach((s) => URL.revokeObjectURL(s.url)); slices = []; };
  const setReady = (ready) => {
    el('download').disabled = !ready;
    el('save-dir').disabled = !ready || !window.showDirectoryPicker;
    el('save-dir').title = window.showDirectoryPicker ? '' : '当前浏览器不支持，请用 Chrome / Edge';
    el('import').disabled = !ready || !canImport;
    el('import').textContent = ready && canImport ? `导入 ${slices.length} 张` : '导入当前项目';
  };

  async function load(file) {
    if (!file || !(imageTypes.has(file.type) || /\.(png|jpe?g|webp)$/i.test(file.name || ''))) { el('info').innerHTML = '<span class="warning">请使用 PNG、JPG 或 WebP 图片。</span>'; return; }
    baseName = (file.name || 'aplus').replace(/\.[^.]+$/, '') || 'aplus';
    const next = new Image();
    const url = URL.createObjectURL(file);
    try { next.src = url; await next.decode(); }
    catch { URL.revokeObjectURL(url); el('info').innerHTML = '<span class="warning">读不了这张图，请换 PNG 或 JPG。</span>'; return; }
    if (imgURL) URL.revokeObjectURL(imgURL);
    img = next; imgURL = url;
    slice();
  }

  async function slice() {
    if (!img) return;
    const current = ++run;
    const W = Math.round(+el('w').value), H = Math.round(+el('h').value);
    if (!(W >= 100 && H >= 100 && W <= 6000 && H <= 6000)) { el('info').innerHTML = '<span class="warning">宽和高需在 100–6000 之间。</span>'; return; }
    const fmt = el('fmt').value, q = Math.min(100, Math.max(50, +el('q').value || 92)) / 100;
    const ext = fmt === 'image/png' ? 'png' : 'jpg';
    // Scale the source to the tile width first, then cut by tile height.
    const scale = W / img.naturalWidth;
    const fullH = Math.round(img.naturalHeight * scale);
    const n = Math.max(1, Math.ceil(fullH / H));
    const rest = fullH % H;
    let msg = `原图 ${img.naturalWidth}×${img.naturalHeight}`;
    if (scale !== 1) msg += `，已等比缩放到宽 ${W}`;
    msg += ` → 切成 <b>${n}</b> 张 ${W}×${H}`;
    if (rest) msg += `<br><span class="warning">高度不是 ${H} 的整数倍，最后一张只有 ${rest}px 内容，下方补白。建议在 Canva 把画布高度改成 ${H} 的倍数（如 ${H * n}）。</span>`;
    el('info').innerHTML = msg;
    resetSlices(); el('grid').innerHTML = ''; setReady(false);
    const made = [];
    for (let k = 0; k < n; k++) {
      const canvas = document.createElement('canvas');
      canvas.width = W; canvas.height = H;
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H);
      ctx.imageSmoothingQuality = 'high';
      ctx.drawImage(img, 0, -k * H, W, img.naturalHeight * scale);
      const blob = await new Promise((resolve) => canvas.toBlob(resolve, fmt, q));
      if (current !== run) { made.forEach((s) => URL.revokeObjectURL(s.url)); return; }
      const name = `${baseName}_${String(k + 1).padStart(2, '0')}.${ext}`;
      const item = { name, blob, url: URL.createObjectURL(blob) };
      made.push(item);
      el('grid').insertAdjacentHTML('beforeend', `<figure class="slicer-tile"><img src="${item.url}" alt="第 ${k + 1} 张"><figcaption><span>${k + 1}/${n} · ${(blob.size / 1024).toFixed(0)} KB</span><a href="${item.url}" download="${esc(name)}">下载</a></figcaption></figure>`);
    }
    slices = made;
    setReady(true);
  }

  const onPaste = (event) => {
    if (event.target.closest?.('input, textarea')) return;
    const file = Array.from(event.clipboardData?.items || []).find((item) => item.kind === 'file')?.getAsFile();
    event.stopPropagation();
    if (file) { event.preventDefault(); load(file); }
  };
  const onDragOver = (event) => {
    if (!event.dataTransfer.types.includes('Files')) return;
    event.preventDefault(); event.stopPropagation();
    event.dataTransfer.dropEffect = 'copy';
    el('pick').classList.add('drag-over');
  };
  const onDrop = (event) => {
    el('pick').classList.remove('drag-over');
    if (!event.dataTransfer.files.length) return;
    event.preventDefault(); event.stopPropagation();
    load(event.dataTransfer.files[0]);
  };
  // Capture on document so the main editor's paste / drop handlers stay out of it.
  document.addEventListener('paste', onPaste, true);
  document.addEventListener('dragover', onDragOver, true);
  document.addEventListener('drop', onDrop, true);
  dialog.addEventListener('dragleave', (event) => { if (!dialog.contains(event.relatedTarget)) el('pick').classList.remove('drag-over'); });

  el('pick').addEventListener('click', () => { el('file').value = ''; el('file').click(); });
  el('file').addEventListener('change', (event) => load(event.target.files[0]));
  for (const name of ['w', 'h', 'fmt', 'q']) el(name).addEventListener('change', slice);
  el('fmt').addEventListener('change', () => { el('q-wrap').hidden = el('fmt').value !== 'image/jpeg'; });
  el('close').addEventListener('click', () => dialog.close());
  el('download').addEventListener('click', async () => {
    for (const s of slices) {
      const a = document.createElement('a'); a.href = s.url; a.download = s.name; a.click();
      await new Promise((resolve) => setTimeout(resolve, 300));
    }
  });
  el('save-dir').addEventListener('click', async () => {
    try {
      const dir = await window.showDirectoryPicker({ mode: 'readwrite' });
      for (const s of slices) {
        const handle = await dir.getFileHandle(s.name, { create: true });
        const writable = await handle.createWritable();
        await writable.write(s.blob); await writable.close();
      }
      el('info').insertAdjacentHTML('beforeend', `<br>已保存 ${slices.length} 张到「${esc(dir.name)}」。`);
    } catch (error) { if (error.name !== 'AbortError') el('info').insertAdjacentHTML('beforeend', `<br><span class="warning">保存失败：${esc(error.message)}</span>`); }
  });
  el('import').addEventListener('click', () => {
    if (!slices.length) return;
    const files = slices.map((s) => new File([s.blob], s.name, { type: s.blob.type }));
    const as = el('as').value;
    dialog.close();
    onImport(files, as);
  });
  dialog.addEventListener('close', () => {
    run++;
    document.removeEventListener('paste', onPaste, true);
    document.removeEventListener('dragover', onDragOver, true);
    document.removeEventListener('drop', onDrop, true);
    resetSlices(); if (imgURL) URL.revokeObjectURL(imgURL);
    dialog.remove();
  }, { once: true });
  dialog.showModal();
  el('pick').focus();
}
