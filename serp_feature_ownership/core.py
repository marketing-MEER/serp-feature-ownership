"""Who owns the SERP features (featured snippets, People Also Ask, videos, images...) on your keywords.

Reads one keyword export per site (you first, then competitors). Each export needs the
SERP features shown for the keyword, and ideally which feature the site itself holds
(Semrush "Position Type", or an "Owned features" column). Every keyword + feature pair
is then labelled defend / steal / open / out of reach.
"""
import re
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

from .report import find_column, to_number

# Canonical feature names. Ahrefs, Semrush and other tools spell them differently.
ALIASES = {
    "featured snippet": "Featured snippet", "snippet": "Featured snippet", "answer box": "Featured snippet",
    "people also ask": "People also ask", "paa": "People also ask", "questions": "People also ask",
    "related questions": "People also ask",
    "video": "Videos", "videos": "Videos", "video carousel": "Videos", "featured video": "Videos",
    "short videos": "Videos",
    "image": "Images", "images": "Images", "image pack": "Images", "thumbnail": "Images", "thumbnails": "Images",
    "carousel": "Carousels", "carousels": "Carousels", "top stories": "Top stories", "news": "Top stories",
    "local pack": "Local pack", "map pack": "Local pack", "local": "Local pack",
    "ai overview": "AI Overview", "ai overviews": "AI Overview", "sge": "AI Overview",
    "related searches": "Related searches", "sitelinks": "Sitelinks", "reviews": "Reviews",
    "knowledge panel": "Knowledge panel", "shopping": "Shopping", "shopping results": "Shopping",
    "discussions and forums": "Discussions and forums", "discussions": "Discussions and forums",
}

# Share of SERPs showing each feature in 2024 (2023 in brackets), STAT Search Analytics,
# quoted by Neil Patel: https://neilpatel.com/marketing-stats/top-serp-features/
NP_PRESENCE_2024 = {"Related searches": 99, "Videos": 76, "People also ask": 74, "Carousels": 65, "Images": 64}

# What to build to win each feature. Videos, Images, Carousels and Related searches follow the
# insights of the top-serp-features stat; AI Overview follows serp-real-estate-google-first-page
# ("natural language phrasing", "brand FAQs in structured data"); the rest is general best practice.
ACTIONS = {
    "Videos": "Make a short video for the query and embed it with a matching title and description",
    "Images": "Add original charts or screenshots with descriptive file names and alt text",
    "Carousels": "Use consistent templates, clear sections and schema so Google can group your pages",
    "Related searches": "Publish supporting pages for the adjacent intents and interlink them",
    "People also ask": "Add question headings with a direct 1-2 sentence answer under each",
    "Featured snippet": "Answer the query in 40-60 words right under a heading that repeats it",
    "AI Overview": "Write the answer in natural language and add FAQ structured data",
    "Local pack": "Complete and update the Google Business Profile for the location",
    "Top stories": "Publish timely news content with article schema",
    "Reviews": "Add review schema to pages with genuine reviews",
}
DEFAULT_ACTION = "Check what the current owner shows and match the format"

STATUS_ORDER = ["steal", "open", "defend", "out of reach", "not ownable"]
# Shown on the SERP but not held by any one site: counted in the landscape, never an opportunity.
NOT_OWNABLE = {"Related searches"}


def canon(name: str) -> str:
    key = re.sub(r"\s+", " ", str(name).strip().lower())
    return ALIASES.get(key, key[:1].upper() + key[1:])


def split_features(text) -> list[str]:
    if text is None or (isinstance(text, float) and text != text):
        return []
    parts = re.split(r"[,;|]", str(text))
    return sorted({canon(p) for p in parts if p.strip() and p.strip().lower() not in ("nan", "organic", "-")})


def site_name(raw: pd.DataFrame, url_col: str | None, path) -> str:
    if url_col:
        for url in raw[url_col].dropna().astype(str):
            host = urlparse(url if "://" in url else "https://" + url).netloc.lower()
            if host:
                return host[4:] if host.startswith("www.") else host
    return Path(path).stem


def load_export(path) -> tuple[str, pd.DataFrame]:
    raw = pd.read_csv(path)
    kw = find_column(raw, ["keyword", "query", "search term"])
    pos = find_column(raw, ["position", "current position", "rank", "pos"])
    vol = find_column(raw, ["volume", "search volume", "avg. monthly searches"])
    feats = find_column(raw, ["serp features", "serp features by keyword", "serp_features", "features"])
    owned = find_column(raw, ["owned features", "owned serp features", "position type", "type"])
    url = find_column(raw, ["url", "current url", "landing page", "page"])
    if not kw or not feats:
        raise ValueError(f"{path}: need keyword and SERP features columns. Found: {list(raw.columns)}")
    df = pd.DataFrame({
        "keyword": raw[kw].astype(str).str.strip().str.lower(),
        "position": to_number(raw[pos]) if pos else 0,
        "volume": to_number(raw[vol]) if vol else 0,
        "features": raw[feats].map(split_features),
        "owned": raw[owned].map(split_features) if owned else [[] for _ in range(len(raw))],
    })
    df = df[df["keyword"] != ""].sort_values("position").drop_duplicates("keyword")
    return site_name(raw, url, path), df


def analyze(you_path, competitor_paths, top: int = 10):
    """Return (pairs, sites): one row per keyword + feature present on its SERP."""
    me, mine = load_export(you_path)
    exports = [(me, mine)] + [load_export(p) for p in competitor_paths]
    sites = []
    for i, (name, _) in enumerate(exports):
        sites.append(name if name not in sites else f"{name} ({i + 1})")

    keywords: dict[str, dict] = {}
    for site, (_, df) in zip(sites, exports):
        for row in df.itertuples(index=False):
            k = keywords.setdefault(row.keyword, {"volume": 0, "features": set(), "owners": {}, "pos": {}})
            k["volume"] = max(k["volume"], row.volume)
            k["features"].update(row.features)
            k["features"].update(row.owned)
            if row.position > 0:
                k["pos"][site] = row.position
            for f in row.owned:
                k["owners"].setdefault(f, []).append(site)

    rows = []
    for kw, k in keywords.items():
        you_pos = k["pos"].get(me)
        for feat in sorted(k["features"]):
            owners = k["owners"].get(feat, [])
            if feat in NOT_OWNABLE:
                status = "not ownable"
            elif me in owners:
                status = "defend"
            elif you_pos is not None and you_pos <= top:
                status = "steal" if owners else "open"
            else:
                status = "out of reach"
            rows.append({"keyword": kw, "feature": feat, "status": status, "volume": int(k["volume"]),
                         "your_position": you_pos, "owner": ", ".join(owners) if owners else "not tracked",
                         "action": ACTIONS.get(feat, DEFAULT_ACTION)})
    pairs = pd.DataFrame(rows, columns=["keyword", "feature", "status", "volume", "your_position", "owner", "action"])
    pairs["_s"] = pairs["status"].map(STATUS_ORDER.index)
    pairs = pairs.sort_values(["_s", "volume"], ascending=[True, False]).drop(columns="_s").reset_index(drop=True)
    return pairs, sites, len(keywords)


def landscape(pairs: pd.DataFrame, n_keywords: int) -> pd.DataFrame:
    rows = []
    for feat, g in pairs.groupby("feature"):
        rows.append({
            "feature": feat,
            "keywords": len(g),
            "share_of_keywords_pct": round(len(g) / max(n_keywords, 1) * 100, 1),
            "benchmark_presence_2024_pct": NP_PRESENCE_2024.get(feat),
            "volume": int(g["volume"].sum()),
            "you_own": int((g["status"] == "defend").sum()),
            "steal": int((g["status"] == "steal").sum()),
            "open": int((g["status"] == "open").sum()),
            "action": ACTIONS.get(feat, DEFAULT_ACTION),
        })
    cols = ["feature", "keywords", "share_of_keywords_pct", "benchmark_presence_2024_pct", "volume", "you_own", "steal",
            "open", "action"]
    return pd.DataFrame(rows, columns=cols).sort_values("keywords", ascending=False).reset_index(drop=True)


def ownership(pairs: pd.DataFrame, sites: list[str]) -> pd.DataFrame:
    """Feature x site: how many keywords each site holds the feature for."""
    counts = {site: [] for site in sites}
    feats = sorted(pairs["feature"].unique())
    for feat in feats:
        owners = pairs.loc[pairs["feature"] == feat, "owner"]
        for site in sites:
            counts[site].append(int(owners.map(lambda o: site in [s.strip() for s in o.split(",")]).sum()))
    out = pd.DataFrame({"feature": feats, **counts})
    out["not_tracked"] = [int(((pairs["feature"] == f) & (pairs["owner"] == "not tracked")).sum()) for f in feats]
    return out
