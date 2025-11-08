import os
import json
import argparse
import datetime
import asyncio
import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from urllib.parse import quote_plus, urlparse
from email.utils import parsedate_to_datetime

# Optional: improve main content extraction if available
try:
    from readability import Document
    HAVE_READABILITY = True
except Exception:
    HAVE_READABILITY = False

USER_AGENT = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
}

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
BING_NEWS_KEY = os.getenv("BING_NEWS_KEY")  # Azure Cognitive Services (Bing News Search v7)
FINNHUB_KEY = os.getenv("FINNHUB_KEY")

# ---------------------------------------------------------------------------
# SIMPLE HEURISTICS FOR PRIORITIZATION (no external deps)
# ---------------------------------------------------------------------------

# Simple domain prefrence (optional; values ~0..0.6 as additive bonus)
DOMAIN_BONUS = {
    "reuters.com": 0.40,
    "bloomberg.com": 0.50,
    "wsj.com": 0.50,
    "cnbc.com": 0.30,
    "marketwatch.com": 0.25,
    "finance.yahoo.com": 0.20,
    "seekingalpha.com": 0.25,
    "ft.com": 0.50,
}

# Simple "wordlist" for relevance/sentiment signal in headline/summary
KEYWORD_WEIGHTS = {
    # Positive
    "beat": 0.6, "beats": 0.6, "surge": 0.6, "soar": 0.6, "soars": 0.6,
    "record": 0.5, "raise guidance": 0.8, "guidance raised": 0.8,
    "upgrade": 0.7, "upgrades": 0.7, "overweight": 0.5, "outperform": 0.5,
    "buyback": 0.5, "acquisition": 0.7, "merger": 0.6,
    # Negative
    "miss": -0.7, "misses": -0.7, "downgrade": -0.8, "downgrades": -0.8,
    "cut guidance": -0.9, "guidance cut": -0.9, "warning": -0.5,
    "lawsuit": -0.6, "probe": -0.5, "sec": -0.4, "recall": -0.6,
    "plunge": -0.7, "falls": -0.6, "missed": -0.6, "layoff": -0.5, "bankruptcy": -1.0
}

# ---------------------------------------------------------------------------
# UTILITIES
# ---------------------------------------------------------------------------

def is_recent(date: datetime.datetime, max_age_days: int) -> bool:
    if date.tzinfo is None:
        date = date.replace(tzinfo=datetime.timezone.utc)
    now = datetime.datetime.now(datetime.timezone.utc)
    return (now - date).days <= max_age_days

async def fetch_page(session: ClientSession, url: str, source: str, topic: str) -> str:
    """Fetch HTML content asynchronously with error reporting."""
    try:
        async with session.get(url, headers=USER_AGENT, timeout=20) as resp:
            resp.raise_for_status()
            return await resp.text()
    except Exception as e:
        print(f"[ERROR] {source}:{topic} - Failed request: {e} ({url})")
        return ""

def ensure_datetime(dt_value: Optional[object]) -> datetime.datetime:
    if isinstance(dt_value, datetime.datetime):
        return dt_value
    if isinstance(dt_value, str):
        try:
            return datetime.datetime.fromisoformat(dt_value.replace("Z", "+00:00"))
        except Exception:
            pass
        try:
            return parsedate_to_datetime(dt_value)
        except Exception:
            pass
    return datetime.datetime.now(datetime.timezone.utc)

def json_default(o):
    if isinstance(o, datetime.datetime):
        if o.tzinfo is None:
            o = o.replace(tzinfo=datetime.timezone.utc)
        return o.isoformat()
    return str(o)

def extract_main_text(html: str, extractor: str = "readability") -> str:
    """Extracts main article text from HTML."""
    text = ""
    try:
        if extractor == "readability" and HAVE_READABILITY:
            doc = Document(html)
            content_html = doc.summary(html_partial=True)
            text = BeautifulSoup(content_html, "html.parser").get_text("\n", strip=True)
        else:
            soup = BeautifulSoup(html, "html.parser")
            paragraphs = [p.get_text(strip=False) for p in soup.find_all("p")]
            text = "\n".join(paragraphs)
    except Exception as e:
        # Fallback: raw paragraphs if readability failed
        try:
            soup = BeautifulSoup(html, "html.parser")
            paragraphs = [p.get_text(strip=False) for p in soup.find_all("p")]
            text = "\n".join(paragraphs)
        except Exception as e2:
            print(f"[WARN] Extraction failed twice: {e2}")
            text = ""
    return text

def _domain_from_url(url: str) -> str:
    try:
        netloc = urlparse(url).netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc
    except Exception:
        return ""

def _keyword_score(text: str) -> float:
    score = 0.0
    if not text:
        return score
    ltext = text.lower()
    for kw, w in KEYWORD_WEIGHTS.items():
        if kw in ltext:
            score += w
    return score

def _recency_score(published_at: datetime.datetime, now_utc: datetime.datetime) -> float:
    # 0..2 by freshness (newer = more)
    delta_h = max(0.0, (now_utc - published_at).total_seconds() / 3600.0)
    if delta_h <= 1:
        return 2.0
    if delta_h <= 6:
        return 1.6
    if delta_h <= 24:
        return 1.2
    if delta_h <= 72:
        return 0.8
    return 0.4

def compute_article_score(article: Dict, topic: str, now_utc: datetime.datetime) -> float:
    published_at = ensure_datetime(article.get("published_at"))
    title = article.get("title") or ""
    summary = article.get("summary") or article.get("description") or ""
    url = article.get("url") or ""

    recency = _recency_score(published_at, now_utc)
    text = f"{title}\n{summary}".strip()
    kw_score = _keyword_score(text)

    # Boost, if ticker/term is directly mentioned in title/summary
    mention_boost = 0.4 if topic.lower() in text.lower() else 0.0

    # Small domain bonus
    domain = _domain_from_url(url)
    domain_bonus = DOMAIN_BONUS.get(domain, 0.0)

    return recency + kw_score + mention_boost + domain_bonus

def select_top_n_indices(articles: List[Dict], topic: str, top_n: int) -> Tuple[set, List[float]]:
    """
    Returns: (set of indices for full-fetch, score list in original ordering).
    """
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    scored = [(i, compute_article_score(a, topic, now_utc)) for i, a in enumerate(articles)]
    scored.sort(key=lambda t: t[1], reverse=True)
    top_idx = set(i for i, _ in scored[:top_n]) if top_n > 0 else set()
    # Map score back to ordering
    scores_in_order = [0.0] * len(articles)
    for i, s in scored:
        scores_in_order[i] = s
    return top_idx, scores_in_order

async def save_articles(
    session: ClientSession,
    articles: List[Dict],
    topic: str,
    source: str,
    output_base: Path,
    content_opts: Dict
):
    """
    Save each article as a JSON file. Optionally fetch and extract full content.
    Uses provided 'summary' when available to avoid fetching webpages unnecessarily.
    """
    output_dir = output_base / source / topic
    os.makedirs(output_dir, exist_ok=True)

    sem = asyncio.Semaphore(6)  # limit parallel downloads per source/topic
    fetch_full = bool(content_opts.get("fetch_full_content", False))
    extractor = content_opts.get("content_extractor", "readability")
    max_chars = int(content_opts.get("max_content_chars", 8000))
    fetch_full_top_n = int(content_opts.get("fetch_full_top_n", 0))  # 0 = don't se top-N mode

    # If top-N mode is on, we count the score and choose indices for a full fetch
    indices_for_full_fetch: set = set()
    scores_in_order: List[float] = [0.0] * len(articles)
    if fetch_full and fetch_full_top_n > 0 and len(articles) > 0:
        indices_for_full_fetch, scores_in_order = select_top_n_indices(articles, topic, fetch_full_top_n)
    elif fetch_full and fetch_full_top_n <= 0:
        # No limit on N -> fetch for all
        indices_for_full_fetch = set(range(len(articles)))
        # Optionally compute score, so we can save it
        _, scores_in_order = select_top_n_indices(articles, topic, 0)

    async def save_one(article, idx):
        async with sem:
            published_at = ensure_datetime(article.get("published_at"))
            filename = f"{idx+1:03d}_{published_at.strftime('%Y-%m-%d')}.json"
            filepath = output_dir / filename
            url = article.get("url", "")

            # Prefer provided summary/description to avoid hitting the site
            content_text = (article.get("summary") or article.get("description") or "").strip()

            # Decide, whether to pull full content for ths article
            should_fetch_full = fetch_full and (idx in indices_for_full_fetch)

            # Optionally fetch the full content
            if should_fetch_full and url:
                html = await fetch_page(session, url, source, topic)
                if html:
                    extracted = extract_main_text(html, extractor=extractor).strip()
                    if extracted:
                        content_text = extracted

            if max_chars and content_text and len(content_text) > max_chars:
                content_text = content_text[:max_chars].rstrip() + "..."

            record = {
                "source": source,
                "topic": topic,
                "title": article.get("title"),
                "url": url,
                "published_at": published_at,  # serialized via json_default
                "content": content_text,
                "score": float(scores_in_order[idx]) if 0 <= idx < len(scores_in_order) else None
            }

            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(record, f, indent=2, ensure_ascii=False, default=json_default)
                print(f"[SAVED] {filepath}")
            except Exception as e:
                print(f"[ERROR] {source}:{topic} - Failed to save article: {e} ({url})")

    await asyncio.gather(*(save_one(a, i) for i, a in enumerate(articles)))

# ---------------------------------------------------------------------------
# SOURCE SCRAPERS / ADAPTERS
# Keep in-memory 'published_at' as datetime; JSON serialization happens in save_articles.
# Include 'summary' when the API provides it.
# ---------------------------------------------------------------------------

async def fetch_yahoo_finance(session: ClientSession, topic: str, max_age_days: int) -> List[Dict]:
    base_url = "https://finance.yahoo.com"
    search_url = f"{base_url}/quote/{quote_plus(topic)}/news?p={quote_plus(topic)}"
    html = await fetch_page(session, search_url, "YahooFinance", topic)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    articles: List[Dict] = []
    for item in soup.find_all("li", {"class": "js-stream-content"}):
        try:
            link = item.find("a", href=True)
            time_tag = item.find("time")
            if not link:
                continue
            url = link["href"]
            if not url.startswith("http"):
                url = base_url + url
            title = link.get_text(strip=True)

            if time_tag and time_tag.get("datetime"):
                published_at = ensure_datetime(time_tag["datetime"])
            else:
                published_at = datetime.datetime.now(datetime.timezone.utc)

            if is_recent(published_at, max_age_days):
                # Yahoo page provides no summary here; leave empty
                articles.append({"title": title, "url": url, "published_at": published_at})
        except Exception as e:
            print(f"[ERROR] YahooFinance:{topic} - Parsing failed: {e}")
    return articles

async def fetch_google_news(session: ClientSession, topic: str, max_age_days: int) -> List[Dict]:
    url = f"https://news.google.com/search?q={quote_plus(topic)}+finance&hl=en&gl=US&ceid=US:en"
    html = await fetch_page(session, url, "GoogleNews", topic)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    articles: List[Dict] = []
    for item in soup.find_all("article"):
        try:
            link_tag = item.find("a", href=True)
            if not link_tag:
                continue
            href = link_tag["href"]
            if href.startswith("./"):
                href = "https://news.google.com" + href[1:]
            title = link_tag.get_text(strip=True)
            published_at = datetime.datetime.now(datetime.timezone.utc)
            if is_recent(published_at, max_age_days):
                articles.append({"title": title, "url": href, "published_at": published_at})
        except Exception as e:
            print(f"[ERROR] GoogleNews:{topic} - Parsing failed: {e}")
    return articles

async def fetch_marketwatch(session: ClientSession, topic: str, max_age_days: int) -> List[Dict]:
    url = f"https://www.marketwatch.com/search?q={quote_plus(topic)}"
    html = await fetch_page(session, url, "MarketWatch", topic)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    articles: List[Dict] = []
    for item in soup.select("div.article__content"):
        try:
            link = item.find("a", href=True)
            date_tag = item.find("time")
            if not link:
                continue
            title = link.get_text(strip=True)
            href = link["href"]
            if date_tag and date_tag.has_attr("datetime"):
                published_at = ensure_datetime(date_tag["datetime"])
            else:
                published_at = datetime.datetime.now(datetime.timezone.utc)
            if is_recent(published_at, max_age_days):
                articles.append({"title": title, "url": href, "published_at": published_at})
        except Exception as e:
            print(f"[ERROR] MarketWatch:{topic} - Parsing failed: {e}")
    return articles

async def fetch_reuters(session: ClientSession, topic: str, max_age_days: int) -> List[Dict]:
    url = f"https://www.reuters.com/site-search/?query={quote_plus(topic)}&section=business"
    html = await fetch_page(session, url, "Reuters", topic)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    articles: List[Dict] = []
    for item in soup.select("div.search-result-content"):
        try:
            link = item.find("a", href=True)
            date_tag = item.find("time")
            if not link:
                continue
            href = link["href"]
            if href and href.startswith("/"):
                href = "https://www.reuters.com" + href
            title = link.get_text(strip=True)
            if date_tag and date_tag.has_attr("datetime"):
                published_at = ensure_datetime(date_tag["datetime"])
            else:
                published_at = datetime.datetime.now(datetime.timezone.utc)
            if is_recent(published_at, max_age_days):
                articles.append({"title": title, "url": href, "published_at": published_at})
        except Exception as e:
            print(f"[ERROR] Reuters:{topic} - Parsing failed: {e}")
    return articles

async def fetch_cnbc(session: ClientSession, topic: str, max_age_days: int) -> List[Dict]:
    url = f"https://www.cnbc.com/search/?query={quote_plus(topic)}&qsearchterm={quote_plus(topic)}"
    html = await fetch_page(session, url, "CNBC", topic)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    articles: List[Dict] = []
    for item in soup.select("div.SearchResultCard"):
        try:
            link = item.find("a", href=True)
            if not link:
                continue
            href = link["href"]
            if not href.startswith("http"):
                href = "https://www.cnbc.com" + href
            title = link.get_text(strip=True)
            published_at = datetime.datetime.now(datetime.timezone.utc)
            if is_recent(published_at, max_age_days):
                articles.append({"title": title, "url": href, "published_at": published_at})
        except Exception as e:
            print(f"[ERROR] CNBC:{topic} - Parsing failed: {e}")
    return articles

# ---- Google News RSS (includes description) -------------------------------

async def fetch_google_news_rss(session: ClientSession, topic: str, max_age_days: int) -> List[Dict]:
    when = f"when%3A{max(1, max_age_days)}d"
    url = f"https://news.google.com/rss/search?q={quote_plus(topic)}%20{when}&hl=en-US&gl=US&ceid=US:en"
    xml = await fetch_page(session, url, "GoogleNewsRSS", topic)
    if not xml:
        return []
    soup = BeautifulSoup(xml, "xml")
    items = soup.find_all("item")
    articles: List[Dict] = []
    for it in items:
        try:
            title = it.title.get_text(strip=True) if it.title else None
            link = it.link.get_text(strip=True) if it.link else None
            pub = it.pubDate.get_text(strip=True) if it.pubDate else None
            desc = it.description.get_text(strip=True) if it.description else None
            published_at = ensure_datetime(pub) if pub else datetime.datetime.now(datetime.timezone.utc)
            if title and link and is_recent(published_at, max_age_days):
                articles.append({
                    "title": title,
                    "url": link,
                    "published_at": published_at,
                    "summary": desc or ""
                })
        except Exception as e:
            print(f"[ERROR] GoogleNewsRSS:{topic} - Parsing failed: {e}")
    return articles

# ---- NewsAPI.org (description/content fields) ----------------------------

async def fetch_newsapi(session: ClientSession, topic: str, max_age_days: int) -> List[Dict]:
    if not NEWSAPI_KEY:
        print("[INFO] NEWSAPI_KEY not set; skipping NewsAPI.org")
        return []
    q = quote_plus(topic)
    url = f"https://newsapi.org/v2/everything?q={q}&sortBy=publishedAt&language=en&pageSize=100&apiKey={NEWSAPI_KEY}"
    try:
        async with session.get(url, timeout=20) as resp:
            resp.raise_for_status()
            data = await resp.json()
    except Exception as e:
        print(f"[ERROR] NewsAPI:{topic} - Request failed: {e}")
        return []
    articles: List[Dict] = []
    for art in data.get("articles", []):
        try:
            title = art.get("title")
            link = art.get("url")
            desc = art.get("description") or ""
            # NewsAPI 'content' is often shortened; save as summary
            content_snip = art.get("content") or ""
            published_at = ensure_datetime(art.get("publishedAt"))
            if title and link and is_recent(published_at, max_age_days):
                articles.append({
                    "title": title,
                    "url": link,
                    "published_at": published_at,
                    "summary": desc or content_snip
                })
        except Exception as e:
            print(f"[ERROR] NewsAPI:{topic} - Parse failed: {e}")
    return articles

# ---- Bing News Search (Azure) (has 'description') -------------------------

async def fetch_bing_news(session: ClientSession, topic: str, max_age_days: int) -> List[Dict]:
    if not BING_NEWS_KEY:
        print("[INFO] BING_NEWS_KEY not set; skipping Bing News")
        return []
    q = quote_plus(topic)
    url = f"https://api.bing.microsoft.com/v7.0/news/search?q={q}&mkt=en-US&freshness={max(1, max_age_days)}d&count=100&sortBy=Date"
    headers = {"Ocp-Apim-Subscription-Key": BING_NEWS_KEY}
    try:
        async with session.get(url, headers=headers, timeout=20) as resp:
            resp.raise_for_status()
            data = await resp.json()
    except Exception as e:
        print(f"[ERROR] BingNews:{topic} - Request failed: {e}")
        return []
    articles: List[Dict] = []
    for v in data.get("value", []):
        try:
            title = v.get("name")
            link = v.get("url")
            desc = v.get("description") or ""
            date_str = v.get("datePublished")
            published_at = ensure_datetime(date_str)
            if title and link and is_recent(published_at, max_age_days):
                articles.append({
                    "title": title,
                    "url": link,
                    "published_at": published_at,
                    "summary": desc
                })
        except Exception as e:
            print(f"[ERROR] BingNews:{topic} - Parse failed: {e}")
    return articles

# ---- Finnhub company-news (has 'summary') ---------------------------------

async def fetch_finnhub(session: ClientSession, topic: str, max_age_days: int) -> List[Dict]:
    if not FINNHUB_KEY:
        print("[INFO] FINNHUB_KEY not set; skipping Finnhub")
        return []
    to_dt = datetime.datetime.utcnow().date()
    from_dt = to_dt - datetime.timedelta(days=max(1, max_age_days))
    url = (
        f"https://finnhub.io/api/v1/company-news"
        f"?symbol={quote_plus(topic)}&from={from_dt.isoformat()}&to={to_dt.isoformat()}&token={FINNHUB_KEY}"
    )
    try:
        async with session.get(url, timeout=20) as resp:
            resp.raise_for_status()
            data = await resp.json()
    except Exception as e:
        print(f"[ERROR] Finnhub:{topic} - Request failed: {e}")
        return []
    articles: List[Dict] = []
    if isinstance(data, list):
        for it in data:
            try:
                title = it.get("headline")
                link = it.get("url")
                summary = it.get("summary") or ""
                ts = it.get("datetime")
                if ts is not None:
                    published_at = datetime.datetime.fromtimestamp(int(ts), tz=datetime.timezone.utc)
                else:
                    published_at = datetime.datetime.now(datetime.timezone.utc)
                if title and link and is_recent(published_at, max_age_days):
                    articles.append({
                        "title": title,
                        "url": link,
                        "published_at": published_at,
                        "summary": summary
                    })
            except Exception as e:
                print(f"[ERROR] Finnhub:{topic} - Parse failed: {e}")
    return articles

# ---------------------------------------------------------------------------
# ASYNC EXECUTION
# ---------------------------------------------------------------------------

SOURCES = {
    # HTML scrapers (use only when allowed)
    "yahoofinance": fetch_yahoo_finance,
    "googlenews": fetch_google_news,
    "marketwatch": fetch_marketwatch,
    "reuters": fetch_reuters,
    "cnbc": fetch_cnbc,
    # Preferred sources:
    "googlenews_rss": fetch_google_news_rss,
    "newsapi": fetch_newsapi,
    "bingnews": fetch_bing_news,
    "finnhub": fetch_finnhub,
}

async def gather_for_topic(
    session: ClientSession,
    topic: str,
    sources: List[str],
    max_age_days: int,
    output_base: Path,
    content_opts: Dict
):
    for source in sources:
        print(f"\n=== Fetching '{topic}' from {source.title()} ===")
        fetch_func = SOURCES.get(source)
        if not fetch_func:
            print(f"[ERROR] Unknown source: {source}")
            continue
        articles = await fetch_func(session, topic, max_age_days)
        if not articles:
            print(f"[INFO] No articles found for '{topic}' on {source.title()}")
            continue
        await save_articles(session, articles, topic, source, output_base, content_opts)

async def main_async(config: Dict, output_base: Path):
    conn = aiohttp.TCPConnector(limit_per_host=8)
    timeout = aiohttp.ClientTimeout(total=60)
    content_opts = {
        "fetch_full_content": bool(config.get("fetch_full_content", False)),
        "content_extractor": config.get("content_extractor", "readability"),
        "max_content_chars": int(config.get("max_content_chars", 8000)),
        "fetch_full_top_n": int(config.get("fetch_full_top_n", 0)),
    }
    async with aiohttp.ClientSession(connector=conn, timeout=timeout) as session:
        tasks = [
            gather_for_topic(session, topic, config["sources"], config["max_age_days"], output_base, content_opts)
            for topic in config["topics"]
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

def main():
    parser = argparse.ArgumentParser(description="Async financial news fetcher using JSON config and output control.")
    parser.add_argument("--config", required=True, help="Path to JSON configuration file.")
    parser.add_argument("--output_dir", help="Optional output directory. Defaults to current working directory.")
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    output_base = Path(args.output_dir) if args.output_dir else Path.cwd()
    asyncio.run(main_async(config, output_base))

if __name__ == "__main__":
    main()

