---
project: true
status: Active
coins: 0
xp: 0
tags: [project, nft, ai, pets, web3, base]
updated: 2026-05-08
---

# 🐾 BROskiPets — LLM dNFT

## Why Matters
AI-evolving pets that live on-chain (Base). Dev actions = pet XP. Pets persist across reloads. Squad row = social proof. Path to Legend stage.

> Two repos contribute: `BROskiPets-LLM-dNFT` (78 EEPs on Ethereum Sepolia, port 8098) and the **course-side mint stack** in `Hyper-Vibe-Coding-Course/frontend/src/components/pets/` + `supabase/functions/mint-pet-auth/` (10 species, Base Sepolia + Base mainnet, RainbowKit). This note tracks the **course-side mint stack**.

## Current Status (May 8, 2026)
- ✅ **Phase 0** — Web3 stack wired (RainbowKit + wagmi + viem) — May 7
- ✅ **Phase 1** — Mint UI live, 10 species, Pinata CIDs, Edge Fn auth, EIP-712 v2 — May 7
- ✅ **Phase 2A** — Persistent collection (Edge Fn v4 + `pets` table + `top_pets` view + RLS) — May 8 AM
- ✅ **Phase 2B** — Evolution Timeline (6 stages, current highlight, progress to next) — May 8 PM
- ✅ **Phase 2C** — Squad row from `top_pets` + How-XP-feeds-your-pet (3-col education) — May 8 PM
- ✅ **Phase 2D** — Polish pass: skeletons, gold sweep, border-pulse, empty state, fade-in-up — May 8 PM

## 🔴 Blockers
- 🔴 `VITE_MINT_VIA_RELAY=true` not on Vercel — Phase 2A persistence is RELAY-MODE-ONLY
- 🔴 Relayer wallet needs Base ETH

## Next Phase Options
- [ ] **Phase 2A.5** — `mint-pet-confirm` Edge Fn → wallet-signed mode persistence (closes the relay-only gap)
- [ ] **Phase 3** — On-chain evolve transactions (needs contract method + agent key wiring)
- [ ] **V2.4 sync question** — does V2.4 need a `pets`/`mint_nonces` sync endpoint?

## 💡 Elevation Ideas (from design-brain audit, May 8)
> Score 7→8.5/10 after Phase 2D. These would push to 9+:
- **Asymmetric Timeline** — current stage tile spans 2 cols on `lg`, with thin connector line through unlocked tiles → grid becomes a path
- **Trading-card tilt** on PetCard hover — `perspective(1000px) rotateY(2deg) rotateX(-1deg)` 250ms ease-out → holographic Pokémon feel
- **#1 squad card hero treatment** — first card in `PetSquadRow` gets `lg:col-span-2`, larger image, "🥇 Top evolver" tag
- **BROski$ earn celebration** — every BROski$ event deserves micro-celebration (confetti emoji burst + counter tween)
- **Reduced-motion review** — current `motion-safe:` coverage is ~95% — verify all animation paths once on a `prefers-reduced-motion: reduce` browser

## File Inventory (course-side, all in `H:\Hyper-Vibe-Coding-Course\frontend\src\`)
| File | Phase | Purpose |
|---|---|---|
| `lib/species.ts` | 1 | 10 species + Pinata CIDs |
| `lib/evolution.ts` | 2A | 6 stages + `progressInStage()` + `baseScanTxUrl()` |
| `lib/wagmi.ts` | 1 | Base config (Sepolia + mainnet) |
| `lib/contracts/broskiPet.ts` | 1 | ABI + address |
| `hooks/useMintPet.ts` | 1 (updated 2A) | Two modes: wallet-signed + relay |
| `hooks/useMyPets.ts` | 2A | RLS-safe collection fetch |
| `hooks/useTopPets.ts` | 2C | Public squad row data |
| `components/pets/SpeciesPicker.tsx` | 1 | Visual picker UI |
| `components/pets/MintPetButton.tsx` | 1 (updated 2A) | Full Web3 mint flow |
| `components/pets/PetCard.tsx` | 2A (updated 2D) | Hero card (full + mini) + freshMint sweep |
| `components/pets/PetCardSkeleton.tsx` | 2D | Shape-matched skeleton |
| `components/pets/XPBar.tsx` | 2A (updated 2D) | Stage-aware progress bar |
| `components/pets/MoodBadge.tsx` | 2A | 4-mood tag |
| `components/pets/EvolutionTimeline.tsx` | 2B | 6-stage path, current highlight |
| `components/pets/PetSquadRow.tsx` | 2C | Top 12 mini-card row |
| `pages/Pets.tsx` | 1 (extended 2A/B/C/D) | Sections 0–6 |
| `supabase/migrations/20260508120000_broskipets_persistence.sql` | 2A | `pets` table + `top_pets` view |
| `supabase/functions/mint-pet-auth/` | 1→v4 | Auth + sign + relay + INSERT |

## Tailwind Keyframes Added (May 8 PM)
- `shimmer` — skeleton sweep
- `goldSweep` — one-shot fresh-mint celebration
- `fadeInUp` — stagger entrance for lists/grids

## Links
- [Repo (LLM dNFT side)](https://github.com/welshDog/BROskiPets-LLM-dNFT)
- [[Hyper-Vibe-Course]]
- [[HyperCode-V2.4]]
