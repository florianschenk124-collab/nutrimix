import { useState, useEffect } from 'react'
import { useI18n } from '../hooks/useI18n'
import { fetchCompatibilityMatrix } from '../api'
const SC={ok:'var(--success)',info:'var(--info)',warning:'var(--warning)',critical:'var(--error)'}
const SB={ok:'rgba(94,189,122,0.1)',info:'rgba(91,155,213,0.1)',warning:'rgba(224,164,88,0.1)',critical:'rgba(212,95,95,0.1)'}
export default function Compatibility(){const{t,td}=useI18n();const[data,setData]=useState(null);const[loading,setLoading]=useState(true);const[filter,setFilter]=useState('all')
useEffect(()=>{fetchCompatibilityMatrix().then(setData).finally(()=>setLoading(false))},[])
if(loading)return<div className="placeholder-view"><span className="spinner"/></div>;if(!data)return null
const filtered=filter==='all'?data.checks:data.checks.filter(c=>c.severity===filter)
const cc=data.checks.filter(c=>c.severity==='critical').length,wc=data.checks.filter(c=>c.severity==='warning').length,oc=data.checks.filter(c=>c.severity==='ok').length
return(<div><div className="page-header"><h1 className="page-title">{t('compat.title')}</h1><p className="page-subtitle">{t('compat.subtitle')}</p></div>
<div className="stats-grid" style={{marginBottom:16}}>
<div className="stat-item"><div className="stat-label">{t('compat.stat_salts')}</div><div className="stat-value">{data.salts.length}</div></div>
<div className="stat-item"><div className="stat-label">{t('compat.stat_ok')}</div><div className="stat-value success">{oc}</div></div>
<div className="stat-item"><div className="stat-label">{t('compat.stat_warn')}</div><div className="stat-value warning">{wc}</div></div>
<div className="stat-item"><div className="stat-label">{t('compat.stat_critical')}</div><div className="stat-value error">{cc}</div></div></div>
<div className="card" style={{display:'flex',gap:10}}>
{[{key:'all',label:`${t('compat.filter_all')} (${data.checks.length})`},{key:'critical',label:`${t('compat.stat_critical')} (${cc})`},{key:'warning',label:`${t('compat.stat_warn')} (${wc})`},{key:'ok',label:`OK (${oc})`}].map(f=>(
<button key={f.key} className="btn" style={{padding:'5px 14px',fontSize:12,background:filter===f.key?'var(--accent-bg-hover)':'var(--bg-input)',color:filter===f.key?'var(--text-accent)':'var(--text-secondary)',border:`1px solid ${filter===f.key?'var(--accent)':'var(--border-subtle)'}`}} onClick={()=>setFilter(f.key)}>{f.label}</button>))}</div>
<div className="card" style={{padding:0}}><table className="result-table"><thead><tr>
<th style={{padding:'10px 14px'}}>{t('compat.col_salt_a')}</th><th style={{padding:'10px 14px'}}>{t('compat.col_salt_b')}</th>
<th style={{padding:'10px 14px'}}>{t('calc.col_status')}</th><th style={{padding:'10px 14px'}}>{t('compat.col_precip')}</th>
<th style={{padding:'10px 14px'}}>{t('compat.col_desc')}</th></tr></thead>
<tbody>{filtered.map((c,i)=>(<tr key={i} style={{background:SB[c.severity]||undefined}}>
<td style={{padding:'7px 14px',fontSize:12}}>{td(c.salt_a)}</td><td style={{padding:'7px 14px',fontSize:12}}>{td(c.salt_b)}</td>
<td style={{padding:'7px 14px'}}><span style={{fontSize:11,fontWeight:600,color:SC[c.severity],textTransform:'uppercase'}}>{c.severity}</span></td>
<td style={{padding:'7px 14px',fontFamily:'var(--font-mono)',fontSize:12}}>{td(c.precipitate)||'–'}</td>
<td style={{padding:'7px 14px',fontSize:12,color:'var(--text-secondary)'}}>{td(c.reason)}</td></tr>))}</tbody></table></div></div>)}
