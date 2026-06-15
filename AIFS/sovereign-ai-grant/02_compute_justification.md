# Compute Justification Statement
## UK Sovereign AI Fund — Access to Sovereign Compute
**Applicant:** Lyndz Williams (WelshDog)  
**Project:** Hyperfocus Zone Ecosystem  
**Location:** Llanelli, Wales, United Kingdom  
**Date:** 15 June 2026  
**Compute Requested:** Up to 1,000,000 GPU hours (AIRR / Isambard-AI / Dawn)

---

## 1. Current Infrastructure and Compute Constraints

The Hyperfocus Zone Ecosystem currently operates a 30-container Docker stack (HyperCode-V2.4), 
orchestrated across 20 Compose files with 80 defined services, running on commodity hardware 
in Llanelli, Wales. The stack includes:

- FastAPI backend with multi-agent routing
- Redis (DB1: cache, DB2: rate limiting)
- PostgreSQL persistent storage
- Prometheus + Grafana observability pipeline
- An Ollama local inference container (CPU-bound, 4-8 tokens/sec throughput)
- A 35-agent swarm across 5 Docker networks (app-net, agents-net, hyper-brain-net, etc.)

The agent orchestration layer (HyperAgent-SDK, published as @w3lshdog/hyper-agent on npm) 
coordinates task routing, skill dispatch, context retention, and session lifecycle management 
across the swarm. All LLM inference currently routes through third-party APIs (Claude/Anthropic, 
OpenAI) due to local GPU constraints. The Ollama container is CPU-only and cannot run models 
above 7B parameters at useful inference speeds for multi-agent workflows.

This constraint is a hard blocker for three critical R&D workstreams described below.

---

## 2. What Sovereign Compute Would Unlock

### Workstream 1: Fine-Tuning Custom Agent Behaviour Models (approx. 400,000 GPU hours)

The current agent swarm relies entirely on general-purpose frontier LLMs for task reasoning. This creates three technical problems:

1. **Latency:** Each inter-agent call incurs API round-trip latency of 800–2,000ms, creating cascading delays in multi-hop agent chains.
2. **Context drift:** General-purpose models do not retain domain-specific vocabulary, agent role definitions, or task decomposition heuristics. Each call must re-inject ~3,000 tokens of system context.
3. **Sovereignty:** All inference currently exits the UK to US-based API endpoints, creating data residency and latency risks.

Sovereign compute access would allow fine-tuning of a 7B–13B parameter base model (Mistral/LLaMA-class) on the HyperFocus agent interaction dataset, producing a UK-hosted, domain-adapted inference model purpose-built for task decomposition, agent role dispatch, context retention, and neurodivergent-first response scaffolding.

Estimated compute: ~400,000 H100 GPU hours.

---

### Workstream 2: Neurodivergent Productivity Dataset Creation (approx. 350,000 GPU hours)

The platform has generated structured interaction data from HyperFocus sessions: task decomposition trees, focus session logs, morning briefing narratives, and agent skill dispatch records (89 skills, 192-node knowledge graph with 401 edges).

This data represents a novel, underexplored AI training signal: structured productivity workflows for ADHD and dyslexic users. No public dataset of this type exists at meaningful scale.

Sovereign compute would enable:
1. **Large-scale synthetic data generation:** 100,000+ labelled task decomposition examples
2. **Embedding generation:** Vector embeddings for the full knowledge graph for RAG-based agent memory
3. **Reward modelling:** A lightweight reward model on user session quality signals

This dataset will be published as an open UK AI asset under a permissive licence.

Estimated compute: ~350,000 H100 GPU hours.

---

### Workstream 3: Multi-Agent Orchestration Benchmarking (approx. 250,000 GPU hours)

The HyperCode agent swarm has no rigorous benchmark suite for evaluating orchestration quality at scale. Sovereign compute would enable:

1. **Synthetic evaluation harness:** 10,000+ agent simulation episodes across the full 35-agent swarm
2. **Failure mode mapping:** Stress-testing the Healer Circuit-Breaker Protocol and 5 Mandatory Agent Guardrails
3. **Architecture search:** Ablations across agent role hierarchy configurations

Estimated compute: ~250,000 H100 GPU hours.

---

## 3. Why Local or Commercial Cloud Compute Cannot Substitute

| Option | Limitation |
|--------|------------|
| Local CPU (current) | Ollama CPU-only, max 7B @ 4 tok/s — unusable for fine-tuning |
| Consumer GPU (RTX 4090) | 24GB VRAM — insufficient for 7B+ fine-tuning with full gradients |
| Commercial cloud (AWS/GCP/Azure) | Cost-prohibitive: ~£2.50–£4.00/H100 hr = £2.5M–£4M for 1M hrs |
| UK commercial cloud | No UK-sovereign H100 capacity available at this scale without AIRR |

The sovereign compute pathway via AIRR (Isambard-AI: 5,444 x H100 GPUs, Bristol) or Dawn (Cambridge) is the only technically viable and financially accessible route.

---

## 4. Outputs and UK Sovereign Value

| Output | Timeline | UK Value |
|--------|----------|----------|
| Fine-tuned agent behaviour model (7B–13B) | Month 6 | UK-hosted, open-weight, sovereign inference |
| Neurodivergent productivity dataset (100k+ examples) | Month 9 | Openly published UK AI asset |
| Multi-agent orchestration benchmark suite | Month 12 | UK-first evaluation framework |
| Published technical report | Month 12 | UK research contribution |

---

## 5. Summary

Sovereign compute access is the critical path dependency for advancing from a deployed 30-container agent infrastructure to a UK-sovereign, fine-tuned, benchmarked, and openly documented multi-agent AI platform.

Without it: the project continues to rely on US API endpoints for inference, cannot produce the neurodivergent dataset, and cannot run the benchmarks needed to validate agent safety and quality at scale.

With it: within 12 months, the project delivers three novel UK AI assets — a fine-tuned model, an open dataset, and a benchmark suite.

**Compute requested: up to 1,000,000 GPU hours**  
**Preferred infrastructure: Isambard-AI (H100) or Dawn**  
**Timeline: 12-month R&D programme**

---
*Submitted by: Lyndz Williams (WelshDog), Llanelli, Wales | GitHub: github.com/welshDog | Date: 15 June 2026*
