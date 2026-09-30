// Verified PostHog activity counts, captured through 2026-09-30 03:35 UTC.
// Periods use America/Los_Angeles and Monday-start weeks.
const fields = ['loaded','q1','emails','business','revenue','calendar','time','booked'];
const weeks = [
  {label:'Sep 1–6',note:'Partial week · 6 days',days:6,values:[451,47,33,27,27,21,20,20]},
  {label:'Sep 7–13',note:'Full week',days:7,values:[1114,111,89,65,65,52,43,41]},
  {label:'Sep 14–20',note:'Full week',days:7,values:[1665,192,140,117,116,77,68,67]},
  {label:'Sep 21–27',note:'Full week',days:7,values:[1227,181,135,102,101,59,56,56]},
  {label:'Sep 28–29',note:'Ongoing · 2 days so far',days:2,values:[464,69,50,41,41,25,21,19]},
].map(w => ({...w,...Object.fromEntries(fields.map((f,i)=>[f,w.values[i]]))}));
const month = {label:'September so far',...Object.fromEntries(fields.map((f,i)=>[f,[4786,580,433,347,346,231,207,202][i]]))};
const percent = (part,total) => total ? (part/total*100).toFixed(1)+'%' : '—';
const change = (current,previous) => previous ? ((current-previous)/previous*100).toFixed(1)+'%' : '—';
if (typeof module !== 'undefined') module.exports = {fields,weeks,month,percent,change};
