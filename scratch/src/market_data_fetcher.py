"""
Historical market data fetcher for stock analysis.

This script fetches historical stock price data that can be used alongside
article sentiment analysis to provide context to the LLM.
"""

import os
import json
import argparse
import datetime
from pathlib import Path
from typing import Dict, List, Optional
import time

# Try multiple data sources
try:
    import yfinance as yf
    HAVE_YFINANCE = True
except ImportError:
    HAVE_YFINANCE = False
    print("Warning: yfinance library not found. Install with: pip install yfinance")

try:
    import requests
    HAVE_REQUESTS = True
except ImportError:
    HAVE_REQUESTS = False
    print("Warning: requests library not found. Install with: pip install requests")


def fetch_yahoo_finance_data(symbol: str, days: int = 30) -> Optional[Dict]:
    """
    Fetch historical stock data from Yahoo Finance using yfinance.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'TSLA', 'MSFT')
        days: Number of days of historical data to fetch
    
    Returns:
        Dictionary with historical data or None if failed
    """
    if not HAVE_YFINANCE:
        print("[ERROR] yfinance library not available")
        return None
    
    try:
        ticker = yf.Ticker(symbol)
        
        # Calculate date range
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        
        # Fetch historical data
        hist = ticker.history(start=start_date, end=end_date)
        
        if hist.empty:
            print(f"[WARNING] No data found for {symbol}")
            return None
        
        # Calculate statistics
        latest_price = float(hist['Close'].iloc[-1])
        first_price = float(hist['Close'].iloc[0])
        price_change = latest_price - first_price
        price_change_pct = (price_change / first_price) * 100
        
        high_price = float(hist['High'].max())
        low_price = float(hist['Low'].min())
        avg_volume = float(hist['Volume'].mean())
        
        # Get company info
        info = ticker.info
        company_name = info.get('longName', symbol)
        market_cap = info.get('marketCap', None)
        sector = info.get('sector', 'Unknown')
        
        result = {
            "symbol": symbol,
            "company_name": company_name,
            "sector": sector,
            "market_cap": market_cap,
            "period_days": days,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "latest_price": round(latest_price, 2),
            "first_price": round(first_price, 2),
            "price_change": round(price_change, 2),
            "price_change_percent": round(price_change_pct, 2),
            "period_high": round(high_price, 2),
            "period_low": round(low_price, 2),
            "avg_volume": int(avg_volume),
            "data_points": len(hist),
            "daily_prices": []
        }
        
        # Add daily price data (limited to save space)
        for idx, row in hist.iterrows():
            result["daily_prices"].append({
                "date": idx.strftime("%Y-%m-%d"),
                "open": round(float(row['Open']), 2),
                "high": round(float(row['High']), 2),
                "low": round(float(row['Low']), 2),
                "close": round(float(row['Close']), 2),
                "volume": int(row['Volume'])
            })
        
        return result
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch data for {symbol}: {e}")
        return None


def format_market_context(market_data: Dict) -> str:
    """
    Format market data into a human-readable context string for LLM.
    
    Args:
        market_data: Historical market data dictionary
    
    Returns:
        Formatted string with market context
    """
    if not market_data:
        return "No market data available."
    
    symbol = market_data['symbol']
    company = market_data.get('company_name', symbol)
    period = market_data['period_days']
    
    # Price movement
    change_pct = market_data['price_change_percent']
    if change_pct > 0:
        trend = f"up {change_pct:.2f}%"
    elif change_pct < 0:
        trend = f"down {abs(change_pct):.2f}%"
    else:
        trend = "flat"
    
    context = f"""
MARKET CONTEXT FOR {symbol} ({company}):

Recent Performance ({period} days):
- Current Price: ${market_data['latest_price']:.2f}
- Price Change: {trend}
- Period High: ${market_data['period_high']:.2f}
- Period Low: ${market_data['period_low']:.2f}
- Average Daily Volume: {market_data['avg_volume']:,}

Company Information:
- Sector: {market_data.get('sector', 'Unknown')}
"""
    
    if market_data.get('market_cap'):
        market_cap_b = market_data['market_cap'] / 1e9
        context += f"- Market Cap: ${market_cap_b:.2f}B\n"
    
    # Add recent price trend (last 7 days)
    if len(market_data.get('daily_prices', [])) >= 7:
        recent_prices = market_data['daily_prices'][-7:]
        context += "\nRecent Daily Closes:\n"
        for day_data in recent_prices:
            context += f"  {day_data['date']}: ${day_data['close']:.2f}\n"
    
    return context.strip()


def save_market_data(market_data: Dict, output_dir: Path):
    """
    Save market data to JSON file.
    
    Args:
        market_data: Historical market data dictionary
        output_dir: Directory to save the data
    """
    symbol = market_data['symbol']
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{symbol}_market_data.json"
    filepath = output_dir / filename
    
    # Add fetch timestamp
    market_data['fetched_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(market_data, f, indent=2, ensure_ascii=False)
    
    print(f"[SAVED] Market data -> {filepath}")


def load_market_data(symbol: str, market_data_dir: Path) -> Optional[Dict]:
    """
    Load cached market data if available and recent.
    
    Args:
        symbol: Stock ticker symbol
        market_data_dir: Directory containing market data files
    
    Returns:
        Market data dictionary or None if not found/outdated
    """
    filename = f"{symbol}_market_data.json"
    filepath = market_data_dir / filename
    
    if not filepath.exists():
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if data is recent (less than 24 hours old)
        fetched_at = datetime.datetime.fromisoformat(data.get('fetched_at', ''))
        age = datetime.datetime.now(datetime.timezone.utc) - fetched_at.replace(tzinfo=datetime.timezone.utc)
        
        if age.total_seconds() < 86400:  # 24 hours
            print(f"[CACHE] Using cached market data for {symbol} ({age.seconds // 3600}h old)")
            return data
        else:
            print(f"[CACHE] Market data for {symbol} is outdated ({age.days} days old)")
            return None
            
    except Exception as e:
        print(f"[WARNING] Could not load cached data for {symbol}: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Fetch historical market data for stock symbols"
    )
    parser.add_argument(
        "symbols",
        nargs="+",
        help="Stock ticker symbols to fetch (e.g., TSLA MSFT AAPL)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days of historical data (default: 30)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="market_data",
        help="Directory to save market data (default: market_data)"
    )
    parser.add_argument(
        "--use-cache",
        action="store_true",
        help="Use cached data if available and recent (< 24h old)"
    )
    parser.add_argument(
        "--show-context",
        action="store_true",
        help="Display formatted market context for LLM"
    )
    
    args = parser.parse_args()
    
    if not HAVE_YFINANCE:
        print("[ERROR] yfinance library is required. Install with: pip install yfinance")
        return 1
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Fetching market data for {len(args.symbols)} symbol(s)")
    print(f"Historical period: {args.days} days")
    print(f"Output directory: {output_dir}")
    print()
    
    results = []
    for i, symbol in enumerate(args.symbols):
        print(f"[{i+1}/{len(args.symbols)}] Processing {symbol}...")
        
        # Try to load from cache first
        market_data = None
        if args.use_cache:
            market_data = load_market_data(symbol, output_dir)
        
        # Fetch if not cached
        if market_data is None:
            market_data = fetch_yahoo_finance_data(symbol, args.days)
            
            if market_data:
                save_market_data(market_data, output_dir)
                results.append(market_data)
            else:
                print(f"[FAILED] Could not fetch data for {symbol}")
        else:
            results.append(market_data)
        
        # Small delay to avoid rate limiting
        if i < len(args.symbols) - 1:
            time.sleep(0.5)
    
    print(f"\n[DONE] Successfully fetched {len(results)}/{len(args.symbols)} symbols")
    
    # Show formatted context if requested
    if args.show_context and results:
        print("\n" + "=" * 70)
        print("FORMATTED MARKET CONTEXT (for LLM)")
        print("=" * 70)
        for market_data in results:
            print()
            print(format_market_context(market_data))
            print("-" * 70)
    
    return 0 if results else 1


if __name__ == "__main__":
    exit(main())
