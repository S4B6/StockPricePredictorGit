# Markets Since 1998 — History

Public, database-free History frontend for the Stock Price Predictor project.

## Current scope

- History landing page with the six planned asset classes.
- Three published Policy Rates articles: Fed, ECB, and Key Global Policy Rates.
- Five interactive Global Policy Rates charts generated from the committed CSV snapshot.
- Explicit restoration notices for the exact Fed and ECB chart datasets that are not present in GitHub.
- Momentum and Forecasts intentionally excluded.

## Run locally

Requires Node.js 22.13 or newer.

```bash
npm run install:ci
npm run dev
```

## Validate

```bash
npm run lint
npm exec tsc -- --noEmit
npm test
```

The production build targets the Sites Cloudflare Worker runtime through Vinext.
