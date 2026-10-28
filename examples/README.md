# 📂 Sample data

Three **made-up** keyword exports with SERP features for a fictional CRM market:

| File | Format | Site |
|---|---|---|
| `brightcrm_serp.csv` | Semrush style (`SERP Features by Keyword`, `Position Type`) | brightcrm.io ("you") |
| `pipelinehq_serp.csv` | Ahrefs style plus an `Owned features` column | pipelinehq.com |
| `salesdeck_serp.csv` | Ahrefs style plus an `Owned features` column | salesdeck.io |

The sites, rankings and features are fictional. Keywords that mention real products are only search terms.

```bash
serp-feature-ownership examples/brightcrm_serp.csv examples/pipelinehq_serp.csv examples/salesdeck_serp.csv
```
