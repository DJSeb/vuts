import os
import json
import argparse
import datetime
import asyncio
import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from typing import List, Dict
from pathlib import Path  # <- NEW: for flexible output paths

USER_AGENT = {"User-Agent": "Mozilla/5.0"}

# ---------------------------------------------------------------------------
# UTILITIES
# ---------------------------------------------------------------------------

def is_recent(date: datetime.datetime, max_age_days: int) -> bool:
    return (datetime.datetime.utcnow() - date).days <= max_age_days

async def fetch_page(session: ClientSession, url: str, source: str, topic: str) -> str:
    """Fetch HTML content asynchronously with error reporting."""
    try:
        async with session.get(url, headers=USER_AGENT, timeout=10) as resp:
            resp.raise_for_status()  # <- NEW: raises exception for HTTP errors
            return await resp.text()
    except Exception as e:
        print(f"[ERROR] {source}:{topic} - Failed request: {e} ({url})")
        return ""

async def save_articles(session: ClientSession, articles: List[Dict], topic: str, source: str, output_base: Path):
    """Save each article as a plain text file (JSON for better structure)."""
    output_dir = output_base / source / topic
    os.makedirs(output_dir, exist_ok=True)

    async def save_one(article, idx):
        filename = f"{idx+1:03d}_{article['date'].strftime('%Y-%m-%d')}.json"  # <- Changed to JSON
        filepath = output_dir / filename
        html = await fetch_page(session, article["url"], source, topic)

        if not html:
            return
        try:
            soup = BeautifulSoup(html, "html.parser")
            paragraphs = [p.get_text() for p in soup.find_all("p")]
            article["content"] = "\n".join(paragraphs)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(article, f, indent=2, ensure_ascii=False)  # <- JSON save

            print(f"[SAVED] {filepath}")
        except Exception as e:
            print(f"[ERROR] {source}:{topic} - Failed to save article: {e} ({article['url']})")

    await asyncio.gather(*(save_one(a, i) for i, a in enumerate(articles)))

# ---------------------------------------------------------------------------
# SOURCE SCRAPERS (no major changes, just added source/topic for error reporting)
# ---------------------------------------------------------------------------
async def fetch_yahoo_finance(session: ClientSession, topic: str, max_age_days: int) -> List[Dict]:
    base_url = "https://finance.yahoo.com"
    search_url = f"{base_url}/quote/{topic}/news?p={topic}"
    html = await fetch_page(session, search_url, "YahooFinance", topic)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    articles = []
    for item in soup.find_all("li", {"class": "js-stream-content"}):
        try:  # <- NEW: wrap parsing in try to catch exceptions
            link = item.find("a")
            time_tag = item.find("time")
            if not link:
                continue
            url = link["href"]
            if not url.startswith("http"):
                url = base_url + url
            title = link.text.strip()

            if time_tag and time_tag.get("datetime"):
                try:
                    published_date = datetime.datetime.fromisoformat(time_tag["datetime"].replace("Z", "+00:00"))
                except Exception:
                    published_date = datetime.datetime.utcnow()
            else:
                published_date = datetime.datetime.utcnow()

            if is_recent(published_date, max_age_days):
                articles.append({"title": title, "url": url, "date": published_date.isoformat()})
        except Exception as e:
            print(f"[ERROR] YahooFinance:{topic} - Parsing failed: {e}")
    return articles


async def fetch_google_news(session: ClientSession, topic: str, max_age_days: int) -> List[Dict]:
    url = f"https://news.google.com/search?q={topic}+finance&hl=en&gl=US&ceid=US:en"
    html = await fetch_page(session, url, "GoogleNews", topic)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    articles = []
    for item in soup.find_all("article"):
        try:
            link_tag = item.find("a", href=True)
            if not link_tag:
                continue
            href = link_tag["href"]
            if href.startswith("./"):
                href = "https://news.google.com" + href[1:]
            title = link_tag.text.strip()
            date = datetime.datetime.utcnow()
            if is_recent(date, max_age_days):
                articles.append({"title": title, "url": href, "date": date.isoformat()})
        except Exception as e:
            print(f"[ERROR] GoogleNews:{topic} - Parsing failed: {e}")
    return articles


async def fetch_marketwatch(session: ClientSession, topic: str, max_age_days: int) -> List[Dict]:
    url = f"https://www.marketwatch.com/search?q={topic}"
    html = await fetch_page(session, url, "MarketWatch", topic)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    articles = []
    for item in soup.select("div.article__content"):
        try:
            link = item.find("a", href=True)
            date_tag = item.find("time")
            if not link:
                continue
            title = link.text.strip()
            href = link["href"]
            if date_tag and date_tag.has_attr("datetime"):
                try:
                    published_date = datetime.datetime.fromisoformat(date_tag["datetime"].replace("Z", "+00:00"))
                except Exception:
                    published_date = datetime.datetime.utcnow()
            else:
                published_date = datetime.datetime.utcnow()
            if is_recent(published_date, max_age_days):
                articles.append({"title": title, "url": href, "date": date.isoformat()})
        except Exception as e:
            print(f"[ERROR] MarketWatch:{topic} - Parsing failed: {e}")
    return articles


async def fetch_reuters(session: ClientSession, topic: str, max_age_days: int) -> List[Dict]:
    url = f"https://www.reuters.com/site-search/?query={topic}&section=business"
    html = await fetch_page(session, url, "Reuters", topic)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    articles = []
    for item in soup.select("div.search-result-content"):
        try:
            link = item.find("a", href=True)
            date_tag = item.find("time")
            if not link:
                continue
            href = "https://www.reuters.com" + link["href"]
            title = link.text.strip()
            if date_tag and date_tag.has_attr("datetime"):
                try:
                    published_date = datetime.datetime.fromisoformat(date_tag["datetime"].replace("Z", "+00:00"))
                except Exception:
                    published_date = datetime.datetime.utcnow()
            else:
                published_date = datetime.datetime.utcnow()
            if is_recent(published_date, max_age_days):
                articles.append({"title": title, "url": href, "date": date.isoformat()})
        except Exception as e:
            print(f"[ERROR] Reuters:{topic} - Parsing failed: {e}")
    return articles


async def fetch_cnbc(session: ClientSession, topic: str, max_age_days: int) -> List[Dict]:
    url = f"https://www.cnbc.com/search/?query={topic}&qsearchterm={topic}"
    html = await fetch_page(session, url, "CNBC", topic)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    articles = []
    for item in soup.select("div.SearchResultCard"):
        try:
            link = item.find("a", href=True)
            if not link:
                continue
            href = link["href"]
            if not href.startswith("http"):
                href = "https://www.cnbc.com" + href
            title = link.text.strip()
            date = datetime.datetime.utcnow()
            if is_recent(date, max_age_days):
                articles.append({"title": title, "url": href, "date": date.isoformat()})
        except Exception as e:
            print(f"[ERROR] CNBC:{topic} - Parsing failed: {e}")
    return articles


# ---------------------------------------------------------------------------
# ASYNC EXECUTION
# ---------------------------------------------------------------------------
SOURCES = {
    "yahoofinance": fetch_yahoo_finance,
    "googlenews": fetch_google_news,
    "marketwatch": fetch_marketwatch,
    "reuters": fetch_reuters,
    "cnbc": fetch_cnbc,
}


async def gather_for_topic(session: ClientSession, topic: str, sources: List[str], max_age_days: int, output_base: Path):
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
        await save_articles(session, articles, topic, source, output_base)


async def main_async(config: Dict, output_base: Path):
    async with aiohttp.ClientSession() as session:
        tasks = [
            gather_for_topic(session, topic, config["sources"], config["max_age_days"], output_base)
            for topic in config["topics"]
        ]
        await asyncio.gather(*tasks, return_exceptions=True)


def main():
    parser = argparse.ArgumentParser(description="Async financial news fetcher using with JSON config and output control.")
    parser.add_argument("--config", required=True, help="Path to JSON configuration file.")
    parser.add_argument("--output_dir", help="Optional output directory. Defaults to current working directory.")
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    output_base = Path(args.output_dir) if args.output_dir else Path.cwd()
    asyncio.run(main_async(config, output_base))


if __name__ == "__main__":
    main()

