# BROskiPets — Canonical State — 2026-05-07
> **Vault authority:** AUTHORITATIVE ✅ — agents READ this, do not rewrite from scratch
> **Owner:** welshDog / Lyndz Williams, Llanelli 🏴󠁧󠁢󠁷󠁬󠁳󠁠
> **Last updated:** 2026-05-07 (patch v2 — 5 inaccuracies fixed by main session)
> **Source:** [[BROskiPets-LLM-dNFT]] repo + live session handoff
> **⚠️ Verification rule for agents:** Before trusting "another agent shipped X" claims,
> verify via Read/git/MCP. Three of three such claims in the May 7 session were false.

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
  - Real recent commits: `c12ee98` (pet_evolver_agent + PINATA_DEPLOY_CHECKLIST), `bffe26c` (evo sprite images)
  - Pinata deploy notes: `PINATA_DEPLOY_CHECKLIST.md` in repo root (NOT `HANDOFF.md` — that file does not exist)
- [[Hyper-Vibe-Coding-Course]] → https://github.com/welshDog/Hyper-Vibe-Coding-Course
  - Real recent commit: `be78fb5` (BROskiPet dNFT minting with RainbowKit + wagmi — last session)
  - Working-tree-only (uncommitted) this session: SpeciesPicker, MintPetButton, updated Pets.tsx, species.ts, pinata_upload_all.py, lockdown migration
- ⚠️ Hash `457812b` referenced by an earlier agent does **not exist** in any repo — was hallucinated. Ignore it.
- [[HyperCode-V2.4]] | [[HyperAgent-SDK]]

---

## ✅ DONE — Do NOT Redo

### Migrations (in order — all applied)
| # | Version | Name | What it actually did |
|---|---------|------|----------------------|
| 1 | `20260507065011` | `broskipet_mint_nonces` | Created `mint_nonces` table + RLS policy `mint_nonces_no_public_access` + `next_pet_id()` with `SET search_path=public` + `cleanup_expired_mint_nonces()` + indexes |
| 2 | `20260507070922` | `broskipet_mint_infrastructure` | Added `prune_expired_nonces()` + `USAGE` grant on `broskipet_id_seq`. ⚠️ Also introduced 3 regressions (search_path lost on `next_pet_id`, duplicate `"service only"` policy, missing revokes) |
| 3 | `20260507092020` | `broskipet_mint_hardening` | Restored `search_path=''` (empty — stricter) on all 3 functions. ⚠️ Did NOT actually drop the duplicate policy (its DO-block targeted policy names that didn't exist) and `REVOKE FROM PUBLIC` was a no-op vs Supabase's anon/authenticated default grants |
| 4 | `20260507100000` | `broskipet_grants_lockdown` | **Real fix:** dropped duplicate `"service only"` RLS policy, REVOKED execute from `anon, authenticated` on all 3 BROskiPet helper functions. Verified clean via `pg_proc.proacl` + `pg_policies`. Cleared 13 advisor warnings. |

After migration #4 the live state is:
- `next_pet_id`, `prune_expired_nonces`, `cleanup_expired_mint_nonces` callable by `service_role` only
- `mint_nonces` has exactly one RLS policy: `mint_nonces_no_public_access` (FOR ALL anon,authenticated USING/WITH CHECK false)
- `search_path = ''` set on all 3 functions

### Edge Functions
- `mint-pet-auth` v2 deployed ✅ — viem-based EIP-712 signing, correct typehash `string petId, string ipfsCID`, refund on every failure path. Source tracked at `supabase/functions/mint-pet-auth/index.ts`
- `get-pet-balance` v1 deployed + audited ✅ — JWT'd, returns `{ broski_tokens, mint_cost: 100, can_mint }`. Source tracked at `supabase/functions/get-pet-balance/index.ts`

### Frontend (working tree this session — uncommitted)
- `frontend/src/lib/species.ts` ✅ — 10-species catalogue (id/displayName/emoji/imageUrl/babyMetadataCid) + `Rarity` types + `isRealCid()` guard. CIDs are PLACEHOLDER_* until Step 1 runs.
- `frontend/src/components/pets/SpeciesPicker.tsx` ✅ — 10-card grid, image with emoji fallback, HVZ violet ring on selected
- `frontend/src/components/pets/MintPetButton.tsx` ✅ — RainbowKit ConnectButton, `get-pet-balance` gate, step trail (Reserve/Sign/Mine/Confirm), Basescan link on success, refuses mint while CID is `PLACEHOLDER_*`
- `frontend/src/pages/Pets.tsx` ✅ — mock data deleted, 3-step flow (pick species → name + rarity → mint), session-local minted-pets list
- `frontend/public/pets/{species}.png` ✅ — 10 evo1 PNGs copied (~16MB total) so Step 2 of the original "next steps" is already done

### Frontend (committed last session — `be78fb5`)
- `frontend/src/hooks/useMintPet.ts` ✅ — string petId/ipfsCID matching contract, chain auto-switch, contract/chain mismatch guard
- `frontend/src/lib/wagmi.ts` ✅ — RainbowKit getDefaultConfig, Base Sepolia default + Base mainnet on env flag
- `frontend/src/lib/contracts/broskiPet.ts` ✅ — minimal ABI (mintWithAuth + reads + PetMinted event)
- `frontend/src/main.tsx` ✅ — wrapped in `<WagmiProvider><QueryClientProvider><RainbowKitProvider>`
- `frontend/vercel.json` CSP ✅ — Base RPC + WalletConnect + IPFS gateways allowlisted

### BROskiPets repo
- `pet_evolver_agent.py` audited ✅ — OpenAI + Ollama both wired via `USE_OLLAMA` flag, deterministic fallback. ⚠️ Neither path live-tested against deployed contract yet.
- `broski_pet_metadata.py` ✅ — Baby-stage metadata builder + Pinata uploader, dry-run validated
- `pinata_upload_all.py` ✅ — Pinata v3 + group support, iterates 10 species, builds Baby metadata via `BROskiPetMetadata`, outputs CID map + paste-ready TS snippet. Dry-run smoke passed.
- `contracts/src/BROskiPet.sol` ✅ — 22/22 Foundry tests passing
- `contracts/script/DeployBROskiPet.s.sol` ✅ — Base Sepolia deploy ready

---

## ⏳ NEXT STEPS (in order)

> Step 2 ("copy PNGs") from the previous version is **already done** this session — removed.

1. **Upload 10× evo1 images + Baby metadata to Pinata**
   ```bash
   cd H:/dNFTpet/BROskiPets-LLM-dNFT
   python pinata_upload_all.py --out species_cids.json
   # uploads 10 images + 10 metadata JSONs to BROski_pets_dNFTs group
   # output JSON includes `ts_snippet` ready to paste into species.ts
   ```
   After running, the main agent should patch `frontend/src/lib/species.ts`
   replacing `PLACEHOLDER_*_BABY_CID` strings with the real CIDs from the output.

2. **Generate signer wallet**
   ```bash
   cast wallet new
   # save BOTH: BACKEND_SIGNER_ADDRESS (public, for forge env) and
   #            BACKEND_SIGNER_PRIVATE_KEY (secret, for Supabase secret only)
   # NEVER reuse the deployer key for the signer.
   ```

3. **Deploy contract on Base Sepolia**
   ```bash
   cd H:/dNFTpet/BROskiPets-LLM-dNFT/contracts
   export ADMIN_ADDRESS=0x...           # Gnosis Safe on mainnet, EOA on testnet
   export BACKEND_SIGNER_ADDRESS=0x...  # public addr from cast wallet new
   export AGENT_ADDRESS=0x...           # LLM/evolver backend wallet
   forge script script/DeployBROskiPet.s.sol \
     --rpc-url https://sepolia.base.org \
     --private-key $DEPLOYER_KEY \
     --broadcast --verify \
     --etherscan-api-key $ETHERSCAN_API_KEY
   # save: BROSKIPET_CONTRACT_ADDRESS from the logs
   ```

4. **Add Supabase Edge Function secrets** (Settings → Edge Functions → Secrets)
   - `BACKEND_SIGNER_PRIVATE_KEY` (from Step 2)
   - `BROSKIPET_CONTRACT_ADDRESS` (from Step 3)
   - `BROSKIPET_CHAIN_ID=84532`

5. **Get WalletConnect Project ID** (free, 1 min)
   - URL: https://cloud.walletconnect.com → create project → copy Project ID

6. **Add Vercel env vars** (all 3 environments)
   - `VITE_BROSKIPET_CONTRACT_ADDRESS` (from Step 3)
   - `VITE_BROSKIPET_CHAIN_ID=84532`
   - `VITE_WALLETCONNECT_PROJECT_ID` (from Step 5)

7. **Create Pinata OpenClaw evolver agent**
   - URL: https://agents.pinata.cloud/agents
   - Source: `pet_evolver_agent.py` (commit `c12ee98`)
   - See `PINATA_DEPLOY_CHECKLIST.md` for the full secrets list

8. **First end-to-end mint** — `cd frontend && npm run dev` → `/pets` → connect → mint → see Basescan tx

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
10. `MintPetButton` MUST refuse mint while `babyMetadataCid` starts with `PLACEHOLDER_` — protects users from spending 100 BROski$ on broken metadata. Guard lives in `frontend/src/lib/species.ts:isRealCid()`.
11. `mint-pet-auth` Edge Function MUST use viem `signTypedData` — never hand-rolled EIP-712 (v1 had 3 encoding bugs: wrong typehash + wrong petId encoding + wrong address padding).
12. EVERY post-spend failure path in `mint-pet-auth` MUST refund via `award_tokens` — petId allocation, nonce insert, signing, etc. (v1 leaked tokens on 2 of 3 paths.)
13. Helper functions (`next_pet_id`, `prune_expired_nonces`, `cleanup_expired_mint_nonces`) are `service_role` only. NEVER `GRANT EXECUTE TO authenticated` — they're called by Edge Functions with the service-role key.

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
| Contract tests | `H:/dNFTpet/BROskiPets-LLM-dNFT/contracts/test/BROskiPet.t.sol` |
| Deploy script | `H:/dNFTpet/BROskiPets-LLM-dNFT/contracts/script/DeployBROskiPet.s.sol` |
| Edge functions (git) | `H:/Hyper-Vibe-Coding-Course/supabase/functions/{mint-pet-auth,get-pet-balance}/index.ts` |
| Migrations | `H:/Hyper-Vibe-Coding-Course/supabase/migrations/2026050700*` (4 files) |
| Hook | `H:/Hyper-Vibe-Coding-Course/frontend/src/hooks/useMintPet.ts` |
| ABI module | `H:/Hyper-Vibe-Coding-Course/frontend/src/lib/contracts/broskiPet.ts` |
| wagmi config | `H:/Hyper-Vibe-Coding-Course/frontend/src/lib/wagmi.ts` |
| **Species catalogue** | `H:/Hyper-Vibe-Coding-Course/frontend/src/lib/species.ts` ← edit after Step 1 |
| UI components | `H:/Hyper-Vibe-Coding-Course/frontend/src/components/pets/{SpeciesPicker,MintPetButton}.tsx` |
| Pets page | `H:/Hyper-Vibe-Coding-Course/frontend/src/pages/Pets.tsx` |
| Pinata uploader | `H:/dNFTpet/BROskiPets-LLM-dNFT/pinata_upload_all.py` |
| Metadata builder | `H:/dNFTpet/BROskiPets-LLM-dNFT/broski_pet_metadata.py` |
| Source images | `H:/dNFTpet/BROskiPets-LLM-dNFT/broski_pets/{species}/{species}_evo{1..5}.png` |
| Frontend images | `H:/Hyper-Vibe-Coding-Course/frontend/public/pets/{species}.png` (10 copies of evo1) |

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
