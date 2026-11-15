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
}
function renderQuotes(){
  const query=$('#search').value.trim().toUpperCase();
  const body=$('#quotes-body');body.replaceChildren();
  const rows=quotes.filter(r=>(r.symbol||'').toUpperCase().includes(query));
  if(!rows.length){const tr=document.createElement('tr'),td=document.createElement('td');td.colSpan=5;td.textContent='No saved quotes match.';tr.append(td);body.append(tr);return;}
  rows.forEach(r=>{const tr=document.createElement('tr');[r.symbol,r.exchange,Number.isFinite(Number(r.close))&&r.close!==''?'$'+Number(r.close).toFixed(2):'—',r.quote_date,r.retrieved_at_utc].forEach(value=>{const td=document.createElement('td');td.textContent=value||'—';tr.append(td);});body.append(tr);});
}
async function updateQuotes(){try{const response=await fetch('/api/quotes',{cache:'no-store'});if(!response.ok)throw Error();const data=await response.json();quotes=data.rows;$('#status').textContent=data.status.message;renderQuotes();}catch{$('#status').textContent='Quote data unavailable. Check the local snapshot and collector.';}}
document.querySelectorAll('.nav').forEach(button=>button.addEventListener('click',()=>{document.querySelectorAll('.nav').forEach(b=>b.classList.toggle('active',b===button));document.querySelectorAll('.view').forEach(v=>{v.hidden=v.id!==button.dataset.view;});$('#crumb').textContent=button.textContent.trim().replace(/^\d+\s*/, '').toUpperCase();}));
$('#period').addEventListener('change',renderHistory);$('#search').addEventListener('input',renderQuotes);
barChart('#risk-chart',[-21.274674782767956,-25.355233489553463],['Rule','Buy and hold'],['#5685a4','#0b376b']);
fetch('/api/historical',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error();return r.json();}).then(data=>{historical=data.rows;renderHistory();}).catch(()=>{$('#rule-return').textContent='Unavailable';$('#buy-return').textContent='Unavailable';$('#difference').textContent='Unavailable';});
updateQuotes();setInterval(updateQuotes,30000);
