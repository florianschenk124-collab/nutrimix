import { useState, useEffect } from 'react'
import { useI18n } from '../hooks/useI18n'
import { fetchSalts, fetchRecipes, fetchWaterProfiles, calculate } from '../api'
export default function CostManager(){const{t,td}=useI18n();const[salts,setSalts]=useState([]);const[costs,setCosts]=useState({});const[recipes,setRecipes]=useState([]);const[wp,setWp]=useState([]);const[cr,setCr]=useState('');const[cw,setCw]=useState('Osmosewasser');const[res,setRes]=useState(null);const[saving,setSaving]=useState(false);const[msg,setMsg]=useState('')
useEffect(()=>{Promise.all([fetchSalts(),fetchRecipes(),fetchWaterProfiles(),fetch('/api/salts/costs/all').then(r=>r.json())]).then(([s,r,w,c])=>{setSalts(s.filter(x=>!x.is_premix));setRecipes(r);setWp(w);setCosts(c||{});if(r.length>0)setCr(r[0].name)})},[])
const setP=(f,v)=>setCosts(prev=>({...prev,[f]:v}))
const saveP=async()=>{setSaving(true);try{await fetch('/api/salts/costs',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({costs})});setMsg(t('costs.saved'));setTimeout(()=>setMsg(''),3000)}catch{setMsg(t('costs.err'))};setSaving(false)}
const calcC=async()=>{try{setRes(await calculate({recipe_name:cr,water_profile_name:cw,volume_l:1000,concentrate_factor:100}))}catch(e){console.error(e)}}
const fmt=(v,d=2)=>Number(v).toFixed(d)
const cats={macro:t('costs.cat_macro'),chelate:t('costs.cat_chelate'),micro:t('costs.cat_micro')}
return(<div><div className="page-header"><h1 className="page-title">{t('costs.title')}</h1><p className="page-subtitle">{t('costs.subtitle')}</p></div>
<div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
<div className="card" style={{maxHeight:'70vh',overflow:'auto'}}><div className="card-title">{t('costs.card_prices')}</div><p style={{fontSize:11,color:'var(--text-muted)',marginBottom:14}}>{t('costs.prices_hint')}</p>
{Object.entries(cats).map(([cat,label])=>{const cs=salts.filter(s=>s.category===cat);if(!cs.length)return null;return(<div key={cat} style={{marginBottom:16}}>
<div style={{fontSize:11,fontWeight:600,color:'var(--text-muted)',textTransform:'uppercase',marginBottom:6}}>{label}</div>
{cs.map(s=>(<div key={s.formula} style={{display:'flex',alignItems:'center',gap:10,padding:'4px 0',borderBottom:'1px solid var(--border-subtle)'}}>
<span style={{flex:1,fontSize:12}}>{td(s.name)}</span>
<input className="form-input" type="number" step="0.1" style={{width:80,textAlign:'right',fontSize:12,padding:'4px 8px'}} value={costs[s.formula]||''} placeholder="0" onChange={e=>setP(s.formula,Number(e.target.value))}/>
<span style={{fontSize:11,color:'var(--text-muted)',width:30}}>€/kg</span></div>))}</div>)})}
<div style={{display:'flex',alignItems:'center',gap:12,marginTop:12}}><button className="btn btn-primary" onClick={saveP} disabled={saving}>{t('costs.btn_save')}</button>
{msg&&<span style={{fontSize:12,color:'var(--success)'}}>{msg}</span>}</div></div>
<div><div className="card"><div className="card-title">{t('costs.card_calc')}</div><div className="form-grid">
<div className="form-group"><label className="form-label">{t('c.recipe')}</label><select className="form-select" value={cr} onChange={e=>setCr(e.target.value)}>{recipes.map(r=><option key={r.name} value={r.name}>{r.name}</option>)}</select></div>
<div className="form-group"><label className="form-label">{t('c.water_profile')}</label><select className="form-select" value={cw} onChange={e=>setCw(e.target.value)}>{wp.map(w=><option key={w.name} value={w.name}>{td(w.name)}</option>)}</select></div></div>
<button className="btn btn-primary" style={{marginTop:12}} onClick={calcC}>{t('costs.btn_calc')}</button></div>
{res&&(<div className="card"><div className="card-title">{t('costs.card_result')}</div><div className="stats-grid" style={{marginBottom:14}}>
<div className="stat-item"><div className="stat-label">{t('costs.stat_total')}</div><div className="stat-value">{fmt(res.total_cost,2)} €</div></div>
<div className="stat-item"><div className="stat-label">{t('costs.stat_per_l')}</div><div className="stat-value">{fmt(res.cost_per_liter,4)} €</div></div></div>
<table className="result-table"><thead><tr><th>{t('calc.col_salt')}</th><th style={{textAlign:'right'}}>g</th><th style={{textAlign:'right'}}>€/kg</th><th style={{textAlign:'right'}}>{t('costs.stat_total')}</th></tr></thead>
<tbody>{[...res.tank_a,...res.tank_b].filter(s=>s.g_total>0).map(s=>(<tr key={s.salt_formula}><td style={{fontSize:12}}>{td(s.salt_name)}</td>
<td className="num">{fmt(s.g_total,1)}</td><td className="num" style={{color:'var(--text-muted)'}}>{costs[s.salt_formula]?fmt(costs[s.salt_formula],1):'–'}</td>
<td className="num" style={{fontWeight:600}}>{s.cost_total>0?fmt(s.cost_total,3)+' €':'–'}</td></tr>))}</tbody></table></div>)}</div></div></div>)}
