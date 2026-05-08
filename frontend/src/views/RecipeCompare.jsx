import { useState, useEffect } from 'react'
import { useI18n } from '../hooks/useI18n'
import { fetchRecipes } from '../api'
const ALL_IONS=['NO3','NH4','H2PO4','K','Ca','Mg','SO4','Fe','Mn','Zn','Cu','B','Mo']
export default function RecipeCompare(){const{t}=useI18n();const[recipes,setRecipes]=useState([]);const[nameA,setNameA]=useState('');const[nameB,setNameB]=useState('');const[compared,setCompared]=useState(null)
useEffect(()=>{fetchRecipes().then(r=>{setRecipes(r);if(r.length>=2){setNameA(r[0].name);setNameB(r[1].name)}else if(r.length===1){setNameA(r[0].name);setNameB(r[0].name)}})},[])
const doC=()=>{const a=recipes.find(r=>r.name===nameA),b=recipes.find(r=>r.name===nameB);if(a&&b)setCompared({a,b})}
const fmt=v=>v>0?Number(v).toFixed(2):'–'
const pct=(a,b)=>{if(!b||b===0)return'';const d=((a-b)/b*100);if(Math.abs(d)<0.5)return'';return d>0?`+${d.toFixed(0)}%`:`${d.toFixed(0)}%`}
const dC=(a,b)=>{if(!b||b===0)return'var(--text-muted)';const d=Math.abs((a-b)/b*100);return d<5?'var(--success)':d<20?'var(--warning)':'var(--error)'}
return(<div><div className="page-header"><h1 className="page-title">{t('compare.title')}</h1><p className="page-subtitle">{t('compare.subtitle')}</p></div>
<div className="card" style={{display:'flex',gap:16,alignItems:'flex-end',flexWrap:'wrap'}}>
<div className="form-group" style={{flex:1,minWidth:200}}><label className="form-label">{t('compare.recipe_a')}</label><select className="form-select" value={nameA} onChange={e=>setNameA(e.target.value)}>{recipes.map(r=><option key={r.name} value={r.name}>{r.name}</option>)}</select></div>
<div style={{color:'var(--text-muted)',fontSize:18,paddingBottom:8}}>⇄</div>
<div className="form-group" style={{flex:1,minWidth:200}}><label className="form-label">{t('compare.recipe_b')}</label><select className="form-select" value={nameB} onChange={e=>setNameB(e.target.value)}>{recipes.map(r=><option key={r.name} value={r.name}>{r.name}</option>)}</select></div>
<button className="btn btn-primary" onClick={doC}>{t('compare.btn')}</button></div>
{compared&&(<div><div className="card"><div className="card-title">{t('compare.card_ions')}</div>
<table className="result-table"><thead><tr><th>{t('calc.col_ion')}</th><th style={{textAlign:'right',color:'var(--tank-a)'}}>{compared.a.name}</th><th style={{textAlign:'right',color:'var(--tank-b)'}}>{compared.b.name}</th><th style={{textAlign:'right'}}>Δ</th></tr></thead>
<tbody>{ALL_IONS.filter(i=>(compared.a.ions_mg[i]||0)>0||(compared.b.ions_mg[i]||0)>0).map(i=>{const a=compared.a.ions_mg[i]||0,b=compared.b.ions_mg[i]||0
return(<tr key={i}><td style={{fontWeight:600}}>{i}</td><td className="num" style={{color:'var(--tank-a)'}}>{fmt(a)}</td><td className="num" style={{color:'var(--tank-b)'}}>{fmt(b)}</td><td className="num" style={{color:dC(a,b),fontWeight:500}}>{pct(a,b)}</td></tr>)})}</tbody></table></div>
<div className="card"><div className="card-title">{t('compare.card_visual')}</div>
{['NO3','K','Ca','Mg','SO4','H2PO4'].map(i=>{const a=compared.a.ions_mg[i]||0,b=compared.b.ions_mg[i]||0,m=Math.max(a,b,1)
return(<div key={i} style={{marginBottom:10}}><div style={{fontSize:12,fontWeight:600,color:'var(--text-secondary)',marginBottom:4}}>{i}</div>
<div style={{display:'flex',gap:8,alignItems:'center'}}><div style={{flex:1,height:8,background:'var(--bg-input)',borderRadius:4,overflow:'hidden'}}><div style={{width:`${(a/m)*100}%`,height:'100%',background:'var(--tank-a)',borderRadius:4}}/></div><span className="num" style={{fontSize:11,width:50,color:'var(--tank-a)'}}>{fmt(a)}</span></div>
<div style={{display:'flex',gap:8,alignItems:'center',marginTop:2}}><div style={{flex:1,height:8,background:'var(--bg-input)',borderRadius:4,overflow:'hidden'}}><div style={{width:`${(b/m)*100}%`,height:'100%',background:'var(--tank-b)',borderRadius:4}}/></div><span className="num" style={{fontSize:11,width:50,color:'var(--tank-b)'}}>{fmt(b)}</span></div></div>)})}</div></div>)}</div>)}
