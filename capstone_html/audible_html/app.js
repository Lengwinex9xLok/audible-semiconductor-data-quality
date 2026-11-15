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
  const rows=['2022','2023','2024','2025'].map(period=>historical.find(r=>r.period===period&&r.level==='Sample'&&r.item==='All 20'));
  const svg=$('#annual-chart'); svg.replaceChildren();
  const valid=rows.every(r=>r && r.rule_return_pct!=='' && r.buy_hold_return_pct!=='' && Number.isFinite(Number(r.rule_return_pct)) && Number.isFinite(Number(r.buy_hold_return_pct)));
  $('#annual-status').hidden=valid;
  if(!valid){svg.setAttribute('aria-label','Annual results unavailable');return;}
  const vals=rows.flatMap(r=>[Number(r.rule_return_pct),Number(r.buy_hold_return_pct)]);
  const min=Math.min(0,...vals), max=Math.max(0,...vals), range=max-min || 1;
  const x=v=>180+((v-min)/range)*535, zero=x(0);
  svg.append(svgEl('line',{x1:zero,y1:15,x2:zero,y2:265,stroke:'#aab8c8','stroke-width':1}));
  svg.append(svgEl('text',{x:zero,y:289,fill:'#40566d','font-size':13,'font-family':'Arial','text-anchor':'middle'},'0%'));
  rows.forEach((r,i)=>{
    const y=23+i*61;
    svg.append(svgEl('text',{x:10,y:y+20,fill:'#40566d','font-size':15,'font-family':'Arial'},r.period));
    [Number(r.rule_return_pct),Number(r.buy_hold_return_pct)].forEach((value,j)=>{
      const ybar=y+j*23;
      svg.append(svgEl('rect',{x:Math.min(zero,x(value)),y:ybar,width:Math.abs(x(value)-zero),height:16,fill:j?'#0b376b':'#5685a4'}));
      svg.append(svgEl('text',{x:value<0?x(value)-7:x(value)+7,y:ybar+13,fill:'#153759','font-size':13,'font-family':'Arial','text-anchor':value<0?'end':'start'},fmt(value)));
    });
  });
  svg.setAttribute('aria-label','Annual gross returns. '+rows.map(r=>`${r.period}: rule ${fmt(r.rule_return_pct)}, buy and hold ${fmt(r.buy_hold_return_pct)}`).join('; ')+'.');
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
  if(!row){$('#rule-return').textContent='Unavailable';return;}
  const a=Number(row.rule_return_pct),b=Number(row.buy_hold_return_pct),d=Number(row.difference_pp);
  if(![a,b,d].every(Number.isFinite)) return;
  $('#rule-return').textContent=fmt(a);$('#buy-return').textContent=fmt(b);$('#difference').textContent=pp(d);
  const periodLabel=period==='All'?'2022–2025':period;
  $('#period-tag').textContent=period==='All'?'FULL PERIOD · 2022–2025':period;
  $('#return-title').textContent=`${periodLabel}: rule vs. buy and hold`;
  $('#return-chart').setAttribute('aria-label', `${periodLabel} gross return: rule ${fmt(a)}; buy and hold ${fmt(b)}.`);
  barChart('#return-chart',[a,b],['Rule','Buy and hold'],['#5685a4','#0b376b']);
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
document.querySelectorAll('.nav').forEach(button=>button.addEventListener('click',()=>{document.querySelectorAll('.nav').forEach(b=>b.classList.toggle('active',b===button));document.querySelectorAll('.view').forEach(v=>{v.hidden=v.id!==button.dataset.view;});$('#crumb').textContent=button.textContent.trim().replace(/^\d+\s*/, '').toUpperCase();$('#scope-equity').hidden=button.dataset.view==='phase2';$('#scope-phase2').hidden=button.dataset.view!=='phase2';}));
$('#period').addEventListener('change',renderHistory);$('#search').addEventListener('input',renderQuotes);
$('#sample').addEventListener('change',renderSample);
barChart('#risk-chart',[-21.274674782767956,-25.355233489553463],['Rule','Buy and hold'],['#5685a4','#0b376b']);
fetch('/api/historical',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error();return r.json();}).then(data=>{historical=data.rows;prepareSampleSelector();renderHistory();renderAnnual();}).catch(()=>{$('#rule-return').textContent='Unavailable';$('#buy-return').textContent='Unavailable';$('#difference').textContent='Unavailable';$('#sample-status').hidden=false;$('#annual-status').hidden=false;});
updateQuotes();setInterval(updateQuotes,30000);
