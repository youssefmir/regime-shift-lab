import test from 'node:test';
import assert from 'node:assert/strict';
import {evaluateBrief,validateAnswers,QUESTIONS} from '../lib/jev.mjs';
const valid={model:'jev-1.14.0',answers:Object.fromEntries(Object.keys(QUESTIONS).map(k=>[k,{type:'noul',noul:.75}]))};
test('rejects missing and out-of-range model probabilities',()=>{
 assert.throws(()=>validateAnswers({}));
 const bad=structuredClone(valid);bad.answers.hedge_breakdown.noul=1.1;assert.throws(()=>validateAnswers(bad));
});
test('direct TypeSafe uses System One protocol and pinned Jev',async()=>{
 let body;
 const r=await evaluateBrief('diversification',{env:{TYPESAFE_API_KEY:'test-only'},fetcher:async(url,options)=>{
 assert.equal(url,'https://api.typesafe.ai/v1/systemone');body=JSON.parse(options.body);
 return {ok:true,json:async()=>valid};}});
 assert.equal(body.model,'jev-1.14.0');assert.ok(body.questions.hedge_breakdown);assert.equal(r.answers.hedge_breakdown,.75);
});
test('OIDC selects exact Jev gateway model and compatibility endpoint',async()=>{
 await evaluateBrief('gold',{env:{VERCEL_OIDC_TOKEN:'test-only'},fetcher:async(url,options)=>{
 assert.equal(url,'https://ai-gateway.vercel.sh/typesafe/v1/systemone');assert.equal(JSON.parse(options.body).model,'typesafe-ai/jev-1.14.0');return {ok:true,json:async()=>valid};}});
});
test('missing configuration and provider failures do not fabricate a result',async()=>{
 await assert.rejects(()=>evaluateBrief('gold',{env:{}}),/NOT_CONFIGURED/);
 await assert.rejects(()=>evaluateBrief('gold',{env:{TYPESAFE_API_KEY:'test-only'},fetcher:async()=>({ok:false,status:401})}),/PROVIDER_401/);
});
