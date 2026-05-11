import { useState, useEffect } from 'react'
import { useI18n } from '../hooks/useI18n'
import { fetchRecipes, fetchWaterProfiles, calculate } from '../api'
export default function Labels(){const{t,td}=useI18n();const[recipes,setRecipes]=useState([]);const[wp,setWp]=useState([]);const[params,setParams]=useState({recipe_name:'',water_profile_name:'Osmosewasser',concentrate_factor:100,volume_l:10,note:''});const[result,setResult]=useState(null);const[loading,setLoading]=useState(false)
useEffect(()=>{Promise.all([fetchRecipes(),fetchWaterProfiles()]).then(([r,w])=>{setRecipes(r);setWp(w);if(r.length>0)setParams(prev=>({...prev,recipe_name:r[0].name}))})},[])
const set=(k,v)=>setParams(prev=>({...prev,[k]:v}))
const gen=async()=>{setLoading(true);try{setResult(await calculate({recipe_name:params.recipe_name,water_profile_name:params.water_profile_name,volume_l:1000,concentrate_factor:params.concentrate_factor}))}catch(e){console.error(e)};setLoading(false)}
const today=new Date().toLocaleDateString();const fmt=(v,d=1)=>Number(v).toFixed(d);const recipe=recipes.find(r=>r.name===params.recipe_name)
return(<div><div className="page-header"><h1 className="page-title">{t('labels.title')}</h1><p className="page-subtitle">{t('labels.subtitle')}</p></div>
<div className="card"><div className="card-title">{t('labels.card_settings')}</div><div className="form-grid">
<div className="form-group"><label className="form-label">{t('c.recipe')}</label><select className="form-select" value={params.recipe_name} onChange={e=>set('recipe_name',e.target.value)}>{recipes.map(r=><option key={r.name} value={r.name}>{td(r.name)}</option>)}</select></div>
<div className="form-group"><label className="form-label">{t('c.water_profile')}</label><select className="form-select" value={params.water_profile_name} onChange={e=>set('water_profile_name',e.target.value)}>{wp.map(w=><option key={w.name} value={w.name}>{td(w.name)}</option>)}</select></div>
<div className="form-group"><label className="form-label">{t('c.conc_factor')}</label><input className="form-input" type="number" value={params.concentrate_factor} onChange={e=>set('concentrate_factor',Number(e.target.value))}/></div>
<div className="form-group"><label className="form-label">{t('labels.tank_vol')}</label><input className="form-input" type="number" value={params.volume_l} onChange={e=>set('volume_l',Number(e.target.value))}/></div>
<div className="form-group" style={{gridColumn:'1/-1'}}><label className="form-label">{t('labels.note')}</label><input className="form-input" value={params.note} onChange={e=>set('note',e.target.value)} placeholder="..."/></div></div>
<div style={{marginTop:14,display:'flex',gap:12}}><button className="btn btn-primary" onClick={gen} disabled={loading}>{loading?<span className="spinner"/>:null} {t('labels.btn_generate')}</button>
{result&&<button className="btn" style={{border:'1px solid var(--border-default)',color:'var(--text-secondary)'}} onClick={()=>window.print()}>🖨️ {t('labels.btn_print')}</button>}</div></div>
{result&&(<div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}} id="print-area">
<LC t={t} tank="A" color="var(--tank-a)" rn={params.recipe_name} water={params.water_profile_name} factor={params.concentrate_factor} tv={params.volume_l} date={today} note={params.note} salts={result.tank_a} ec={result.ec_ionic} ph={recipe?`${recipe.ph_min}–${recipe.ph_max}`:'–'} dA={result.dose_ratio_a} dB={result.dose_ratio_b}/>
<LC t={t} tank="B" color="var(--tank-b)" rn={params.recipe_name} water={params.water_profile_name} factor={params.concentrate_factor} tv={params.volume_l} date={today} note={params.note} salts={result.tank_b} ec={result.ec_ionic} ph={recipe?`${recipe.ph_min}–${recipe.ph_max}`:'–'} dA={result.dose_ratio_a} dB={result.dose_ratio_b}/></div>)}
<style>{`@media print{body *{visibility:hidden}#print-area,#print-area *{visibility:visible}#print-area{position:absolute;top:0;left:0;width:100%;display:grid;grid-template-columns:1fr 1fr;gap:12px}.label-card{border:2px solid #333!important;background:white!important;color:black!important}}`}</style></div>)}
function LC({t,tank,color,rn,water,factor,tv,date,note,salts,ec,ph,dA,dB}){const fmt=(v,d=1)=>Number(v).toFixed(d);const ml=1000/factor;const oT=tank==='A'?'B':'A'
return(<div className="card label-card" style={{borderColor:color,borderWidth:2}}>
<div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:12}}>
<div style={{display:'flex',alignItems:'center',gap:10}}><span className={`tank-badge tank-${tank.toLowerCase()}`} style={{width:36,height:36,fontSize:16}}>{tank}</span>
<div><div style={{fontSize:16,fontWeight:700}}>Tank {tank}</div><div style={{fontSize:11,color:'var(--text-muted)'}}>{tank==='A'?t('labels.tank_a_desc'):t('labels.tank_b_desc')}</div></div></div>
<div style={{textAlign:'right',fontSize:11,color:'var(--text-secondary)'}}><div>{date}</div><div>{factor}x {t('labels.concentrate')}</div></div></div>
<div style={{background:'var(--bg-input)',borderRadius:'var(--radius-sm)',padding:'8px 12px',marginBottom:12,fontSize:12}}><div style={{fontWeight:600}}>📋 {rn}</div><div style={{color:'var(--text-muted)'}}>💧 {water}</div></div>
<table className="result-table" style={{marginBottom:12}}><thead><tr><th>{t('calc.col_salt')}</th><th style={{textAlign:'right'}}>g / {tv}L</th></tr></thead>
<tbody>{salts.map(s=><tr key={s.salt_formula}><td style={{fontSize:12}}>{td(s.salt_name)}</td><td className="num" style={{fontWeight:700}}>{fmt(s.g_concentrate*(tv/(1000/factor)),1)}</td></tr>)}</tbody></table>
<div style={{background:'var(--accent-bg)',borderRadius:'var(--radius-sm)',padding:'8px 12px',fontSize:12,marginBottom:8}}>
<div style={{fontWeight:600,marginBottom:4}}>{t('labels.dosing')}</div>
<div>{fmt(ml*(tank==='A'?dA:dB)/(dA+dB)*2)} mL {tank} + {fmt(ml*(tank==='A'?dB:dA)/(dA+dB)*2)} mL {oT} / L</div>
<div style={{color:'var(--text-muted)',marginTop:2}}>EC: ~{fmt(ec,2)} mS/cm · pH: {ph}</div></div>
<div style={{fontSize:10,color:'var(--warning)',marginBottom:4}}>{t('labels.no_mix')}</div>
{note&&<div style={{fontSize:11,color:'var(--text-secondary)',fontStyle:'italic'}}>📝 {note}</div>}</div>)}
