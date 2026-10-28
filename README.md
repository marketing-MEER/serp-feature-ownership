<div align="center">

# 🏆 serp-feature-ownership

### Find out who owns the featured snippets, People Also Ask boxes, videos and images on your keywords, and which ones you can take.

[![tests](https://github.com/marketing-MEER/serp-feature-ownership/actions/workflows/ci.yml/badge.svg)](https://github.com/marketing-MEER/serp-feature-ownership/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![No API keys](https://img.shields.io/badge/API%20keys-none%20needed-brightgreen)
[![Part of SEO Toolbox](https://img.shields.io/badge/part%20of-SEO%20Toolbox-orange)](https://github.com/marketing-MEER/seo-toolbox)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Meer%20Hamza-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/meerhamza-seo)

[🚀 Quick start](#quick-start) · [⚙️ How it works](#how-it-works) · [📄 Report](#report) · [❓ FAQ](#faq) · [👤 Author](#author)

</div>

---

## 💡 What it does

A blue link at position 3 is not the whole page any more. Most keywords show a mix of People Also Ask, videos, images and AI Overviews, and somebody holds each of them. Working out who, keyword by keyword, means a lot of filtering in Ahrefs or Semrush.

`serp-feature-ownership` takes your keyword export plus up to 5 competitor exports and labels every keyword + feature pair: **steal** (a competitor holds it and you already rank top 10), **open** (no tracked site holds it), **defend** (you hold it) or **out of reach** (win the ranking first). Each row comes with what to build to win that feature.

- ✅ Feature landscape: how often each feature shows on your keywords, next to 2024 benchmark presence rates
- ✅ An ownership matrix (feature × site) and a prioritised steal list
- ✅ Reads Semrush and Ahrefs spellings ("Video carousel", "Image pack", "PAA"...) as one feature
- ✅ Free, MIT licensed, no API keys. Works with the exports you already have

## 📊 Why this matters

> **Top SERP Features** · STAT Search Analytics, November 2024
> - Related Searches presence rose from 84% (2023) to 99% (2024).
> - Videos presence increased from 53% (2023) to 76% (2024).
> - People Also Ask presence dipped from 79% (2023) to 74% (2024).
> - Images presence jumped from 38% (2023) to 64% (2024).
>
> **What Takes Up The First Page of Google Search Results** · NP Digital, June 2025
> - Informational queries are 62% organic, 11% AI Overview, and 14% branded content.
> - Transactional queries are 56% organic, 13% paid, 18% zero-click.
>
> Data: [top SERP features](https://neilpatel.com/marketing-stats/top-serp-features/) · [first page of Google](https://neilpatel.com/marketing-stats/serp-real-estate-google-first-page/)

**How serp-feature-ownership uses this:** with videos on three in four SERPs and images on nearly two in three, a page that only targets the blue link leaves a lot of the page to others. The report puts your own feature mix next to these presence rates, and the build actions come from the insights: *"create short explainer clips that match the primary query"* for videos, *"add original charts, screenshots, and annotated visuals with descriptive filenames and alt text"* for images, and *"use natural language phrasing"* plus FAQ structured data for AI Overviews. Featured snippet and PAA actions are general best practice.

<a id="quick-start"></a>

## 🚀 Quick start

```bash
git clone https://github.com/marketing-MEER/serp-feature-ownership.git
cd serp-feature-ownership
pip install -e .
serp-feature-ownership examples/brightcrm_serp.csv examples/pipelinehq_serp.csv examples/salesdeck_serp.csv
```

The first file is **you**; the rest (0 to 5) are competitors. This writes **`serp_features.html`** (a formatted report you can share or print to PDF) and **`serp_features.xlsx`** (all data, one sheet per status).

> [!TIP]
> If the `serp-feature-ownership` command isn't found, use `python -m serp_feature_ownership`.

## 📥 Input

One keyword export per site. Columns are detected automatically:

| Column | Accepted names | Needed? |
|---|---|---|
| Keyword | `Keyword`, `Query` | yes |
| SERP features on the page | `SERP Features by Keyword` (Semrush), `SERP features` (Ahrefs) | yes |
| Feature the site holds | `Position Type` (Semrush), `Owned features` | for ownership |
| Position, volume, URL | `Position` / `Current position`, `Volume` / `Search Volume`, `URL` / `Current URL` | recommended |

Features can be separated by commas, semicolons or `|`. If an export has no ownership column, that site is simply never counted as an owner. Add an `Owned features` column by hand for the keywords you care about if your tool doesn't export one.

<a id="how-it-works"></a>

## ⚙️ How it works

1. **Load** each export and normalise feature names (Video carousel → Videos, Image pack → Images, PAA → People also ask, AI Overviews → AI Overview, ...).
2. **Join** all sites on the keyword. A feature counts as present if any export lists it.
3. **Label** each keyword + feature pair:

| Status | Rule | What to do |
|---|---|---|
| 🔴 **steal** | A competitor holds the feature; you rank in the top `--top` | Build the format the owner uses, better |
| 🟡 **open** | No tracked site holds it; you rank in the top `--top` | Add the format; nobody you track is in the way |
| 🟢 **defend** | You hold it | Keep the page fresh |
| ⚪ **out of reach** | You rank below `--top` or not at all | Win the ranking first |
| ➖ **not ownable** | Related searches | Context only |

4. **Sort** steal first, then by volume.

### Options

| Option | Default | What it does |
|---|---|---|
| `--top` | `10` | You must rank at or above this position for a feature to count as winnable |
| `-o`, `--output` | `serp_features` | Report name; writes `.html` and `.xlsx` |

<a id="report"></a>

## 📄 The report

| Section / Excel sheet | Shows |
|---|---|
| Summary cards | Keywords, pairs, defend / steal / open counts |
| Benchmark panels | The two Neil Patel stats behind the checks |
| **Landscape** | Per feature: keywords, share of your keywords, 2024 benchmark presence, volume, you own / steal / open, action |
| **Ownership** | Feature × site: how many keywords each site holds the feature for |
| **Steal / Open / Defend** | One table each, with owner, your position and the action |
| **All pairs** | Everything in one sheet |

<details>
<summary>📄 Example: real output from <code>examples/</code> (fictional CRM sites)</summary>

**Feature landscape** (action column left out here)

| feature | keywords | share of keywords pct | benchmark presence 2024 pct | volume | you own | steal | open |
|---|---|---|---|---|---|---|---|
| Related searches | 24 | 100 | 99 | 74,520 | 0 | 0 | 0 |
| People also ask | 19 | 79.2 | 74 | 47,130 | 7 | 2 | 2 |
| Images | 14 | 58.3 | 64 | 40,200 | 4 | 1 | 3 |
| Featured snippet | 12 | 50 |  | 47,490 | 2 | 1 | 3 |
| Videos | 11 | 45.8 | 76 | 54,430 | 4 | 1 | 2 |
| AI Overview | 9 | 37.5 |  | 13,460 | 2 | 2 | 0 |
| Reviews | 3 | 12.5 |  | 14,400 | 1 | 1 | 0 |
| Local pack | 1 | 4.2 |  | 210 | 0 | 0 | 1 |

**Steal list** (top 5)

| keyword | feature | volume | your position | owner |
|---|---|---|---|---|
| crm for real estate agents | AI Overview | 1,900 | 3 | pipelinehq.com |
| crm vs erp | Images | 1,600 | 3 | salesdeck.io |
| crm vs erp | Reviews | 1,600 | 3 | pipelinehq.com |
| how to build a sales pipeline | Featured snippet | 1,300 | 5 | salesdeck.io |
| how to build a sales pipeline | People also ask | 1,300 | 5 | pipelinehq.com |

**Who owns what**

| feature | brightcrm.io | pipelinehq.com | salesdeck.io | not tracked |
|---|---|---|---|---|
| AI Overview | 2 | 3 | 1 | 3 |
| Featured snippet | 2 | 2 | 2 | 6 |
| Images | 4 | 2 | 1 | 7 |
| People also ask | 7 | 2 | 2 | 8 |
| Videos | 4 | 1 | 3 | 3 |

</details>

## 🧰 More free SEO tools

This repo is one tool in the **[SEO Toolbox](https://github.com/marketing-MEER/seo-toolbox)**, a family of free, single-purpose SEO tools. Related:
- [serp-competitor-finder](https://github.com/marketing-MEER/serp-competitor-finder): find who you really compete with, by share of voice
- [keyword-gap-analyzer](https://github.com/marketing-MEER/keyword-gap-analyzer): keywords competitors win and you don't, ranked by revenue potential
- [seo-workhorse](https://github.com/marketing-MEER/seo-workhorse): audit, clustering, redirects and GSC quick wins in one CLI

<a id="faq"></a>

## ❓ FAQ

<details><summary><b>My tool doesn't say which feature I hold. What then?</b></summary>

Semrush's `Position Type` does. For Ahrefs, filter Organic keywords by "SERP features: owned" and add the result as an `Owned features` column. Without it, the report still shows the landscape and the open pairs.
</details>

<details><summary><b>Why is "Related searches" never an opportunity?</b></summary>

Google fills it with queries, not with a site, so nobody holds it. It stays in the landscape because it shows which adjacent topics to cover.
</details>

<details><summary><b>Why only keywords where I rank top 10?</b></summary>

Most features go to pages already on page one. Below that, the work is ranking first. Change it with `--top`.
</details>

<details><summary><b>Is my data sent anywhere?</b></summary>

No. It reads your CSV files and writes the report on your computer. It makes no network requests.
</details>

## 🧪 Tests

```bash
python -m unittest discover -s tests -t . -v
```

## 📄 License

[MIT](LICENSE). Free for personal and commercial use. Benchmark figures © their original publishers, quoted with a link to the source.

<a id="author"></a>

## 👤 Author

**Meer Hamza** · SEO Team Lead · Berlin 🇩🇪
10+ years in SEO, AEO and GEO. I build small tools that take the spreadsheet work out of SEO.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/meerhamza-seo)
[![Email](https://img.shields.io/badge/Email-meerhamza5%40gmail.com-D14836?logo=gmail&logoColor=white)](mailto:meerhamza5@gmail.com)

<div align="center">

**If this saved you time, a ⭐ helps other SEOs find it.**

</div>
