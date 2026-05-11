import { useState, useEffect } from 'react'
import { useI18n } from '../hooks/useI18n'
import { fetchRecipes, fetchWaterProfiles, createRecipe, createWaterProfile } from '../api'
export default function ExportImport(){const{t,td}=useI18n();const[recipes,setRecipes]=useState([]);const[wp,setWp]=useState([]);const[er,setEr]=useState('__all__');const[ew,setEw]=useState('__all__');const[it,setIt]=useState('');const[msg,setMsg]=useState('');const[im,setIm]=useState('')
const reload=()=>{Promise.all([fetchRecipes(),fetchWaterProfiles()]).then(([r,w])=>{setRecipes(r);setWp(w)})};useEffect(reload,[])
const dl=(d,f)=>{const b=new Blob([JSON.stringify(d,null,2)],{type:'application/json'});const u=URL.createObjectURL(b);const a=document.createElement('a');a.href=u;a.download=f;a.click();URL.revokeObjectURL(u)}
const exR=()=>{const d=er==='__all__'?recipes:recipes.filter(r=>r.name===er);dl(d,'nutrientmixer_recipes.json');setMsg(`${d.length} ${t('export.msg_recipes')}`)}
const exW=()=>{const d=ew==='__all__'?wp:wp.filter(w=>w.name===ew);dl(d,'nutrientmixer_water.json');setMsg(`${d.length} ${t('export.msg_water')}`)}
const exA=()=>{dl({recipes,water_profiles:wp,exported_at:new Date().toISOString(),version:'0.5.0'},'nutrientmixer_full.json');setMsg(t('export.msg_full'))}
const hf=e=>{const f=e.target.files[0];if(!f)return;const r=new FileReader();r.onload=ev=>setIt(ev.target.result);r.readAsText(f)}
const doI=async()=>{if(!it.trim()){setIm(t('export.msg_no_data'));return};let d;try{d=JSON.parse(it)}catch{setIm(t('export.msg_bad_json'));return}
let ir=0,iw=0,err=[];if(d.recipes&&d.water_profiles){for(const r of d.recipes){try{await createRecipe(r);ir++}catch(e){err.push(e.message)}};for(const w of d.water_profiles){try{await createWaterProfile(w);iw++}catch(e){err.push(e.message)}}}
else if(Array.isArray(d)){for(const i of d){if(i.no3_n!==undefined){try{await createRecipe(i);ir++}catch(e){err.push(e.message)}}else if(i.hco3!==undefined||i.ec!==undefined){try{await createWaterProfile(i);iw++}catch(e){err.push(e.message)}}}}
else if(d.name){if(d.no3_n!==undefined){try{await createRecipe(d);ir++}catch(e){err.push(e.message)}}else{try{await createWaterProfile(d);iw++}catch(e){err.push(e.message)}}}
let p=[];if(ir>0)p.push(`${ir} ${t('export.msg_recipes')}`);if(iw>0)p.push(`${iw} ${t('export.msg_water')}`);if(err.length>0)p.push(`${err.length} ${t('export.msg_errors')}`);setIm(p.length>0?`${t('export.msg_imported')}: ${p.join(', ')}`:t('export.msg_nothing'));setIt('');reload()}
return(<div><div className="page-header"><h1 className="page-title">{t('export.title')}</h1><p className="page-subtitle">{t('export.subtitle')}</p></div>
<div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:16}}>
<div><div className="card"><div className="card-title">📤 {t('export.card_recipes')}</div>
<div className="form-group" style={{marginBottom:12}}><label className="form-label">{t('c.recipe')}</label><select className="form-select" value={er} onChange={e=>setEr(e.target.value)}><option value="__all__">{t('export.all_label')}</option>{recipes.map(r=><option key={r.name} value={r.name}>{r.name}</option>)}</select></div>
<button className="btn btn-primary" style={{width:'100%'}} onClick={exR}>{t('export.btn_recipe')}</button></div>
<div className="card"><div className="card-title">📤 {t('export.card_water')}</div>
<div className="form-group" style={{marginBottom:12}}><label className="form-label">{t('export.profile')}</label><select className="form-select" value={ew} onChange={e=>setEw(e.target.value)}><option value="__all__">{t('export.all_label')}</option>{wp.map(w=><option key={w.name} value={w.name}>{w.name}</option>)}</select></div>
<button className="btn btn-primary" style={{width:'100%'}} onClick={exW}>{t('export.btn_water')}</button></div>
<div className="card"><div className="card-title">{t('export.card_full')}</div><p style={{fontSize:12,color:'var(--text-secondary)',marginBottom:12}}>{t('export.full_desc')}</p>
<button className="btn btn-primary" style={{width:'100%'}} onClick={exA}>{t('export.btn_full')}</button></div>
{msg&&<div className="alert alert-success">{msg}</div>}</div>
<div><div className="card"><div className="card-title">{t('export.card_import')}</div><p style={{fontSize:12,color:'var(--text-secondary)',marginBottom:12}}>{t('export.import_desc')}</p>
<div className="form-group" style={{marginBottom:12}}><label className="form-label">{t('export.file_label')}</label><input type="file" accept=".json" onChange={hf} style={{fontSize:12,color:'var(--text-secondary)',padding:'6px 0'}}/></div>
<div className="form-group" style={{marginBottom:12}}><label className="form-label">{t('export.paste_label')}</label><textarea className="form-input" rows={8} value={it} onChange={e=>setIt(e.target.value)} placeholder='{"name":"..."}' style={{fontFamily:'var(--font-mono)',fontSize:11,resize:'vertical'}}/></div>
<button className="btn btn-primary" style={{width:'100%'}} onClick={doI} disabled={!it.trim()}>{t('export.btn_import')}</button>
{im&&<div className={`alert ${im.includes(t('export.msg_errors'))?'alert-warning':'alert-success'}`} style={{marginTop:12}}>{im}</div>}</div>
<div className="card"><div className="card-title">{t('export.card_format')}</div>
<pre style={{fontFamily:'var(--font-mono)',fontSize:11,color:'var(--text-secondary)',whiteSpace:'pre-wrap',background:'var(--bg-input)',padding:12,borderRadius:'var(--radius-sm)'}}>
{`{
  "name": "My Recipe",
  "no3_n": 150, "nh4_n": 10,
  "p": 40, "k": 200, ...
}

// Full export:
{ "recipes": [...], "water_profiles": [...] }`}
</pre></div></div></div></div>)}
