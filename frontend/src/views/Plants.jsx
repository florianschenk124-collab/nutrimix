import { useState, useEffect } from 'react'
import { useI18n } from '../hooks/useI18n'
import { fetchPlants, fetchRecipes } from '../api'
const CATEGORY_FILTERS=[{key:'',locale:'plants.filter_all'},{key:'Fruchtgemüse',locale:'plants.filter_fruit'},{key:'Blattgemüse',locale:'plants.filter_leafy'},{key:'Kohlgemüse',locale:'plants.filter_brassica'},{key:'Kräuter',locale:'plants.filter_herbs'},{key:'Sonstiges',locale:'plants.filter_other'}]
const CATEGORIES=['Fruchtgemüse','Blattgemüse','Kohlgemüse','Kräuter','Wurzelgemüse','Sonstiges','Beeren']
const EMPTY={name:'',category:'Fruchtgemüse',ec_min:1.0,ec_max:2.5,ph_min:5.5,ph_max:6.5,notes:'',keywords:[]}
export default function Plants(){const{t}=useI18n();const[plants,setPlants]=useState([]);const[recipes,setRecipes]=useState([]);const[selected,setSelected]=useState(null);const[filter,setFilter]=useState('');const[search,setSearch]=useState('');const[showAdd,setShowAdd]=useState(false);const[form,setForm]=useState({...EMPTY});const[keywordsStr,setKeywordsStr]=useState('');const[msg,setMsg]=useState('')
const load=()=>{Promise.all([fetchPlants(),fetchRecipes()]).then(([p,r])=>{setPlants(p);setRecipes(r)})}
useEffect(load,[])
const filtered=plants.filter(p=>{if(filter&&p.category!==filter)return false;if(search)return p.name.toLowerCase().includes(search.toLowerCase());return true})
const getMatch=(plant)=>{if(!plant.keywords?.length)return[];return recipes.filter(r=>r.suitable_plants?.some(sp=>plant.keywords.some(kw=>sp.toLowerCase().includes(kw.toLowerCase()))))}
const setF=(k,v)=>setForm(prev=>({...prev,[k]:v}))
const saveNew=async()=>{if(!form.name.trim())return;try{await fetch('/api/plants',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...form,keywords:keywordsStr.split(',').map(s=>s.trim()).filter(Boolean)})});setMsg('✅');setShowAdd(false);setForm({...EMPTY});setKeywordsStr('');load()}catch(e){setMsg(t('gen.error')+': '+e.message)}}
return(<div><div className="page-header"><h1 className="page-title">{t('plants.title')}</h1><p className="page-subtitle">{t('plants.subtitle')}</p></div>
<div className="card" style={{display:'flex',gap:10,alignItems:'center',flexWrap:'wrap'}}>
{CATEGORY_FILTERS.map(f=>(<button key={f.key} className="btn" style={{padding:'5px 12px',fontSize:12,background:filter===f.key?'var(--accent-bg-hover)':'var(--bg-input)',color:filter===f.key?'var(--text-accent)':'var(--text-secondary)',border:`1px solid ${filter===f.key?'var(--accent)':'var(--border-subtle)'}`}} onClick={()=>setFilter(f.key)}>{t(f.locale)}</button>))}
<input className="form-input" placeholder={t('c.search_plant')} value={search} onChange={e=>setSearch(e.target.value)} style={{maxWidth:180,marginLeft:'auto'}}/>
<button className="btn btn-primary" style={{padding:'6px 14px',fontSize:12}} onClick={()=>setShowAdd(!showAdd)}>{showAdd?'✕':t('plants.btn_add')}</button></div>
{showAdd&&(<div className="card"><div className="card-title">{t('plants.add_title')}</div><div className="form-grid">
<div className="form-group"><label className="form-label">{t('plants.name')}</label><input className="form-input" value={form.name} placeholder={t('plants.name_ph')} onChange={e=>setF('name',e.target.value)}/></div>
<div className="form-group"><label className="form-label">{t('plants.category')}</label><select className="form-select" value={form.category} onChange={e=>setF('category',e.target.value)}>{CATEGORIES.map(c=><option key={c} value={c}>{c}</option>)}</select></div>
<div className="form-group"><label className="form-label">EC min</label><input className="form-input" type="number" step="0.1" value={form.ec_min} onChange={e=>setF('ec_min',Number(e.target.value))}/></div>
<div className="form-group"><label className="form-label">EC max</label><input className="form-input" type="number" step="0.1" value={form.ec_max} onChange={e=>setF('ec_max',Number(e.target.value))}/></div>
<div className="form-group"><label className="form-label">pH min</label><input className="form-input" type="number" step="0.1" value={form.ph_min} onChange={e=>setF('ph_min',Number(e.target.value))}/></div>
<div className="form-group"><label className="form-label">pH max</label><input className="form-input" type="number" step="0.1" value={form.ph_max} onChange={e=>setF('ph_max',Number(e.target.value))}/></div>
<div className="form-group" style={{gridColumn:'1/-1'}}><label className="form-label">{t('plants.notes_label')}</label><input className="form-input" value={form.notes} placeholder={t('plants.notes_ph')} onChange={e=>setF('notes',e.target.value)}/></div>
<div className="form-group" style={{gridColumn:'1/-1'}}><label className="form-label">Keywords</label><input className="form-input" value={keywordsStr} placeholder="tomate, tomato" onChange={e=>setKeywordsStr(e.target.value)}/></div>
</div><div style={{marginTop:12,display:'flex',gap:12,alignItems:'center'}}><button className="btn btn-primary" onClick={saveNew}>{t('plants.btn_save')}</button>{msg&&<span style={{fontSize:12,color:'var(--success)'}}>{msg}</span>}</div></div>)}
<div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(280px,1fr))',gap:14}}>
{filtered.map(p=>{const matching=getMatch(p);const isS=selected?.name===p.name;return(
<div key={p.name} className="card" onClick={()=>setSelected(isS?null:p)} style={{cursor:'pointer',borderColor:isS?'var(--accent)':undefined}}>
<div><div style={{fontSize:16,fontWeight:600}}>{p.name}</div><div style={{fontSize:11,color:'var(--text-muted)'}}>{p.category}</div></div>
<div className="stats-grid" style={{marginTop:12,gridTemplateColumns:'1fr 1fr'}}>
<div className="stat-item" style={{padding:'8px 10px'}}><div className="stat-label" style={{fontSize:10}}>EC</div><div className="stat-value" style={{fontSize:13}}>{p.ec_min} – {p.ec_max}</div></div>
<div className="stat-item" style={{padding:'8px 10px'}}><div className="stat-label" style={{fontSize:10}}>pH</div><div className="stat-value" style={{fontSize:13}}>{p.ph_min} – {p.ph_max}</div></div></div>
{isS&&(<div style={{marginTop:12}}>{p.notes&&<div style={{fontSize:12,color:'var(--text-secondary)',marginBottom:10}}>{p.notes}</div>}
{matching.length>0?matching.map(r=>(<div key={r.name} className="alert alert-info" style={{padding:'6px 10px',fontSize:12}}>📋 {r.name} (EC: {r.ec_target||'–'})</div>)):<div style={{fontSize:11,color:'var(--text-muted)',fontStyle:'italic'}}>{t('plants.no_match')}</div>}</div>)}</div>)})}</div></div>)}
