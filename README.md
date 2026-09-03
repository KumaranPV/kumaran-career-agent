# Kumaran Career Agent — Dossier V2

This package replaces the current monolithic FAQ-led structure with an evidence-first RAG model.

## Use
- `system_rules.md` — assistant behaviour and boundaries
- `bio_v2.md` — canonical executive identity
- `experience_v2.md` — career history and evidence
- `projects_v2.md` — ACF, financial orchestration and YiPay
- `faq_v2.md` — adversarial / hiring-manager FAQ
- `scoring_rules.md` — JD-fit scoring model
- `evidence_ledger.yaml` — stable evidence IDs and approved/prohibited wording

## Migration recommendation
1. Keep the old files in a backup branch.
2. Replace `faq.md` with `faq_v2.md` after testing retrieval.
3. Replace or map `bio.md`, `experience.md`, and `projects.md` to the V2 files.
4. Add `system_rules.md` and `scoring_rules.md` to the agent's always-on prompt/context.
5. Index `evidence_ledger.yaml` so answers can cite stable claim IDs.
6. Test with 15–20 adversarial questions before publishing.
