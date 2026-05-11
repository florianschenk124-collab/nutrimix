import { useState, useEffect } from 'react'
import { useI18n } from '../hooks/useI18n'
import { fetchRecipes, createRecipe } from '../api'
const MF=[{key:'no3_n',label:'NO₃-N'},{key:'nh4_n',label:'NH₄-N'},{key:'p',label:'P'},{key:'k',label:'K'},{key:'ca',label:'Ca'},{key:'mg',label:'Mg'},{key:'s',label:'S'}]
const MIF=[{key:'fe',label:'Fe'},{key:'mn',label:'Mn'},{key:'zn',label:'Zn'},{key:'cu',label:'Cu'},{key:'b',label:'B'},{key:'mo',label:'Mo'}]
const E={name:'',description:'',no3_n:0,nh4_n:0,p:0,k:0,ca:0,mg:0,s:0,fe:0,mn:0,zn:0,cu:0,b:0,mo:0,ph_min:5.5,ph_max:6.5,ec_target:0,suitable_plants:[],source:''}
export default function RecipeEditor(){const{t,td}=useI18n();const[recipes,setRecipes]=useState([]);const[form,setForm]=useState({...E});const[template,setTemplate]=useState('');const[plantsStr,setPlantsStr]=useState('');const[saving,setSaving]=useState(false);const[msg,setMsg]=useState('')
useEffect(()=>{fetchRecipes().then(setRecipes)},[])
const set=(k,v)=>setForm(prev=>({...prev,[k]:v}))
const loadT=(name)=>{setTemplate(name);if(!name){setForm({...E});setPlantsStr('');return};const r=recipes.find(x=>x.name===name);if(r){setForm({name:r.name+' (Copy)',description:r.description,no3_n:r.no3_n,nh4_n:r.nh4_n,p:r.p,k:r.k,ca:r.ca,mg:r.mg,s:r.s,fe:r.fe,mn:r.mn,zn:r.zn,cu:r.cu,b:r.b,mo:r.mo,ph_min:r.ph_min,ph_max:r.ph_max,ec_target:r.ec_target,suitable_plants:r.suitable_plants,source:r.source});setPlantsStr(r.suitable_plants.join(', '))}}
const save=async()=>{if(!form.name.trim()){setMsg(t('editor.err_name'));return};setSaving(true);try{await createRecipe({...form,suitable_plants:plantsStr.split(',').map(s=>s.trim()).filter(Boolean)});setMsg(t('editor.saved'));setRecipes(await fetchRecipes())}catch(e){setMsg(t('gen.error')+': '+e.message)};setSaving(false)}
return(<div><div className="page-header"><h1 className="page-title">{t('editor.title')}</h1><p className="page-subtitle">{t('editor.subtitle')}</p></div>
<div className="card"><div className="card-title">{t('editor.card_template')}</div>
<div className="form-group" style={{maxWidth:300}}><label className="form-label">{t('editor.template')}</label>
<select className="form-select" value={template} onChange={e=>loadT(e.target.value)}><option value="">{t('editor.empty')}</option>
{recipes.map(r=><option key={r.name} value={r.name}>{r.name}</option>)}</select></div></div>
<div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
<div className="card"><div className="card-title">{t('editor.card_info')}</div><div className="form-grid">
<div className="form-group" style={{gridColumn:'1/-1'}}><label className="form-label">{t('editor.name')}</label><input className="form-input" value={form.name} placeholder={t('editor.name_ph')} onChange={e=>set('name',e.target.value)}/></div>
<div className="form-group" style={{gridColumn:'1/-1'}}><label className="form-label">{t('editor.desc')}</label><input className="form-input" value={form.description} placeholder={t('editor.desc_ph')} onChange={e=>set('description',e.target.value)}/></div>
<div className="form-group"><label className="form-label">{t('editor.ph_min')}</label><input className="form-input" type="number" step="0.1" value={form.ph_min} onChange={e=>set('ph_min',Number(e.target.value))}/></div>
<div className="form-group"><label className="form-label">{t('editor.ph_max')}</label><input className="form-input" type="number" step="0.1" value={form.ph_max} onChange={e=>set('ph_max',Number(e.target.value))}/></div>
<div className="form-group"><label className="form-label">{t('editor.ec_target')}</label><input className="form-input" type="number" step="0.1" value={form.ec_target} onChange={e=>set('ec_target',Number(e.target.value))}/></div>
<div className="form-group"><label className="form-label">{t('editor.source')}</label><input className="form-input" value={form.source} placeholder={t('editor.source_ph')} onChange={e=>set('source',e.target.value)}/></div>
<div className="form-group" style={{gridColumn:'1/-1'}}><label className="form-label">{t('editor.plants')}</label><input className="form-input" value={plantsStr} onChange={e=>setPlantsStr(e.target.value)} placeholder={t('editor.plants_ph')}/></div></div></div>
<div><div className="card"><div className="card-title">{t('editor.card_macros')}</div><div className="form-grid">{MF.map(({key,label})=>(<div className="form-group" key={key}><label className="form-label">{label}</label><input className="form-input" type="number" step="0.1" value={form[key]} onChange={e=>set(key,Number(e.target.value))}/></div>))}</div></div>
<div className="card"><div className="card-title">{t('editor.card_micros')}</div><div className="form-grid">{MIF.map(({key,label})=>(<div className="form-group" key={key}><label className="form-label">{label}</label><input className="form-input" type="number" step="0.001" value={form[key]} onChange={e=>set(key,Number(e.target.value))}/></div>))}</div></div></div></div>
<div style={{display:'flex',alignItems:'center',gap:16,marginTop:8}}><button className="btn btn-primary" onClick={save} disabled={saving}>{t('editor.btn_save')}</button>
{msg&&<span style={{fontSize:13,color:msg.includes('⚠')?'var(--error)':'var(--success)'}}>{msg}</span>}</div></div>)}
