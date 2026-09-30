/** Original source formulas are retained in data/source-content.json. */
export const toolDefinitions = {
  t1: {
    formula: '盈亏平衡 ACoS = 单件毛利 ÷ 售价 × 100%',
    help: { t1p: '产品的单件销售价格。', t1m: '扣除产品及销售成本后、广告费之前的毛利。' },
    note: '这是单件订单的广告盈亏平衡线。单件毛利应扣除与该订单有关的成本，并与售价使用相同口径。',
    conceptIds: ['acos', 'acos-19'],
  },
  t0: {
    formula: '单点击 EV = 转化率 ÷ 100 × 单件毛利\n点击期望利润 = EV − 当前 CPC',
    help: { t0c: '以百分数填写，例如 10 表示 10%。', t0m: '扣除产品及销售成本后、广告费之前的毛利。', t0p: '使用实际平均点击成本，不等同于设置的基础出价。' },
    note: 'EV 是按平均转化率估算的单次点击毛利，扣除 CPC 后才是期望利润；实际效果会波动。',
    conceptIds: ['ev', 'cpc', 'cvr'],
  },
  t2: {
    formula: '允许 CPC = 目标 ACoS ÷ 100 × 转化率 ÷ 100 × 客单价',
    help: { t2a: '以百分数填写，例如 25 表示 25%。', t2c: '使用对应广告的平均转化率。', t2p: '广告带来的平均每单销售额。' },
    note: '原站名称为“反推保本 CPC”。此公式求的是目标 ACoS 对应的允许 CPC；只有目标 ACoS 等于毛利率时，才表示盈亏平衡。基础出价与实际 CPC 也可能不同。',
    conceptIds: ['acos', 'cpc', 'cvr'],
  },
  t3: {
    formula: '估算点击数 = 向上取整(1 ÷ (转化率 ÷ 100))\n日预算参考 = 估算点击数 × CPC',
    help: { t3c: '以百分数填写，例如 10 表示 10%。', t3p: '沿用原站输入；建议使用实际平均 CPC 估算。' },
    note: '原站名称为“保底日预算”。这是按平均转化率估算一单的预算参考，不保证每日必定出单。原站结果按整数美元取整，工作台同时保留两位小数。',
    conceptIds: ['cvr', 'cpc', 'ev'],
  },
  t4: {
    formula: '平均出单点击数 = 1 ÷ (平均转化率 ÷ 100)\n原站检查阈值 = 平均出单点击数 × 1.5（四舍五入）',
    help: { t4c: '使用相关广告或关键词的平均转化率。' },
    note: '原站说明给出 1.5–2 倍区间，计算按钮采用 1.5 倍。本工作台保留该计算方式。阈值是复查提示，仍需结合相关性、归因延迟与实际样本判断。',
    conceptIds: ['cvr', 'cpa'],
  },
};

function number(values, key, name, { positive = false, percent = false, signed = false } = {}) {
  const raw = values[key];
  if (raw === undefined || raw === null || String(raw).trim() === '') throw new Error(`请填写${name}。`);
  const value = Number(raw);
  if (!Number.isFinite(value)) throw new Error(`${name}需要是有效数字。`);
  if (positive ? value <= 0 : !signed && value < 0) throw new Error(`${name}需要${positive ? '大于 0' : '大于或等于 0'}。`);
  if (percent && value > 100) throw new Error(`${name}不能超过 100%。`);
  return value;
}
const metric = (label, value, unit = '', precision = 2, note = '') => ({ label, value, unit, precision, note });

export function calculateTool(id, values) {
  let result;
  if (id === 't1') {
    const price = number(values, 't1p', '售价', { positive: true });
    const margin = number(values, 't1m', '单件毛利', { signed: true });
    if (margin > price) throw new Error('单件毛利不能超过售价，请检查成本口径。');
    const acos = margin / price * 100;
    result = { metrics: [metric('盈亏平衡 ACoS', acos, '%', 1), metric('单件毛利', margin, 'USD', 2)], summary: margin <= 0 ? '毛利不为正，当前成本下没有正向广告费空间。' : '广告 ACoS 低于这条线时，才有单件广告利润空间。' };
  } else if (id === 't0') {
    const cvr = number(values, 't0c', '转化率', { percent: true }) / 100;
    const margin = number(values, 't0m', '单件毛利', { signed: true });
    const cpc = number(values, 't0p', '当前 CPC');
    const ev = cvr * margin;
    const difference = ev - cpc;
    const tolerance = Number.EPSILON * Math.max(1, Math.abs(ev), Math.abs(cpc)) * 8;
    const net = Math.abs(difference) <= tolerance ? 0 : difference;
    result = { metrics: [metric('单点击期望价值 EV', ev, 'USD'), metric('点击期望利润', net, 'USD'), metric('当前 CPC', cpc, 'USD')], summary: net > 0 ? '正期望：平均每次点击的预计毛利高于点击成本。' : net < 0 ? '负期望：可以检查出价、投放相关性和转化率。' : '盈亏平衡：预计毛利与点击成本相等。' };
  } else if (id === 't2') {
    const acos = number(values, 't2a', '目标 ACoS') / 100;
    const cvr = number(values, 't2c', '转化率', { percent: true }) / 100;
    const price = number(values, 't2p', '客单价', { positive: true });
    const cpc = acos * cvr * price;
    result = { metrics: [metric('目标 ACoS 对应 CPC', cpc, 'USD'), metric('目标 ACoS', acos * 100, '%', 1)], summary: '要达到输入的 ACoS 目标，实际平均 CPC 应不高于此值。' };
  } else if (id === 't3') {
    const cvr = number(values, 't3c', '转化率', { positive: true, percent: true }) / 100;
    const cpc = number(values, 't3p', '单次出价 CPC');
    const clicks = Math.ceil(1 / cvr);
    const budget = clicks * cpc;
    result = { metrics: [metric('日预算参考', budget, 'USD'), metric('估算一单所需点击数', clicks, '次', 0), metric('原站取整显示', budget, 'USD', 0)], summary: '按当前平均转化率，预留这些点击的费用作为预算参考。' };
  } else if (id === 't4') {
    const cvr = number(values, 't4c', '平均转化率', { positive: true, percent: true }) / 100;
    const average = 1 / cvr;
    result = { metrics: [metric('原站检查阈值', Number((average * 1.5).toFixed(0)), '次点击', 0), metric('平均出单点击数', average, '次', 1)], summary: '超过阈值仍无订单时，检查相关性、实际转化率和归因延迟，再决定是否调整。' };
  } else {
    throw new Error('找不到此计算工具。');
  }
  if (result.metrics.some(item => !Number.isFinite(item.value))) throw new Error('参数过大或过小，计算结果超出范围，请调整后重试。');
  return { ...result, note: toolDefinitions[id].note };
}
