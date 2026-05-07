# BROskiPets — Canonical State — 2026-05-07
> **Vault authority:** AUTHORITATIVE ✅ — agents READ this, do not rewrite from scratch
> **Owner:** welshDog / Lyndz Williams, Llanelli 🏴󠁧󠁢󠁷󠁬󠁳󠁠
> **Last updated:** 2026-05-07 10:45 BST
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

- **Name:** `BROski_pets_dNFTs`
- **ID:** `2aedcf70-d4bb-4e13-94c9-ef6098d49aca`
- ⚠️ Do NOT touch the old EEPs group

---

## 📁 Repo Links

- [[BROskiPets-LLM-dNFT]] → https://github.com/welshDog/BROskiPets-LLM-dNFT
- Last commit: `457812b` (scaffolded UI + corrected HANDOFF.md)
- Full handoff doc: `HANDOFF.md` in repo root — read it
- [[HyperCode-V2.4]] | [[HyperAgent-SDK]] | [[Hyper-Vibe-Coding-Course]]

---

## ✅ DONE — Do NOT Redo

- `broskipet_mint_hardening` migration **APPLIED** ✅
  - Fixed `search_path` on `next_pet_id()` → returns bigint via `broskipet_id_seq`
  - Fixed `search_path` on `prune_expired_nonces()` → returns void
  - Fixed `search_path` on `cleanup_expired_mint_nonces()` → returns integer
  - Duplicate RLS on `mint_nonces` removed
  - PUBLIC execute revoked on all 3 security definer functions
- `SpeciesPicker.tsx` scaffolded ✅ — 10 species, evo1 images, emoji fallback
- `MintPetButton.tsx` scaffolded ✅ — drives `useMintPet()`, balance gate, step trail
- `Pets.tsx` scaffolded ✅ — 3-step flow, replaces mock data, `PLACEHOLDER_CID` clearly labelled
- `pet_evolver_agent.py` audited ✅ — OpenAI + Ollama both wired, deterministic fallback
- `HANDOFF.md` corrected ✅ — lie removed, 3 additions added

---

## ⏳ NEXT STEPS (in order)

1. **Upload 10x evo1 images to Pinata**
   ```bash
   python pinata_upload_all.py
   # outputs pinata_cids.json
   # replace PLACEHOLDER_CID in Pets.tsx + {CID_PLACEHOLDER} in pet_evolver_agent.py
   ```

2. **Copy evo1 PNGs to frontend**
   - Source: `H:/dNFTpet/BROskiPets-LLM-dNFT/broski_pets/{species}/{species}_evo1.png`
   - Dest: `frontend/public/pets/`

3. **Generate wallet**
   ```bash
   cast wallet new
   # save: BACKEND_SIGNER_PRIVATE_KEY + BACKEND_SIGNER_ADDRESS
   ```

4. **Deploy contract**
   ```bash
   forge script DeployBROskiPet.s.sol --rpc-url https://sepolia.base.org --broadcast --verify
   # save: BROSKIPET_CONTRACT_ADDRESS
   ```

5. **Add Supabase Edge Function secrets:**
   - `BACKEND_SIGNER_PRIVATE_KEY`
   - `BROSKIPET_CONTRACT_ADDRESS`
   - `BROSKIPET_CHAIN_ID=84532`

6. **Create Pinata agent**
   - URL: https://agents.pinata.cloud/agents
   - See `PINATA_DEPLOY_CHECKLIST.md` in repo for full config

7. **Get WalletConnect Project ID**
   - URL: https://cloud.walletconnect.com
   - Add as `VITE_WALLETCONNECT_PROJECT_ID` in frontend `.env`

---

## 🚨 CRITICAL RULES — Sacred, Do Not Break

1. ABI types: `string petId`, `string ipfsCID` — NOT `uint256`/`bytes32` (v1 bug)
2. Typehash: `"MintAuth(address to,string petId,string ipfsCID,uint256 nonce,uint256 expiry)"`
3. `useMintPet.ts` — **DO NOT regenerate, DO NOT change types**
4. `wagmi.ts` + RainbowKit — **DO NOT replace with `injected()` only**
5. Import path: `@/lib/supabase` (NOT `@/lib/supabaseClient`)
6. Contract: `BROskiPet.sol` (NOT `EEPVengers.sol` — that's legacy)
7. Chain: Base Sepolia `chainId=84532` (testnet) / Base mainnet `8453` (prod)
8. `IPFS_GATEWAY` must have `https://` prefix
9. Pinata group: `BROski_pets_dNFTs` ONLY

---

## 🗃️ Nonce Functions — Both Exist, Both Needed

| Function | Purpose |
|----------|---------|
| `cleanup_expired_mint_nonces()` | Deletes UNUSED expired nonces — prevents bloat |
| `prune_expired_nonces()` | Deletes USED expired nonces — archive cleanup |

⚠️ Do NOT merge or delete either.

---

## 📂 Key Source Paths

| File | Path |
|------|------|
| Contract | `H:/dNFTpet/BROskiPets-LLM-dNFT/contracts/src/BROskiPet.sol` |
| Deploy script | `H:/dNFTpet/BROskiPets-LLM-dNFT/contracts/script/DeployBROskiPet.s.sol` |
| Edge functions | `H:/Hyper-Vibe-Coding-Course/supabase/functions/{mint-pet-auth,get-pet-balance}/index.ts` |
| Hook | `H:/Hyper-Vibe-Coding-Course/frontend/src/hooks/useMintPet.ts` |
| ABI module | `H:/Hyper-Vibe-Coding-Course/frontend/src/lib/contracts/broskiPet.ts` |
| wagmi config | `H:/Hyper-Vibe-Coding-Course/frontend/src/lib/wagmi.ts` |
| UI components | `H:/Hyper-Vibe-Coding-Course/frontend/src/components/pets/` |
| Pets page | `H:/Hyper-Vibe-Coding-Course/frontend/src/pages/Pets.tsx` |
| Images | `H:/dNFTpet/BROskiPets-LLM-dNFT/broski_pets/{species}/{species}_evo1.png` |
| Migrations | `H:/Hyper-Vibe-Coding-Course/supabase/migrations/` |

---

## 🧪 Verify Commands

```bash
forge test --match-contract BROskiPet -v     # 22/22 should pass
cd frontend && npx tsc --noEmit              # 0 errors expected
python broski_pet_metadata.py --name X --species cyber_fox --rarity uncommon --dry-run
```

---

## 🧠 Stack

| Layer | Tech |
|-------|------|
| Frontend | React + Vite + wagmi + RainbowKit |
| Backend | Supabase Edge Functions (Deno) |
| Smart contract | Solidity + Foundry |
| Storage | Pinata IPFS + Pinata OpenClaw agent |
| Network | Base Sepolia (testnet) → Base mainnet |

---

## 🔗 Related Vault Pages

- [[cyber_fox]] — pet species page (stub, needs creating)
- [[BROski-Tokenomics]] — BROski$ earn/spend rules
- [[Hyper-Vibe-Coding-Course]] — course platform state
- [[HyperCode-V2.4]] — 29-container Docker ecosystem
