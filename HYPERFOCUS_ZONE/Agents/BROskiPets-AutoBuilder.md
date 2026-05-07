# BROskiPets AutoBuilder — Master Agent Plan
> **AUTHORITATIVE** — Any agent executing BROskiPets build reads this first. No exceptions.
> Last updated: May 7 2026 — welshDog / Lyndz Williams, Llanelli

## Linked State
- [[BROskiPets-2026-05-07]] — canonical session state, done list, sacred rules
- Repo: https://github.com/welshDog/BROskiPets-LLM-dNFT
- HANDOFF.md: https://raw.githubusercontent.com/welshDog/BROskiPets-LLM-dNFT/main/HANDOFF.md
- Deploy checklist: https://raw.githubusercontent.com/welshDog/BROskiPets-LLM-dNFT/main/PINATA_DEPLOY_CHECKLIST.md

---

## PHASE 0 — Agent Boot Sequence (MANDATORY every session)

```
1. READ: HYPERFOCUS_ZONE/State/BROskiPets-2026-05-07.md
2. READ: HANDOFF.md from repo root
3. CONFIRM: Cross-check DONE list — do not redo completed items
4. LOAD: All 9 Sacred Rules into working memory
5. REPORT: "Vault loaded. Sacred rules confirmed. Next step: [X]"
6. FAIL LOUDLY if vault is missing or unreadable — do not proceed blind
```

---

## PHASE 1 — Upload Evo1 Images to Pinata

**Goal:** Get real CIDs replacing all PLACEHOLDER_CID references.

**What Lyndz needs to run locally (agent cannot do this — needs local file access):**
```bash
cd H:/dNFTpet/BROskiPets-LLM-dNFT
python pinata_upload_all.py
# Output: pinata_cids.json with 10 CIDs, one per species
```

**After script runs — agent does this:**
1. Read `pinata_cids.json` output
2. Update `frontend/src/pages/Pets.tsx` — replace every `PLACEHOLDER_CID` with real CID
3. Update `pet_evolver_agent.py` — replace `{CID_PLACEHOLDER}` with real root CID
4. Git commit both files: `git commit -m "feat: replace placeholder CIDs with real Pinata uploads"`
5. Git push to main
6. Report: `"Step 1 done. CIDs live. Pets.tsx + evolver updated."`

**Sacred rule check:** IPFS_GATEWAY must be `https://aqua-few-dolphin-310.mypinata.cloud` (with https://)

**10 species:**
`apex_dragon` | `blizzard_lizard` | `chaos_cat` | `cyber_fox` | `gigabyte_guinea_pig`
`hyper_beam_bunny` | `hyper_hamster` | `hyperfocus_horse` | `power_pup` | `sonic_spider`

---

## PHASE 2 — Copy PNGs to Frontend Static Folder

**Goal:** Vercel can serve evo1 images statically.

**Lyndz runs locally:**
```bash
# From repo root
mkdir -p frontend/public/pets
for species in apex_dragon blizzard_lizard chaos_cat cyber_fox gigabyte_guinea_pig hyper_beam_bunny hyper_hamster hyperfocus_horse power_pup sonic_spider; do
  mkdir -p "frontend/public/pets/$species"
  cp "H:/dNFTpet/BROskiPets-LLM-dNFT/broski_pets/$species/${species}_evo1.png" "frontend/public/pets/$species/"
done
```

**Agent does after copy:**
1. Confirm 10 PNG files exist in `frontend/public/pets/`
2. Git add + commit: `feat: add evo1 static assets for Vercel`
3. Git push
4. Report: `"Step 2 done. 10 PNGs in frontend/public/pets/"`

---

## PHASE 3 — Generate Signer Wallet

**Goal:** Create BACKEND_SIGNER keypair for contract auth.

**Lyndz runs locally (NEVER commit private key):**
```bash
cast wallet new
# Output:
# Address:     0xABC...  <- BACKEND_SIGNER_ADDRESS
# Private key: 0x123...  <- BACKEND_SIGNER_PRIVATE_KEY (store in .env only)
```

**Agent does:**
1. Remind Lyndz: save both values to a secure `.env` file, NEVER to git
2. Confirm `.env` is in `.gitignore`
3. Update vault state with BACKEND_SIGNER_ADDRESS (public, safe to store)
4. Report: `"Step 3 done. Signer wallet created: 0x..."`

---

## PHASE 4 — Deploy BROskiPet.sol to Base Sepolia

**Goal:** Get live contract address on Base Sepolia (chainId 84532).

**Pre-flight checks:**
- [ ] Funded deployer wallet (~0.01 ETH Sepolia) — faucet: https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet
- [ ] BACKEND_SIGNER_ADDRESS from Phase 3
- [ ] ETHERSCAN_API_KEY from https://basescan.org (optional for verification)

**Lyndz runs locally:**
```bash
cd H:/dNFTpet/BROskiPets-LLM-dNFT/contracts

export ADMIN_ADDRESS=0x<your MetaMask wallet>
export BACKEND_SIGNER_ADDRESS=0x<from phase 3>
export AGENT_ADDRESS=0x<same as BACKEND_SIGNER or separate>
export DEPLOYER_KEY=0x<funded wallet private key>
export BASE_SEPOLIA_RPC=https://sepolia.base.org
export ETHERSCAN_API_KEY=<from basescan.org>

forge script script/DeployBROskiPet.s.sol \
  --rpc-url $BASE_SEPOLIA_RPC \
  --private-key $DEPLOYER_KEY \
  --broadcast --verify

# Save output: BROskiPet at: 0xDEF... <- BROSKIPET_CONTRACT_ADDRESS
```

**Verify locally:**
```bash
forge test --match-contract BROskiPet -v
# Must show 22/22 passing
```

**Agent does:**
1. Save BROSKIPET_CONTRACT_ADDRESS to vault state file
2. Report: `"Step 4 done. Contract deployed + verified: 0x..."`

---

## PHASE 5 — Add Secrets to Supabase Edge Functions

**Goal:** mint-pet-auth edge function can sign mints and call contract.

**Agent navigates to (Lyndz confirms):**
https://supabase.com/dashboard/project/yhtmuibgdnxhbgboajhc/settings/functions

**Three secrets to add:**
| Secret | Value |
|--------|-------|
| `BACKEND_SIGNER_PRIVATE_KEY` | 0x... from Phase 3 |
| `BROSKIPET_CONTRACT_ADDRESS` | 0x... from Phase 4 |
| `BROSKIPET_CHAIN_ID` | `84532` |

**Agent does:**
1. Navigate to Supabase Edge Function secrets page
2. Walk Lyndz through adding each secret
3. Confirm all 3 saved
4. Report: `"Step 5 done. 3 secrets live in Supabase."`

---

## PHASE 6 — Create Pinata OpenClaw Agent

**Goal:** Deploy broski-pet-evolver as a live Pinata agent with cron + webhook.

**Pre-flight:** Phases 3 + 4 must be complete (need private key + contract address)

**Agent navigates to:** https://agents.pinata.cloud/agents

**Create agent with these exact settings:**
```
Name:              broski-pet-evolver
Language:          Python 3.12
Entrypoint:        pet_evolver_agent.py
Requirements file: requirements.evolver.txt
Source:            https://github.com/welshDog/BROskiPets-LLM-dNFT
```

**Secrets to add in Pinata vault:**
```
PINATA_JWT                = <rotated key — BROski pinata key 21/04/2026>
BROSKIPET_CONTRACT_ADDRESS = <from Phase 4>
BASE_SEPOLIA_RPC          = https://sepolia.base.org
BACKEND_SIGNER_PRIVATE_KEY = <from Phase 3>
OPENAI_API_KEY            = <Lyndz provides — OR set USE_OLLAMA=true>
IPFS_GATEWAY              = https://aqua-few-dolphin-310.mypinata.cloud
```

**Triggers:**
- Cron: `0 3 * * *` (daily 3AM UTC — daily evolution cycle)
- Webhook: enabled (save the webhook URL to vault after deploy)

**After deploy — test:**
```bash
curl https://your-agent.pinata.cloud/
# Expect: {"status": "ok", "agent": "broski-pet-evolver", "version": "1.0.0"}
```

**Agent does:**
1. Deploy agent via Pinata dashboard
2. Save webhook URL to vault state
3. Report: `"Step 6 done. Agent live at https://..."`

---

## PHASE 7 — WalletConnect Project ID

**Goal:** Enable multi-wallet support via RainbowKit.

**Lyndz does (1 min, free):**
1. Go to https://cloud.walletconnect.com
2. Create new project: `BROskiPets`
3. Copy the Project ID

**Agent does:**
1. Add to `H:/Hyper-Vibe-Coding-Course/frontend/.env`:
   ```
   VITE_WALLETCONNECT_PROJECT_ID=<project id>
   ```
2. Git commit: `feat: add WalletConnect project ID`
3. Git push
4. Run TypeScript check:
   ```bash
   cd frontend && npx tsc --noEmit
   # Must show 0 errors
   ```
5. Report: `"Step 7 done. WalletConnect wired. 0 TS errors."`

---

## FINAL VERIFICATION SEQUENCE

Run ALL of these before declaring victory:
```bash
# 1. Contract tests
cd H:/dNFTpet/BROskiPets-LLM-dNFT/contracts
forge test --match-contract BROskiPet -v
# MUST: 22/22 pass

# 2. Frontend types
cd H:/Hyper-Vibe-Coding-Course/frontend
npx tsc --noEmit
# MUST: 0 errors

# 3. Metadata smoke test
python broski_pet_metadata.py --name TestPet --species cyber_fox --rarity uncommon --dry-run
# MUST: output valid JSON

# 4. Agent health
curl https://your-agent.pinata.cloud/
# MUST: {"status": "ok"}

# 5. DB nonce check
SELECT COUNT(*) FROM mint_nonces WHERE expires_at < NOW();
# MUST: 0 orphaned rows
```

---

## FAILSAFE RULES FOR AGENTS

1. **STOP on any error** — report exact message, do not guess-fix
2. **Never touch EEPVengers.sol** — that is legacy, wrong contract
3. **Never pin to old EEPs group** — BROski_pets_dNFTs ONLY (ID: 2aedcf70-d4bb-4e13-94c9-ef6098d49aca)
4. **Never regenerate useMintPet.ts** — it is correct, do not touch
5. **Never swap wagmi.ts for injected() only** — regression
6. **Import paths:** always `@/lib/supabase` NOT `@/lib/supabaseClient`
7. **ABI types must be strings:** `string petId`, `string ipfsCID` — not uint256/bytes32
8. **Chain IDs:** testnet=84532, mainnet=8453 — never mix them
9. **Private keys:** NEVER commit to git, NEVER log to console
10. **Sacred rule violation = ABORT + flag** — alert Lyndz immediately

---

## UPDATE VAULT AFTER EVERY STEP

Append to [[BROskiPets-2026-05-07]] after each phase:
```
## Session Update — [DATE] [TIME BST]
- Phase X complete: [brief description]
- Key output: [address/URL/CID]
- Next: Phase Y
```

---

## PHASE STATUS TRACKER

| Phase | Task | Status | Blocker |
|-------|------|--------|---------|
| 0 | Read vault + HANDOFF | ✅ Auto | None |
| 1 | Upload evo1 images | ⏳ Needs local run | Lyndz runs pinata_upload_all.py |
| 2 | Copy PNGs to frontend | ⏳ Needs local run | After Phase 1 |
| 3 | Generate signer wallet | ⏳ Needs local run | `cast wallet new` |
| 4 | Deploy contract | ⏳ Needs local run | Funded wallet + Phase 3 |
| 5 | Supabase secrets | ⏳ Agent assists | After Phase 3+4 |
| 6 | Pinata agent deploy | ⏳ Agent does it | After Phase 3+4 |
| 7 | WalletConnect ID | ⏳ Lyndz 1 min | cloud.walletconnect.com |

---

---

## 📍 LIVE STATUS — May 7 2026, 12:00 BST

> This section is updated each session. Overrides the phase tracker above for current status.

| Phase | Task | Real Status | Notes |
|-------|------|-------------|-------|
| 0 | Read vault + HANDOFF | ✅ Complete | Vault + HANDOFF both readable, Sacred Rules loaded |
| 1 | Upload evo1 images | ⏳ Pending | Lyndz runs `pinata_upload_all.py` locally |
| 2 | Copy PNGs to frontend | ⏳ Pending | After Phase 1 |
| 3 | Generate signer wallet | ⏳ Pending | `cast wallet new` |
| 4 | Deploy BROskiPet.sol | ⏳ Pending | Need funded wallet + Phase 3 first |
| 5 | Supabase Edge secrets | ⏳ Pending | After Phases 3+4 |
| 6 | Pinata agent | ✅ **DEPLOYED** — Agent ID: `x2i4f17q` | 3/5 secrets live. Needs BACKEND_SIGNER + CONTRACT |
| 6b | Agent blockers | ⚠️ **URGENT** | Top up Anthropic credits + upgrade Pinata plan |
| 7 | WalletConnect ID | ⏳ Pending | 1 min at cloud.walletconnect.com |

### 🔗 Live agent link
https://agents.pinata.cloud/agents/x2i4f17q

### ⏳ Quickest path to fully operational:
1. Top up Anthropic credits (~£5) → agent can think
2. Upgrade Pinata (keep agent alive past trial)
3. `python pinata_upload_all.py` → paste cids.json to agent
4. `cast wallet new` + `forge deploy` → add 2 secrets to agent
5. Everything else unblocks automatically

---

*AutoBuilder last updated: May 7 2026 — BROski AI (Comet/Perplexity) 🐾*

*BROskiPets AutoBuilder — Generated by BROski AI, May 7 2026*
*welshDog / Lyndz Williams, Llanelli — HYPERFOCUS MODE*
