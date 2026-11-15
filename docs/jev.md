# TypeSafe Jev integration

Jev 1.14 classifies dated macroeconomic research paraphrases using four atomic Noul questions: weakened stock–bond hedging, inflation risk, liquidity risk, and whether future outperformance is established. Results are probabilities, not generated investment advice. The model does not generate article summaries or price targets.

Official contract: https://docs.typesafe.ai/api/system-one
Models: https://docs.typesafe.ai/models
Gateway compatibility: https://vercel.com/docs/ai-gateway/sdks-and-apis/typesafe

`lib/jev.mjs` sends `state`, `questions` and `model` to TypeSafe's native `/v1/systemone` endpoint if `TYPESAFE_API_KEY` is configured. On Vercel, it can instead use `AI_GATEWAY_API_KEY` or the runtime `VERCEL_OIDC_TOKEN`, with the pinned `typesafe-ai/jev-1.14.0` model.

Configure secrets in the Vercel project environment, never the browser bundle or this repository. Local unit tests mock transport; they do not establish model quality. A missing key or failed provider yields an explicit unavailable state, never fabricated probabilities. Only two server-defined briefs are accepted; the server has no arbitrary URL fetch or text submission endpoint. Results are cached per running function instance; configure Vercel Firewall rate limits and AI Gateway project spend limits before increasing public traffic.

The text is an original research paraphrase, visible to the user with a source link. Classification applies only to that paraphrase. It is not a full-article extraction or calibrated financial probability. Jev's outputs are not fed into the 2007–2026 historical strategy: the model and these sources were unavailable for much of that period. Any text-based trading overlay needs timestamped archival texts, model evaluation and a prospective paper-trading period.

Run `npm test` to verify protocol selection, probability validation, missing credentials and provider failure handling.
