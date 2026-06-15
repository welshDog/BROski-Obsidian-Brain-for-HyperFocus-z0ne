# Budget Request
**Applicant:** Lyndz Williams (WelshDog)  
**Project:** Hyperfocus Zone Ecosystem  
**Date:** 15 June 2026  
**Total Ask: Up to 1,000,000 GPU hours (H100 equivalent) via AIRR / Isambard-AI / Dawn**

---

## Summary

This is a compute-only request. No cash grant is being requested at this stage. The sole ask is access to sovereign GPU compute via the AIRR programme (Isambard-AI or Dawn) to execute three R&D workstreams over 12 months.

---

## Compute Budget Breakdown

| Workstream | Activity | GPU Hours | Notes |
|-----------|----------|-----------|-------|
| **1. Fine-tuned agent model** | Base model fine-tuning runs (x3) | 180,000 | 7B model, 3 runs with different hyperparams |
| | Larger model runs (13B) | 120,000 | 2 runs — best config from 7B phase |
| | Validation + ablation studies | 60,000 | Held-out eval sets, ablation across agent roles |
| | Safety alignment (RLHF) | 40,000 | Reward model training + PPO fine-tune |
| **Workstream 1 subtotal** | | **400,000** | |
| **2. ND productivity dataset** | Synthetic data generation (100k+ examples) | 150,000 | LLM-driven from seed session logs |
| | Embedding generation (192-node graph) | 80,000 | Dense vector embeddings for RAG memory |
| | Reward model training | 70,000 | Session quality signal → reward model |
| | Data validation + quality filtering | 50,000 | Automated + human-in-loop QA |
| **Workstream 2 subtotal** | | **350,000** | |
| **3. Benchmark suite** | Agent simulation episodes (10k+) | 120,000 | Full 35-agent swarm topology |
| | Failure mode / adversarial stress tests | 80,000 | Circuit-breaker + guardrail validation |
| | Architecture search (routing ablations) | 50,000 | Throne Ladder pattern variants |
| **Workstream 3 subtotal** | | **250,000** | |
| **TOTAL** | | **1,000,000** | |

---

## Commercial Equivalent Cost

For transparency, the commercial cost of this compute at market rates:

| Provider | H100 rate | 1M hrs cost |
|----------|-----------|-------------|
| AWS (p4d.24xlarge) | ~£3.50/hr per GPU | **~£3,500,000** |
| GCP (a3-highgpu) | ~£3.20/hr per GPU | **~£3,200,000** |
| Azure (ND H100 v5) | ~£3.80/hr per GPU | **~£3,800,000** |
| **AIRR / sovereign route** | Academic allocation | **£0 cash cost** |

This makes sovereign compute access the only financially viable pathway for an early-stage independent UK founder.

---

## Infrastructure Costs (Existing — No Additional Ask)

The following are already funded by the project and require no additional grant support:

| Item | Monthly Cost | Annual Cost | Source |
|------|-------------|-------------|--------|
| Local server (commodity hardware) | ~£30 electricity | ~£360 | Self-funded |
| Vercel hosting (course platform) | £0 (free tier) | £0 | Free tier |
| Supabase (course + MC) | ~£25/mo | ~£300 | Revenue |
| Domain + SSL | ~£5/mo | ~£60 | Self-funded |
| Anthropic / OpenAI API (current inference) | ~£80/mo | ~£960 | Self-funded |
| **Total running costs** | **~£140/mo** | **~£1,680/yr** | **Self-funded** |

Note: sovereign compute access would reduce the Anthropic/OpenAI API cost to near-zero once the fine-tuned model is deployed on UK infrastructure.

---

## Timeline and Milestones

| Month | Milestone | Compute used |
|-------|-----------|-------------|
| 1–2 | Environment setup, data prep, base model selection | ~20,000 hrs |
| 3–4 | First fine-tuning runs (7B model) | ~120,000 hrs |
| 5–6 | 13B runs + validation — **Model v1.0 delivered** | ~160,000 hrs |
| 7–8 | Synthetic dataset generation | ~150,000 hrs |
| 9 | Dataset QA + embeddings — **Dataset v1.0 published** | ~130,000 hrs |
| 10–11 | Benchmark simulation episodes | ~170,000 hrs |
| 12 | Final ablations + report — **Benchmark suite published** | ~250,000 hrs |
| **Total** | | **~1,000,000 hrs** |

---

## Value Return to UK

Every output is open source and published as a UK AI asset:

| Output | Licence | UK Value |
|--------|---------|----------|
| Fine-tuned agent model (7B–13B) | Apache 2.0 | Sovereign UK inference, free to use |
| Neurodivergent productivity dataset | CC BY 4.0 | Open UK AI asset, first of its kind |
| Multi-agent benchmark suite | MIT | Free evaluation framework for UK AI community |
| Technical report | Open access | UK research contribution |

**Cost per open UK AI asset: effectively £0 cash** — only compute access required.

---

## Why This Is Efficient Use of Sovereign Compute

- No cash grant requested — compute only
- All outputs openly published — maximum UK return
- Existing production stack means zero infrastructure setup time
- Training data already collected — no data acquisition cost
- Solo founder = no salary overhead, no org bureaucracy
- 12-month programme = short, defined, measurable

---
*File: AIFS/sovereign-ai-grant/04_budget_request.md*  
*Built by welshDog — Llanelli, Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁥*
