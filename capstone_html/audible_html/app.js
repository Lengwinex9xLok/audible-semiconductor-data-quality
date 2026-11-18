'use strict';
const $ = s => document.querySelector(s);
let historical = [];
let quotes = [];
const fmt = n => `${Number(n).toFixed(2)}%`;
const pp = n => `${Number(n) > 0 ? '+' : ''}${Number(n).toFixed(2)} pp`;
const ns = 'http://www.w3.org/2000/svg';
function svgEl(name, attrs, text) {
  const el = document.createElementNS(ns, name);
  Object.entries(attrs).forEach(([k,v]) => el.setAttribute(k, String(v)));
  if (text !== undefined) el.textContent = text;
  return el;
}
function barChart(target, values, labels, colors) {
  const svg = $(target); svg.replaceChildren();
  const min = Math.min(0, ...values), max = Math.max(0, ...values);
  const range = max - min || 1, left=200, width=510;
  const x = v => left + ((v-min)/range)*width;
  const zero=x(0);
  svg.append(svgEl('line',{x1:zero,y1:20,x2:zero,y2:145,stroke:'#aab8c8','stroke-width':1}));
  svg.append(svgEl('text',{x:zero,y:166,fill:'#40566d','font-size':13,'font-family':'Arial','text-anchor':'middle'},'0%'));
  values.forEach((v,i)=>{
    const y=35+i*57;
    svg.append(svgEl('text',{x:0,y:y+15,fill:'#40566d','font-size':15,'font-family':'Arial'},labels[i]));
    svg.append(svgEl('rect',{x:Math.min(zero,x(v)),y,width:Math.max(1,Math.abs(x(v)-zero)),height:23,fill:colors[i]}));
    const negative = v < 0;
    svg.append(svgEl('text',{x:negative?x(v)-7:x(v)+7,y:y+17,fill:'#153759','font-size':14,'font-family':'Arial','text-anchor':negative?'end':'start'},fmt(v)));
  });
}
function renderAnnual() {
  if (!$('#contribution-figure').hidden) renderContributions();
  if ($('#wealth-chart').clientWidth) renderWealth();
  const years = ['2022', '2023', '2024', '2025'];
  const rows = years.map(year => historical.find(row =>
    row.period === year && row.level === 'Sample' && row.item === 'All 20'));
  const chart = $('#annual-chart');
  chart.replaceChildren();
  const valid = rows.every(row => row && row.difference_pp != null &&
    String(row.difference_pp).trim() !== '' && Number.isFinite(Number(row.difference_pp)));
  $('#annual-status').hidden = valid;
  if (!valid) return;

  const limit = Math.max(1, ...rows.map(row => Math.abs(Number(row.difference_pp))));
  for (const row of rows) {
    const gap = Number(row.difference_pp);
    const width = 49 * Math.abs(gap) / limit;
    const line = document.createElement('li');
    const year = document.createElement('span');
    year.textContent = row.period;
    const track = svgEl('svg', {viewBox:'0 0 100 30', preserveAspectRatio:'none', 'aria-hidden':'true'});
    track.append(svgEl('rect', {x:gap < 0 ? 50 - width : 50, y:10, width, height:10,
      fill:gap < 0 ? '#203f66' : '#22786e'}));
    track.append(svgEl('line', {x1:50, y1:0, x2:50, y2:30, stroke:'#acbac5',
      'vector-effect':'non-scaling-stroke'}));
    const value = document.createElement('strong');
    value.textContent = pp(gap);
    line.append(year, track, value);
    chart.append(line);
  }
}
function returnValue(row, field) {
  const raw = row?.[field];
  return raw == null || String(raw).trim() === '' ? NaN : Number(raw);
}

function renderWealth() {
  const svg = $('#wealth-chart');
  const status = $('#wealth-status');
  svg.replaceChildren();
  const series = [
    {label:'Buy and hold', field:'buy_hold_return_pct', color:'#203f66', balances:[100]},
    {label:'Rule', field:'rule_return_pct', color:'#22786e', balances:[100]},
  ];
  const years = ['2022', '2023', '2024', '2025'];
  for (const year of years) {
    const row = historical.find(r => r.period === year && r.level === 'Sample' && r.item === 'All 20');
    for (const line of series) {
      const rate = returnValue(row, line.field);
      if (!Number.isFinite(rate)) {
        status.textContent = 'Year-end portfolio values are unavailable.';
        return;
      }
      line.balances.push(line.balances.at(-1) * (1 + rate / 100));
    }
  }
  const width = Math.max(240, Math.round(svg.getBoundingClientRect().width));
  const right = width < 450 ? 9 : 24;
  const x = i => 43 + i * (width - 43 - right) / years.length;
  const balances = series.flatMap(line => line.balances);
  const low = Math.floor(Math.min(...balances) / 25) * 25;
  const high = Math.max(low + 25, Math.ceil(Math.max(...balances) / 25) * 25);
  const y = v => 17 + (high - v) / (high - low) * 150;
  svg.setAttribute('viewBox', `0 0 ${width} 199`);
  for (let tick = low; tick <= high; tick += 25) {
    svg.append(svgEl('line', {x1:x(0), x2:x(4), y1:y(tick), y2:y(tick), stroke:tick === 100 ? '#a6b4c2' : '#e4e9ec'}));
    svg.append(svgEl('text', {x:34, y:y(tick) + 4, 'text-anchor':'end'}, '$' + tick));
  }
  ['Start', ...years].forEach((label, i) => {
    svg.append(svgEl('text', {x:x(i), y:191, 'text-anchor':i === 4 ? 'end' : 'middle'}, label));
  });
  for (const line of series) {
    const points = line.balances.map((v,i) => `${x(i)},${y(v)}`).join(' ');
    svg.append(svgEl('polyline', {points, fill:'none', stroke:line.color, 'stroke-width':2.5,
      'stroke-dasharray':line.label === 'Rule' ? '6 3' : 'none'}));
    line.balances.forEach((balance,i) => {
      const dot = svgEl('circle', {cx:x(i), cy:y(balance), r:3.7, fill:line.color});
      dot.append(svgEl('title', {}, `${line.label}, ${i ? years[i-1] : 'start'}: $${balance.toFixed(2)}`));
      svg.append(dot);
    });
  }
  svg.setAttribute('aria-label', series.map(line =>
    line.label + ' from start through each year-end: ' + line.balances.map(v => '$' + v.toFixed(2)).join(', ')
  ).join('. '));
  status.replaceChildren();
  for (const line of series) {
    const label = document.createElement('span');
    label.className = line.field;
    label.textContent = `${line.label}  $${line.balances.at(-1).toFixed(2)}`;
    status.append(label);
  }
}

function renderNvdaCheck(portfolio) {
  const remaining = historical.filter(r => r.period === 'All' && r.level === 'Stock' && r.item !== 'NVDA');
  if (remaining.length !== 19) return;
  const chart = $('#nvda-chart');
  chart.replaceChildren();
  const comparisons = ['rule_return_pct', 'buy_hold_return_pct'].map(field => ({
    full: returnValue(portfolio, field),
    rest: remaining.reduce((sum, row) => sum + returnValue(row, field), 0) / remaining.length,
  }));
  const endpoints = comparisons.flatMap(pair => [pair.full, pair.rest]);
  if (!endpoints.every(Number.isFinite)) return;
  const low = Math.min(0, ...endpoints);
  const high = Math.max(100, ...endpoints);
  const position = value => (9 + 82 * (value - low) / (high - low)) + '%';
  for (const [field, label] of [['full', 'All 20 stocks'], ['rest', '19 without NVIDIA']]) {
    const row = document.createElement('div');
    row.className = 'nvda-pair';
    const name = document.createElement('b');
    name.textContent = label;
    const [rule, hold] = comparisons.map(pair => pair[field]);
    const svg = svgEl('svg', {role:'img', 'aria-label':label + ', rule ' + fmt(rule) + ', buy and hold ' + fmt(hold)});
    svg.append(svgEl('line', {x1:position(low), x2:position(high), y1:18, y2:18, stroke:'#dce3e9'}));
    if (field === 'rest') {
      svg.classList.add('nvda-axis');
      for (const tick of [low, (low + high) / 2, high]) {
        svg.append(svgEl('text', {x:position(tick), y:40, 'text-anchor':'middle', fill:'#54687b', 'font-size':11}, tick.toFixed(0) + '%'));
      }
    }
    svg.append(svgEl('line', {x1:position(rule), x2:position(hold), y1:18, y2:18, stroke:'#a2b2be', 'stroke-width':2}));
    for (const [value, color] of [[rule,'#22786e'], [hold,'#203f66']]) {
      svg.append(svgEl('circle', {cx:position(value), cy:18, r:5, fill:color}));
    }
    const figures = document.createElement('span');
    for (const [series, value] of [['Rule', rule], ['Buy and hold', hold]]) {
      const entry = document.createElement('span');
      entry.className = series === 'Rule' ? 'pair-rule' : 'pair-hold';
      entry.textContent = series + ' ' + fmt(value);
      figures.append(entry);
    }
    row.append(name, svg, figures);
    chart.append(row);
  }
  $('#nvda-gap').textContent = 'Without NVIDIA, rule minus buy and hold was ' +
    pp(comparisons[0].rest - comparisons[1].rest) + '. Both portfolios allocated 1/19 of starting capital to each remaining stock.';
  $('#nvda-check').hidden = false;
}

function renderContributions() {
  const chart = $('#contribution-chart');
  const table = $('#contribution-table');
  const note = $('#contribution-note');
  chart.replaceChildren();
  table.replaceChildren();
  $('#stock-evidence').hidden = true;
  $('#nvda-check').hidden = true;
  const rows = historical.filter(row => row.period === 'All' && row.level === 'Stock')
    .map(row => ({symbol:row.item, gap:returnValue(row, 'difference_pp')}))
    .sort((a, b) => a.gap - b.gap);
  const portfolio = historical.find(row => row.period === 'All' && row.level === 'Sample' && row.item === 'All 20');
  const reported = returnValue(portfolio, 'difference_pp');
  const total = rows.reduce((sum, row) => sum + row.gap / 20, 0);
  if (new Set(rows.map(row => row.symbol)).size !== 20 || rows.length !== 20 ||
      !Number.isFinite(total) || !Number.isFinite(reported) || Math.abs(total - reported) > 0.00001) {
    note.textContent = 'A reconciled 20-stock breakdown is unavailable.';
    return;
  }
  const losses = rows.filter(row => row.gap < 0);
  const gains = rows.filter(row => row.gap > 0);
  $('#contribution-title').textContent = `The rule trailed on ${losses.length} of 20 stocks`;
  const parts = losses.slice(0, 3).map(row => ({name:row.symbol, change:row.gap / 20}));
  const otherLosses = losses.slice(3);
  if (otherLosses.length) parts.push({name:`Other ${otherLosses.length} laggards`, change:otherLosses.reduce((s,r) => s+r.gap/20,0)});
  if (gains.length) parts.push({name:`${gains.length} outperformers`, change:gains.reduce((s,r) => s+r.gap/20,0)});
  let running = 0;
  const steps = parts.map(part => {
    const start = running;
    running += part.change;
    return {...part, start, end:running};
  });
  steps.push({name:'Portfolio gap', start:0, end:total, change:total, total:true});
  const minimum = Math.min(0, ...steps.map(step => step.end));
  const maximum = Math.max(0, ...steps.map(step => step.end));
  const x = value => 2 + 96 * (value - minimum) / (maximum - minimum || 1);
  for (const step of steps) {
    const row = document.createElement('div');
    row.className = step.total ? 'waterfall-row waterfall-total' : 'waterfall-row';
    const name = document.createElement('span');
    name.textContent = step.name;
    const track = svgEl('svg', {viewBox:'0 0 100 32', preserveAspectRatio:'none', 'aria-hidden':'true'});
    track.append(svgEl('line', {x1:x(0), x2:x(0), y1:0, y2:32, stroke:'#b9c6cd', 'vector-effect':'non-scaling-stroke'}));
    if (!step.total) track.append(svgEl('line', {x1:x(step.start), x2:x(step.start), y1:0, y2:16, stroke:'#8d9aa5', 'vector-effect':'non-scaling-stroke'}));
    track.append(svgEl('rect', {x:Math.min(x(step.start),x(step.end)), y:10, height:12,
      width:Math.abs(x(step.end)-x(step.start)), fill:step.change > 0 ? '#22786e' : '#203f66'}));
    if (!step.total) track.append(svgEl('line', {x1:x(step.end), x2:x(step.end), y1:16, y2:32, stroke:'#8d9aa5', 'vector-effect':'non-scaling-stroke'}));
    const value = document.createElement('strong');
    value.textContent = pp(step.change);
    row.append(name, track, value);
    chart.append(row);
  }
  for (const row of rows) {
    const tr = document.createElement('tr');
    const symbol = document.createElement('th');
    symbol.scope = 'row';
    symbol.textContent = row.symbol;
    tr.append(symbol);
    for (const value of [row.gap, row.gap / 20]) {
      const td = document.createElement('td');
      td.textContent = pp(value);
      tr.append(td);
    }
    table.append(tr);
  }
  $('#stock-evidence').hidden = false;
  renderNvdaCheck(portfolio);
  note.textContent = 'Source: WRDS / CRSP. Each stock started at 5%. Its four-year portfolio contribution equals its own gross return gap multiplied by 5%. The total uses unrounded values.';
}

function prepareSampleSelector(){
  const select=$('#sample');
  [['Sample','Selected groups'],['Stock','Individual stocks']].forEach(([level,label])=>{
    const group=document.createElement('optgroup');group.label=label;
    [...new Set(historical.filter(r=>r.level===level&&r.item!=='All 20').map(r=>r.item))].sort().forEach(item=>{
      const option=document.createElement('option');option.value=`${level}|${item}`;option.textContent=item;group.append(option);
    });
    select.append(group);
  });
}
function renderSample(){
  const [level,item]=$('#sample').value.split('|'),period=$('#period').value;
  const row=historical.find(r=>r.period===period&&r.level===level&&r.item===item);
  const svg=$('#sample-chart');svg.replaceChildren();
  const valid=row && row.rule_return_pct!=='' && row.buy_hold_return_pct!=='' && Number.isFinite(Number(row.rule_return_pct)) && Number.isFinite(Number(row.buy_hold_return_pct));
  $('#sample-status').hidden=Boolean(valid);
  const periodLabel=period==='All'?'2022–2025':period;
  $('#sample-title').textContent=`${item}: ${periodLabel}`;
  if(!valid){svg.setAttribute('aria-label','Selected results unavailable');return;}
  const values=[Number(row.rule_return_pct),Number(row.buy_hold_return_pct)];
  svg.setAttribute('aria-label',`${item}, ${periodLabel}: rule ${fmt(values[0])}, buy and hold ${fmt(values[1])}.`);
  barChart('#sample-chart',values,['Rule','Buy and hold'],['#5685a4','#0b376b']);
}
function renderHistory(){
  const period=$('#period').value;
  const row=historical.find(r=>r.period===period&&r.level==='Sample'&&r.item==='All 20');
  const periodLabel=period==='All'?'2022–2025':period;
  $('#return-title').textContent = `Portfolio returns · ${periodLabel}`;
  for (const [target, field, format] of [
    ['#rule-return', 'rule_return_pct', fmt],
    ['#buy-return', 'buy_hold_return_pct', fmt],
    ['#difference', 'difference_pp', pp],
  ]) {
    const value = row?.[field];
    $(target).textContent = value != null && String(value).trim() !== '' && Number.isFinite(Number(value))
      ? format(value) : 'Unavailable';
  }
  renderSample();
}
function renderQuotes(){
  const query=$('#search').value.trim().toUpperCase();
  const body=$('#quotes-body');body.replaceChildren();
  const rows=quotes.filter(r=>(r.symbol||'').toUpperCase().includes(query));
  if(!rows.length){const tr=document.createElement('tr'),td=document.createElement('td');td.colSpan=5;td.textContent='No saved quotes match.';tr.append(td);body.append(tr);return;}
  rows.forEach(r=>{const tr=document.createElement('tr');[r.symbol,r.exchange,Number.isFinite(Number(r.close))&&r.close!==''?'$'+Number(r.close).toFixed(2):'—',r.quote_date,r.retrieved_at_utc].forEach(value=>{const td=document.createElement('td');td.textContent=value||'—';tr.append(td);});body.append(tr);});
}
async function updateQuotes(){try{const response=await fetch('/api/quotes',{cache:'no-store'});if(!response.ok)throw Error();const data=await response.json();quotes=data.rows;$('#status').textContent=data.status.message;renderQuotes();}catch{$('#status').textContent='Quote data unavailable. Check the local snapshot and collector.';}}
document.querySelectorAll('.nav').forEach(button=>button.addEventListener('click',()=>{
  const view=button.dataset.view;
  document.querySelectorAll('.nav').forEach(b=>{
    b.classList.toggle('active',b===button);
    if (b===button) b.setAttribute('aria-current','page');
    else b.removeAttribute('aria-current');
  });
  document.querySelectorAll('.view').forEach(v=>{v.hidden=v.id!==view;});
  $('#crumb').textContent=button.textContent.trim().replace(/^\d+\s*/, '').toUpperCase();
  $('#scope-equity').hidden=['phase2','ytd','quotes'].includes(view);
  $('#scope-quotes').hidden=view!=='quotes';
  $('#scope-phase2').hidden=view!=='phase2';
  $('#scope-ytd').hidden=view!=='ytd';
  window.scrollTo(0, 0);
}));
$('#period').addEventListener('change',renderHistory);$('#search').addEventListener('input',renderQuotes);
$('#sample').addEventListener('change',renderSample);
const evidenceButtons = document.querySelectorAll('.evidence-switch button');
evidenceButtons.forEach(button => button.addEventListener('click', () => {
  for (const item of evidenceButtons) {
    const selected = item === button;
    item.setAttribute('aria-pressed', String(selected));
    document.getElementById(item.getAttribute('aria-controls')).hidden = !selected;
  }
  if (!$('#contribution-figure').hidden) renderContributions();
  if (!$('#wealth-figure').hidden) renderWealth();
}));
new ResizeObserver(() => {
  if ($('#wealth-chart').clientWidth) renderWealth();
}).observe($('#wealth-chart'));
barChart('#risk-chart',[-21.274674782767956,-25.355233489553463],['Rule','Buy and hold'],['#5685a4','#0b376b']);
barChart('#invested-chart',[10443 / 20060 * 100,100],['Rule','Buy and hold'],['#5685a4','#0b376b']);
fetch('/api/historical',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error();return r.json();}).then(data=>{historical=data.rows;prepareSampleSelector();renderHistory();renderAnnual();}).catch(()=>{$('#rule-return').textContent='Unavailable';$('#buy-return').textContent='Unavailable';$('#difference').textContent='Unavailable';$('#sample-status').hidden=false;$('#annual-status').hidden=false;});
updateQuotes();setInterval(updateQuotes,30000);
