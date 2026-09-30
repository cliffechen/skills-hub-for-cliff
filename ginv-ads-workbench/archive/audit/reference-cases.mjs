// Read-only audit: execute the calculator functions extracted from the captured source.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const html = fs.readFileSync(path.join(root, 'archive/source/app.html'), 'utf8');
const start = html.indexOf('function num(id)');
const end = html.indexOf('// ---------- 访客', start);
assert(start >= 0 && end > start, 'Original calculator source is missing');
const source = html.slice(start, end);

const cases = [
  { name: 'ACoS-default', fn: 'calBeAc', output: 't1o', inputs: {t1p: '29.99', t1m: '9'}, expected: '可承受最高 ACoS ≈ 30.0%（即每个点击的保本 EV 上限占比）' },
  { name: 'ACoS-custom', fn: 'calBeAc', output: 't1o', inputs: {t1p: '40', t1m: '12'}, expected: '可承受最高 ACoS ≈ 30.0%（即每个点击的保本 EV 上限占比）' },
  { name: 'ACoS-zero-price', fn: 'calBeAc', output: 't1o', inputs: {t1p: '0', t1m: '9'}, expected: '可承受最高 ACoS ≈ 0.0%' },
  { name: 'ACoS-empty-price', fn: 'calBeAc', output: 't1o', inputs: {t1p: '', t1m: '9'}, expected: '可承受最高 ACoS ≈ 0.0%' },
  { name: 'ACoS-negative-margin', fn: 'calBeAc', output: 't1o', inputs: {t1p: '30', t1m: '-9'}, expected: '可承受最高 ACoS ≈ -30.0%' },
  { name: 'ACoS-over100', fn: 'calBeAc', output: 't1o', inputs: {t1p: '30', t1m: '45'}, expected: '可承受最高 ACoS ≈ 150.0%（即每个点击的保本 EV 上限占比）' },
  { name: 'EV-default', fn: 'calEv', output: 't0o', inputs: {t0c: '10', t0m: '9', t0p: '1'}, expected: '单点击期望价值 EV ≈ $0.90；当前 CPC $1.00 → 负期望，每点击约亏 $0.10，应降出价/换词/否定' },
  { name: 'EV-positive', fn: 'calEv', output: 't0o', inputs: {t0c: '20', t0m: '10', t0p: '1.25'}, expected: '单点击期望价值 EV ≈ $2.00；当前 CPC $1.25 → 正期望，值得投，每点击可赚约 $0.75' },
  { name: 'EV-equal', fn: 'calEv', output: 't0o', inputs: {t0c: '10', t0m: '9', t0p: '0.9'}, expected: '单点击期望价值 EV ≈ $0.90；当前 CPC $0.90 → 正期望，值得投，每点击可赚约 $0.00' },
  { name: 'EV-empty-cpc', fn: 'calEv', output: 't0o', inputs: {t0c: '10', t0m: '9', t0p: ''}, expected: '单点击期望价值 EV ≈ $0.90；当前 CPC $0.00 → 正期望，值得投，每点击可赚约 $0.90' },
  { name: 'EV-zero-margin', fn: 'calEv', output: 't0o', inputs: {t0c: '10', t0m: '0', t0p: '1'}, expected: '请填写参数' },
  { name: 'EV-zero-conversion', fn: 'calEv', output: 't0o', inputs: {t0c: '0', t0m: '9', t0p: '1'}, expected: '请填写参数' },
  { name: 'EV-negative-conversion', fn: 'calEv', output: 't0o', inputs: {t0c: '-10', t0m: '9', t0p: '1'}, expected: '单点击期望价值 EV ≈ $-0.90；当前 CPC $1.00 → 负期望，每点击约亏 $1.90，应降出价/换词/否定' },
  { name: 'CPC-default', fn: 'calCpc', output: 't2o', inputs: {t2a: '25', t2c: '10', t2p: '30'}, expected: '保本 CPC ≈ $0.75；若目标 ACoS 设满即为盈亏平衡，实际出价应 ≤ 该值' },
  { name: 'CPC-custom', fn: 'calCpc', output: 't2o', inputs: {t2a: '30', t2c: '12.5', t2p: '40'}, expected: '保本 CPC ≈ $1.50；若目标 ACoS 设满即为盈亏平衡，实际出价应 ≤ 该值' },
  { name: 'CPC-zero-target', fn: 'calCpc', output: 't2o', inputs: {t2a: '0', t2c: '10', t2p: '30'}, expected: '请填写完整参数' },
  { name: 'CPC-two-negatives', fn: 'calCpc', output: 't2o', inputs: {t2a: '-25', t2c: '-10', t2p: '30'}, expected: '保本 CPC ≈ $0.75；若目标 ACoS 设满即为盈亏平衡，实际出价应 ≤ 该值' },
  { name: 'Budget-default', fn: 'calBud', output: 't3o', inputs: {t3c: '10', t3p: '1'}, expected: '至少 10 次点击出 1 单 → 保底预算 ≈ $10；若 CPC 超过单点 EV 则跑再多也是亏，优先降出价' },
  { name: 'Budget-ceil-and-round', fn: 'calBud', output: 't3o', inputs: {t3c: '7', t3p: '0.9'}, expected: '至少 15 次点击出 1 单 → 保底预算 ≈ $14；若 CPC 超过单点 EV 则跑再多也是亏，优先降出价' },
  { name: 'Budget-zero-cpc', fn: 'calBud', output: 't3o', inputs: {t3c: '10', t3p: '0'}, expected: '请填写参数' },
  { name: 'Budget-negative-conversion', fn: 'calBud', output: 't3o', inputs: {t3c: '-10', t3p: '1'}, expected: '至少 -10 次点击出 1 单 → 保底预算 ≈ $-10' },
  { name: 'Budget-sub-dollar-rounded-zero', fn: 'calBud', output: 't3o', inputs: {t3c: '100', t3p: '0.3'}, expected: '至少 1 次点击出 1 单 → 保底预算 ≈ $0；若 CPC 超过单点 EV 则跑再多也是亏，优先降出价' },
  { name: 'High-click-default', fn: 'calHc', output: 't4o', inputs: {t4c: '10'}, expected: '平均 10.0 点击出 1 单；超过 15 点击仍不出单 → 考虑降价 / 换词' },
  { name: 'High-click-rounding', fn: 'calHc', output: 't4o', inputs: {t4c: '12'}, expected: '平均 8.3 点击出 1 单；超过 13 点击仍不出单 → 考虑降价 / 换词' },
  { name: 'High-click-zero', fn: 'calHc', output: 't4o', inputs: {t4c: '0'}, expected: '请填写参数' },
  { name: 'High-click-negative', fn: 'calHc', output: 't4o', inputs: {t4c: '-10'}, expected: '平均 -10.0 点击出 1 单；超过 -15 点击仍不出单 → 考虑降价 / 换词' },
  { name: 'High-click-over100', fn: 'calHc', output: 't4o', inputs: {t4c: '200'}, expected: '平均 0.5 点击出 1 单；超过 1 点击仍不出单 → 考虑降价 / 换词' },
];

const results = cases.map(test => {
  const elements = {};
  for (const [id, value] of Object.entries(test.inputs)) elements[id] = { value, innerHTML: '' };
  elements[test.output] = { value: '', innerHTML: '' };
  const context = vm.createContext({document: {getElementById: id => elements[id]}});
  vm.runInContext(source, context, { timeout: 1000 });
  vm.runInContext(`${test.fn}()`, context, { timeout: 1000 });
  const actual = elements[test.output].innerHTML;
  assert.equal(actual, test.expected, test.name);
  return { name: test.name, function: test.fn, inputs: test.inputs, actual, passed: true };
});

const destination = path.join(root, 'archive/audit/tool-source-cases.json');
fs.writeFileSync(destination, JSON.stringify({source: 'archive/source/app.html', verifiedCases: results.length, results}, null, 2) + '\n');
console.log(`${results.length} original-source cases passed. Evidence: ${destination}`);
