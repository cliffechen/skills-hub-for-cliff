/* ============================================================
   产品文案工作台 · 前端逻辑
   原生 ES2020，无框架、无构建、无 CDN
   ============================================================ */
(function () {
  'use strict';

  var LS_SPLIT = 'copywb.split';
  var LS_STYLE = 'copywb.style';
  var LS_THEME = 'copywb.theme';
  var HANDLES = ['nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w'];

  var $ = function (id) { return document.getElementById(id); };

  var els = {
    metaProduct: $('metaProduct'),
    metaSpec: $('metaSpec'),
    styleSeg: $('styleSeg'),
    viewSeg: $('viewSeg'),
    btnCalib: $('btnCalib'),
    btnCheck: $('btnCheck'),
    btnSave: $('btnSave'),
    btnTheme: $('btnTheme'),
    ddExport: $('ddExport'),
    btnExport: $('btnExport'),
    exportMenu: $('exportMenu'),
    status: $('status'),
    statusText: $('statusText'),
    left: $('left'),
    right: $('right'),
    flagbar: $('flagbar'),
    canvasWrap: $('canvasWrap'),
    canvas: $('canvas'),
    shot: $('shot'),
    overlay: $('overlay'),
    modmeta: $('modmeta'),
    splitter: $('splitter'),
    cards: $('cards'),
    compare: $('compare'),
    moduleNav: $('moduleNav'),
    modal: $('modal'),
    modalTitle: $('modalTitle'),
    modalBody: $('modalBody'),
    modalClose: $('modalClose'),
    toast: $('toast')
  };

  var state = {
    data: null,
    style: 'A',
    view: 'work',
    modIdx: 0,
    selSlot: null,
    calib: false,
    dirty: false,
    done: {},
    origRects: {},
    openEditor: null,
    nat: null,
    imgName: null,
    toastTimer: null
  };

  /* ---------------------------------------------------------- 工具 */

  function esc(text) {
    return String(text == null ? '' : text)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function p05(n) { return Math.round(n * 2) / 2; }

  function hashStr(s) {
    var h = 5381;
    for (var i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0;
    return (h >>> 0).toString(36);
  }

  /* 「完成」勾选按产品隔离：换产品后互不影响 */
  function doneKey() {
    var p = (state.data && state.data.meta && state.data.meta.product) || '';
    return 'copywb.done.' + (p ? hashStr(p) : 'default');
  }

  function clone(value) { return JSON.parse(JSON.stringify(value)); }

  function pad2(n) { return (n < 10 ? '0' : '') + n; }

  function hhmmss(iso) {
    if (!iso) return '';
    var d = new Date(iso);
    if (isNaN(d.getTime())) return '';
    return pad2(d.getHours()) + ':' + pad2(d.getMinutes()) + ':' + pad2(d.getSeconds());
  }

  /** 判定 → 样式类后缀 */
  function judgeClass(judge) {
    var j = judge || '';
    if (j.indexOf('疑似') >= 0) return 'suspect';
    if (j.indexOf('推定') >= 0) return 'presume';
    if (j.indexOf('保留') >= 0) return 'preserve';
    return 'slot';
  }

  /**
   * 富文本渲染：`**x**` 加粗不显示星号；单独 `*` 标为脚注；
   * `｜` 与 `  ·  ` 为设计分隔符，保留原样但弱化显示。换行交给 pre-wrap。
   */
  function renderRich(raw) {
    var text = esc(raw);
    var re = /\*\*([\s\S]+?)\*\*|\*|｜/g;
    var out = '';
    var last = 0;
    var m;
    while ((m = re.exec(text)) !== null) {
      out += text.slice(last, m.index);
      if (m[1] !== undefined) {
        out += '<b>' + m[1] + '</b>';
      } else if (m[0] === '｜') {
        out += '<span class="sep">｜</span>';
      } else {
        out += '<span class="fn">*</span>';
      }
      last = m.index + m[0].length;
    }
    out += text.slice(last);
    return out;
  }

  /** 去掉 `**加粗**` 标记后是否仍有脚注星号 */
  function hasFootnoteMark(raw) {
    return String(raw || '').replace(/\*\*[\s\S]+?\*\*/g, '').indexOf('*') >= 0;
  }

  /* ---------------------------------------------------------- 数据访问 */

  function curModule() { return state.data.modules[state.modIdx]; }

  function slotById(id) {
    var mods = state.data.modules;
    for (var i = 0; i < mods.length; i++) {
      var slots = mods[i].slots || [];
      for (var k = 0; k < slots.length; k++) {
        if (slots[k].id === id) return { module: mods[i], slot: slots[k], mi: i };
      }
    }
    return null;
  }

  function fieldValue(slot, field) {
    if (field === 'text') return slot.text || '';
    if (field === 'rec' || field === 'alt') {
      var v = (slot.values || {})[state.style] || {};
      return v[field] || '';
    }
    if (field.indexOf('row:') === 0) {
      var rows = (slot.rows || {})[state.style] || [];
      return rows[Number(field.slice(4))] || '';
    }
    var card = (slot.cards || {})[state.style] || {};
    return card[field] || '';
  }

  function setField(slot, field, value) {
    if (field === 'rec' || field === 'alt') {
      if (!slot.values) slot.values = {};
      if (!slot.values[state.style]) slot.values[state.style] = {};
      slot.values[state.style][field] = value;
      return;
    }
    if (field.indexOf('row:') === 0) {
      if (!slot.rows) slot.rows = {};
      if (!slot.rows[state.style]) slot.rows[state.style] = [];
      slot.rows[state.style][Number(field.slice(4))] = value;
      return;
    }
    if (!slot.cards) slot.cards = {};
    if (!slot.cards[state.style]) slot.cards[state.style] = {};
    slot.cards[state.style][field] = value;
  }

  /* ---------------------------------------------------------- 状态条 / Toast */

  function setStatus(kind, detail) {
    els.status.className = 'status' + (kind ? ' ' + kind : '');
    if (kind === 'dirty') {
      els.statusText.textContent = '有未保存修改';
    } else if (kind === 'saved') {
      els.statusText.textContent = '已保存 ' + (detail || hhmmss(new Date().toISOString()));
    } else if (kind === 'failed') {
      els.statusText.textContent = '保存失败：' + (detail || '未知原因');
    } else {
      els.statusText.textContent = detail || '就绪';
    }
  }

  function toast(message, isError, actionLabel, actionFn) {
    els.toast.innerHTML = '';
    els.toast.className = 'toast' + (isError ? ' err' : '');
    var span = document.createElement('span');
    span.textContent = message;
    els.toast.appendChild(span);
    if (actionLabel && actionFn) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.textContent = actionLabel;
      btn.addEventListener('click', function () { hideToast(); actionFn(); });
      els.toast.appendChild(btn);
    }
    els.toast.classList.add('show');
    if (state.toastTimer) clearTimeout(state.toastTimer);
    state.toastTimer = setTimeout(hideToast, actionLabel ? 12000 : 3200);
  }

  function hideToast() {
    els.toast.classList.remove('show');
    if (state.toastTimer) { clearTimeout(state.toastTimer); state.toastTimer = null; }
  }

  function markDirty() {
    if (!state.dirty) {
      state.dirty = true;
      setStatus('dirty');
    }
  }

  function markCardDirty(slotId) {
    var card = els.cards.querySelector('.card[data-slot="' + slotId + '"]');
    if (card) card.classList.add('dirty');
  }

  function clearCardDirty() {
    var list = els.cards.querySelectorAll('.card.dirty');
    Array.prototype.forEach.call(list, function (c) { c.classList.remove('dirty'); });
  }

  /* ---------------------------------------------------------- 画布 */

  function fitCanvas() {
    if (!state.nat || !state.nat.w || !state.nat.h) return;
    var wrap = els.canvasWrap.getBoundingClientRect();
    var availW = Math.max(60, wrap.width);
    var availH = Math.max(60, wrap.height);
    var ar = state.nat.w / state.nat.h;
    var w = availW;
    var h = w / ar;
    if (h > availH) { h = availH; w = h * ar; }
    els.canvas.style.width = Math.floor(w) + 'px';
    els.canvas.style.height = Math.floor(h) + 'px';
    els.canvas.style.aspectRatio = String(ar);
  }

  function loadImage(name) {
    if (state.imgName === name && state.nat) { fitCanvas(); return; }
    state.imgName = name;
    state.nat = null;
    els.shot.onload = function () {
      state.nat = { w: els.shot.naturalWidth, h: els.shot.naturalHeight };
      fitCanvas();
    };
    els.shot.onerror = function () {
      els.modmeta.innerHTML = '<span style="color:#a3271b">图片加载失败：' + esc(name) + '</span>';
    };
    els.shot.src = '/' + encodeURIComponent(name);
  }

  function renderOverlay() {
    var mod = curModule();
    els.overlay.innerHTML = '';
    (mod.slots || []).forEach(function (slot) {
      var rects = slot.rects || [];
      rects.forEach(function (r, ri) {
        var d = document.createElement('div');
        d.className = 'hotspot j-' + judgeClass(slot.judge);
        if (state.done[slot.id]) d.classList.add('is-done');
        if (slot.id === state.selSlot) d.classList.add('sel');
        if (state.calib && slot.id === state.selSlot) d.classList.add('calib');
        d.dataset.slot = slot.id;
        d.dataset.rect = String(ri);
        applyRect(d, r);
        var tag = document.createElement('span');
        tag.className = 'sid';
        tag.textContent = slot.id;
        d.appendChild(tag);
        if (state.calib && slot.id === state.selSlot) {
          HANDLES.forEach(function (h) {
            var hd = document.createElement('div');
            hd.className = 'handle';
            hd.dataset.h = h;
            d.appendChild(hd);
          });
        }
        els.overlay.appendChild(d);
      });
    });
  }

  function applyRect(node, r) {
    node.style.left = r[0] + '%';
    node.style.top = r[1] + '%';
    node.style.width = r[2] + '%';
    node.style.height = r[3] + '%';
  }

  function repaintSelRects() {
    if (!state.selSlot) return;
    var found = slotById(state.selSlot);
    if (!found) return;
    var rects = found.slot.rects || [];
    var nodes = els.overlay.querySelectorAll('.hotspot[data-slot="' + state.selSlot + '"]');
    Array.prototype.forEach.call(nodes, function (node) {
      var ri = Number(node.dataset.rect);
      if (rects[ri]) applyRect(node, rects[ri]);
    });
  }

  function highlightHotspot(slotId) {
    els.overlay.classList.add('dimmed');
    var nodes = els.overlay.querySelectorAll('.hotspot');
    Array.prototype.forEach.call(nodes, function (node) {
      node.classList.toggle('hl', node.dataset.slot === slotId);
    });
  }

  function clearHotspotHighlight() {
    els.overlay.classList.remove('dimmed');
    var nodes = els.overlay.querySelectorAll('.hotspot.hl');
    Array.prototype.forEach.call(nodes, function (node) { node.classList.remove('hl'); });
  }

  /* ---------------------------------------------------------- 模块提示 / 元信息 / 导航 */

  function renderFlags() {
    var mod = curModule();
    els.flagbar.innerHTML = '';
    (mod.flags || []).forEach(function (f) {
      var d = document.createElement('div');
      d.className = 'flag ' + (f.level || 'info');
      var b = document.createElement('b');
      b.textContent = { warn: '提示', error: '必须处理', info: '说明' }[f.level] || f.level;
      var s = document.createElement('span');
      s.textContent = f.text || '';
      d.appendChild(b);
      d.appendChild(s);
      els.flagbar.appendChild(d);
    });
  }

  function renderModMeta() {
    var mod = curModule();
    els.modmeta.innerHTML =
      '<span>模块 <b class="t">' + esc(mod.id) + '</b>　' + esc(mod.name) + '</span>' +
      '<span>本图任务：<span class="t">' + esc(mod.task || '') + '</span></span>' +
      '<span>槽位 ' + (mod.slots || []).length + ' 个</span>' +
      '<span>图片：<span class="t">' + esc(mod.img) + '</span></span>';
  }

  function renderNav() {
    els.moduleNav.innerHTML = '';
    state.data.modules.forEach(function (mod, i) {
      var b = document.createElement('button');
      b.type = 'button';
      b.textContent = mod.id + ' ' + mod.name;
      b.title = mod.img;
      if (i === state.modIdx) b.classList.add('on');
      b.addEventListener('click', function () { gotoModule(i); });
      els.moduleNav.appendChild(b);
    });
  }

  /* ---------------------------------------------------------- 槽位卡 */

  function makeField(slot, field, labelText, readonly) {
    var wrap = document.createElement('div');
    wrap.className = 'field';

    var lab = document.createElement('div');
    lab.className = 'field-label';
    var name = document.createElement('span');
    name.textContent = labelText;
    lab.appendChild(name);
    var tag = document.createElement('span');
    tag.className = 'style-tag';
    tag.dataset.styleTag = field;
    lab.appendChild(tag);
    var grow = document.createElement('span');
    grow.className = 'grow';
    lab.appendChild(grow);
    if (!readonly) {
      var cp = document.createElement('button');
      cp.type = 'button';
      cp.className = 'mini';
      cp.textContent = '复制';
      cp.dataset.act = 'copy';
      cp.dataset.slot = slot.id;
      cp.dataset.field = field;
      lab.appendChild(cp);
    }
    wrap.appendChild(lab);

    var text = document.createElement('div');
    text.className = 'text' + (readonly ? ' ro' : '');
    text.dataset.slot = slot.id;
    text.dataset.field = field;
    wrap.appendChild(text);
    return wrap;
  }

  function kv(key, value, needs) {
    var d = document.createElement('div');
    d.className = 'kv' + (needs ? ' needs' : '');
    var k = document.createElement('span');
    k.className = 'k';
    k.textContent = key;
    var v = document.createElement('span');
    v.textContent = value;
    d.appendChild(k);
    d.appendChild(v);
    return d;
  }

  function buildCoords(slot) {
    var box = document.createElement('div');
    box.className = 'coords';
    box.dataset.coords = slot.id;
    var rects = slot.rects || [];

    rects.forEach(function (r, ri) {
      var row = document.createElement('div');
      row.className = 'coordrow';
      var idx = document.createElement('span');
      idx.className = 'idx';
      idx.textContent = rects.length > 1 ? ('#' + (ri + 1)) : 'x y w h';
      row.appendChild(idx);
      ['x', 'y', 'w', 'h'].forEach(function (axis, ai) {
        var inp = document.createElement('input');
        inp.type = 'number';
        inp.step = '0.5';
        inp.value = r[ai];
        inp.dataset.act = 'coord';
        inp.dataset.slot = slot.id;
        inp.dataset.rect = String(ri);
        inp.dataset.axis = String(ai);
        inp.title = axis + '（%）';
        row.appendChild(inp);
      });
      box.appendChild(row);
    });

    var actions = document.createElement('div');
    actions.className = 'alt-actions';
    var reset = document.createElement('button');
    reset.type = 'button';
    reset.className = 'mini';
    reset.textContent = '重置本槽坐标';
    reset.dataset.act = 'resetrect';
    reset.dataset.slot = slot.id;
    actions.appendChild(reset);
    var tip = document.createElement('span');
    tip.className = 'kv';
    tip.style.margin = '0';
    tip.innerHTML = '<span class="k">精度</span>0.5%';
    actions.appendChild(tip);
    box.appendChild(actions);
    return box;
  }

  function buildCard(slot) {
    var cls = judgeClass(slot.judge);
    var art = document.createElement('article');
    art.className = 'card k-' + slot.kind + ' j-' + cls;
    art.dataset.slot = slot.id;
    if (state.done[slot.id]) art.classList.add('done');

    /* 卡头 */
    var head = document.createElement('div');
    head.className = 'card-head';
    head.innerHTML =
      '<code class="sid">' + esc(slot.id) + '</code>' +
      '<span class="slabel">' + esc(slot.label || '') + '</span>' +
      '<span class="badge badge-' + cls + '">' + esc(slot.judge || '') + '</span>' +
      '<span class="grow"></span>';
    var locate = document.createElement('button');
    locate.type = 'button';
    locate.className = 'mini';
    locate.textContent = '定位';
    locate.dataset.act = 'locate';
    locate.dataset.slot = slot.id;
    head.appendChild(locate);
    var doneLabel = document.createElement('label');
    doneLabel.className = 'done';
    var cb = document.createElement('input');
    cb.type = 'checkbox';
    cb.checked = !!state.done[slot.id];
    cb.dataset.act = 'done';
    cb.dataset.slot = slot.id;
    doneLabel.appendChild(cb);
    doneLabel.appendChild(document.createTextNode(' 完成'));
    head.appendChild(doneLabel);
    art.appendChild(head);

    /* 正文 */
    if (slot.kind === 'text') {
      art.appendChild(makeField(slot, 'rec', '产出英文', false));
      var alt = document.createElement('details');
      alt.className = 'sub';
      var sum = document.createElement('summary');
      sum.textContent = '备选（点击展开）';
      alt.appendChild(sum);
      var altBody = document.createElement('div');
      altBody.className = 'body';
      var fld = makeField(slot, 'alt', '备选', false);
      var promote = document.createElement('button');
      promote.type = 'button';
      promote.className = 'mini';
      promote.textContent = '用此版';
      promote.dataset.act = 'promote';
      promote.dataset.slot = slot.id;
      fld.querySelector('.field-label').appendChild(promote);
      altBody.appendChild(fld);
      alt.appendChild(altBody);
      art.appendChild(alt);
    } else if (slot.kind === 'card') {
      art.appendChild(makeField(slot, 'name', '名称', false));
      art.appendChild(makeField(slot, 'dose', '剂量', false));
      art.appendChild(makeField(slot, 'line1', '说明 1', false));
      art.appendChild(makeField(slot, 'line2', '说明 2', false));
    } else if (slot.kind === 'table') {
      var rows = (slot.rows || {})[state.style] || [];
      rows.forEach(function (row, ri) {
        art.appendChild(makeField(slot, 'row:' + ri, '第 ' + (ri + 1) + ' 行', false));
      });
    } else if (slot.kind === 'preserve') {
      art.appendChild(makeField(slot, 'text', '保留原文（只读）', true));
    }

    /* 折叠详情 */
    var det = document.createElement('details');
    det.className = 'sub';
    var detSum = document.createElement('summary');
    detSum.textContent = '详情（指令原文 / 中文说明 / 必须上图 / 当前坐标）';
    det.appendChild(detSum);
    var detBody = document.createElement('div');
    detBody.className = 'body';
    if (slot.insp) detBody.appendChild(kv('指令原文', slot.insp, false));
    if (slot.note) detBody.appendChild(kv('中文说明', slot.note, false));
    if (slot.needs) detBody.appendChild(kv('必须上图', slot.needs, true));
    detBody.appendChild(buildCoords(slot));
    det.appendChild(detBody);
    art.appendChild(det);

    return art;
  }

  function renderCards() {
    var mod = curModule();
    els.cards.innerHTML = '';
    (mod.slots || []).forEach(function (slot) {
      els.cards.appendChild(buildCard(slot));
    });
    paintCards();
  }

  function paintCards() {
    var nodes = els.cards.querySelectorAll('.text[data-slot]');
    Array.prototype.forEach.call(nodes, function (node) {
      if (state.openEditor && state.openEditor.node === node) return;
      var found = slotById(node.dataset.slot);
      if (!found) return;
      node.innerHTML = renderRich(fieldValue(found.slot, node.dataset.field));
    });
    var tags = els.cards.querySelectorAll('.style-tag');
    Array.prototype.forEach.call(tags, function (tag) {
      tag.textContent = '· ' + state.style;
    });
    var sel = els.cards.querySelectorAll('.card.sel');
    Array.prototype.forEach.call(sel, function (c) { c.classList.remove('sel'); });
    if (state.selSlot) {
      var cur = els.cards.querySelector('.card[data-slot="' + state.selSlot + '"]');
      if (cur) cur.classList.add('sel');
    }
  }

  /* ---------------------------------------------------------- 编辑 */

  function autoGrow(ta) {
    ta.style.height = 'auto';
    ta.style.height = Math.max(74, ta.scrollHeight + 2) + 'px';
  }

  function beginEdit(node) {
    var found = slotById(node.dataset.slot);
    if (!found) return;
    if (found.slot.kind === 'preserve' || node.classList.contains('ro')) return;
    commitEditor();

    var raw = fieldValue(found.slot, node.dataset.field);
    node.classList.add('editing');
    node.innerHTML = '';
    var ta = document.createElement('textarea');
    ta.value = raw;
    node.appendChild(ta);
    state.openEditor = { node: node, slotId: found.slot.id, field: node.dataset.field, raw: raw, ta: ta };
    ta.focus();
    autoGrow(ta);
    ta.addEventListener('input', function () { autoGrow(ta); });
    ta.addEventListener('blur', function () { commitEditor(); });
    ta.addEventListener('keydown', function (ev) {
      var k = ev.key;
      if ((ev.ctrlKey || ev.metaKey) && (k === 's' || k === 'S')) {
        ev.preventDefault();
        commitEditor();
        save();
        return;
      }
      if (k === 'Enter' && (ev.ctrlKey || ev.metaKey)) {
        ev.preventDefault();
        ev.stopPropagation();
        commitEditor();
        return;
      }
      if (k === 'Escape') {
        ev.preventDefault();
        ev.stopPropagation();
        cancelEditor();
      }
    });
  }

  function commitEditor() {
    var ed = state.openEditor;
    if (!ed) return;
    state.openEditor = null;
    var found = slotById(ed.slotId);
    ed.node.classList.remove('editing');
    if (!found) { ed.node.innerHTML = ''; return; }
    if (ed.ta.value !== ed.raw) {
      setField(found.slot, ed.field, ed.ta.value);
      markDirty();
      markCardDirty(ed.slotId);
    }
    ed.node.innerHTML = renderRich(fieldValue(found.slot, ed.field));
    if (state.view === 'compare') renderCompare();
  }

  function cancelEditor() {
    var ed = state.openEditor;
    if (!ed) return;
    state.openEditor = null;
    var found = slotById(ed.slotId);
    ed.node.classList.remove('editing');
    ed.node.innerHTML = found ? renderRich(fieldValue(found.slot, ed.field)) : '';
  }

  /* ---------------------------------------------------------- 选中 / 联动 */

  function selectSlot(slotId, scroll) {
    state.selSlot = slotId;
    var nodes = els.overlay.querySelectorAll('.hotspot');
    Array.prototype.forEach.call(nodes, function (node) {
      node.classList.toggle('sel', node.dataset.slot === slotId);
    });
    var list = els.cards.querySelectorAll('.card');
    Array.prototype.forEach.call(list, function (c) {
      c.classList.toggle('sel', c.dataset.slot === slotId);
    });
    if (scroll) {
      var card = els.cards.querySelector('.card[data-slot="' + slotId + '"]');
      if (card) card.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
    if (state.calib) renderOverlay();
    if (state.view === 'compare') renderCompare();
  }

  function hoverSlotFromCanvas(slotId) {
    highlightHotspot(slotId);
    var list = els.cards.querySelectorAll('.card');
    Array.prototype.forEach.call(list, function (c) {
      c.classList.toggle('hl', c.dataset.slot === slotId);
    });
    var card = els.cards.querySelector('.card[data-slot="' + slotId + '"]');
    if (card) {
      if (state.view === 'work') card.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
  }

  function unhoverSlotFromCanvas() {
    clearHotspotHighlight();
    var list = els.cards.querySelectorAll('.card.hl');
    Array.prototype.forEach.call(list, function (c) { c.classList.remove('hl'); });
  }

  /* ---------------------------------------------------------- 对比视图 */

  function compareCell(slot, style) {
    var kind = slot.kind;
    if (kind === 'text') {
      var v = (slot.values || {})[style] || {};
      return v.rec || '';
    }
    if (kind === 'card') {
      var c = (slot.cards || {})[style] || {};
      return [c.name, c.dose, c.line1, c.line2].filter(Boolean).join('\n');
    }
    if (kind === 'table') {
      return ((slot.rows || {})[style] || []).join('\n');
    }
    return slot.text || '';
  }

  function renderCompare() {
    if (state.view !== 'compare') return;
    var mod = curModule();
    var styles = state.data.styles;
    els.compare.innerHTML = '';

    if (state.selSlot) {
      var found = slotById(state.selSlot);
      if (found) {
        var tip = document.createElement('div');
        tip.className = 'cmp-tip';
        tip.textContent = '已选中槽位 ' + found.slot.id + '｜' + (found.slot.label || '') +
          '　·　四风格并排对照（只读，编辑请切回「工作台」视图）';
        els.compare.appendChild(tip);

        var grid = document.createElement('div');
        grid.className = 'cmp-grid';
        styles.forEach(function (st) {
          var col = document.createElement('div');
          col.className = 'cmp-col' + (st.id === state.style ? ' on' : '');
          var head = document.createElement('div');
          head.className = 'cmp-head';
          head.innerHTML = '<span>' + esc(st.id) + ' · ' + esc(st.name) + '</span><span class="grow"></span>';
          var cp = document.createElement('button');
          cp.type = 'button';
          cp.className = 'mini';
          cp.textContent = '复制';
          cp.dataset.act = 'copycmp';
          cp.dataset.slot = found.slot.id;
          cp.dataset.style = st.id;
          head.appendChild(cp);
          col.appendChild(head);
          var body = document.createElement('div');
          body.className = 'cmp-body';
          var t = document.createElement('div');
          t.className = 'text';
          t.style.margin = '0';
          t.innerHTML = renderRich(compareCell(found.slot, st.id));
          body.appendChild(t);
          col.appendChild(body);
          grid.appendChild(col);
        });
        els.compare.appendChild(grid);
        return;
      }
    }

    var tip2 = document.createElement('div');
    tip2.className = 'cmp-tip';
    tip2.textContent = '模块 ' + mod.id + '｜' + mod.name +
      '　·　全部槽位四风格对照（点击图上高亮框或左侧卡片可单独展开）。「真实内容·保留」的槽位无风格差异。';
    els.compare.appendChild(tip2);

    var table = document.createElement('table');
    table.className = 'cmp-table';
    var thead = document.createElement('thead');
    var hr = document.createElement('tr');
    hr.innerHTML = '<th style="width:110px">槽位</th>' +
      styles.map(function (st) { return '<th>' + esc(st.id) + ' · ' + esc(st.name) + '</th>'; }).join('');
    thead.appendChild(hr);
    table.appendChild(thead);

    var tbody = document.createElement('tbody');
    (mod.slots || []).forEach(function (slot) {
      var tr = document.createElement('tr');
      if (slot.id === state.selSlot) tr.className = 'cur';
      var td0 = document.createElement('td');
      td0.className = 'slotcell';
      td0.textContent = slot.id;
      td0.title = slot.label || '';
      tr.appendChild(td0);
      styles.forEach(function (st) {
        var td = document.createElement('td');
        var html = renderRich(compareCell(slot, st.id));
        if (slot.kind === 'preserve') {
          html += '<div class="sep">（保留·无风格差异）</div>';
        }
        td.innerHTML = '<div class="ctext">' + html + '</div>';
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    els.compare.appendChild(table);
  }

  function setView(view) {
    commitEditor();
    state.view = view;
    Array.prototype.forEach.call(els.viewSeg.querySelectorAll('button'), function (b) {
      b.classList.toggle('on', b.dataset.view === view);
    });
    if (view === 'compare') {
      els.cards.classList.add('hidden');
      els.compare.classList.remove('hidden');
      renderCompare();
    } else {
      els.compare.classList.add('hidden');
      els.cards.classList.remove('hidden');
    }
  }

  /* ---------------------------------------------------------- 风格 */

  function renderStyleSeg() {
    els.styleSeg.innerHTML = '';
    state.data.styles.forEach(function (st) {
      var b = document.createElement('button');
      b.type = 'button';
      b.textContent = st.id + ' ' + st.name;
      b.title = st.desc || '';
      b.dataset.style = st.id;
      if (st.id === state.style) b.classList.add('on');
      b.addEventListener('click', function () { setStyle(st.id); });
      els.styleSeg.appendChild(b);
    });
  }

  function setStyle(id) {
    if (id === state.style) return;
    commitEditor();
    state.style = id;
    try { localStorage.setItem(LS_STYLE, id); } catch (e) { /* 忽略 */ }
    Array.prototype.forEach.call(els.styleSeg.querySelectorAll('button'), function (b) {
      b.classList.toggle('on', b.dataset.style === id);
    });
    /* 各风格的版式单元数一致，所以只重绘文案、不重建卡片，
       以保留右侧滚动位置与「备选」的展开状态；行数不一致时才重建。 */
    var needRebuild = (curModule().slots || []).some(function (slot) {
      if (slot.kind !== 'table') return false;
      var want = ((slot.rows || {})[id] || []).length;
      var have = els.cards.querySelectorAll('.text[data-slot="' + slot.id + '"]').length;
      return want !== have;
    });
    if (needRebuild) renderCards();
    else paintCards();
    if (state.view === 'compare') renderCompare();
  }

  /* ---------------------------------------------------------- 模块切换 */

  function gotoModule(index) {
    commitEditor();
    var total = state.data.modules.length;
    state.modIdx = ((index % total) + total) % total;
    state.selSlot = null;
    renderFlags();
    renderModMeta();
    renderNav();
    loadImage(curModule().img);
    renderOverlay();
    renderCards();
    if (state.view === 'compare') renderCompare();
    els.cards.scrollTop = 0;
  }

  function goSlot(delta) {
    var slots = curModule().slots || [];
    if (!slots.length) return;
    var idx = -1;
    for (var i = 0; i < slots.length; i++) if (slots[i].id === state.selSlot) idx = i;
    var next = idx + delta;
    if (idx < 0) next = delta > 0 ? 0 : slots.length - 1;
    next = ((next % slots.length) + slots.length) % slots.length;
    selectSlot(slots[next].id, true);
  }

  /* ---------------------------------------------------------- 标定模式 */

  function setCalib(on) {
    if (on && !state.selSlot) {
      var slots = curModule().slots || [];
      if (slots.length) selectSlot(slots[0].id, true);
      if (!state.selSlot) return;
    }
    state.calib = on;
    els.btnCalib.classList.toggle('on', on);
    els.overlay.classList.toggle('calib', on);
    renderOverlay();
    if (on) {
      toast('标定模式：拖动选中槽位的高亮框或 8 个手柄调整坐标（精度 0.5%），保存后写回 copy.json。Esc 退出。');
    }
  }

  function applyDrag(base, handle, dx, dy) {
    var x = base[0];
    var y = base[1];
    var w = base[2];
    var h = base[3];
    if (handle === 'move') {
      x += dx;
      y += dy;
    } else {
      if (handle.indexOf('w') >= 0) { x += dx; w -= dx; }
      if (handle.indexOf('e') >= 0) { w += dx; }
      if (handle.indexOf('n') >= 0) { y += dy; h -= dy; }
      if (handle.indexOf('s') >= 0) { h += dy; }
    }
    if (w < 0.5) w = 0.5;
    if (h < 0.5) h = 0.5;
    x = Math.max(-50, Math.min(150, x));
    y = Math.max(-50, Math.min(150, y));
    w = Math.min(200, w);
    h = Math.min(200, h);
    return [p05(x), p05(y), p05(w), p05(h)];
  }

  function syncCoordInputs(slotId) {
    var found = slotById(slotId);
    if (!found) return;
    var box = els.cards.querySelector('[data-coords="' + slotId + '"]');
    if (!box) return;
    var rects = found.slot.rects || [];
    Array.prototype.forEach.call(box.querySelectorAll('input[data-act="coord"]'), function (inp) {
      var ri = Number(inp.dataset.rect);
      var ai = Number(inp.dataset.axis);
      if (rects[ri]) inp.value = rects[ri][ai];
    });
  }

  function startDrag(ev) {
    var hs = ev.target.closest ? ev.target.closest('.hotspot') : null;
    if (!hs) return;
    if (hs.dataset.slot !== state.selSlot) return;
    var found = slotById(state.selSlot);
    if (!found) return;
    var rects = found.slot.rects || [];
    var ri = Number(hs.dataset.rect);
    if (!rects[ri]) return;

    ev.preventDefault();
    var handle = ev.target.dataset && ev.target.dataset.h ? ev.target.dataset.h : 'move';
    var box = els.canvas.getBoundingClientRect();
    var startX = ev.clientX;
    var startY = ev.clientY;
    var base = rects[ri].slice();

    function onMove(e2) {
      var dx = (e2.clientX - startX) / box.width * 100;
      var dy = (e2.clientY - startY) / box.height * 100;
      rects[ri] = applyDrag(base, handle, dx, dy);
      repaintSelRects();
      syncCoordInputs(state.selSlot);
      markDirty();
    }
    function onUp() {
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
    }
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
  }

  function resetRect(slotId) {
    if (!state.origRects[slotId]) return;
    var found = slotById(slotId);
    if (!found) return;
    found.slot.rects = clone(state.origRects[slotId]);
    repaintSelRects();
    syncCoordInputs(slotId);
    markDirty();
    toast('已把 ' + slotId + ' 的坐标重置为页面加载时的值（保存后写回）。');
  }

  /* ---------------------------------------------------------- 合规检查 */

  function scannedFields(slot) {
    var out = [];
    if (slot.kind === 'text') {
      var v = (slot.values || {})[state.style] || {};
      if (v.rec != null) out.push(['产出英文', v.rec]);
      if (v.alt != null) out.push(['备选', v.alt]);
    } else if (slot.kind === 'card') {
      var c = (slot.cards || {})[state.style] || {};
      [['name', '名称'], ['dose', '剂量'], ['line1', '说明1'], ['line2', '说明2']].forEach(function (pair) {
        if (c[pair[0]] != null) out.push([pair[1], c[pair[0]]]);
      });
    } else if (slot.kind === 'table') {
      ((slot.rows || {})[state.style] || []).forEach(function (row, i) {
        if (row != null) out.push(['第' + (i + 1) + '行', row]);
      });
    }
    return out;
  }

  function runCompliance() {
    var banned = (state.data.meta.banned || []).slice();
    var hits = [];
    var reminders = [];

    state.data.modules.forEach(function (mod, mi) {
      var moduleHasNeeds = (mod.slots || []).some(function (s) { return !!s.needs; });
      (mod.slots || []).forEach(function (slot) {
        var fields = scannedFields(slot);
        fields.forEach(function (pair) {
          var label = pair[0];
          var text = String(pair[1] || '');
          var lower = text.toLowerCase();
          banned.forEach(function (word) {
            var needle = String(word).toLowerCase();
            if (!needle) return;
            var from = 0;
            var at = lower.indexOf(needle, from);
            while (at >= 0) {
              hits.push({
                mi: mi, modId: mod.id, slotId: slot.id, field: label, word: word,
                ctx: text.slice(Math.max(0, at - 24), at + needle.length + 24),
                pre: text.slice(Math.max(0, at - 24), at),
                mid: text.slice(at, at + needle.length),
                post: text.slice(at + needle.length, at + needle.length + 24)
              });
              from = at + needle.length;
              at = lower.indexOf(needle, from);
            }
          });
        });
        if (!moduleHasNeeds) {
          var starred = fields.filter(function (pair) { return hasFootnoteMark(pair[1]); });
          if (starred.length) {
            reminders.push({
              mi: mi, modId: mod.id, slotId: slot.id,
              field: starred.map(function (p) { return p[0]; }).join('、')
            });
          }
        }
      });
    });

    /* 渲染浮层 */
    var curStyleName = '';
    state.data.styles.forEach(function (s) { if (s.id === state.style) curStyleName = s.name; });
    els.modalTitle.textContent = '合规检查 · 当前风格 ' + state.style +
      (curStyleName ? ' · ' + curStyleName : '');
    els.modalBody.innerHTML = '';

    var scannedNote = document.createElement('p');
    scannedNote.className = 'hint-p';
    scannedNote.textContent = '扫描范围：当前风格下全部槽位的「产出英文 / 备选 / 名称 / 剂量 / 说明1 / 说明2 / 表格行」。' +
      '不扫描 note、insp、text 与 DSHEA 声明本身（这些字段会引用已被删除的原文，属正常内容）。' +
      '匹配方式：对 meta.banned 共 ' + banned.length + ' 个词做大小写不敏感子串匹配。';
    els.modalBody.appendChild(scannedNote);

    if (!hits.length) {
      var ok = document.createElement('div');
      ok.className = 'chk-ok';
      ok.textContent = '✓ 未发现黑名单词。';
      els.modalBody.appendChild(ok);
    } else {
      var sec = document.createElement('div');
      sec.className = 'chk-sec';
      sec.textContent = '黑名单命中 ' + hits.length + ' 处（点击可跳转到对应槽位）';
      els.modalBody.appendChild(sec);
      hits.forEach(function (h) {
        var item = document.createElement('div');
        item.className = 'chk-item';
        item.dataset.mi = String(h.mi);
        item.dataset.slot = h.slotId;
        item.innerHTML =
          '<div class="top"><span class="where">' + esc(h.modId) + ' / ' + esc(h.slotId) + '</span>' +
          '<span class="where">' + esc(h.field) + '</span>' +
          '<span class="word">' + esc(h.word) + '</span></div>' +
          '<div class="ctx">' + esc(h.pre) + '<mark>' + esc(h.mid) + '</mark>' + esc(h.post) + '</div>';
        item.addEventListener('click', function () { jumpTo(Number(this.dataset.mi), this.dataset.slot); });
        els.modalBody.appendChild(item);
      });
    }

    var sec2 = document.createElement('div');
    sec2.className = 'chk-sec';
    sec2.textContent = '脚注与免责声明校验';
    els.modalBody.appendChild(sec2);

    if (!reminders.length) {
      var ok2 = document.createElement('div');
      ok2.className = 'chk-ok';
      ok2.textContent = '✓ 所有带 * 脚注的槽位，其所属模块均已声明需要上图 DSHEA 免责声明。';
      els.modalBody.appendChild(ok2);
    } else {
      reminders.forEach(function (r) {
        var item = document.createElement('div');
        item.className = 'chk-item remind';
        item.dataset.mi = String(r.mi);
        item.dataset.slot = r.slotId;
        item.innerHTML =
          '<div class="top"><span class="where">' + esc(r.modId) + ' / ' + esc(r.slotId) + '</span>' +
          '<span class="word">提醒</span></div>' +
          '<div class="ctx">该槽位含 * 脚注（' + esc(r.field) + '），但本模块没有任何槽位声明「必须上图 DSHEA 免责声明」。</div>';
        item.addEventListener('click', function () { jumpTo(Number(this.dataset.mi), this.dataset.slot); });
        els.modalBody.appendChild(item);
      });
    }

    openModal();
  }

  function jumpTo(mi, slotId) {
    closeModal();
    setView('work');
    gotoModule(mi);
    selectSlot(slotId, true);
    highlightHotspot(slotId);
  }

  /* ---------------------------------------------------------- 浮层 */

  function openModal() { els.modal.classList.remove('hidden'); }

  function closeModal() { els.modal.classList.add('hidden'); }

  function showHelp() {
    els.modalTitle.textContent = '快捷键与使用说明';
    els.modalBody.innerHTML =
      '<p class="hint-p">左边看设计稿、右边读对应槽位文案。点击图上高亮框或右侧卡片即选中该槽位；' +
      '点击英文正文可直接修改，保存后写回 <code>copy.json</code>。</p>' +
      '<table class="kbd-table">' +
      '<tr><td><span class="key">←</span> <span class="key">→</span></td><td>上一个 / 下一个模块（M1…M10）</td></tr>' +
      '<tr><td><span class="key">↑</span> <span class="key">↓</span></td><td>上一个 / 下一个槽位</td></tr>' +
      '<tr><td><span class="key">1</span> <span class="key">2</span> <span class="key">3</span> <span class="key">4</span></td><td>切换风格 A / B / C / D</td></tr>' +
      '<tr><td><span class="key">Tab</span></td><td>在「工作台 / 四风格对比」视图间切换</td></tr>' +
      '<tr><td><span class="key">Ctrl</span>+<span class="key">S</span></td><td>保存（写回 copy.json，自动备份）</td></tr>' +
      '<tr><td><span class="key">Ctrl</span>+<span class="key">Enter</span></td><td>编辑态提交</td></tr>' +
      '<tr><td><span class="key">Esc</span></td><td>退出标定模式 / 取消编辑态 / 关闭浮层</td></tr>' +
      '<tr><td><span class="key">?</span></td><td>弹出本说明</td></tr>' +
      '</table>' +
      '<p class="hint-p" style="margin-top:10px">输入框 / 文本域聚焦时，除 Ctrl+S 与 Esc 外全部快捷键禁用。</p>' +
      '<p class="hint-p">标定模式：顶栏 <code>[标定]</code> 进入，拖动选中槽位的高亮框或 8 个手柄调整坐标，' +
      '也可在卡片「详情 → 当前坐标」里手工输入 4 个数字（精度 0.5%），保存后写回 <code>copy.json</code>。</p>' +
      '<p class="hint-p">「完成」勾选按产品保存在浏览器 localStorage（<code>copywb.done.*</code>），<b>不会</b>写入 copy.json；换产品后自动重新计数。</p>' +
      '<p class="hint-p">顶栏 <code>☀️ / 🌙</code> 按钮切换日间 / 夜间主题（默认夜间，选择记忆在浏览器）。' +
      '点击图上高亮框或槽位正文，右侧对应卡片会以高亮色整卡显示当前选中的槽位。</p>';
    openModal();
  }

  /* ---------------------------------------------------------- 保存与导出 */

  function save() {
    commitEditor();
    if (!state.data) return;
    var payload = JSON.stringify(state.data);
    fetch('/api/data', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json;charset=utf-8' },
      body: payload
    }).then(function (res) {
      return res.json().then(function (body) { return { ok: res.ok, body: body }; });
    }).then(function (r) {
      if (!r.ok || !r.body || !r.body.ok) {
        throw new Error((r.body && r.body.error) || 'HTTP 错误');
      }
      state.data.meta.savedAt = r.body.savedAt;
      state.dirty = false;
      clearCardDirty();
      setStatus('saved', hhmmss(r.body.savedAt));
      toast('已保存到 copy.json' + (r.body.backup ? '（备份：' + r.body.backup + '）' : ''));
    }).catch(function (err) {
      setStatus('failed', err.message);
      toast('保存失败：' + err.message, true);
    });
  }

  function collectPending() {
    var out = [];
    state.data.modules.forEach(function (mod) {
      (mod.slots || []).forEach(function (slot) {
        if (slot.judge && slot.judge.indexOf('疑似') >= 0 && !state.done[slot.id]) {
          out.push({ module: mod.id, slot: slot.id, label: slot.label || '' });
        }
      });
    });
    return out;
  }

  function doExport(style) {
    commitEditor();
    var pending = collectPending();
    fetch('/api/export?style=' + encodeURIComponent(style), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json;charset=utf-8' },
      body: JSON.stringify({ pending: pending })
    }).then(function (res) {
      return res.json().then(function (body) { return { ok: res.ok, body: body }; });
    }).then(function (r) {
      if (!r.ok || !r.body || !r.body.ok) throw new Error((r.body && r.body.error) || 'HTTP 错误');
      toast('已导出「风格 ' + style + '」：' + r.body.name, false, '打开文件', function () {
        postOpen({ path: r.body.path });
      });
    }).catch(function (err) {
      toast('导出失败：' + err.message, true);
    });
  }

  function postOpen(payload) {
    fetch('/api/open', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json;charset=utf-8' },
      body: JSON.stringify(payload)
    }).then(function (res) {
      return res.json().then(function (body) { return { ok: res.ok, body: body }; });
    }).then(function (r) {
      if (!r.ok || !r.body || !r.body.ok) throw new Error((r.body && r.body.error) || 'HTTP 错误');
    }).catch(function (err) {
      toast('打开失败：' + err.message, true);
    });
  }

  function copyText(text, label) {
    function done(ok) {
      if (ok) toast('已复制' + (label ? '：' + label : ''));
      else toast('复制失败，请手动选中文本复制', true);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { done(true); }, function () { done(fallbackCopy(text)); });
    } else {
      done(fallbackCopy(text));
    }
  }

  function fallbackCopy(text) {
    try {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.top = '-1000px';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      var ok = document.execCommand('copy');
      document.body.removeChild(ta);
      return ok;
    } catch (e) {
      return false;
    }
  }

  /* ---------------------------------------------------------- 事件绑定 */

  function bindStaticEvents() {
    els.btnSave.addEventListener('click', save);
    els.btnCheck.addEventListener('click', runCompliance);
    els.btnCalib.addEventListener('click', function () { setCalib(!state.calib); });
    els.btnTheme.addEventListener('click', function () {
      var next = document.documentElement.getAttribute('data-theme') === 'day' ? 'night' : 'day';
      try { localStorage.setItem(LS_THEME, next); } catch (e) { /* 忽略 */ }
      applyTheme(next);
      toast(next === 'night' ? '已切换到夜间模式' : '已切换到日间模式');
    });
    els.modalClose.addEventListener('click', closeModal);
    els.modal.addEventListener('mousedown', function (ev) {
      if (ev.target === els.modal) closeModal();
    });

    Array.prototype.forEach.call(els.viewSeg.querySelectorAll('button'), function (b) {
      b.addEventListener('click', function () { setView(b.dataset.view); });
    });

    /* 导出下拉 */
    els.btnExport.addEventListener('click', function (ev) {
      ev.stopPropagation();
      els.exportMenu.classList.toggle('open');
    });
    document.addEventListener('click', function (ev) {
      if (!els.ddExport.contains(ev.target)) els.exportMenu.classList.remove('open');
    });
    els.exportMenu.addEventListener('click', function (ev) {
      var b = ev.target.closest('button');
      if (!b) return;
      els.exportMenu.classList.remove('open');
      if (b.dataset.style) doExport(b.dataset.style);
      else if (b.dataset.act === 'openExportDir') postOpen({ which: 'export' });
    });

    /* 画布 hover / 点击 / 拖动 */
    els.overlay.addEventListener('mouseover', function (ev) {
      var hs = ev.target.closest('.hotspot');
      if (!hs) return;
      hoverSlotFromCanvas(hs.dataset.slot);
    });
    els.overlay.addEventListener('mouseout', function (ev) {
      var hs = ev.target.closest('.hotspot');
      if (!hs) return;
      if (ev.relatedTarget && hs.contains(ev.relatedTarget)) return;
      unhoverSlotFromCanvas();
    });
    els.overlay.addEventListener('click', function (ev) {
      var hs = ev.target.closest('.hotspot');
      if (!hs) return;
      selectSlot(hs.dataset.slot, false);
    });
    els.overlay.addEventListener('mousedown', function (ev) {
      if (!state.calib) return;
      startDrag(ev);
    });

    /* 卡片区联动与操作 */
    els.cards.addEventListener('mouseover', function (ev) {
      var card = ev.target.closest('.card');
      if (!card) return;
      if (ev.relatedTarget && card.contains(ev.relatedTarget)) return;
      highlightHotspot(card.dataset.slot);
    });
    els.cards.addEventListener('mouseout', function (ev) {
      var card = ev.target.closest('.card');
      if (!card) return;
      if (ev.relatedTarget && card.contains(ev.relatedTarget)) return;
      clearHotspotHighlight();
    });
    els.cards.addEventListener('click', function (ev) {
      var card = ev.target.closest('.card');
      if (card) selectSlot(card.dataset.slot, false);

      var btn = ev.target.closest('button');
      if (btn) {
        var found;
        if (btn.dataset.act === 'copy') {
          found = slotById(btn.dataset.slot);
          if (found) copyText(fieldValue(found.slot, btn.dataset.field), btn.dataset.slot + ' · ' + btn.dataset.field);
          return;
        }
        if (btn.dataset.act === 'locate') {
          selectSlot(btn.dataset.slot, true);
          highlightHotspot(btn.dataset.slot);
          return;
        }
        if (btn.dataset.act === 'resetrect') {
          resetRect(btn.dataset.slot);
          return;
        }
        if (btn.dataset.act === 'promote') {
          var fs = slotById(btn.dataset.slot);
          if (fs) promoteAlt(fs.slot);
          return;
        }
      }
      var text = ev.target.closest('.text');
      if (text && !text.classList.contains('ro')) beginEdit(text);
    });

    els.cards.addEventListener('change', function (ev) {
      var inp = ev.target;
      if (inp.dataset && inp.dataset.act === 'done') {
        if (inp.checked) state.done[inp.dataset.slot] = true;
        else delete state.done[inp.dataset.slot];
        persistDone();
        var hs = els.overlay.querySelectorAll('.hotspot[data-slot="' + inp.dataset.slot + '"]');
        Array.prototype.forEach.call(hs, function (node) { node.classList.toggle('is-done', inp.checked); });
      }
    });

    els.cards.addEventListener('input', function (ev) {
      var inp = ev.target;
      if (inp.tagName === 'INPUT' && inp.dataset && inp.dataset.act === 'coord') {
        var found = slotById(inp.dataset.slot);
        if (!found) return;
        var rects = found.slot.rects || [];
        var ri = Number(inp.dataset.rect);
        var ai = Number(inp.dataset.axis);
        if (!rects[ri]) return;
        var val = parseFloat(inp.value);
        if (isNaN(val)) return;
        rects[ri][ai] = p05(val);
        repaintSelRects();
        markDirty();
      }
    });

    els.cards.addEventListener('blur', function (ev) {
      var inp = ev.target;
      if (inp.tagName === 'INPUT' && inp.dataset && inp.dataset.act === 'coord') {
        var found = slotById(inp.dataset.slot);
        if (!found) return;
        var rects = found.slot.rects || [];
        var ri = Number(inp.dataset.rect);
        var ai = Number(inp.dataset.axis);
        if (rects[ri]) inp.value = rects[ri][ai];
      }
    }, true);

    /* 对比视图复制 */
    els.compare.addEventListener('click', function (ev) {
      var btn = ev.target.closest('button');
      if (!btn) return;
      if (btn.dataset.act === 'copycmp') {
        var found = slotById(btn.dataset.slot);
        if (found) copyText(compareCell(found.slot, btn.dataset.style), btn.dataset.slot + ' · 风格 ' + btn.dataset.style);
      }
    });

    /* 分隔条 */
    els.splitter.addEventListener('mousedown', function (ev) {
      ev.preventDefault();
      els.splitter.classList.add('dragging');
      function onMove(e2) {
        var box = $('main').getBoundingClientRect();
        var pct = (e2.clientX - box.left) / box.width * 100;
        pct = Math.max(25, Math.min(75, pct));
        els.left.style.flexBasis = pct + '%';
        try { localStorage.setItem(LS_SPLIT, String(pct)); } catch (e) { /* 忽略 */ }
      }
      function onUp() {
        els.splitter.classList.remove('dragging');
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
        fitCanvas();
      }
      document.addEventListener('mousemove', onMove);
      document.addEventListener('mouseup', onUp);
    });

    window.addEventListener('resize', fitCanvas);
    if (window.ResizeObserver) {
      new ResizeObserver(function () { fitCanvas(); }).observe(els.canvasWrap);
    }

    window.addEventListener('beforeunload', function (ev) {
      if (state.dirty) {
        ev.preventDefault();
        ev.returnValue = '有未保存的修改，确定离开吗？';
        return ev.returnValue;
      }
    });

    document.addEventListener('keydown', onKeyDown);
  }

  function promoteAlt(slot) {
    if (slot.kind !== 'text') return;
    var v = (slot.values || {})[state.style];
    if (!v) return;
    var old = v.rec;
    v.rec = v.alt;
    v.alt = old;
    markDirty();
    markCardDirty(slot.id);
    paintCards();
    if (state.view === 'compare') renderCompare();
    toast('已把「备选」提升为产出英文，原产出英文转为备选（尚未保存）。');
  }

  function onKeyDown(ev) {
    var target = ev.target;
    var tag = (target.tagName || '').toLowerCase();
    var typing = tag === 'textarea' || tag === 'input' || target.isContentEditable;

    var key = ev.key;
    if ((ev.ctrlKey || ev.metaKey) && (key === 's' || key === 'S')) {
      ev.preventDefault();
      save();
      return;
    }
    if (key === 'Escape') {
      if (state.openEditor) { cancelEditor(); return; }
      if (!els.modal.classList.contains('hidden')) { closeModal(); return; }
      if (state.calib) { setCalib(false); return; }
      if (els.exportMenu.classList.contains('open')) { els.exportMenu.classList.remove('open'); return; }
      return;
    }
    if (typing) return;

    if (key === 'ArrowLeft') { ev.preventDefault(); gotoModule(state.modIdx - 1); return; }
    if (key === 'ArrowRight') { ev.preventDefault(); gotoModule(state.modIdx + 1); return; }
    if (key === 'ArrowUp') { ev.preventDefault(); goSlot(-1); return; }
    if (key === 'ArrowDown') { ev.preventDefault(); goSlot(1); return; }
    if (key === 'Tab') { ev.preventDefault(); setView(state.view === 'work' ? 'compare' : 'work'); return; }
    if (key === '?' || (key === '/' && ev.shiftKey)) { ev.preventDefault(); showHelp(); return; }
    if (key >= '1' && key <= '4') {
      var ids = state.data.styles.map(function (s) { return s.id; });
      var idx = Number(key) - 1;
      if (ids[idx]) { ev.preventDefault(); setStyle(ids[idx]); }
    }
  }

  function persistDone() {
    try { localStorage.setItem(doneKey(), JSON.stringify(state.done)); } catch (e) { /* 忽略 */ }
  }

  /* ---------------------------------------------------------- 启动 */

  /* ---------------------------------------------------------- 主题 */

  function applyTheme(theme) {
    var t = theme === 'day' ? 'day' : 'night';
    document.documentElement.setAttribute('data-theme', t);
    if (els.btnTheme) {
      els.btnTheme.textContent = t === 'night' ? '☀️ 日间' : '🌙 夜间';
      els.btnTheme.title = t === 'night' ? '当前：夜间模式，点击切换为日间' : '当前：日间模式，点击切换为夜间';
    }
  }

  function loadLocalPrefs() {
    try {
      var split = parseFloat(localStorage.getItem(LS_SPLIT));
      if (!isNaN(split) && split >= 25 && split <= 75) els.left.style.flexBasis = split + '%';
    } catch (e) { /* 忽略 */ }
    try {
      var style = localStorage.getItem(LS_STYLE);
      if (style && 'ABCD'.indexOf(style) >= 0) state.style = style;
    } catch (e) { /* 忽略 */ }
    var theme = null;
    try { theme = localStorage.getItem(LS_THEME); } catch (e) { /* 忽略 */ }
    applyTheme(theme === 'day' ? 'day' : 'night');
  }

  function fatal(message, detail) {
    els.cards.innerHTML = '';
    var box = document.createElement('div');
    box.className = 'err-box';
    box.innerHTML = '<b>' + esc(message) + '</b><div style="margin-top:6px">' + detail + '</div>';
    els.cards.appendChild(box);
    setStatus('failed', message);
  }

  function boot() {
    loadLocalPrefs();
    bindStaticEvents();

    fetch('/api/data', { cache: 'no-store' }).then(function (res) {
      if (!res.ok) throw new Error('HTTP ' + res.status);
      return res.json();
    }).then(function (data) {
      if (!data || !Array.isArray(data.modules)) throw new Error('copy.json 结构异常：缺少 modules 数组');
      state.data = data;

      try {
        var doneState = JSON.parse(localStorage.getItem(doneKey()) || '{}');
        state.done = (doneState && typeof doneState === 'object' && !Array.isArray(doneState)) ? doneState : {};
      } catch (e) { state.done = {}; }

      els.metaProduct.textContent = data.meta.product || '产品文案工作台';
      els.metaSpec.textContent = data.meta.spec || '';
      document.title = '文案工作台 · ' + (data.meta.product || '');

      if ('ABCD'.indexOf(state.style) < 0 || !data.styles.some(function (s) { return s.id === state.style; })) {
        state.style = (data.styles[0] || {}).id || 'A';
      }

      data.modules.forEach(function (mod) {
        (mod.slots || []).forEach(function (slot) {
          state.origRects[slot.id] = clone(slot.rects || []);
        });
      });

      renderStyleSeg();
      renderNav();
      gotoModule(0);
      setView('work');

      if (data.meta.savedAt) setStatus('saved', hhmmss(data.meta.savedAt));
      else setStatus('', '就绪（尚未保存过）');
    }).catch(function (err) {
      fatal('无法读取 copy.json', '请通过 <code>启动工作台.bat</code>（Windows）或 ' +
        '<code>./启动工作台.sh</code>（macOS / Linux）启动本地服务后访问 ' +
        '<code>http://127.0.0.1:8787/_workbench/</code>，不要直接双击打开 index.html。<br>' +
        '错误详情：' + esc(err.message));
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
