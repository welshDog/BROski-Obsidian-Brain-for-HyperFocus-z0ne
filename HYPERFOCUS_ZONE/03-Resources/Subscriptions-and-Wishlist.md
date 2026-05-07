# Subscriptions & Wishlist

> BROski HyperFocus Brain - Services we pay for, need to top up, or want to add.
> Keep this doc updated so every agent and contributor knows the financial landscape.

---

## Active / Free Tier (Currently Running)

| Service | Plan | Dashboard | Notes |
|---|---|---|---|
| Pinata | Free Trial | https://app.pinata.cloud | URGENT: Trial ends - upgrade needed |
| Supabase | Free Tier | https://supabase.com/dashboard | Fine for testnet + early mainnet |
| Vercel | Free Tier | https://vercel.com/dashboard | Fine for now |
| WalletConnect | Free Tier | https://cloud.walletconnect.com | Fine for now |
| Basescan | Free | https://basescan.org/myapikey | API key registered, free tier |
| GitHub | Free | https://github.com/welshDog | Repo hosting |
| Base Sepolia RPC | Public Free | https://sepolia.base.org | No key needed for testnet |

---

## URGENT - Top Up / Upgrade NOW

| # | Service | Action Needed | Why | Link |
|---|---|---|---|---|
| 1 | Anthropic (Claude) | Top up credits | Pinata agent errors: credit balance too low | https://console.anthropic.com |
| 2 | Pinata | Upgrade to paid plan | Free trial ending - agent will be deleted | https://app.pinata.cloud |

---

## Wishlist - Add When Ready

| # | Service | Why We Need It | Estimated Cost | Link |
|---|---|---|---|---|
| 3 | Alchemy or QuickNode | Production RPC for Base mainnet | ~$49/mo | https://alchemy.com |
| 4 | Supabase Pro | More DB rows, edge functions, backups | $25/mo | https://supabase.com/pricing |
| 5 | Vercel Pro | Custom domains, better build limits | $20/mo | https://vercel.com/pricing |
| 6 | OpenAI API | Fallback LLM if Anthropic credits run dry | Pay-as-you-go | https://platform.openai.com |
| 7 | Base Sepolia ETH | Gas for deploying + testing contracts | Free faucet | https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet |
| 8 | Base Mainnet ETH | Gas for mainnet deploy when ready | Buy via bridge | https://bridge.base.org |
| 9 | ENS / Basename | Human-readable address for BROskiPets contract | ~$5/yr | https://app.ens.domains |

---

## Account Reference

| Service | Dashboard / Login |
|---|---|
| Anthropic billing | https://console.anthropic.com |
| Pinata Agent dashboard | https://agents.pinata.cloud/agents/x2i4f17q |
| Pinata Agents account | https://agents.pinata.cloud - Account |
| Pinata IPFS groups | https://app.pinata.cloud/ipfs/groups |
| Pinata Secrets Vault | https://agents.pinata.cloud/secrets |
| Supabase project | https://supabase.com/dashboard/project/yhtmuibgdnxhbgboajhc |
| Supabase Edge secrets | https://supabase.com/dashboard/project/yhtmuibgdnxhbgboajhc/settings/vault-secrets |
| Vercel dashboard | https://vercel.com/dashboard |
| WalletConnect | https://cloud.walletconnect.com |
| Basescan API keys | https://basescan.org/myapikey |
| Base Sepolia faucet | https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet |
| GitHub | https://github.com/welshDog |

---

## Extra Notes

- **Ollama** - free local LLM alternative to Anthropic/OpenAI for the evolver - set USE_OLLAMA=true in agent secrets to switch
- **PINATA_JWT** was rotated 21/04/2026 - always grab current BROski pinata key from app.pinata.cloud
- **Supabase** free tier is generous - fine for all of testnet + early mainnet
- **Base Sepolia public RPC** (https://sepolia.base.org) is free - only need Alchemy/QuickNode for mainnet prod
- **broski-pet-evolver** agent ID is x2i4f17q - always reference this when adding secrets or checking agent status
- **Priority order**: Top up Anthropic -> Upgrade Pinata -> then everything else when mainnet launch approaches
