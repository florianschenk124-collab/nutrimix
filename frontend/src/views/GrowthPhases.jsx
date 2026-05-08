import { useState, useEffect } from 'react'
import { useI18n } from '../hooks/useI18n'
import { fetchGrowthPlans, fetchRecipes } from '../api'
const FK=[{key:'n_factor',label:'N',color:'#5ebd7a'},{key:'k_factor',label:'K',color:'#c77dba'},{key:'ca_factor',label:'Ca',color:'#5b9bd5'},{key:'mg_factor',label:'Mg',color:'#e0a458'},{key:'p_factor',label:'P',color:'#d45f5f'}]
export default function GrowthPhases(){const{t}=useI18n();const[plans,setPlans]=useState([]);const[recipes,setRecipes]=useState([]);const[selectedName,setSelectedName]=useState('');const[selected,setSelected]=useState(null);const[schedule,setSchedule]=useState(null);const[week,setWeek]=useState(0);const[loading,setLoading]=useState(true);const[error,setError]=useState(null);const[recipeOverride,setRecipeOverride]=useState('')
useEffect(()=>{Promise.all([fetchGrowthPlans(),fetchRecipes()]).then(([p,r])=>{setPlans(p);setRecipes(r);setLoading(false);if(p.length>0){setSelectedName(p[0].name);setSelected(p[0])}}).catch(e=>{setError(e.message);setLoading(false)})},[])
useEffect(()=>{if(!selectedName||loading)return;const plan=plans.find(p=>p.name===selectedName);setSelected(plan||null);setError(null)
const ov=recipeOverride||undefined;const url=ov?`/api/growth-plans/${encodeURIComponent(selectedName)}/schedule?recipe_override=${encodeURIComponent(ov)}`:`/api/growth-plans/${encodeURIComponent(selectedName)}/schedule`
fetch(url).then(r=>{if(!r.ok)throw new Error(`HTTP ${r.status}`);return r.json()}).then(d=>{setSchedule(d);setWeek(0)}).catch(e=>{setSchedule(null);setError(`${t('growth.schedule_err')}: ${e.message}`)})},[selectedName,recipeOverride,loading])
const fmt=(v,d=2)=>Number(v).toFixed(d);const cw=schedule?.weeks?.[week]
if(loading)return<div className="placeholder-view"><span className="spinner"/></div>
return(<div><div className="page-header"><h1 className="page-title">{t('growth.title')}</h1><p className="page-subtitle">{t('growth.subtitle')}</p></div>
<div className="card"><div className="card-title">{t('growth.card_select')}</div>
<div className="form-grid"><div className="form-group"><label className="form-label">{t('growth.plan')}</label>
<select className="form-select" value={selectedName} onChange={e=>{setSelectedName(e.target.value);setRecipeOverride('')}}>{plans.map(p=><option key={p.name} value={p.name}>{p.name}</option>)}</select></div>
<div className="form-group"><label className="form-label">{t('growth.base_label')} (Override)</label>
<select className="form-select" value={recipeOverride} onChange={e=>setRecipeOverride(e.target.value)}><option value="">{t('growth.auto')}</option>
{recipes.map(r=><option key={r.name} value={r.name}>{r.name}</option>)}</select></div></div>
{schedule&&<div style={{fontSize:12,color:'var(--text-secondary)',marginTop:8}}>{selected?.description} — {t('growth.base_label')}: <strong>{schedule.base_recipe}</strong>
{schedule.original_recipe!==schedule.base_recipe&&<span style={{color:'var(--warning)',marginLeft:8}}>(Original: {schedule.original_recipe})</span>}</div>}
{error&&<div className="alert alert-warning" style={{marginTop:8}}>{error}</div>}</div>
{schedule&&(<div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
<div className="card"><div className="card-title">{t('growth.card_phases')}</div>
{selected?.phases?.map((ph,i)=>{const isA=cw?.phase_name===ph.name;return(<div key={i} style={{padding:'10px 14px',borderBottom:'1px solid var(--border-subtle)',background:isA?'var(--accent-bg)':undefined,borderLeft:isA?'3px solid var(--accent)':'3px solid transparent',cursor:'pointer'}} onClick={()=>setWeek(ph.week_start)}>
<div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}><div><div style={{fontWeight:600,fontSize:13}}>{ph.name}</div><div style={{fontSize:11,color:'var(--text-muted)'}}>{t('growth.week_header')} {ph.week_start}–{ph.week_end}{ph.ec_target>0?` · EC ${ph.ec_target}`:''}</div></div>
<div style={{display:'flex',gap:4}}>{FK.map(f=><span key={f.key} style={{fontSize:9,fontFamily:'var(--font-mono)',padding:'1px 4px',borderRadius:3,background:ph[f.key]!==1.0?f.color+'22':'transparent',color:ph[f.key]!==1.0?f.color:'var(--text-muted)'}}>{f.label}×{fmt(ph[f.key],1)}</span>)}</div></div></div>)})}</div>
<div><div className="card"><div className="card-title">{t('growth.card_week')}</div>
<div style={{display:'flex',alignItems:'center',gap:12,marginBottom:12}}>
<button className="btn" style={{padding:'4px 10px',fontSize:16,background:'var(--bg-input)',border:'1px solid var(--border-subtle)',color:'var(--text-primary)'}} onClick={()=>setWeek(Math.max(0,week-1))} disabled={week<=0}>◀</button>
<div style={{flex:1,textAlign:'center'}}><div style={{fontSize:20,fontWeight:700,fontFamily:'var(--font-mono)'}}>{t('growth.week')} {week}</div><div style={{fontSize:11,color:'var(--text-muted)'}}>/ {schedule.total_weeks}</div></div>
<button className="btn" style={{padding:'4px 10px',fontSize:16,background:'var(--bg-input)',border:'1px solid var(--border-subtle)',color:'var(--text-primary)'}} onClick={()=>setWeek(Math.min(schedule.total_weeks,week+1))} disabled={week>=schedule.total_weeks}>▶</button></div>
<input type="range" min="0" max={schedule.total_weeks} value={week} onChange={e=>setWeek(Number(e.target.value))} style={{width:'100%',accentColor:'var(--accent)'}}/></div>
{cw&&(<><div className="stats-grid" style={{marginBottom:12}}>
<div className="stat-item"><div className="stat-label">{t('growth.phase_label')}</div><div className="stat-value" style={{fontSize:14}}>{cw.phase_name}</div></div>
<div className="stat-item"><div className="stat-label">{t('growth.ec_target')}</div><div className="stat-value" style={{fontSize:14}}>{cw.ec_target>0?`${fmt(cw.ec_target,1)} mS/cm`:'–'}</div></div></div>
<div className="card"><div className="card-title">{t('growth.modifiers')}</div>
{FK.map(f=>{const v=cw.factors?.[f.key]||1.0;return(<div key={f.key} style={{display:'flex',alignItems:'center',gap:10,marginBottom:8}}>
<span style={{width:30,fontSize:13,fontWeight:700,color:f.color}}>{f.label}</span>
<div style={{flex:1,height:10,background:'var(--bg-input)',borderRadius:5,overflow:'hidden',position:'relative'}}><div style={{position:'absolute',left:'50%',top:0,width:1,height:'100%',background:'var(--border-default)'}}/><div style={{width:`${Math.min(100,v*50)}%`,height:'100%',background:f.color,borderRadius:5}}/></div>
<span style={{fontFamily:'var(--font-mono)',fontSize:13,width:50,textAlign:'right',fontWeight:600}}>×{fmt(v,2)}</span></div>)})}</div>
<div className="card"><div className="card-title">{t('growth.adjusted_mg')}</div>
<table className="result-table"><thead><tr><th>{t('calc.col_ion')}</th><th style={{textAlign:'right'}}>{t('gen.mg_l')}</th></tr></thead>
<tbody>{Object.entries(cw.adjusted_mg||{}).filter(([,v])=>v>0.01).sort((a,b)=>b[1]-a[1]).map(([ion,v])=><tr key={ion}><td style={{fontWeight:600}}>{ion}</td><td className="num">{fmt(v)}</td></tr>)}</tbody></table></div></>)}</div></div>)}</div>)}
