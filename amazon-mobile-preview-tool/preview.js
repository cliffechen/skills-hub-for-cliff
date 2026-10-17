/* The phone is a renderer only. Project editing and persistence live in app.js. */
const el = (tag, className, text) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
};
const clamp = (value, min, max) => Math.max(min, Math.min(max, Number(value) || 0));
const text = (node, value) => {
  const next = String(value || '');
  if (node.textContent !== next) node.textContent = next;
  node.hidden = !next;
};
const icon = (name, className = '') => {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('class', `preview-ui-icon ${className}`);
  svg.setAttribute('viewBox', '0 0 24 24');
  svg.setAttribute('aria-hidden', 'true');
  const paths = {
    search: 'M20.5 20.5 16 16 M10.5 3a7.5 7.5 0 1 0 0 15 7.5 7.5 0 0 0 0-15Z',
    camera: 'M8 4H4v4 M16 4h4v4 M4 16v4h4 M20 16v4h-4 M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8Z',
    home: 'M3 10.5 12 3l9 7.5 M5.5 9v12H10v-7h4v7h4.5V9',
    user: 'M12 3a4 4 0 1 0 0 8 4 4 0 0 0 0-8Z M4 21v-2a8 6 0 0 1 16 0v2',
    cart: 'M2 3h3l2.5 12h12L22 7H6 M9 19a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3Z M18 19a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3Z',
    menu: 'M3 5h18 M3 12h18 M3 19h18',
    back: 'M15 4 7 12l8 8',
    mic: 'M12 3a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V6a3 3 0 0 0-3-3Z M5 11a7 7 0 0 0 14 0 M12 18v3',
    share: 'M12 15V3 M7 8l5-5 5 5 M5 12v8h14v-8',
    pin: 'M12 21s-6-5.6-6-11a6 6 0 0 1 12 0c0 5.4-6 11-6 11Z M12 8a2 2 0 1 0 0 4 2 2 0 0 0 0-4Z',
    lock: 'M7 11V8a5 5 0 0 1 10 0v3 M5 11h14v10H5z',
    reload: 'M20 12a8 8 0 1 1-2.3-5.7 M20 4v5h-5',
    forward: 'M9 4l8 8-8 8',
    tabs: 'M8 8h12v12H8z M4 16V4h12',
    book: 'M4 5c3-1.3 5.7-1 8 1 2.3-2 5-2.3 8-1v14c-3-1.3-5.7-1-8 1-2.3-2-5-2.3-8-1z M12 6v14',
    dots: 'M12 5h.01 M12 12h.01 M12 19h.01',
    close: 'M6 6l12 12 M18 6 6 18',
  };
  const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  path.setAttribute('d', paths[name]);
  svg.append(path);
  return svg;
};

export class PhonePreview {
  constructor(rootElement, { onViewChange, onSelectAsset, onError } = {}) {
    this.root = rootElement;
    this.callbacks = { onViewChange, onSelectAsset, onError };
    this.project = null;
    this.projectId = null;
    this.galleryIndex = 0;
    this.carouselIndices = {};
    this.modules = new Map();
    this.preservation = null;
    this.programmaticUntil = 0;
    this.root.classList.add('preview-root');
    this._build();
    this.resizeObserver = new ResizeObserver(() => {
      const anchor = this._captureAnchor();
      this._layoutAll();
      this._applyAnchor(anchor);
    });
    this.resizeObserver.observe(this.root);
  }

  _build() {
    // Android Chrome address bar (web surface only).
    this.chromeBar = el('div', 'preview-browser-top preview-web-only preview-android-only preview-shell-only');
    const chromeAddress = el('div', 'preview-address');
    chromeAddress.append(icon('lock', 'preview-address-lock'), el('span', '', 'amazon.com'));
    this.chromeBar.append(icon('home', 'preview-browser-icon'), chromeAddress, el('span', 'preview-tab-count', '3'), icon('dots', 'preview-browser-icon'));

    // Amazon Shopping app header.
    this.header = el('header', 'preview-search-header preview-app-only preview-shell-only');
    const searchRow = el('div', 'preview-search-row');
    const search = el('div', 'preview-search-field');
    search.append(icon('search', 'preview-search-icon'), el('span', 'preview-search-placeholder', 'Search Amazon'), icon('camera', 'preview-camera-icon'), icon('mic', 'preview-mic-icon'));
    searchRow.append(icon('back', 'preview-back-icon'), search);
    const location = el('div', 'preview-location');
    location.append(icon('pin', 'preview-location-icon'), el('span', '', 'Deliver to United States'));
    this.header.append(searchRow, location);

    // amazon.com mobile web header.
    this.webHeader = el('header', 'preview-web-header preview-web-only preview-shell-only');
    const webTop = el('div', 'preview-web-top');
    webTop.append(icon('menu', 'preview-web-icon'), el('span', 'preview-web-logo', 'amazon'), el('span', 'preview-web-signin', 'Sign in ›'), icon('user', 'preview-web-icon'), icon('cart', 'preview-web-icon'));
    const webSearch = el('div', 'preview-web-search');
    webSearch.append(el('span', 'preview-search-placeholder', 'Search Amazon'), icon('search', 'preview-web-search-button'));
    const webLocation = el('div', 'preview-web-location');
    webLocation.append(icon('pin', 'preview-location-icon'), el('span', '', 'Deliver to United States'));
    this.webHeader.append(webTop, webSearch, webLocation);

    this.scroller = el('div', 'preview-scroll');
    this.scroller.tabIndex = 0;
    this.scroller.setAttribute('aria-label', '亚马逊手机预览页面');
    this.productIntro = el('section', 'preview-product-intro preview-shell-only');
    this.productIntro.dataset.previewAnchor = 'product-intro';
    const brandRow = el('div', 'preview-brand-row');
    this.brand = el('div', 'preview-brand');
    this.rating = el('div', 'preview-rating');
    this.ratingValue = el('span', 'preview-rating-value');
    this.stars = el('span', 'preview-stars', '★★★★★');
    this.starsFill = el('span', 'preview-stars-fill', '★★★★★');
    this.stars.append(this.starsFill);
    this.reviewCount = el('span', 'preview-review-count');
    this.rating.append(this.ratingValue, this.stars, this.reviewCount);
    brandRow.append(this.brand, this.rating);
    this.productTitle = el('h1', 'preview-product-title');
    this.productIntro.append(brandRow, this.productTitle);

    this.gallerySection = el('section', 'preview-gallery');
    this.gallerySection.dataset.previewAnchor = 'gallery';
    this.gallerySection.setAttribute('aria-label', '商品主副图');
    this.gallery = this._makeSlider('gallery', () => {
      this.galleryIndex = this.gallery.index;
      this._emitView();
    });
    const galleryTools = el('div', 'preview-gallery-tools preview-shell-only');
    galleryTools.append(icon('share', 'preview-gallery-tool'));
    this.galleryDots = el('div', 'preview-gallery-dots');
    this.gallerySection.append(this.gallery.viewport, galleryTools, this.galleryDots);
    // Tapping a product image opens the full-screen viewer, as in the app.
    this.gallery.viewport.addEventListener('click', event => {
      if (event.target.closest('.preview-image')) this._openViewer(this.gallery.index);
    });

    this.buy = el('section', 'preview-buy preview-shell-only');
    this.buy.dataset.previewAnchor = 'buy';
    this.price = el('div', 'preview-price');
    const prime = el('div', 'preview-prime');
    prime.append(el('span', 'preview-prime-check', '✓'), el('span', 'preview-prime-word', 'prime'));
    const day = offset => new Date(Date.now() + offset * 86400000);
    const delivery = el('div', 'preview-delivery');
    delivery.append('FREE delivery ', el('b', '', day(3).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })));
    const fastest = el('div', 'preview-delivery preview-delivery-fast');
    fastest.append('Or fastest delivery ', el('b', '', `Tomorrow, ${day(1).toLocaleDateString('en-US', { month: 'long', day: 'numeric' })}`));
    const deliverTo = el('div', 'preview-deliver-to');
    deliverTo.append(icon('pin', 'preview-location-icon'), el('span', '', 'Deliver to United States'));
    const cart = el('div', 'preview-purchase-button', 'Add to Cart');
    const purchase = el('div', 'preview-purchase-button preview-purchase-now', 'Buy Now');
    cart.setAttribute('aria-hidden', 'true');
    purchase.setAttribute('aria-hidden', 'true');
    this.soldBy = el('div', 'preview-sold-by');
    this.buy.append(this.price, prime, delivery, fastest, deliverTo, el('div', 'preview-stock', 'In Stock'), el('div', 'preview-quantity', 'Quantity: 1'), cart, purchase, this.soldBy, el('div', 'preview-simulation-note', '商品信息仅用于模拟浏览'));

    this.about = el('section', 'preview-about preview-shell-only');
    this.about.dataset.previewAnchor = 'about';
    this.aboutList = el('ul', 'preview-about-list');
    this.about.append(el('h2', 'preview-section-heading', 'About this item'), this.aboutList);

    this.aplus = el('section', 'preview-aplus');
    this.aplus.dataset.previewAnchor = 'aplus';
    this.aplusHeading = el('h2', 'preview-aplus-heading preview-shell-only', 'Product description');
    this.moduleList = el('div', 'preview-modules');
    this.emptyAplus = el('div', 'preview-aplus-empty', 'A+ 内容将在这里显示');
    this.aplusBadge = el('div', 'preview-guide-badge preview-aplus-badge');
    this.aplus.append(this.aplusBadge, this.aplusHeading, this.moduleList, this.emptyAplus);
    // Customer questions & answers, below the product description as on the product page.
    this.qaSection = el('section', 'preview-qa');
    this.qaSection.dataset.previewAnchor = 'qa';
    const qaSearch = el('div', 'preview-qa-search');
    qaSearch.append(icon('search', 'preview-qa-search-icon'), el('span', '', 'Have a question? Search for answers'));
    this.qaList = el('div', 'preview-qa-list');
    this.qaMore = el('button', 'preview-qa-more');
    this.qaMore.type = 'button';
    this.qaMore.addEventListener('click', () => {
      this.qaExpanded = !this.qaExpanded;
      this._renderQa();
      this._layoutAll();
    });
    this.qaSection.append(el('h2', 'preview-section-heading', 'Customer questions & answers'), qaSearch, this.qaList, this.qaMore);
    this.qaExpanded = false;
    this.foldLine = el('div', 'preview-fold-line');
    this.foldLine.append(el('span', '', '首屏底部 · 打开页面第一眼只看到这条线以上'));
    this.scroller.append(this.productIntro, this.gallerySection, this.buy, this.about, this.aplus, this.qaSection, this.foldLine);

    this.footer = el('nav', 'preview-bottom-nav preview-app-only preview-shell-only');
    this.footer.setAttribute('aria-label', '模拟 Amazon 导航');
    [['home', 'Home'], ['user', 'You'], ['cart', 'Cart'], ['menu', 'Menu']].forEach(([iconName, name], index) => {
      const item = el('div', `preview-nav-item${index === 0 ? ' is-active' : ''}`);
      item.append(icon(iconName, 'preview-nav-icon'), el('span', 'preview-nav-label', name));
      this.footer.append(item);
    });

    // iOS Safari bottom bar (web surface only).
    this.safariBar = el('div', 'preview-safari-bar preview-web-only preview-ios-only preview-shell-only');
    const safariAddress = el('div', 'preview-address');
    safariAddress.append(el('span', 'preview-address-aa', 'AA'), icon('lock', 'preview-address-lock'), el('span', '', 'amazon.com'), icon('reload', 'preview-address-reload'));
    const safariTools = el('div', 'preview-safari-tools');
    for (const name of ['back', 'forward', 'share', 'book', 'tabs']) safariTools.append(icon(name, 'preview-browser-icon'));
    this.safariBar.append(safariAddress, safariTools);

    this._buildViewer();
    this.root.replaceChildren(this.chromeBar, this.header, this.webHeader, this.scroller, this.footer, this.safariBar, this.viewer);
    this.scroller.addEventListener('scroll', () => {
      if (performance.now() < this.programmaticUntil) return;
      clearTimeout(this.scrollTimer);
      this.scrollTimer = setTimeout(() => this._emitView(), 100);
    }, { passive: true });
    for (const name of ['wheel', 'touchstart', 'pointerdown', 'keydown']) {
      this.scroller.addEventListener(name, () => { this.preservation = null; }, { passive: true });
    }
    this._bindTouchScroll();
    this.setEnvironment({});
  }

  update(project, { preservePosition = true } = {}) {
    if (!project) return;
    const changedProject = project.id !== this.projectId;
    const anchor = !changedProject && preservePosition ? this._captureAnchor() : null;
    const selectedGallery = this.gallery.items[this.gallery.index]?.id;
    if (changedProject) {
      this._closeViewer(false);
      this._clearTargetHighlight();
      this.modules.forEach(record => record.video?.pause());
      this.modules.clear();
      this.moduleList.replaceChildren();
      this.gallery.items = [];
      this.gallery.track.replaceChildren();
      this.galleryIndex = Number(project.view?.galleryIndex) || 0;
      this.carouselIndices = { ...(project.view?.carouselIndices || {}) };
      this.preservation = null;
    }
    this.project = project;
    this.projectId = project.id;
    this.root.classList.toggle('preview-content-only', project.settings?.shell === false);
    const product = project.product || {};
    text(this.brand, product.brand ? `Visit the ${product.brand} Store` : 'Visit the Brand Store');
    text(this.productTitle, product.title || 'Your product title');
    const rating = clamp(parseFloat(product.rating) || 4.5, 0, 5);
    this.ratingValue.textContent = rating.toFixed(1);
    this.starsFill.style.width = `${(rating / 5) * 100}%`;
    this.reviewCount.textContent = `(${product.reviews || '128'})`;
    this.rating.setAttribute('aria-label', `${rating.toFixed(1)} out of 5 stars`);
    this._renderPrice(String(product.price || '29.99'));
    text(this.soldBy, `Ships from Amazon · Sold by ${product.brand || 'Brand'}`);
    const bullets = String(product.bullets || '').split('\n').map(line => line.trim()).filter(Boolean);
    this.aboutList.replaceChildren(...bullets.map(line => el('li', '', line)));
    this.about.hidden = !bullets.length;
    if (changedProject) this.qaExpanded = false;
    this._renderQa();
    const galleryItems = project.gallery || [];
    this._syncSlides(this.gallery, galleryItems, item => ({ kind: 'gallery', itemId: item.id }));
    let galleryIndex = this.galleryIndex;
    if (!changedProject && selectedGallery) {
      const movedIndex = galleryItems.findIndex(item => item.id === selectedGallery);
      if (movedIndex >= 0) galleryIndex = movedIndex;
    }
    this._setIndex(this.gallery, galleryIndex, false);
    this.galleryIndex = this.gallery.index;
    this._syncDots();

    const wanted = new Set();
    const orderedModules = [...(project.modules || []).filter(module => module.type === 'brand-story'), ...(project.modules || []).filter(module => module.type !== 'brand-story')];
    for (const module of orderedModules) {
      wanted.add(module.id);
      let record = this.modules.get(module.id);
      if (record && record.type !== module.type) {
        if (this.highlightedTarget === record.node) this._clearTargetHighlight();
        record.video?.pause();
        record.node.remove();
        this.modules.delete(module.id);
        record = null;
      }
      if (!record) {
        record = this._makeModule(module);
        this.modules.set(module.id, record);
      }
      this._updateModule(record, module);
    }
    this.modules.forEach((record, id) => {
      if (!wanted.has(id)) {
        if (this.highlightedTarget === record.node) this._clearTargetHighlight();
        record.video?.pause();
        record.node.remove();
        this.modules.delete(id);
        delete this.carouselIndices[id];
      }
    });
    // insertBefore only moves nodes whose order actually changed, preserving video playback.
    let sibling = this.moduleList.firstChild;
    if (sibling === this.aplusHeading) sibling = sibling.nextSibling;
    for (const module of orderedModules) {
      const node = this.modules.get(module.id).node;
      if (node !== sibling) this.moduleList.insertBefore(node, sibling);
      sibling = node.nextSibling;
      if (sibling === this.aplusHeading) sibling = sibling.nextSibling;
    }
    // Match the editor groups: brand stories first, followed by the product description.
    const firstDescription = orderedModules.find(module => module.type !== 'brand-story');
    this.aplusHeading.hidden = !firstDescription && Boolean(project.modules?.length);
    if (firstDescription) this.moduleList.insertBefore(this.aplusHeading, this.modules.get(firstDescription.id).node);
    else this.aplus.insertBefore(this.aplusHeading, this.moduleList);
    this.emptyAplus.hidden = Boolean(project.modules?.length);
    this._layoutAll();
    if (changedProject || !preservePosition) {
      this.restoreView(project.view || {});
    } else {
      this.preservation = anchor;
      this._applyAnchor(anchor);
      requestAnimationFrame(() => {
        this._layoutAll();
        this._applyAnchor(this.preservation);
      });
    }
  }

  _makeModule(module) {
    const node = el('section', `preview-module preview-module-${module.type}`);
    node.dataset.previewAnchor = `module:${module.id}`;
    node.dataset.moduleId = module.id;
    const title = el('h3', 'preview-module-title');
    const body = el('p', 'preview-module-body');
    const record = { node, title, body, id: module.id, type: module.type };
    node.append(title);
    if (module.type === 'brand-story') {
      record.heading = el('h2', 'preview-brand-story-heading', 'From the brand');
      record.stage = el('div', 'preview-brand-story-stage');
      record.background = this._makeMedia({ kind: 'brand-background', moduleId: module.id }, { selectable: true, placeholderText: '添加背景图（可选）' });
      record.background.node.classList.add('preview-brand-story-background');
      record.header = el('div', 'preview-brand-story-header');
      record.logo = this._makeMedia({ kind: 'brand-logo', moduleId: module.id }, { selectable: true, placeholderText: '添加品牌 Logo（可选）' });
      record.logo.node.classList.add('preview-brand-story-logo');
      record.header.append(record.logo.node);
      record.slider = this._makeSlider('brand-story', () => {
        this.carouselIndices[module.id] = record.slider.index;
        this._emitView();
      });
      record.stage.append(record.background.node, record.header, record.slider.viewport);
      node.replaceChildren(record.heading, title, record.stage);
    } else if (module.type === 'carousel') {
      record.tabs = el('div', 'preview-carousel-tabs');
      record.tabs.setAttribute('role', 'tablist');
      record.tabs.setAttribute('aria-label', 'A+ 轮播导航');
      record.slider = this._makeSlider('carousel', () => {
        this.carouselIndices[module.id] = record.slider.index;
        this._syncTabs(record);
        this._emitView();
      });
      record.tabNodes = new Map();
      node.append(record.tabs, record.slider.viewport);
    } else if (module.type === 'video') {
      record.videoWrap = el('div', 'preview-video-wrap');
      record.video = el('video', 'preview-video');
      record.video.controls = true;
      record.video.preload = 'metadata';
      record.video.playsInline = true;
      record.video.setAttribute('aria-label', 'A+ 产品视频');
      record.videoEmpty = this._makePlaceholder('video');
      record.videoEmpty.addEventListener('click', () => this.callbacks.onSelectAsset?.({ kind: 'video', moduleId: record.id }));
      record.videoError = el('div', 'preview-video-error');
      record.videoError.hidden = true;
      record.video.addEventListener('loadedmetadata', () => {
        if (record.video.videoWidth && record.video.videoHeight) {
          record.video.style.aspectRatio = `${record.video.videoWidth} / ${record.video.videoHeight}`;
          this._afterMediaLoad();
        }
      });
      record.video.addEventListener('error', () => {
        if (!record.video.getAttribute('src')) return;
        const message = '此视频无法播放。请确认文件完整，并使用浏览器支持的 MP4 编码（如 H.264 / AAC）。';
        text(record.videoError, message);
        if (record.reportedErrorSrc !== record.video.getAttribute('src')) {
          record.reportedErrorSrc = record.video.getAttribute('src');
          this.callbacks.onError?.(message);
        }
      });
      record.videoWrap.append(record.video, record.videoEmpty, record.videoError);
      node.append(record.videoWrap);
    } else {
      record.media = this._makeMedia({ kind: 'image', moduleId: module.id });
      node.append(record.media.node);
    }
    node.append(body);
    record.badge = el('span', 'preview-guide-badge preview-module-badge');
    node.append(record.badge);
    return record;
  }

  _updateModule(record, module) {
    text(record.title, module.title);
    text(record.body, module.body);
    if (module.type === 'brand-story' || module.type === 'carousel') {
      if (module.type === 'brand-story') {
        this._setMedia(record.background, module.backgroundAssetId);
        record.logo.placeholderText = module.brandName || '添加品牌 Logo（可选）';
        record.logo.node.classList.toggle('has-brand-name', Boolean(module.brandName));
        this._setMedia(record.logo, module.logoAssetId);
        if (!module.logoAssetId) record.logo.placeholder.lastChild.textContent = record.logo.placeholderText;
      }
      const oldId = record.slider.items[record.slider.index]?.id;
      this._syncSlides(record.slider, module.slides || [], slide => ({ kind: 'slide', moduleId: module.id, slideId: slide.id }));
      const movedIndex = oldId ? record.slider.items.findIndex(item => item.id === oldId) : -1;
      this._setIndex(record.slider, movedIndex >= 0 ? movedIndex : this.carouselIndices[module.id] || 0, false);
      this.carouselIndices[module.id] = record.slider.index;
      this._syncTabs(record);
    } else if (module.type === 'video') {
      const asset = this.project.assets?.[module.videoAssetId];
      const source = asset ? this._assetURL(module.videoAssetId) : '';
      if ((record.video.getAttribute('src') || '') !== source) {
        record.video.pause();
        if (source) record.video.setAttribute('src', source);
        else record.video.removeAttribute('src');
        record.video.load();
        record.videoError.hidden = true;
        record.reportedErrorSrc = null;
      }
      const poster = this.project.assets?.[module.posterAssetId] ? this._assetURL(module.posterAssetId) : '';
      if ((record.video.getAttribute('poster') || '') !== poster) {
        if (poster) record.video.setAttribute('poster', poster);
        else record.video.removeAttribute('poster');
      }
      if (asset?.width && asset?.height) record.video.style.aspectRatio = `${asset.width} / ${asset.height}`;
      else if (!record.video.videoWidth) record.video.style.aspectRatio = '16 / 9';
      record.video.hidden = !source && !poster;
      record.videoEmpty.hidden = Boolean(source || poster);
      record.video.controls = Boolean(source);
      record.video.classList.toggle('preview-poster-only', !source && Boolean(poster));
    } else {
      this._setMedia(record.media, module.assetId);
    }
  }

  _makePlaceholder(kind = 'image') {
    const node = el('button', 'preview-placeholder');
    node.type = 'button';
    node.append(el('span', 'preview-placeholder-icon', kind === 'video' ? '▷' : '▧'), el('span', '', kind === 'video' ? '视频预览' : '图片预览'));
    node.setAttribute('aria-label', kind === 'video' ? '选择视频素材槽' : '选择图片素材槽');
    return node;
  }

  _makeMedia(target, { selectable = false, placeholderText = '图片预览' } = {}) {
    const node = el('div', 'preview-media');
    const image = el('img', 'preview-image');
    image.draggable = false;
    image.decoding = 'async';
    image.hidden = true;
    const placeholder = this._makePlaceholder();
    const record = { node, image, placeholder, target, assetId: null, placeholderText };
    placeholder.lastChild.textContent = placeholderText;
    placeholder.addEventListener('click', () => this.callbacks.onSelectAsset?.(record.target));
    if (selectable) {
      image.tabIndex = 0;
      image.setAttribute('role', 'button');
      const targetLabel = target.kind === 'brand-background' ? '选择品牌故事背景图' : target.kind === 'brand-logo' ? '选择品牌 Logo' : '选择品牌故事卡片';
      image.setAttribute('aria-label', targetLabel);
      placeholder.setAttribute('aria-label', targetLabel);
      image.addEventListener('click', () => this.callbacks.onSelectAsset?.(record.target));
      image.addEventListener('keydown', event => {
        if (event.key !== 'Enter' && event.key !== ' ') return;
        event.preventDefault();
        this.callbacks.onSelectAsset?.(record.target);
      });
    }
    image.addEventListener('load', () => {
      image.hidden = false;
      placeholder.hidden = true;
      const asset = this.project?.assets?.[record.assetId];
      if (!asset?.width || !asset?.height) node.style.aspectRatio = `${image.naturalWidth} / ${image.naturalHeight}`;
      this._afterMediaLoad();
    });
    image.addEventListener('error', () => {
      if (!image.getAttribute('src')) return;
      image.hidden = true;
      placeholder.hidden = false;
      placeholder.lastChild.textContent = '图片无法读取';
      this._afterMediaLoad();
    });
    node.append(image, placeholder);
    return record;
  }

  _setMedia(record, assetId) {
    const asset = this.project.assets?.[assetId];
    record.assetId = assetId || null;
    const source = asset ? this._assetURL(assetId) : '';
    record.node.style.aspectRatio = asset?.width && asset?.height ? `${asset.width} / ${asset.height}` : '4 / 3';
    record.image.alt = asset?.name || '产品设计预览';
    if ((record.image.getAttribute('src') || '') !== source) {
      record.image.hidden = true;
      record.placeholder.hidden = false;
      record.placeholder.lastChild.textContent = record.placeholderText;
      if (source) record.image.src = source;
      else record.image.removeAttribute('src');
    }
    if (!source) {
      record.image.hidden = true;
      record.placeholder.hidden = false;
    } else if (record.image.complete && record.image.naturalWidth) {
      record.image.hidden = false;
      record.placeholder.hidden = true;
    }
  }

  _assetURL(id) {
    return `/api/projects/${encodeURIComponent(this.project.id)}/assets/${encodeURIComponent(id)}`;
  }

  _makeSlider(kind, onChange) {
    const viewport = el('div', `preview-slider preview-slider-${kind}`);
    const track = el('div', 'preview-slider-track');
    viewport.tabIndex = 0;
    viewport.setAttribute('aria-label', kind === 'gallery' ? '左右拖动查看商品图片' : kind === 'brand-story' ? '左右拖动查看品牌故事卡片' : '左右拖动查看 A+ 轮播');
    viewport.setAttribute('aria-roledescription', 'carousel');
    viewport.append(track);
    const record = { kind, viewport, track, items: [], index: 0, onChange, drag: null, suppressClickUntil: 0 };
    viewport.addEventListener('keydown', event => {
      if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
      event.preventDefault();
      this._setIndex(record, record.index + (event.key === 'ArrowLeft' ? -1 : 1), true);
    });
    viewport.addEventListener('pointerdown', event => {
      if (event.button !== 0 || record.items.length < 2) return;
      record.drag = { id: event.pointerId, x: event.clientX, y: event.clientY, scale: this._displayScale(), dx: 0, direction: null, time: performance.now() };
    });
    viewport.addEventListener('pointermove', event => {
      const drag = record.drag;
      if (!drag || event.pointerId !== drag.id) return;
      const dx = (event.clientX - drag.x) / drag.scale;
      const dy = (event.clientY - drag.y) / drag.scale;
      if (!drag.direction && Math.max(Math.abs(dx), Math.abs(dy)) > 7) {
        drag.direction = Math.abs(dx) > Math.abs(dy) ? 'x' : 'y';
        if (drag.direction === 'x') {
          viewport.setPointerCapture(event.pointerId);
          viewport.classList.add('is-dragging');
        }
      }
      if (drag.direction !== 'x') return;
      event.preventDefault();
      drag.dx = dx;
      const atEdge = (record.index === 0 && dx > 0) || (record.index === record.items.length - 1 && dx < 0);
      this._positionSlider(record, dx * (atEdge ? 0.24 : 1));
    });
    const finish = (event, cancelled = false) => {
      const drag = record.drag;
      if (!drag || event.pointerId !== drag.id) return;
      record.drag = null;
      viewport.classList.remove('is-dragging');
      if (viewport.hasPointerCapture(event.pointerId)) viewport.releasePointerCapture(event.pointerId);
      if (drag.direction === 'x') {
        record.suppressClickUntil = performance.now() + 350;
        const threshold = Math.min(70, viewport.clientWidth * 0.18);
        const fastSwipe = Math.abs(drag.dx) > 22 && performance.now() - drag.time < 280;
        const step = !cancelled && (Math.abs(drag.dx) > threshold || fastSwipe) ? (drag.dx < 0 ? 1 : -1) : 0;
        this._setIndex(record, record.index + step, step !== 0);
      }
    };
    viewport.addEventListener('pointerup', event => finish(event));
    viewport.addEventListener('pointercancel', event => finish(event, true));
    viewport.addEventListener('lostpointercapture', event => finish(event, true));
    viewport.addEventListener('pointerleave', event => {
      if (record.drag && record.drag.direction !== 'x') finish(event, true);
    });
    viewport.addEventListener('click', event => {
      if (performance.now() < record.suppressClickUntil) {
        event.preventDefault();
        event.stopImmediatePropagation();
      }
    }, true);
    return record;
  }

  _syncSlides(slider, items, targetFor) {
    const old = new Map(slider.items.map(item => [item.id, item]));
    const next = items.map((item, index) => {
      let entry = old.get(item.id);
      if (!entry) {
        const node = el('div', 'preview-slide');
        const media = this._makeMedia(targetFor(item), { selectable: slider.kind === 'brand-story', placeholderText: slider.kind === 'brand-story' ? '品牌故事卡片' : '图片预览' });
        const title = el('h4', 'preview-slide-title');
        const body = el('p', 'preview-slide-body');
        node.append(media.node, title, body);
        entry = { id: item.id, node, media, title, body };
      }
      entry.label = item.label || `Slide ${index + 1}`;
      entry.media.target = targetFor(item);
      this._setMedia(entry.media, item.assetId);
      text(entry.title, item.title);
      text(entry.body, item.body);
      entry.node.setAttribute('role', 'group');
      entry.node.setAttribute('aria-label', `${index + 1} / ${items.length}`);
      old.delete(item.id);
      return entry;
    });
    old.forEach(item => item.node.remove());
    slider.items = next;
    let sibling = slider.track.firstChild;
    for (const item of next) {
      if (item.node !== sibling) slider.track.insertBefore(item.node, sibling);
      sibling = item.node.nextSibling;
    }
    if (!slider.empty) {
      slider.empty = el('div', 'preview-slider-empty');
      slider.empty.append(el('span', 'preview-placeholder-icon', '▧'), el('span', '', slider.kind === 'gallery' ? '主副图预览' : slider.kind === 'brand-story' ? '品牌故事卡片将在这里显示' : '轮播图片预览'));
      slider.viewport.append(slider.empty);
    }
    slider.empty.hidden = Boolean(items.length);
    slider.track.hidden = !items.length;
  }

  _setIndex(slider, index, notify = false) {
    const oldIndex = slider.index;
    slider.index = clamp(Math.floor(Number(index) || 0), 0, Math.max(0, slider.items.length - 1));
    this._layoutSlider(slider);
    slider.items.forEach((item, itemIndex) => {
      item.node.setAttribute('aria-hidden', String(itemIndex !== slider.index));
      item.media.placeholder.tabIndex = itemIndex === slider.index ? 0 : -1;
      if (item.media.image.getAttribute('role') === 'button') item.media.image.tabIndex = itemIndex === slider.index ? 0 : -1;
    });
    if (slider.kind === 'gallery') {
      this.galleryIndex = slider.index;
      this._syncDots();
    }
    if (notify && oldIndex !== slider.index) slider.onChange();
  }

  _syncDots() {
    if (!this.galleryDots) return;
    if (this.galleryDots.children.length !== this.gallery.items.length) {
      this.galleryDots.replaceChildren(...this.gallery.items.map((item, index) => {
        const dot = el('button', 'preview-dot');
        dot.type = 'button';
        dot.setAttribute('aria-label', `查看第 ${index + 1} 张商品图片`);
        dot.addEventListener('click', () => this._setIndex(this.gallery, index, true));
        return dot;
      }));
    }
    [...this.galleryDots.children].forEach((node, index) => {
      node.classList.toggle('is-active', index === this.gallery.index);
      node.setAttribute('aria-pressed', String(index === this.gallery.index));
    });
    this.galleryDots.hidden = this.gallery.items.length < 2;
  }

  _syncTabs(record) {
    if (!record.tabs) return;
    const ids = new Set();
    let sibling = record.tabs.firstChild;
    record.slider.items.forEach((item, index) => {
      ids.add(item.id);
      let tab = record.tabNodes.get(item.id);
      if (!tab) {
        tab = el('button', 'preview-carousel-tab');
        tab.type = 'button';
        tab.setAttribute('role', 'tab');
        tab.addEventListener('click', () => {
          const nextIndex = record.slider.items.findIndex(slide => slide.id === item.id);
          this._setIndex(record.slider, nextIndex, true);
        });
        record.tabNodes.set(item.id, tab);
      }
      if (tab.textContent !== item.label) tab.textContent = item.label;
      tab.setAttribute('aria-selected', String(index === record.slider.index));
      tab.tabIndex = index === record.slider.index ? 0 : -1;
      tab.classList.toggle('is-active', index === record.slider.index);
      if (tab !== sibling) record.tabs.insertBefore(tab, sibling);
      sibling = tab.nextSibling;
    });
    record.tabNodes.forEach((tab, id) => {
      if (!ids.has(id)) {
        tab.remove();
        record.tabNodes.delete(id);
      }
    });
    record.tabs.hidden = !record.slider.items.length;
    const active = record.tabs.children[record.slider.index];
    if (active) {
      const left = active.offsetLeft;
      const right = left + active.offsetWidth;
      if (left < record.tabs.scrollLeft) record.tabs.scrollLeft = left;
      else if (right > record.tabs.scrollLeft + record.tabs.clientWidth) record.tabs.scrollLeft = right - record.tabs.clientWidth;
    }
  }

  _layoutSlider(slider) {
    const width = slider.viewport.clientWidth;
    if (!width) return;
    const slideWidth = slider.kind === 'gallery' ? Math.max(1, width - 40) : slider.kind === 'brand-story' ? width * 0.76 : width;
    for (const item of slider.items) item.node.style.width = `${slideWidth}px`;
    slider.slideWidth = slideWidth;
    const active = slider.items[slider.index];
    let height = active?.node.offsetHeight || (slider.kind === 'gallery' ? slideWidth : width * 0.75);
    if (slider.kind === 'gallery' && active) height = slideWidth;
    if (slider.kind === 'brand-story') height = Math.max(slideWidth * 1.25, ...slider.items.map(item => item.node.offsetHeight));
    const nextHeight = `${Math.ceil(height)}px`;
    if (slider.viewport.style.height !== nextHeight) slider.viewport.style.height = nextHeight;
    this._positionSlider(slider, slider.drag?.direction === 'x' ? slider.drag.dx : 0);
  }

  _positionSlider(slider, dragOffset = 0) {
    const gap = slider.kind === 'gallery' ? 8 : slider.kind === 'brand-story' ? 12 : 0;
    const inset = slider.kind === 'gallery' ? 20 : 0;
    const x = inset - slider.index * ((slider.slideWidth || 0) + gap) + dragOffset;
    slider.track.style.transform = `translate3d(${x}px, 0, 0)`;
  }

  _layoutAll() {
    this._layoutSlider(this.gallery);
    this.modules.forEach(record => {
      if (record.slider) {
        this._layoutSlider(record.slider);
        this._syncTabs(record);
      }
    });
    this._updateGuides();
  }

  _afterMediaLoad() {
    this._layoutAll();
    this._applyAnchor(this.preservation);
  }

  _captureAnchor() {
    if (!this.project) return null;
    const scrollTop = this.scroller.scrollTop;
    const origin = this.scroller.getBoundingClientRect().top;
    const scale = this._displayScale();
    const candidates = [...this.scroller.querySelectorAll('[data-preview-anchor]')].filter(node => node.getClientRects().length);
    let anchor = null;
    for (const node of candidates) {
      const top = (node.getBoundingClientRect().top - origin) / scale + scrollTop;
      if (top <= scrollTop + 2) anchor = { key: node.dataset.previewAnchor, offset: scrollTop - top, height: node.offsetHeight, scrollTop };
    }
    return anchor || { key: null, scrollTop };
  }

  _applyAnchor(anchor) {
    if (!anchor) return;
    const node = [...this.scroller.querySelectorAll('[data-preview-anchor]')].find(item => item.dataset.previewAnchor === anchor.key && item.getClientRects().length);
    let top = anchor.scrollTop;
    if (node) {
      const position = (node.getBoundingClientRect().top - this.scroller.getBoundingClientRect().top) / this._displayScale() + this.scroller.scrollTop;
      const relative = anchor.height ? (anchor.offset / anchor.height) * node.offsetHeight : anchor.offset;
      top = position + Math.max(0, relative || 0);
    }
    this._scrollTo(top);
  }

  _scrollTo(top) {
    this.programmaticUntil = performance.now() + 100;
    this.scroller.scrollTop = Math.max(0, Number(top) || 0);
  }

  _displayScale() {
    return this.root.clientWidth ? this.root.getBoundingClientRect().width / this.root.clientWidth || 1 : 1;
  }

  captureView() {
    const carouselIndices = {};
    this.modules.forEach((record, id) => {
      if (record.slider) carouselIndices[id] = record.slider.index;
    });
    return { galleryIndex: this.gallery.index, carouselIndices, scrollTop: Math.round(this.scroller.scrollTop) };
  }

  restoreView(view = {}) {
    this._setIndex(this.gallery, view.galleryIndex || 0, false);
    this.galleryIndex = this.gallery.index;
    this.modules.forEach((record, id) => {
      if (record.slider) {
        this._setIndex(record.slider, view.carouselIndices?.[id] || 0, false);
        this.carouselIndices[id] = record.slider.index;
        this._syncTabs(record);
      }
    });
    this._layoutAll();
    this._scrollTo(view.scrollTop || 0);
    this.preservation = this._captureAnchor();
  }

  jumpTo(target) {
    const node = target === 'aplus' ? this.aplus : this.gallerySection;
    this._clearTargetHighlight();
    this.preservation = null;
    const top = (node.getBoundingClientRect().top - this.scroller.getBoundingClientRect().top) / this._displayScale() + this.scroller.scrollTop;
    this._scrollTo(top);
    this._emitView();
    this.scroller.focus({ preventScroll: true });
  }

  revealTarget(target) {
    if (!target || !this.project) return false;
    let node;
    if (target.kind === 'gallery') {
      const index = this.gallery.items.findIndex(item => item.id === target.itemId);
      if (index < 0) return false;
      this._setIndex(this.gallery, index, false);
      node = this.gallerySection;
    } else if (target.kind === 'qa') {
      const position = (this.project.qa || []).filter(item => item.question?.trim() || item.answer?.trim()).findIndex(item => item.id === target.qaId);
      if (position < 0) {
        // A blank new entry is not drawn yet; show where it will appear.
        if (this.qaSection.hidden) return false;
        node = this.qaSection;
      } else {
        if (position >= 3 && !this.qaExpanded) {
          this.qaExpanded = true;
          this._renderQa();
        }
        node = this.qaList.querySelector(`[data-qa-id="${CSS.escape(target.qaId)}"]`) || this.qaSection;
      }
    } else {
      const record = this.modules.get(target.moduleId);
      if (!record) return false;
      if (target.kind === 'slide') {
        const index = record.slider?.items.findIndex(item => item.id === target.slideId) ?? -1;
        if (index < 0) return false;
        this._setIndex(record.slider, index, false);
        this.carouselIndices[record.id] = record.slider.index;
        this._syncTabs(record);
      }
      node = record.node;
    }
    this._clearTargetHighlight();
    clearTimeout(this.scrollTimer);
    this.preservation = null;
    this._layoutAll();
    const top = (node.getBoundingClientRect().top - this.scroller.getBoundingClientRect().top) / this._displayScale() + this.scroller.scrollTop;
    this._scrollTo(top);
    // Pending image loads and editor updates should retain the newly revealed position.
    this.preservation = this._captureAnchor();
    this.highlightedTarget = node;
    // Restart the two flashes even when the same card is clicked repeatedly.
    void node.offsetWidth;
    node.classList.add('is-preview-revealed');
    this.highlightTimer = setTimeout(() => this._clearTargetHighlight(), 650);
    this._emitView();
    return true;
  }

  _clearTargetHighlight() {
    clearTimeout(this.highlightTimer);
    this.highlightedTarget?.classList.remove('is-preview-revealed');
    this.highlightedTarget = null;
  }

  /* Environment: which Amazon surface and phone platform is simulated, plus viewing aids. */
  setEnvironment(env = {}) {
    this.env = { surface: 'app', platform: 'ios', dark: false, guides: true, touch: true, ...this.env, ...env };
    const { surface, platform, dark, guides, touch } = this.env;
    const classes = this.root.classList;
    classes.toggle('preview-surface-app', surface !== 'web');
    classes.toggle('preview-surface-web', surface === 'web');
    classes.toggle('preview-platform-ios', platform !== 'android');
    classes.toggle('preview-platform-android', platform === 'android');
    classes.toggle('preview-dark', Boolean(dark));
    classes.toggle('preview-guides', Boolean(guides));
    classes.toggle('preview-touch', Boolean(touch));
    if (!this.project) return;
    const anchor = this._captureAnchor();
    this._layoutAll();
    this._applyAnchor(anchor);
  }

  _renderQa() {
    const items = (this.project?.qa || []).filter(item => item.question?.trim() || item.answer?.trim());
    const visible = this.qaExpanded ? items : items.slice(0, 3);
    this.qaSection.hidden = !items.length;
    this.qaList.replaceChildren(...visible.map(item => {
      const node = el('div', 'preview-qa-item');
      node.dataset.qaId = item.id;
      const question = el('div', 'preview-qa-question');
      question.append(el('span', 'preview-qa-label', 'Question:'), el('span', 'preview-qa-text', item.question.trim() || '…'));
      const answer = el('div', 'preview-qa-answer');
      answer.append(el('span', 'preview-qa-label', 'Answer:'), el('span', 'preview-qa-text', item.answer.trim() || 'No answer yet.'));
      node.append(question, answer);
      const by = [item.author?.trim() && `By ${item.author.trim()}`, item.date?.trim() && `on ${item.date.trim()}`].filter(Boolean).join(' ');
      const votes = item.votes?.trim() ? `${item.votes.trim()} ${item.votes.trim() === '1' ? 'person' : 'people'} found this helpful` : '';
      if (by || votes) node.append(el('div', 'preview-qa-meta', [by, votes].filter(Boolean).join(' · ')));
      return node;
    }));
    this.qaMore.hidden = items.length <= 3;
    this.qaMore.textContent = this.qaExpanded ? 'See fewer questions' : `See more answered questions (${items.length - 3})`;
  }

  _renderPrice(price) {
    const match = price.replace(/[$\s,]/g, '').match(/^(\d+)(?:\.(\d{1,2}))?$/);
    this.price.hidden = false;
    if (!match) {
      this.price.textContent = price;
      return;
    }
    this.price.replaceChildren(
      el('span', 'preview-price-symbol', '$'),
      el('span', 'preview-price-whole', Number(match[1]).toLocaleString('en-US')),
      el('span', 'preview-price-fraction', (match[2] || '00').padEnd(2, '0')),
    );
  }

  /* First-screen line and "how many screens" badges, measured in this phone's visible height. */
  _updateGuides() {
    if (!this.env?.guides || !this.scroller) return;
    const screen = this.scroller.clientHeight;
    if (!screen) return;
    this.foldLine.style.top = `${screen}px`;
    this.modules.forEach(record => {
      record.badge.textContent = `≈ ${(record.node.offsetHeight / screen).toFixed(1)} 屏`;
    });
    const hasModules = this.modules.size > 0;
    this.aplusBadge.hidden = !hasModules;
    if (hasModules) {
      const top = this.aplus.offsetTop;
      this.aplusBadge.textContent = `图文从第 ${Math.floor(top / screen) + 1} 屏开始 · 共 ≈ ${(this.aplus.offsetHeight / screen).toFixed(1)} 屏`;
    }
  }

  /* Finger-style scrolling: drag the page with the mouse, with momentum and edge bounce. */
  _bindTouchScroll() {
    const scroller = this.scroller;
    let drag = null;
    let frame = 0;
    let suppressClickUntil = 0;
    const stopMomentum = () => { cancelAnimationFrame(frame); frame = 0; };
    const maxScroll = () => Math.max(0, scroller.scrollHeight - scroller.clientHeight);
    const setStretch = (value, animate = false) => {
      scroller.style.transition = animate ? 'transform 320ms cubic-bezier(.2,.8,.2,1)' : 'none';
      scroller.style.transform = value ? `translate3d(0, ${value}px, 0)` : '';
    };
    // Resistance grows the further the page is pulled past its edge.
    const rubber = distance => Math.sign(distance) * (1 - 1 / (Math.abs(distance) / 320 + 1)) * 160;
    scroller.addEventListener('wheel', stopMomentum, { passive: true });
    scroller.addEventListener('pointerdown', event => {
      stopMomentum();
      if (!this.env?.touch || event.pointerType !== 'mouse' || event.button !== 0) return;
      if (event.target.closest('video, input, textarea, select, .preview-carousel-tabs')) return;
      drag = { id: event.pointerId, x: event.clientX, y: event.clientY, top: scroller.scrollTop, direction: null, scale: this._displayScale(), samples: [{ t: performance.now(), y: event.clientY }], stretch: 0 };
    });
    scroller.addEventListener('pointermove', event => {
      if (!drag || event.pointerId !== drag.id) return;
      const dx = (event.clientX - drag.x) / drag.scale;
      const dy = (event.clientY - drag.y) / drag.scale;
      if (!drag.direction && Math.max(Math.abs(dx), Math.abs(dy)) > 7) {
        drag.direction = Math.abs(dy) > Math.abs(dx) ? 'y' : 'x';
        if (drag.direction === 'y') {
          scroller.setPointerCapture(event.pointerId);
          this.root.classList.add('is-panning');
        }
      }
      if (drag.direction !== 'y') return;
      event.preventDefault();
      const wanted = drag.top - dy;
      const limit = maxScroll();
      const clamped = Math.max(0, Math.min(limit, wanted));
      scroller.scrollTop = clamped;
      drag.stretch = wanted < 0 ? rubber(-wanted) : wanted > limit ? -rubber(wanted - limit) : 0;
      setStretch(drag.stretch);
      const now = performance.now();
      drag.samples.push({ t: now, y: event.clientY });
      while (drag.samples.length > 2 && now - drag.samples[0].t > 100) drag.samples.shift();
    });
    const finish = event => {
      if (!drag || event.pointerId !== drag.id) return;
      const done = drag;
      drag = null;
      this.root.classList.remove('is-panning');
      if (scroller.hasPointerCapture(event.pointerId)) scroller.releasePointerCapture(event.pointerId);
      if (done.direction !== 'y') return;
      suppressClickUntil = performance.now() + 350;
      if (done.stretch) {
        setStretch(0, true);
        return;
      }
      const first = done.samples[0];
      const last = done.samples[done.samples.length - 1];
      const elapsed = last.t - first.t;
      if (elapsed <= 0 || performance.now() - last.t > 80) return;
      let velocity = -((last.y - first.y) / done.scale) / elapsed; // px per ms, page direction
      let previous = performance.now();
      const step = now => {
        const dt = Math.min(32, now - previous);
        previous = now;
        const before = scroller.scrollTop;
        scroller.scrollTop = before + velocity * dt;
        velocity *= Math.pow(0.9965, dt);
        const atEdge = scroller.scrollTop === before && Math.abs(velocity * dt) >= 1;
        if (Math.abs(velocity) < 0.02 || atEdge) {
          frame = 0;
          if (atEdge) {
            setStretch(-Math.sign(velocity) * Math.min(40, Math.abs(velocity) * 30));
            requestAnimationFrame(() => setStretch(0, true));
          }
          return;
        }
        frame = requestAnimationFrame(step);
      };
      frame = requestAnimationFrame(step);
    };
    scroller.addEventListener('pointerup', finish);
    scroller.addEventListener('pointercancel', finish);
    scroller.addEventListener('lostpointercapture', finish);
    scroller.addEventListener('click', event => {
      if (performance.now() < suppressClickUntil) {
        event.preventDefault();
        event.stopImmediatePropagation();
      }
    }, true);
    scroller.addEventListener('transitionend', () => { scroller.style.transition = ''; });
  }

  /* Full-screen product image viewer: swipe between images, double-click or wheel to zoom. */
  _buildViewer() {
    this.viewer = el('div', 'preview-viewer');
    this.viewer.hidden = true;
    this.viewer.tabIndex = -1;
    this.viewer.setAttribute('role', 'dialog');
    this.viewer.setAttribute('aria-label', '商品大图');
    const bar = el('div', 'preview-viewer-bar');
    const close = el('button', 'preview-viewer-close');
    close.type = 'button';
    close.setAttribute('aria-label', '关闭大图');
    close.append(icon('close'));
    this.viewerCount = el('span', 'preview-viewer-count');
    bar.append(close, this.viewerCount, el('span', 'preview-viewer-hint', '双击 / 滚轮放大'));
    this.viewerStage = el('div', 'preview-viewer-stage');
    this.viewerImage = el('img', 'preview-viewer-image');
    this.viewerImage.draggable = false;
    this.viewerImage.alt = '';
    this.viewerStage.append(this.viewerImage);
    this.viewerThumbs = el('div', 'preview-viewer-thumbs');
    this.viewer.append(bar, this.viewerStage, this.viewerThumbs);
    this.viewerState = { index: 0, zoom: 1, x: 0, y: 0, items: [], drag: null };
    close.addEventListener('click', () => this._closeViewer());
    this.viewer.addEventListener('keydown', event => {
      if (event.key === 'Escape') this._closeViewer();
      else if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') this._viewerGo(this.viewerState.index + (event.key === 'ArrowLeft' ? -1 : 1));
      else return;
      event.preventDefault();
      event.stopPropagation();
    });
    const stage = this.viewerStage;
    stage.addEventListener('pointerdown', event => {
      if (event.button !== 0) return;
      const s = this.viewerState;
      stage.setPointerCapture(event.pointerId);
      s.drag = { id: event.pointerId, x: event.clientX, y: event.clientY, startX: s.x, startY: s.y, scale: this._displayScale(), dx: 0 };
    });
    stage.addEventListener('pointermove', event => {
      const s = this.viewerState;
      if (!s.drag || event.pointerId !== s.drag.id) return;
      const dx = (event.clientX - s.drag.x) / s.drag.scale;
      const dy = (event.clientY - s.drag.y) / s.drag.scale;
      if (s.zoom > 1) {
        s.x = s.drag.startX + dx;
        s.y = s.drag.startY + dy;
        this._viewerApply();
      } else {
        s.drag.dx = dx;
        this._viewerApply(dx);
      }
    });
    const end = event => {
      const s = this.viewerState;
      if (!s.drag || event.pointerId !== s.drag.id) return;
      const { dx } = s.drag;
      s.drag = null;
      if (s.zoom === 1 && Math.abs(dx) > 50) this._viewerGo(s.index + (dx < 0 ? 1 : -1));
      else this._viewerApply();
    };
    stage.addEventListener('pointerup', end);
    stage.addEventListener('pointercancel', end);
    stage.addEventListener('dblclick', event => {
      const s = this.viewerState;
      if (s.zoom > 1) {
        Object.assign(s, { zoom: 1, x: 0, y: 0 });
      } else {
        const rect = stage.getBoundingClientRect();
        const scale = this._displayScale();
        s.zoom = 2.5;
        s.x = -((event.clientX - rect.left - rect.width / 2) / scale) * (s.zoom - 1);
        s.y = -((event.clientY - rect.top - rect.height / 2) / scale) * (s.zoom - 1);
      }
      this._viewerApply();
    });
    stage.addEventListener('wheel', event => {
      event.preventDefault();
      const s = this.viewerState;
      const next = clamp(s.zoom * (event.deltaY < 0 ? 1.15 : 1 / 1.15), 1, 4);
      s.x *= (next - 1) / Math.max(0.0001, s.zoom - 1) || 0;
      s.y *= (next - 1) / Math.max(0.0001, s.zoom - 1) || 0;
      s.zoom = next < 1.02 ? 1 : next;
      this._viewerApply();
    }, { passive: false });
  }

  _viewerApply(dragX = 0) {
    const s = this.viewerState;
    const maxX = ((s.zoom - 1) * this.viewerStage.clientWidth) / 2;
    const maxY = ((s.zoom - 1) * this.viewerStage.clientHeight) / 2;
    s.x = clamp(s.x, -maxX, maxX);
    s.y = clamp(s.y, -maxY, maxY);
    this.viewerImage.classList.toggle('is-dragging', Boolean(s.drag));
    this.viewerImage.style.transform = `translate3d(${s.x + dragX}px, ${s.y}px, 0) scale(${s.zoom})`;
    this.viewerStage.classList.toggle('is-zoomed', s.zoom > 1);
  }

  _openViewer(galleryIndex) {
    const items = this.gallery.items.map((item, index) => ({ item, index })).filter(({ item }) => item.media.assetId && this.project?.assets?.[item.media.assetId]);
    if (!items.length) return;
    const s = this.viewerState;
    s.items = items;
    this.viewerThumbs.replaceChildren(...items.map(({ item }, position) => {
      const thumb = el('button', 'preview-viewer-thumb');
      thumb.type = 'button';
      thumb.setAttribute('aria-label', `查看第 ${position + 1} 张`);
      const image = el('img');
      image.src = this._assetURL(item.media.assetId);
      image.alt = '';
      image.draggable = false;
      thumb.append(image);
      thumb.addEventListener('click', () => this._viewerGo(position));
      return thumb;
    }));
    this.viewer.hidden = false;
    this._viewerGo(Math.max(0, items.findIndex(entry => entry.index === galleryIndex)));
    this.viewer.focus({ preventScroll: true });
  }

  _viewerGo(position) {
    const s = this.viewerState;
    if (!s.items.length) return;
    s.index = clamp(position, 0, s.items.length - 1);
    Object.assign(s, { zoom: 1, x: 0, y: 0, drag: null });
    const { item } = s.items[s.index];
    const source = this._assetURL(item.media.assetId);
    if (this.viewerImage.getAttribute('src') !== source) this.viewerImage.src = source;
    this.viewerCount.textContent = `${s.index + 1} / ${s.items.length}`;
    [...this.viewerThumbs.children].forEach((thumb, index) => thumb.classList.toggle('is-active', index === s.index));
    const active = this.viewerThumbs.children[s.index];
    if (active) this.viewerThumbs.scrollLeft = active.offsetLeft - (this.viewerThumbs.clientWidth - active.offsetWidth) / 2;
    this._viewerApply();
  }

  _closeViewer(syncGallery = true) {
    if (!this.viewer || this.viewer.hidden) return;
    this.viewer.hidden = true;
    const s = this.viewerState;
    // Return to the image last viewed, as the app does.
    if (syncGallery && s.items[s.index]) this._setIndex(this.gallery, s.items[s.index].index, true);
    if (syncGallery) this.scroller.focus({ preventScroll: true });
  }

  _emitView() {
    this.callbacks.onViewChange?.(this.captureView());
  }

  destroy() {
    clearTimeout(this.scrollTimer);
    this._clearTargetHighlight();
    this.resizeObserver.disconnect();
    this.modules.forEach(record => record.video?.pause());
  }
}
