// Shared formatting and snapshot validation; no credentials or customer records.
const fields = ['loaded','q1','emails','business','revenue','calendar','time','booked'];
const percent = (part,total) => total ? (part/total*100).toFixed(1)+'%' : '—';
const change = (current,previous) => previous ? ((current-previous)/previous*100).toFixed(1)+'%' : '—';
const dateLabel = value => new Date(value+'T12:00:00Z').toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric',timeZone:'UTC'});
const lastDay = end => new Date(Date.parse(end+'T00:00:00Z')-86400000).toISOString().slice(0,10);
const rangeLabel = row => `${dateLabel(row.start)} – ${dateLabel(lastDay(row.end))}`;
const isStale = (report,now=Date.now()) => now-Date.parse(report.generatedAt)>36*60*60*1000;
function validateReport(report){
 const validDate = value => typeof value==='string' && /^\d{4}-\d{2}-\d{2}$/.test(value) && Number.isFinite(Date.parse(value+'T00:00:00Z')) && new Date(value+'T00:00:00Z').toISOString().slice(0,10)===value;
 if(report.schemaVersion!==1 || report.timezone!=='America/Los_Angeles' || !validDate(report.through) || !validDate(report.coverageStart) || !Number.isFinite(Date.parse(report.generatedAt)) || !Array.isArray(report.ranges) || !report.ranges.length) throw new Error('Invalid report');
 const ids = new Set();
 for(const period of report.ranges){
  if(!/^(\d{4}-\d{2}|last(?:7|30|90))$/.test(period.id) || ids.has(period.id) || typeof period.label!=='string' || !validDate(period.requestedStart) || !Array.isArray(period.weeks) || !period.weeks.length) throw new Error('Invalid period');
  ids.add(period.id);
  for(const row of [period,...period.weeks]){
   if(!validDate(row.start) || !validDate(row.end) || row.start>=row.end || row.start<report.coverageStart || lastDay(row.end)>report.through) throw new Error('Invalid dates');
  }
  let next=period.start;
  for(const week of period.weeks){
   if(week.start!==next || !Number.isInteger(week.days) || week.days<1 || week.days>7 || (Date.parse(week.end)-Date.parse(week.start))/86400000!==week.days) throw new Error('Invalid weeks');
   next=week.end;
  }
  if(next!==period.end) throw new Error('Incomplete weeks');
  for(const row of [period.totals,...period.weeks]){
   if(!row || fields.some(f=>!Number.isSafeInteger(row[f]) || row[f]<0)) throw new Error('Invalid counts');
  }
 }
 return report;
}
if(typeof module!=='undefined') module.exports={fields,percent,change,dateLabel,lastDay,rangeLabel,isStale,validateReport};
