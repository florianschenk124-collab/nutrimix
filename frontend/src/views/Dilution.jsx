import { useState, useEffect } from 'react'
import { useI18n } from '../hooks/useI18n'
import { fetchRecipes, fetchWaterProfiles, calculate, calcDilution } from '../api'
export default function Dilution(){const{t,td}=useI18n();const[recipes,setRecipes]=useState([]);const[wp,setWp]=useState([]);const[params,setParams]=useState({recipe_name:'',water_profile_name:'Osmosewasser',concentrate_factor:100,target_ec:1.5,volume_l:10,water_ec:0,dose_ratio:'1:1'});const[cr,setCr]=useState(null);const[dr,setDr]=useState(null);const[dt,setDt]=useState([]);const[loading,setLoading]=useState(false)
useEffect(()=>{Promise.all([fetchRecipes(),fetchWaterProfiles()]).then(([r,w])=>{setRecipes(r);setWp(w);if(r.length>0)setParams(prev=>({...prev,recipe_name:r[0].name}))})},[])
const set=(k,v)=>setParams(prev=>({...prev,[k]:v}))
const doC=async()=>{setLoading(true);try{const full=await calculate({recipe_name:params.recipe_name,water_profile_name:params.water_profile_name,volume_l:1000,concentrate_factor:params.concentrate_factor,dose_ratio:params.dose_ratio});setCr(full)
const dil=await calcDilution({target_ec:params.target_ec,base_ec:full.ec_ionic,concentrate_factor:params.concentrate_factor,volume_l:params.volume_l,water_ec:params.water_ec,dose_ratio_a:full.dose_ratio_a,dose_ratio_b:full.dose_ratio_b,achieved_mg:full.achieved_mg});setDr(dil)
const tb=[];for(const ec of[0.5,0.8,1.0,1.2,1.5,1.8,2.0,2.5,3.0]){if(ec<=full.ec_ionic){const d=await calcDilution({target_ec:ec,base_ec:full.ec_ionic,concentrate_factor:params.concentrate_factor,volume_l:params.volume_l,water_ec:params.water_ec,dose_ratio_a:full.dose_ratio_a,dose_ratio_b:full.dose_ratio_b,achieved_mg:full.achieved_mg});tb.push({ec,...d})}};setDt(tb)}catch(e){console.error(e)};setLoading(false)}
const fmt=(v,d=2)=>Number(v).toFixed(d)
return(<div><div className="page-header"><h1 className="page-title">{t('dil.title')}</h1><p className="page-subtitle">{t('dil.subtitle')}</p></div>
<div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
<div className="card"><div className="card-title">{t('dil.card_stock')}</div><div className="form-grid">
<div className="form-group"><label className="form-label">{t('c.recipe')}</label><select className="form-select" value={params.recipe_name} onChange={e=>set('recipe_name',e.target.value)}>{recipes.map(r=><option key={r.name} value={r.name}>{r.name}</option>)}</select></div>
<div className="form-group"><label className="form-label">{t('c.water_profile')}</label><select className="form-select" value={params.water_profile_name} onChange={e=>set('water_profile_name',e.target.value)}>{wp.map(w=><option key={w.name} value={w.name}>{td(w.name)}</option>)}</select></div>
<div className="form-group"><label className="form-label">{t('c.conc_factor')}</label><input className="form-input" type="number" value={params.concentrate_factor} onChange={e=>set('concentrate_factor',Number(e.target.value))}/></div></div></div>
<div className="card"><div className="card-title">{t('dil.card_dilution')}</div><div className="form-grid">
<div className="form-group"><label className="form-label">{t('dil.target_ec')}</label><input className="form-input" type="number" step="0.1" value={params.target_ec} onChange={e=>set('target_ec',Number(e.target.value))}/></div>
<div className="form-group"><label className="form-label">{t('c.volume_l')}</label><input className="form-input" type="number" value={params.volume_l} onChange={e=>set('volume_l',Number(e.target.value))}/></div>
<div className="form-group"><label className="form-label">{t('dil.water_ec')}</label><input className="form-input" type="number" step="0.01" value={params.water_ec} onChange={e=>set('water_ec',Number(e.target.value))}/></div></div></div></div>
<div style={{marginBottom:24}}><button className="btn btn-primary" onClick={doC} disabled={loading||!params.recipe_name}>{loading?<span className="spinner"/>:null} {t('dil.btn')}</button></div>
{dr&&(<div><div className="card"><div className="card-title">{t('dil.card_dosing')}</div><div className="stats-grid">
<div className="stat-item"><div className="stat-label">{t('dil.tank_a_per_l')}</div><div className="stat-value">{fmt(dr.ml_a_per_liter)} mL</div></div>
<div className="stat-item"><div className="stat-label">{t('dil.tank_b_per_l')}</div><div className="stat-value">{fmt(dr.ml_b_per_liter)} mL</div></div>
<div className="stat-item"><div className="stat-label">{t('dil.tank_a_total')}</div><div className="stat-value">{fmt(dr.ml_a_total,1)} mL</div></div>
<div className="stat-item"><div className="stat-label">{t('dil.tank_b_total')}</div><div className="stat-value">{fmt(dr.ml_b_total,1)} mL</div></div>
<div className="stat-item"><div className="stat-label">{t('dil.ec_achieved')}</div><div className="stat-value success">{fmt(dr.achieved_ec)} mS/cm</div></div>
<div className="stat-item"><div className="stat-label">{t('dil.factor')}</div><div className="stat-value">{fmt(dr.dilution_factor,3)}</div></div></div></div>
{dt.length>0&&(<div className="card"><div className="card-title">{t('dil.card_table')}</div>
<table className="result-table"><thead><tr><th style={{textAlign:'right'}}>EC (mS/cm)</th><th style={{textAlign:'right'}}>mL A/L</th><th style={{textAlign:'right'}}>mL B/L</th><th style={{textAlign:'right'}}>mL A ges.</th><th style={{textAlign:'right'}}>mL B ges.</th></tr></thead>
<tbody>{dt.map(r=>(<tr key={r.ec} style={{background:Math.abs(r.ec-params.target_ec)<0.05?'var(--accent-bg)':undefined}}>
<td className="num" style={{fontWeight:600}}>{fmt(r.ec,1)}</td><td className="num">{fmt(r.ml_a_per_liter)}</td><td className="num">{fmt(r.ml_b_per_liter)}</td><td className="num">{fmt(r.ml_a_total,1)}</td><td className="num">{fmt(r.ml_b_total,1)}</td></tr>))}</tbody></table></div>)}
{Object.keys(dr.diluted_mg).length>0&&(<div className="card"><div className="card-title">{t('dil.card_ions')}</div>
<table className="result-table"><thead><tr><th>{t('calc.col_ion')}</th><th style={{textAlign:'right'}}>{t('dil.col_diluted')}</th></tr></thead>
<tbody>{Object.entries(dr.diluted_mg).filter(([,v])=>v>0.01).sort((a,b)=>b[1]-a[1]).map(([i,v])=><tr key={i}><td style={{fontWeight:600}}>{i}</td><td className="num">{fmt(v)}</td></tr>)}</tbody></table></div>)}</div>)}</div>)}
