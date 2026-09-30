import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {calculateTool} from '../../workbench/dist/calculators.js';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const results = [];
function check(name, action) {
  try { action(); results.push({name, passed: true}); }
  catch (error) { results.push({name, passed: false, message: error.message}); }
}
function assert(condition, message) { if (!condition) throw new Error(message); }
function normal(name, id, inputs, expected, display) {
  check(name, () => {
    const result = calculateTool(id, inputs);
    assert(result.metrics.length === expected.length, 'Unexpected metric count');
    result.metrics.forEach((metric, index) => {
      assert(Number.isFinite(metric.value), `Nonfinite ${metric.label}`);
      assert(Math.abs(metric.value - expected[index]) <= 1e-12 * Math.max(1, Math.abs(expected[index])), `Incorrect ${metric.label}: ${metric.value}, expected ${expected[index]}`);
      if (display) assert(metric.value.toFixed(metric.precision) === display[index], `Incorrect rounding ${metric.label}: ${metric.value.toFixed(metric.precision)}, expected ${display[index]}`);
    });
  });
}
function rejected(name, id, inputs) {
  check(name, () => {
    let error;
    try { calculateTool(id, inputs); } catch (issue) { error = issue; }
    assert(error instanceof Error && error.message.length > 0, 'Invalid values accepted');
  });
}
const defaults = {
  t1: {t1p: '29.99', t1m: '9'},
  t0: {t0c: '10', t0m: '9', t0p: '1'},
  t2: {t2a: '25', t2c: '10', t2p: '30'},
  t3: {t3c: '10', t3p: '1'},
  t4: {t4c: '10'},
};

normal('ACoS-default', 't1', defaults.t1, [9/29.99*100,9], ['30.0','9.00']);
normal('ACoS-custom', 't1', {t1p:40,t1m:12}, [30,12], ['30.0','12.00']);
normal('ACoS-zero-margin', 't1', {t1p:40,t1m:0}, [0,0], ['0.0','0.00']);
normal('ACoS-negative-margin', 't1', {t1p:30,t1m:-9}, [-30,-9], ['-30.0','-9.00']);
normal('EV-default', 't0', defaults.t0, [.9,-.1,1], ['0.90','-0.10','1.00']);
normal('EV-positive', 't0', {t0c:20,t0m:10,t0p:1.25}, [2,.75,1.25], ['2.00','0.75','1.25']);
normal('EV-equal-default-formula', 't0', {t0c:10,t0m:9,t0p:.9}, [.9,0,.9], ['0.90','0.00','0.90']);
normal('EV-zero-conversion-valid', 't0', {t0c:0,t0m:9,t0p:1}, [0,-1,1], ['0.00','-1.00','1.00']);
normal('EV-zero-margin-valid', 't0', {t0c:10,t0m:0,t0p:1}, [0,-1,1], ['0.00','-1.00','1.00']);
normal('EV-negative-margin-valid', 't0', {t0c:10,t0m:-9,t0p:1}, [-.9,-1.9,1], ['-0.90','-1.90','1.00']);
normal('CPC-default', 't2', defaults.t2, [.75,25], ['0.75','25.0']);
normal('CPC-decimal-input', 't2', {t2a:30,t2c:12.5,t2p:40}, [1.5,30], ['1.50','30.0']);
normal('CPC-zero-conversion-valid', 't2', {t2a:25,t2c:0,t2p:30}, [0,25], ['0.00','25.0']);
normal('CPC-zero-target-valid', 't2', {t2a:0,t2c:10,t2p:30}, [0,0], ['0.00','0.0']);
normal('CPC-over100-target-allowed', 't2', {t2a:150,t2c:10,t2p:30}, [4.5,150], ['4.50','150.0']);
normal('Budget-default', 't3', defaults.t3, [10,10,10], ['10.00','10','10']);
normal('Budget-ceil-and-precision', 't3', {t3c:7,t3p:.9}, [13.5,15,13.5], ['13.50','15','14']);
normal('Budget-zero-cpc-valid', 't3', {t3c:10,t3p:0}, [0,10,0], ['0.00','10','0']);
normal('Budget-sub-dollar', 't3', {t3c:100,t3p:.3}, [.3,1,.3], ['0.30','1','0']);
normal('High-click-default', 't4', defaults.t4, [15,10], ['15','10.0']);
normal('High-click-source-rounding', 't4', {t4c:12}, [13,100/12], ['13','8.3']);
normal('High-click-100-percent', 't4', {t4c:100}, [2,1], ['2','1.0']);

for (const [id, values] of Object.entries(defaults)) {
  for (const key of Object.keys(values)) {
    rejected(`${id}-empty-${key}`, id, {...values,[key]:''});
    rejected(`${id}-whitespace-${key}`, id, {...values,[key]:' '});
    rejected(`${id}-missing-${key}`, id, {...values,[key]:undefined});
    rejected(`${id}-nan-${key}`, id, {...values,[key]:'NaN'});
    rejected(`${id}-infinity-${key}`, id, {...values,[key]:'Infinity'});
  }
}
rejected('ACoS-zero-price', 't1', {t1p:0,t1m:9});
rejected('ACoS-negative-price', 't1', {t1p:-30,t1m:9});
rejected('ACoS-margin-over-price', 't1', {t1p:30,t1m:31});
rejected('EV-negative-cpc', 't0', {t0c:10,t0m:9,t0p:-1});
rejected('CPC-negative-target', 't2', {t2a:-25,t2c:10,t2p:30});
rejected('CPC-zero-price', 't2', {t2a:25,t2c:10,t2p:0});
rejected('CPC-negative-price', 't2', {t2a:25,t2c:10,t2p:-30});
rejected('Budget-negative-cpc', 't3', {t3c:10,t3p:-1});
for (const [id,key] of [['t0','t0c'],['t2','t2c'],['t3','t3c'],['t4','t4c']]) {
  rejected(`${id}-negative-conversion`, id, {...defaults[id],[key]:-10});
  rejected(`${id}-over100-conversion`, id, {...defaults[id],[key]:100.01});
}
rejected('Budget-zero-conversion', 't3', {t3c:0,t3p:1});
rejected('High-click-zero-conversion', 't4', {t4c:0});
rejected('ACoS-output-overflow', 't1', {t1p:5e-324,t1m:-1});
rejected('EV-output-overflow', 't0', {t0c:100,t0m:-1e308,t0p:1e308});
rejected('CPC-output-overflow', 't2', {t2a:1e308,t2c:100,t2p:1e308});
rejected('Budget-output-overflow', 't3', {t3c:1e-307,t3p:1e308});
rejected('High-click-underflow-denominator', 't4', {t4c:5e-324});
rejected('Unknown-tool', 'unknown', {});

for (const [name, inputs] of [
  ['EV-break-even-positive-floating-error', {t0c:10,t0m:7,t0p:.7}],
  ['EV-break-even-negative-floating-error', {t0c:30,t0m:3,t0p:.9}],
]) {
  check(name, () => {
    const result = calculateTool('t0', inputs);
    assert(result.metrics[1].value === 0, `Mathematical break-even net not normalized: ${result.metrics[1].value}`);
    assert(result.summary.startsWith('盈亏平衡'), `Misleading state: ${result.summary}`);
    assert(!result.metrics[1].value.toFixed(2).includes('-0.00'), 'Negative zero displayed');
  });
}

check('Input-handler-clears-old-result', () => {
  const app = fs.readFileSync(path.join(root,'workbench/dist/app.js'),'utf8');
  const begin = app.indexOf("} else if (event.target.closest('#calculator-form'))");
  const end = app.indexOf("root.addEventListener('submit'", begin);
  const handler = app.slice(begin,end);
  assert(begin >= 0 && /calculatorResults\.delete\(activeRoute\.id\)/.test(handler), 'Input change does not delete old result');
  assert(/#blue-panel/.test(handler) && /toolResultPanel/.test(handler), 'Input change does not repaint result panel');
});
check('Error-handler-clears-old-result', () => {
  const app = fs.readFileSync(path.join(root,'workbench/dist/app.js'),'utf8');
  const begin = app.indexOf('} catch (issue)');
  const end = app.indexOf("root.addEventListener('click'", begin);
  const handler = app.slice(begin,end);
  assert(begin >= 0 && /calculatorResults\.delete\(form\.dataset\.tool\)/.test(handler), 'Calculation error does not delete old result');
  assert(/#blue-panel/.test(handler) && /toolResultPanel/.test(handler), 'Calculation error does not repaint result panel');
});

const failed = results.filter(result => !result.passed);
fs.writeFileSync(path.join(root,'archive/audit/workbench-calculator-cases.json'), JSON.stringify({total:results.length,passed:results.length-failed.length,failed:failed.length,results},null,2)+'\n');
console.log(JSON.stringify({total:results.length,passed:results.length-failed.length,failed}));
if (failed.length) process.exitCode=1;
