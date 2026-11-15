import { evaluateBrief, BRIEFS } from '../lib/jev.mjs';
const cache=new Map(); const pending=new Map();
export default async function handler(req,res) {
  res.setHeader('Cache-Control','no-store');
  if(req.method!=='POST') {res.setHeader('Allow','POST');return res.status(405).json({error:'POST requis'});}
  const body=typeof req.body==='string'?(()=>{try{return JSON.parse(req.body);}catch{return {};}})():req.body;
  const id=body?.brief_id;
  if(!Object.hasOwn(BRIEFS,id||'')) return res.status(400).json({error:'Source inconnue'});
  try {
    if(!cache.has(id)) {
      if(!pending.has(id)) pending.set(id,evaluateBrief(id).then(x=>{cache.set(id,x);return x;}).finally(()=>pending.delete(id)));
      await pending.get(id);
    }
    return res.status(200).json(cache.get(id));
  } catch(error) {
    const code=error.message;
    return res.status(code==='JEV_NOT_CONFIGURED'?503:502).json({error:code==='JEV_NOT_CONFIGURED'?'Jev est prêt à être connecté. Configuration du fournisseur requise.':'Le fournisseur Jev est indisponible. Aucun résultat n’a été inventé.',code:/^JEV_(NOT_CONFIGURED|PROVIDER_\d+)$/.test(code)?code:'JEV_UNAVAILABLE'});
  }
}
