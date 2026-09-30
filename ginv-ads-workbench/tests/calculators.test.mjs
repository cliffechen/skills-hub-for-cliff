import test from 'node:test';
import assert from 'node:assert/strict';
import { calculateTool } from '../workbench/dist/calculators.js';
const value = (id, input, index = 0) => calculateTool(id, input).metrics[index].value;
const cases = [
  ['ACoS默认', 't1', {t1p:29.99,t1m:9}, 30.010003334444814],
  ['ACoS售价40毛利12', 't1', {t1p:40,t1m:12}, 30],
  ['EV默认', 't0', {t0c:10,t0m:9,t0p:1}, .9],
  ['EV正期望', 't0', {t0c:20,t0m:10,t0p:1.25}, .75, 1],
  ['CPC默认', 't2', {t2a:25,t2c:10,t2p:30}, .75],
  ['CPC小数', 't2', {t2a:30,t2c:12.5,t2p:40}, 1.5],
  ['预算默认', 't3', {t3c:10,t3p:1}, 10],
  ['预算先上取整再乘CPC', 't3', {t3c:7,t3p:.9}, 13.5],
  ['预算保留小额美元', 't3', {t3c:100,t3p:.3}, .3],
  ['高点击默认', 't4', {t4c:10}, 15],
  ['高点击原站取整', 't4', {t4c:12}, 13],
];
for (const [name,id,input,expected,index] of cases) test(name, () => assert.ok(Math.abs(value(id,input,index)-expected) < 1e-12));
test('数学相等的EV避免浮点误差被标为盈亏', () => {
  for (const input of [{t0c:10,t0m:7,t0p:.7},{t0c:30,t0m:3,t0p:.9},{t0c:10,t0m:9,t0p:.9}]) {
    const result=calculateTool('t0',input); assert.equal(result.metrics[1].value,0); assert.match(result.summary,/盈亏平衡/);
  }
});
test('真实微小亏损不会因美元显示精度被忽略', () => {
  const result=calculateTool('t0',{t0c:10,t0m:9,t0p:.9001}); assert.ok(result.metrics[1].value<0); assert.match(result.summary,/负期望/);
});
test('空必填值与非有限输入必须报错', () => {
  for (const input of ['', ' ', null, undefined, NaN, Infinity]) assert.throws(()=>calculateTool('t1',{t1p:input,t1m:9}));
});
test('CVR范围与零分母检查', () => {
  for (const input of [-1,0,101]) { assert.throws(()=>calculateTool('t3',{t3c:input,t3p:1})); assert.throws(()=>calculateTool('t4',{t4c:input})); }
  assert.throws(()=>calculateTool('t1',{t1p:0,t1m:9}));
});
test('负CPC与超出范围的数值不产生误导结果', () => {
  assert.throws(()=>calculateTool('t0',{t0c:10,t0m:9,t0p:-1}));
  assert.throws(()=>calculateTool('t2',{t2a:1e308,t2c:100,t2p:1e308}));
});
test('没有广告利润空间的毛利仍可计算并明确解释', () => {
  assert.match(calculateTool('t1',{t1p:30,t1m:0}).summary,/没有/);
  assert.match(calculateTool('t1',{t1p:30,t1m:-2}).summary,/没有/);
});
