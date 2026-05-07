# BROskiPets — Canonical State — 2026-05-07
> **Vault authority:** AUTHORITATIVE ✅ — agents READ this, do not rewrite from scratch
> **Owner:** welshDog / Lyndz Williams, Llanelli 🏴󠁧󠁢󠁷󠁬󠁳󠁿
> **Last updated:** 2026-05-07 12:00 BST
> **Source:** [[BROskiPets-LLM-dNFT]] repo + live session handoff

---

## 🔑 Keys & Config

| Key | Value / Note |
|-----|-------------|
| `PINATA_JWT` | See "BROski pinata key" — ROTATED 21/04/2026 — use current one ONLY |
| `IPFS_GATEWAY` | `https://aqua-few-dolphin-310.mypinata.cloud` — **https:// required** |
| Auth method | JWT only — NEVER use `PINATA_API_KEY` or `PINATA_API_SECRET` |
| Supabase Project | Hyper Vibe Coding Course — ID: `yhtmuibgdnxhbgboajhc` — Region: `eu-west-2` |

---

## 📦 Pinata Group

| Field | Value |
|-------|-------|
| Name | `BROski_pets_dNFTs` |
| ID | `2aedcf70-d4bb-4e13-94c9-ef6098d49aca` |
| Status | **EMPTY** ⏳ — evo1 images not yet uploaded |
| Rule | NEVER pin to old EEPs group |

---

## 🤖 Pinata OpenClaw Agent — DEPLOYED ✅

| Field | Value |
|-------|-------|
| Name | `broski-pet-evolver` |
| Agent ID | `x2i4f17q` |
| URL | https://agents.pinata.cloud/agents/x2i4f17q |
| AI Provider | **Anthropic (Claude)** ✅ — connected |
| Status | **LIVE** ✅ — deployed May 7 2026 |
| Trial | Free trial — **UPGRADE PINATA PLAN** to keep alive |

### Secrets injected into agent ✅

| Secret | Value | Status |
|--------|-------|--------|
| `BASE_SEPOLIA_RPC` | `https://sepolia.base.org` | ✅ Live |
| `BROSKIPET_CHAIN_ID` | `84532` | ✅ Live |
| `IPFS_GATEWAY` | `https://aqua-few-dolphin-310.mypinata.cloud` | ✅ Live |
| `PINATA_JWT` | auto-injected by Pinata platform | ✅ Live |
| `BACKEND_SIGNER_PRIVATE_KEY` | **MISSING** — add after `cast wallet new` | ❌ Needed |
| `BROSKIPET_CONTRACT_ADDRESS` | **MISSING** — add after forge deploy | ❌ Needed |

### 🚨 Agent Blockers
- **Anthropic credits low** — go to console.anthropic.com → Plans & Billing → top up (~£5)
- **Pinata free trial expiring** — upgrade at agents.pinata.cloud → Account

---

## 🖥️ Repo

| Field | Value |
|-------|-------|
| Repo | https://github.com/welshDog/BROskiPets-LLM-dNFT |
| Last commit | `457812b` (scaffolded UI + corrected HANDOFF.md) |
| HANDOFF.md | https://raw.githubusercontent.com/welshDog/BROskiPets-LLM-dNFT/main/HANDOFF.md |
| Deploy checklist | https://raw.githubusercontent.com/welshDog/BROskiPets-LLM-dNFT/main/PINATA_DEPLOY_CHECKLIST.md |

---

## ✅ DONE — Do NOT Redo

| Item | Status |
|------|--------|
| `broskipet_mint_hardening` migration | ✅ Applied — fixed search_path, RLS, PUBLIC execute revoked |
| `SpeciesPicker.tsx` | ✅ Scaffolded — 10 species, evo1 images, emoji fallback |
| `MintPetButton.tsx` | ✅ Scaffolded — drives `useMintPet()`, balance gate, step trail |
| `Pets.tsx` | ✅ Scaffolded — 3-step flow, replaces mock data, PLACEHOLDER_CID labelled |
| `pet_evolver_agent.py` | ✅ Audited — OpenAI + Ollama + deterministic fallback |
| `HANDOFF.md` | ✅ Corrected — lie removed, 3 additions added |
| Vault state file created | ✅ `HYPERFOCUS_ZONE/State/BROskiPets-2026-05-07.md` |
| AutoBuilder plan created | ✅ `HYPERFOCUS_ZONE/Agents/BROskiPets-AutoBuilder.md` |
| Pinata secrets pre-loaded | ✅ BASE_SEPOLIA_RPC, BROSKIPET_CHAIN_ID, IPFS_GATEWAY |
| `broski-pet-evolver` agent deployed | ✅ Agent ID: x2i4f17q — Anthropic connected |
| Full context handoff sent to agent | ✅ Sacred rules + vault URLs loaded |

---

## ⏳ NEXT STEPS — In Order

### Lyndz does locally first:

**Step 1 — Fix Agent Blockers (5 min)**
```
1. Top up Anthropic credits: console.anthropic.com → Plans & Billing → ~£5
2. Upgrade Pinata plan: agents.pinata.cloud → Account → Upgrade (keep agent alive)
```

**Step 2 — Upload Evo1 Images**
```bash
cd H:/dNFTpet/BROskiPets-LLM-dNFT
python pinata_upload_all.py
# Output: pinata_cids.json with 10 CIDs
# Then paste cids.json to broski-pet-evolver agent chat → it updates Pets.tsx + evolver
```

**Step 3 — Copy PNGs to Frontend**
```bash
mkdir -p frontend/public/pets
for species in apex_dragon blizzard_lizard chaos_cat cyber_fox gigabyte_guinea_pig hyper_beam_bunny hyper_hamster hyperfocus_horse power_pup sonic_spider; do
  mkdir -p "frontend/public/pets/$species"
  cp "H:/dNFTpet/BROskiPets-LLM-dNFT/broski_pets/$species/${species}_evo1.png" "frontend/public/pets/$species/"
done
```

**Step 4 — Generate Signer Wallet**
```bash
cast wallet new
# Save: BACKEND_SIGNER_ADDRESS (public, safe)
# Save: BACKEND_SIGNER_PRIVATE_KEY (to .env only, NEVER commit)
```

**Step 5 — Deploy Contract to Base Sepolia**
```bash
cd H:/dNFTpet/BROskiPets-LLM-dNFT/contracts
# Need ~0.01 ETH Sepolia: https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet
forge script script/DeployBROskiPet.s.sol \
  --rpc-url https://sepolia.base.org \
  --private-key $DEPLOYER_KEY \
  --broadcast --verify
# Save output: BROSKIPET_CONTRACT_ADDRESS = 0x...
```

**Step 6 — Add 3 Secrets to Supabase Edge Functions**
```
URL: https://supabase.com/dashboard/project/yhtmuibgdnxhbgboajhc/settings/functions
Add:
  BACKEND_SIGNER_PRIVATE_KEY  = 0x... (from Step 4)
  BROSKIPET_CONTRACT_ADDRESS  = 0x... (from Step 5)
  BROSKIPET_CHAIN_ID          = 84532
```

**Step 7 — Add 2 Secrets to Pinata Agent**
```
URL: https://agents.pinata.cloud/agents/x2i4f17q → Secrets tab
Add:
  BACKEND_SIGNER_PRIVATE_KEY  = 0x... (from Step 4)
  BROSKIPET_CONTRACT_ADDRESS  = 0x... (from Step 5)
```

**Step 8 — WalletConnect Project ID (1 min, free)**
```
URL: https://cloud.walletconnect.com → New Project → copy ID
Add to: H:/Hyper-Vibe-Coding-Course/frontend/.env
  VITE_WALLETCONNECT_PROJECT_ID=<id>
```

---

## 🚨 Sacred Rules — Never Break

1. ABI types: `string petId`, `string ipfsCID` — NOT `uint256`/`bytes32`
2. Typehash: `"MintAuth(address to,string petId,string ipfsCID,uint256 nonce,uint256 expiry)"`
3. `useMintPet.ts` — **DO NOT regenerate, DO NOT change types**
4. `wagmi.ts` + RainbowKit — **DO NOT replace with injected() only**
5. Import: `@/lib/supabase` (NOT `@/lib/supabaseClient` — file doesn't exist)
6. Contract: `BROskiPet.sol` (NOT `EEPVengers.sol` — legacy)
7. Chain: Base Sepolia `84532` (testnet) / Base `8453` (prod) — never mix
8. `IPFS_GATEWAY` must have `https://` prefix
9. Pinata group: `BROski_pets_dNFTs` ONLY (ID: `2aedcf70-d4bb-4e13-94c9-ef6098d49aca`)

---

## 🗃️ Nonce Functions — Both Exist, Both Needed

| Function | Does | When |
|----------|------|------|
| `cleanup_expired_mint_nonces()` | Deletes **unused** expired nonces | Routine — prevents bloat |
| `prune_expired_nonces()` | Deletes **used** expired nonces | After mint activity |

Do NOT merge or delete either.

---

## 📂 Key Source Paths

| File | Path |
|------|------|
| Contract | `H:/dNFTpet/BROskiPets-LLM-dNFT/contracts/src/BROskiPet.sol` |
| Contract tests | `H:/dNFTpet/BROskiPets-LLM-dNFT/contracts/test/BROskiPet.t.sol` |
| Deploy script | `H:/dNFTpet/BROskiPets-LLM-dNFT/contracts/script/DeployBROskiPet.s.sol` |
| Edge functions | `H:/Hyper-Vibe-Coding-Course/supabase/functions/{mint-pet-auth,get-pet-balance}/index.ts` |
| Hook | `H:/Hyper-Vibe-Coding-Course/frontend/src/hooks/useMintPet.ts` |
| ABI module | `H:/Hyper-Vibe-Coding-Course/frontend/src/lib/contracts/broskiPet.ts` |
| wagmi config | `H:/Hyper-Vibe-Coding-Course/frontend/src/lib/wagmi.ts` |
| SpeciesPicker | `H:/Hyper-Vibe-Coding-Course/frontend/src/components/pets/SpeciesPicker.tsx` |
| MintPetButton | `H:/Hyper-Vibe-Coding-Course/frontend/src/components/pets/MintPetButton.tsx` |
| Pets page | `H:/Hyper-Vibe-Coding-Course/frontend/src/pages/Pets.tsx` |
| Metadata builder | `H:/dNFTpet/BROskiPets-LLM-dNFT/broski_pet_metadata.py` |
| Pinata uploader | `H:/dNFTpet/BROskiPets-LLM-dNFT/pinata_upload_all.py` |
| Species images | `H:/dNFTpet/BROskiPets-LLM-dNFT/broski_pets/{species}/{species}_evo1.png` |
| Evolver agent | `H:/dNFTpet/BROskiPets-LLM-dNFT/pet_evolver_agent.py` |
| Migrations | `H:/Hyper-Vibe-Coding-Course/supabase/migrations/` |

---

## 🧪 Verify Commands

```bash
# Contract tests (must be 22/22)
cd H:/dNFTpet/BROskiPets-LLM-dNFT/contracts
forge test --match-contract BROskiPet -v

# Frontend types (must be 0 errors)
cd H:/Hyper-Vibe-Coding-Course/frontend
npx tsc --noEmit

# Metadata smoke test
python broski_pet_metadata.py --name TestPet --species cyber_fox --rarity uncommon --dry-run

# Agent health (after deploy complete)
curl https://agents.pinata.cloud/agents/x2i4f17q/
# Expect: {"status": "ok", "agent": "broski-pet-evolver"}

# DB nonce check (must be 0)
SELECT COUNT(*) FROM mint_nonces WHERE expires_at < NOW();
```

---

## 🧠 Stack

| Layer | Tech |
|-------|------|
| Frontend | React + Vite + wagmi + RainbowKit |
| Contract | Solidity 0.8.x + Foundry (22/22 tests) |
| Backend | Supabase Edge Functions (Deno/TypeScript) |
| IPFS | Pinata JWT — gateway: `aqua-few-dolphin-310.mypinata.cloud` |
| Agent | Pinata OpenClaw — `broski-pet-evolver` (ID: x2i4f17q) — Claude/Anthropic |
| Chain | Base Sepolia `84532` → Base mainnet `8453` |

---

## 📝 Session Log

### Session 1 — May 7 2026, ~10:00 BST
- `broskipet_mint_hardening` migration applied ✅
- UI components scaffolded (SpeciesPicker, MintPetButton, Pets.tsx) ✅
- `pet_evolver_agent.py` audited ✅
- `HANDOFF.md` corrected ✅

### Session 2 — May 7 2026, ~11:00 BST
- Vault state file created (`BROskiPets-2026-05-07.md`) ✅
- AutoBuilder master plan created (`HYPERFOCUS_ZONE/Agents/BROskiPets-AutoBuilder.md`) ✅
- Confirmed Pinata group `BROski_pets_dNFTs` exists — currently empty ✅
- 3 non-sensitive secrets pre-loaded to Pinata Secrets Vault ✅
- `broski-pet-evolver` agent DEPLOYED on Pinata OpenClaw ✅
  - Agent ID: `x2i4f17q`
  - AI: Anthropic (Claude) — connected + available
  - Secrets injected: BASE_SEPOLIA_RPC, BROSKIPET_CHAIN_ID, IPFS_GATEWAY
  - Full context handoff sent to agent (vault URLs, Sacred Rules, next steps)
- **Blockers found:**
  - Anthropic API credits low → top up at console.anthropic.com
  - Pinata free trial expiring → upgrade plan to keep agent alive

### Session 3 — May 7 2026, ~12:00 BST
- All docs updated with full current state ✅
- HANDOFF.md in repo updated with agent details ✅
- AutoBuilder phase tracker updated ✅

---

## 📊 Phase Status Tracker

| Phase | Task | Status | Blocker |
|-------|------|--------|---------|
| 0 | Read vault + HANDOFF | ✅ Complete | None |
| 1 | Upload evo1 images to Pinata | ⏳ Pending | Lyndz runs `pinata_upload_all.py` |
| 2 | Copy PNGs to frontend/public/pets/ | ⏳ Pending | After Phase 1 |
| 3 | Generate signer wallet | ⏳ Pending | `cast wallet new` |
| 4 | Deploy BROskiPet.sol to Base Sepolia | ⏳ Pending | Funded wallet + Phase 3 |
| 5 | Supabase Edge Function secrets | ⏳ Pending | After Phases 3+4 |
| 6 | Pinata agent secrets | ✅ Partial — 3/5 secrets live | Add BACKEND_SIGNER + CONTRACT after Phases 3+4 |
| 6b | Fix agent blockers | ⚠️ Urgent | Top up Anthropic credits + upgrade Pinata |
| 7 | WalletConnect Project ID | ⏳ Pending | 1 min at cloud.walletconnect.com |

---

*BROskiPets Canonical State — welshDog / Lyndz Williams, Llanelli*
*Updated by BROski AI (Comet/Perplexity), May 7 2026 🐾*
