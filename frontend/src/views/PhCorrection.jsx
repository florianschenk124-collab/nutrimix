import { useState, useEffect } from 'react'
import { useI18n } from '../hooks/useI18n'
import { fetchAcids, fetchBases, fetchRecipes, fetchWaterProfiles, calcPhCorrection, calculate } from '../api'
const BI=[{ion:'H2PO4',name:'H₂PO₄⁻/HPO₄²⁻',pka:7.2,color:'#d45f5f'},{ion:'NH4',name:'NH₄⁺/NH₃',pka:9.25,color:'#e0a458'},{ion:'HCO3',name:'HCO₃⁻/CO₃²⁻',pka:6.35,color:'#5b9bd5'},{ion:'SO4',name:'SO₄²⁻',pka:null,color:'#c77dba'}]
export default function PhCorrection(){const{t,td}=useI18n();const[acids,setAcids]=useState([]);const[recipes,setRecipes]=useState([]);const[wp,setWp]=useState([])
const[params,setParams]=useState({water_hco3_mg:140,water_ph:7.4,target_ph:5.8,volume_l:1000,acid_name:'HNO3_65',base_name:null})
const[result,setResult]=useState(null);const[loading,setLoading]=useState(false);const[sr,setSr]=useState('');const[sw,setSw]=useState('');const[bd,setBd]=useState(null)
useEffect(()=>{Promise.all([fetchAcids(),fetchBases(),fetchRecipes(),fetchWaterProfiles()]).then(([a,b,r,w])=>{setAcids(a);setRecipes(r);setWp(w)})},[])
const set=(k,v)=>setParams(prev=>({...prev,[k]:v}));const fmt=(v,d=2)=>Number(v).toFixed(d)
const doC=async()=>{setLoading(true);try{setResult(await calcPhCorrection(params))}catch{setResult(null)};setLoading(false)}
const calcB=async()=>{if(!sr)return;try{const res=await calculate({recipe_name:sr,water_profile_name:sw||'Osmosewasser',volume_l:1000,concentrate_factor:100})
const ions={...res.achieved_mg};const water=res.water_mg||{};for(const k of Object.keys(water))ions[k]=(ions[k]||0)+(water[k]||0)
const bufs=[];for(const bi of BI){const mg=bi.ion==='HCO3'?params.water_hco3_mg:(ions[bi.ion]||0);if(mg<=0&&bi.ion!=='HCO3')continue
const mm=bi.ion==='H2PO4'?96.99:bi.ion==='NH4'?18.04:bi.ion==='HCO3'?61.02:bi.ion==='SO4'?96.06:1;const mmol=mg/mm;let bc=0
if(bi.pka!==null){const H=Math.pow(10,-params.target_ph),Ka=Math.pow(10,-bi.pka);bc=2.303*mmol*Ka*H/Math.pow(Ka+H,2)}
bufs.push({...bi,mg,mmol,bufferCap:bc})};const tot=bufs.reduce((s,b)=>s+b.bufferCap,0);setBd({buffers:bufs,totalBuffer:tot,ions})}catch(e){console.error(e);setBd(null)}}
return(<div><div className="page-header"><h1 className="page-title">{t('ph.title')}</h1><p className="page-subtitle">{t('ph.subtitle')}</p></div>
<div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
<div className="card"><div className="card-title">{t('ph.card_params')}</div><div className="form-grid">
<div className="form-group"><label className="form-label">{t('ph.hco3')}</label><input className="form-input" type="number" step="1" value={params.water_hco3_mg} onChange={e=>set('water_hco3_mg',Number(e.target.value))}/></div>
<div className="form-group"><label className="form-label">{t('ph.water_ph')}</label><input className="form-input" type="number" step="0.1" value={params.water_ph} onChange={e=>set('water_ph',Number(e.target.value))}/></div>
<div className="form-group"><label className="form-label">{t('ph.target_ph')}</label><input className="form-input" type="number" step="0.1" value={params.target_ph} onChange={e=>set('target_ph',Number(e.target.value))}/></div>
<div className="form-group"><label className="form-label">{t('c.volume_l')}</label><input className="form-input" type="number" value={params.volume_l} onChange={e=>set('volume_l',Number(e.target.value))}/></div></div></div>
<div className="card"><div className="card-title">{t('ph.card_acid_base')}</div><div className="form-group"><label className="form-label">{t('ph.acid')}</label>
<select className="form-select" value={params.acid_name} onChange={e=>set('acid_name',e.target.value)}>{acids.map(a=><option key={a.key} value={a.key}>{td(a.name)} ({a.formula})</option>)}</select></div></div></div>
<div style={{marginBottom:24}}><button className="btn btn-primary" onClick={doC} disabled={loading}>{loading?<span className="spinner"/>:null} {t('ph.btn')}</button></div>
{result&&(<div><div className="card"><div className="card-title">{t('ph.card_result')}</div><div className="stats-grid">
{result.acid_ml>0&&(<><div className="stat-item"><div className="stat-label">{result.acid_name}</div><div className="stat-value">{fmt(result.acid_ml_per_l,3)} mL/L</div></div>
<div className="stat-item"><div className="stat-label">{t('ph.col_total')} ({params.volume_l} L)</div><div className="stat-value">{fmt(result.acid_ml,1)} mL</div></div></>)}
{result.base_ml>0&&(<><div className="stat-item"><div className="stat-label">{result.base_name}</div><div className="stat-value">{fmt(result.base_ml_per_l,3)} mL/L</div></div>
<div className="stat-item"><div className="stat-label">{t('ph.col_total')} ({params.volume_l} L)</div><div className="stat-value">{fmt(result.base_ml,1)} mL</div></div></>)}</div>
{Object.keys(result.ion_changes_mg).length>0&&(<div style={{marginTop:16}}><div className="card-title" style={{fontSize:12}}>{t('ph.extra_ions')}</div>
<table className="result-table"><thead><tr><th>{t('calc.col_ion')}</th><th style={{textAlign:'right'}}>{t('ph.col_addition')}</th></tr></thead>
<tbody>{Object.entries(result.ion_changes_mg).filter(([,v])=>Math.abs(v)>0.01).map(([i,v])=><tr key={i}><td style={{fontWeight:600}}>{i}</td><td className="num" style={{color:'var(--info)'}}>+{fmt(v)}</td></tr>)}</tbody></table></div>)}</div>
{result.steps.length>0&&<div className="card"><div className="card-title">{t('ph.card_steps')}</div>{result.steps.map((s,i)=><div className="protocol-step" key={i}>{s}</div>)}</div>}
{result.warnings.length>0&&<div className="card"><div className="card-title">{t('ph.card_notes')}</div>{result.warnings.map((w,i)=><div className="alert alert-warning" key={i}>{w}</div>)}</div>}</div>)}
<div className="card" style={{marginTop:24}}><div className="card-title">{t('ph.buf_title')}</div>
<p style={{fontSize:12,color:'var(--text-secondary)',marginBottom:12}}>{t('ph.buf_desc')}</p>
<div className="form-grid"><div className="form-group"><label className="form-label">{t('c.recipe')}</label>
<select className="form-select" value={sr} onChange={e=>setSr(e.target.value)}><option value="">{t('ph.buf_select')}</option>{recipes.map(r=><option key={r.name} value={r.name}>{td(r.name)}</option>)}</select></div>
<div className="form-group"><label className="form-label">{t('c.water_profile')}</label>
<select className="form-select" value={sw} onChange={e=>setSw(e.target.value)}><option value="">Osmosewasser</option>{wp.map(w=><option key={w.name} value={w.name}>{td(w.name)}</option>)}</select></div></div>
<button className="btn btn-primary" style={{marginTop:12}} onClick={calcB} disabled={!sr}>{t('ph.buf_btn')}</button>
{bd&&(<div style={{marginTop:16}}><div className="stats-grid" style={{marginBottom:14}}>
<div className="stat-item"><div className="stat-label">{t('ph.buf_total')}</div><div className="stat-value" style={{fontSize:14}}>{fmt(bd.totalBuffer,4)} mol/L·pH</div></div>
<div className="stat-item"><div className="stat-label">{t('ph.buf_rating')}</div><div className={`stat-value ${bd.totalBuffer>0.005?'success':bd.totalBuffer>0.001?'warning':'error'}`} style={{fontSize:14}}>{bd.totalBuffer>0.005?t('ph.buf_good'):bd.totalBuffer>0.001?t('ph.buf_moderate'):t('ph.buf_weak')}</div></div></div>
<table className="result-table"><thead><tr><th>{t('ph.buf_col_system')}</th><th style={{textAlign:'right'}}>{t('gen.mg_l')}</th><th style={{textAlign:'right'}}>{t('gen.mmol_l')}</th><th style={{textAlign:'right'}}>pKa</th><th style={{textAlign:'right'}}>β</th><th>{t('ph.buf_col_contrib')}</th></tr></thead>
<tbody>{bd.buffers.map(b=>{const pct=bd.totalBuffer>0?(b.bufferCap/bd.totalBuffer*100):0;return(<tr key={b.ion}><td><span style={{color:b.color,fontWeight:600}}>{b.name}</span></td>
<td className="num">{fmt(b.mg,1)}</td><td className="num">{fmt(b.mmol,3)}</td><td className="num">{b.pka!==null?fmt(b.pka,2):'–'}</td><td className="num" style={{fontWeight:600}}>{fmt(b.bufferCap,5)}</td>
<td><div style={{display:'flex',alignItems:'center',gap:6}}><div style={{width:60,height:6,background:'var(--bg-input)',borderRadius:3,overflow:'hidden'}}><div style={{width:`${Math.min(100,pct)}%`,height:'100%',background:b.color,borderRadius:3}}/></div><span style={{fontSize:11,color:'var(--text-muted)'}}>{fmt(pct,0)}%</span></div></td></tr>)})}</tbody></table></div>)}</div></div>)}
