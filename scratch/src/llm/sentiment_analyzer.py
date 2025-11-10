"""
LLM-based sentiment analysis for financial news articles.

This script reads articles collected by the financial_news_collector_async.py script,
sends them to an LLM (OpenAI API) for sentiment analysis, and stores the scores.

The LLM returns a score between -10.00 and +10.00 indicating the sentiment.
"""

import os
import json
import argparse
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import datetime

# Check for OpenAI library
try:
    from openai import OpenAI
    HAVE_OPENAI = True
except ImportError:
    HAVE_OPENAI = False
    print("Warning: openai library not found. Install with: pip install openai")

# Alternative: check for requests for basic HTTP calls
try:
    import requests
    HAVE_REQUESTS = True
except ImportError:
    HAVE_REQUESTS = False


def load_prompt_template(prompt_path: Path) -> str:
    """Load the LLM prompt template from file."""
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def format_prompt(template: str, article: Dict, market_context: str = "") -> str:
    """Format the prompt template with article data and optional market context."""
    prompt = template.format(
        title=article.get("title", "N/A"),
        published_at=article.get("published_at", "N/A"),
        source=article.get("source", "N/A"),
        topic=article.get("topic", "N/A"),
        content=article.get("content", "N/A")
    )
    
    # Add market context if provided
    if market_context:
        prompt = market_context + "\n\n" + prompt
    
    return prompt


def load_market_context(topic: str, market_data_dir: Path) -> str:
    """
    Load market context for a given topic/symbol.
    
    Args:
        topic: Stock symbol
        market_data_dir: Directory containing market data files
    
    Returns:
        Formatted market context string or empty string if not found
    """
    try:
        # Import the formatter from market module
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from market.data_fetcher import format_market_context
        
        market_file = market_data_dir / f"{topic}_market_data.json"
        if not market_file.exists():
            return ""
        
        with open(market_file, 'r', encoding='utf-8') as f:
            market_data = json.load(f)
        
        return format_market_context(market_data)
    except Exception as e:
        print(f"[WARNING] Could not load market context for {topic}: {e}")
        return ""


def call_openai_api(prompt: str, api_key: str, model: str = "gpt-4o-mini") -> Optional[str]:
    """
    Call OpenAI API to get sentiment score and explanation.
    
    Args:
        prompt: The formatted prompt with article content
        api_key: OpenAI API key
        model: Model to use (default: gpt-4o-mini for cost efficiency)
    
    Returns:
        The response text containing score and explanation, or None if failed
    """
    if not HAVE_OPENAI:
        print("[ERROR] OpenAI library not available")
        return None
    
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent scoring
            max_tokens=200  # Enough for score + brief explanation
        )
        
        response_text = response.choices[0].message.content.strip()
        return response_text
        
    except Exception as e:
        print(f"[ERROR] OpenAI API call failed: {e}")
        return None


def parse_llm_response(response_text: str) -> Tuple[Optional[float], Optional[str]]:
    """
    Parse the LLM response to extract score and explanation.
    
    Args:
        response_text: The raw text response from LLM
    
    Returns:
        Tuple of (score, explanation) or (None, None) if parsing failed
    """
    try:
        lines = response_text.strip().split('\n')
        score = None
        explanation = None
        
        for line in lines:
            line = line.strip()
            
            # Look for score line
            if line.startswith('SCORE:'):
                score_text = line.replace('SCORE:', '').strip().replace('+', '')
                try:
                    score = float(score_text)
                    if not (-10.0 <= score <= 10.0):
                        print(f"[WARNING] Score {score} out of range [-10.00, +10.00]")
                        score = None
                    else:
                        score = round(score, 2)
                except ValueError:
                    print(f"[WARNING] Could not parse score from: {score_text}")
                    score = None
            
            # Look for explanation line
            elif line.startswith('EXPLANATION:'):
                explanation = line.replace('EXPLANATION:', '').strip()
        
        # Handle case where explanation continues on next lines
        if explanation is not None and len(lines) > 2:
            # Find the explanation line index
            for i, line in enumerate(lines):
                if line.strip().startswith('EXPLANATION:'):
                    # Collect all remaining lines as part of explanation
                    remaining_lines = [lines[i].replace('EXPLANATION:', '').strip()]
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip() and not lines[j].strip().startswith('SCORE:'):
                            remaining_lines.append(lines[j].strip())
                    explanation = ' '.join(remaining_lines)
                    break
        
        if score is None:
            print(f"[WARNING] Could not extract score from response: {response_text[:100]}")
            return None, None
        
        if explanation is None or not explanation:
            print(f"[WARNING] Could not extract explanation from response")
            explanation = "No explanation provided"
        
        return score, explanation
        
    except Exception as e:
        print(f"[WARNING] Failed to parse LLM response: {e}")
        return None, None


def validate_score(score_text: str) -> Optional[float]:
    """
    Validate and parse the score from LLM response.
    
    Args:
        score_text: The raw text response from LLM
    
    Returns:
        Float score if valid, None otherwise
    """
    try:
        # Remove any + signs and whitespace
        score_text = score_text.strip().replace("+", "")
        score = float(score_text)
        
        # Check if score is in valid range
        if -10.0 <= score <= 10.0:
            return round(score, 2)
        else:
            print(f"[WARNING] Score {score} out of range [-10.00, +10.00]")
            return None
            
    except ValueError:
        print(f"[WARNING] Could not parse score from: {score_text}")
        return None


def find_article_files(data_dir: Path, max_age_days: int = 1) -> List[Path]:
    """
    Find article JSON files that are recent enough.
    
    Args:
        data_dir: Base directory containing article data
        max_age_days: Maximum age of articles to process
    
    Returns:
        List of paths to article JSON files
    """
    article_files = []
    cutoff_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=max_age_days)
    
    # Search for JSON files in source/topic directories
    for json_file in data_dir.rglob("*.json"):
        # Skip files in llm_scores directory
        if "llm_scores" in json_file.parts:
            continue
            
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                article = json.load(f)
                
            # Check if article has required fields
            if "content" not in article or not article.get("content"):
                continue
                
            # Parse published date
            pub_date_str = article.get("published_at")
            if pub_date_str:
                try:
                    pub_date = datetime.datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
                    if pub_date.tzinfo is None:
                        pub_date = pub_date.replace(tzinfo=datetime.timezone.utc)
                    
                    if pub_date >= cutoff_date:
                        article_files.append(json_file)
                except Exception:
                    pass
                    
        except Exception as e:
            print(f"[WARNING] Could not read {json_file}: {e}")
            
    return article_files


def save_llm_score(article_file: Path, article: Dict, score: float, 
                   explanation: str, llm_scores_dir: Path, model_used: str):
    """
    Save the LLM score result to the llm_scores directory.
    
    Args:
        article_file: Original article file path
        article: Article data
        score: LLM sentiment score
        explanation: LLM explanation for the score
        llm_scores_dir: Base directory for LLM scores
        model_used: Name of the model used
    """
    topic = article.get("topic", "unknown")
    topic_dir = llm_scores_dir / topic
    topic_dir.mkdir(parents=True, exist_ok=True)
    
    # Create filename based on original article file
    score_filename = article_file.stem + "_score.json"
    score_filepath = topic_dir / score_filename
    
    score_record = {
        "article_file": str(article_file),
        "topic": topic,
        "source": article.get("source"),
        "title": article.get("title"),
        "url": article.get("url"),
        "published_at": article.get("published_at"),
        "llm_score": score,
        "llm_explanation": explanation,
        "model": model_used,
        "scored_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    
    with open(score_filepath, "w", encoding="utf-8") as f:
        json.dump(score_record, f, indent=2, ensure_ascii=False)
    
    print(f"[SAVED] Score {score:+.2f} -> {score_filepath}")


async def process_articles(article_files: List[Path], prompt_template: str,
                          llm_scores_dir: Path, api_key: str, 
                          max_articles: int = 10, model: str = "gpt-4o-mini",
                          market_data_dir: Optional[Path] = None):
    """
    Process articles and get LLM sentiment scores.
    
    Args:
        article_files: List of article file paths to process
        prompt_template: The prompt template string
        llm_scores_dir: Directory to save scores
        api_key: OpenAI API key
        max_articles: Maximum number of articles to process
        model: OpenAI model to use
        market_data_dir: Optional directory containing market data for context
    """
    processed = 0
    
    for article_file in article_files[:max_articles]:
        if processed >= max_articles:
            break
            
        try:
            # Load article
            with open(article_file, "r", encoding="utf-8") as f:
                article = json.load(f)
            
            # Check if already scored
            topic = article.get("topic", "unknown")
            score_filename = article_file.stem + "_score.json"
            score_filepath = llm_scores_dir / topic / score_filename
            
            if score_filepath.exists():
                print(f"[SKIP] Already scored: {article_file.name}")
                continue
            
            print(f"\n[PROCESSING] {article_file}")
            print(f"  Title: {article.get('title', 'N/A')[:80]}...")
            print(f"  Topic: {topic}")
            
            # Load market context if available
            market_context = ""
            if market_data_dir and market_data_dir.exists():
                market_context = load_market_context(topic, market_data_dir)
                if market_context:
                    print(f"  Including market context for {topic}")
            
            # Format prompt
            prompt = format_prompt(prompt_template, article, market_context)
            
            # Call LLM
            print(f"  Calling {model}...")
            response_text = call_openai_api(prompt, api_key, model)
            
            if response_text is None:
                print(f"  [FAILED] Could not get response from LLM")
                continue
            
            # Parse score and explanation
            score, explanation = parse_llm_response(response_text)
            if score is None:
                print(f"  [FAILED] Could not parse score from response")
                continue
            
            print(f"  Score: {score:+.2f}")
            print(f"  Explanation: {explanation[:80]}..." if len(explanation) > 80 else f"  Explanation: {explanation}")
            
            # Save score and explanation
            save_llm_score(article_file, article, score, explanation, llm_scores_dir, model)
            
            processed += 1
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"[ERROR] Failed to process {article_file}: {e}")
            continue
    
    print(f"\n[DONE] Processed {processed} articles")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze financial news articles using LLM for sentiment scoring"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=".",
        help="Base directory containing fetched article data (default: current directory)"
    )
    parser.add_argument(
        "--prompt-file",
        type=str,
        default="sentiment_prompt.txt",
        help="Path to the LLM prompt template file"
    )
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=1,
        help="Maximum age of articles to process in days (default: 1)"
    )
    parser.add_argument(
        "--max-articles",
        type=int,
        default=10,
        help="Maximum number of articles to process (default: 10)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="OpenAI model to use (default: gpt-4o-mini)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="OpenAI API key (default: read from OPENAI_API_KEY env var)"
    )
    parser.add_argument(
        "--market-data-dir",
        type=str,
        default=None,
        help="Directory containing market data for context (optional)"
    )
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[ERROR] OpenAI API key not provided. Set OPENAI_API_KEY environment variable or use --api-key")
        return 1
    
    # Setup paths
    data_dir = Path(args.data_dir).resolve()
    prompt_file = Path(args.prompt_file)
    
    # If prompt file is relative, check in script directory
    if not prompt_file.is_absolute():
        script_dir = Path(__file__).parent
        prompt_file = script_dir / prompt_file
    
    if not prompt_file.exists():
        print(f"[ERROR] Prompt file not found: {prompt_file}")
        return 1
    
    # Create llm_scores directory
    llm_scores_dir = data_dir / "llm_scores"
    llm_scores_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup market data directory if provided
    market_data_dir = None
    if args.market_data_dir:
        market_data_dir = Path(args.market_data_dir)
        if not market_data_dir.exists():
            print(f"[WARNING] Market data directory not found: {market_data_dir}")
            market_data_dir = None
    
    print(f"Data directory: {data_dir}")
    print(f"Prompt file: {prompt_file}")
    print(f"LLM scores output: {llm_scores_dir}")
    if market_data_dir:
        print(f"Market data directory: {market_data_dir}")
    print(f"Model: {args.model}")
    print(f"Max articles: {args.max_articles}")
    print(f"Max age: {args.max_age_days} days")
    
    # Load prompt template
    print("\n[LOADING] Prompt template...")
    prompt_template = load_prompt_template(prompt_file)
    
    # Find articles to process
    print(f"\n[SEARCHING] Articles in {data_dir}...")
    article_files = find_article_files(data_dir, args.max_age_days)
    
    print(f"[FOUND] {len(article_files)} recent articles")
    
    if not article_files:
        print("[INFO] No articles to process")
        return 0
    
    # Process articles
    print(f"\n[STARTING] LLM sentiment analysis...")
    asyncio.run(process_articles(
        article_files,
        prompt_template,
        llm_scores_dir,
        api_key,
        args.max_articles,
        args.model,
        market_data_dir
    ))
    
    return 0


if __name__ == "__main__":
    exit(main())
