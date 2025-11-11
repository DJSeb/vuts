"""
Flask web application for VUTS sentiment analysis reports.

This application provides a web interface to view sentiment analysis results,
browse article history by topic, and manage system configurations.
"""

import os
import sys
import json
import subprocess
import shlex
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.datetime_utils import ensure_datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration
DEFAULT_DATA_DIR = Path(__file__).parent.parent.parent / "output"
DEFAULT_DEMO_DIR = Path(__file__).parent.parent.parent / "demo_output"


def get_data_directory() -> Path:
    """Get the data directory, checking for output or demo_output."""
    data_dir = Path(os.environ.get('VUTS_DATA_DIR', DEFAULT_DATA_DIR))
    
    # If default doesn't exist, try demo output
    if not data_dir.exists() and DEFAULT_DEMO_DIR.exists():
        data_dir = DEFAULT_DEMO_DIR
    
    return data_dir


def load_sentiment_scores(data_dir: Path) -> Dict[str, List[Dict]]:
    """
    Load all sentiment scores organized by topic.
    
    Returns:
        Dictionary mapping topic names to lists of scored articles
    """
    scores_dir = data_dir / "llm_scores"
    
    if not scores_dir.exists():
        return {}
    
    topic_scores = {}
    
    for topic_dir in scores_dir.iterdir():
        if not topic_dir.is_dir():
            continue
        
        topic = topic_dir.name
        scores = []
        
        for score_file in topic_dir.glob("*_score.json"):
            try:
                with open(score_file, 'r', encoding='utf-8') as f:
                    score_data = json.load(f)
                    scores.append(score_data)
            except Exception as e:
                print(f"Error loading {score_file}: {e}")
                continue
        
        if scores:
            # Sort by publication date (newest first)
            scores.sort(
                key=lambda x: ensure_datetime(x.get('published_at', '')),
                reverse=True
            )
            topic_scores[topic] = scores
    
    return topic_scores


def load_article_content(article_file: str) -> Optional[Dict]:
    """Load the full article content from the original file."""
    try:
        if not os.path.exists(article_file):
            return None
        
        with open(article_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading article {article_file}: {e}")
        return None


def calculate_topic_summary(scores: List[Dict]) -> Dict:
    """Calculate summary statistics for a topic."""
    if not scores:
        return {
            'count': 0,
            'avg_score': 0.0,
            'latest_score': 0.0,
            'sentiment': 'neutral'
        }
    
    total = sum(s.get('llm_score', 0) for s in scores)
    avg = total / len(scores)
    latest = scores[0].get('llm_score', 0) if scores else 0
    
    # Determine sentiment category
    if avg >= 4:
        sentiment = 'very positive'
    elif avg >= 2:
        sentiment = 'positive'
    elif avg >= 0.5:
        sentiment = 'slightly positive'
    elif avg > -0.5:
        sentiment = 'neutral'
    elif avg > -2:
        sentiment = 'slightly negative'
    elif avg > -4:
        sentiment = 'negative'
    else:
        sentiment = 'very negative'
    
    return {
        'count': len(scores),
        'avg_score': round(avg, 2),
        'latest_score': round(latest, 2),
        'sentiment': sentiment
    }


def load_config_file(config_path: Path = None) -> Optional[Dict]:
    """Load configuration from JSON file."""
    if config_path is None:
        # Try default locations
        possible_paths = [
            Path(__file__).parent.parent.parent / "example_data" / "copilot-gpt5-cfg.json",
            Path(__file__).parent.parent.parent / "config.json",
        ]
        
        for path in possible_paths:
            if path.exists():
                config_path = path
                break
    
    if config_path and config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    return None


@app.route('/')
def index():
    """Home page - redirect to reports."""
    return redirect(url_for('reports'))


@app.route('/reports')
@app.route('/reports/')
def reports():
    """Main reports page showing all topics."""
    data_dir = get_data_directory()
    topic_scores = load_sentiment_scores(data_dir)
    
    # Calculate summaries for each topic
    topic_summaries = {}
    for topic, scores in topic_scores.items():
        topic_summaries[topic] = calculate_topic_summary(scores)
    
    return render_template(
        'reports.html',
        topics=sorted(topic_scores.keys()),
        topic_summaries=topic_summaries,
        data_dir=str(data_dir)
    )


@app.route('/reports/topics')
@app.route('/reports/topics/')
def reports_topics():
    """Topics overview with detailed scores."""
    data_dir = get_data_directory()
    topic_scores = load_sentiment_scores(data_dir)
    
    # Add summaries
    for topic, scores in topic_scores.items():
        summary = calculate_topic_summary(scores)
        topic_scores[topic] = {
            'scores': scores,
            'summary': summary
        }
    
    return render_template(
        'reports_topics.html',
        topic_scores=topic_scores,
        data_dir=str(data_dir)
    )


@app.route('/reports/topics/<topic>')
def topic_detail(topic: str):
    """Detailed view of a specific topic's sentiment scores."""
    data_dir = get_data_directory()
    topic_scores = load_sentiment_scores(data_dir)
    
    if topic not in topic_scores:
        return render_template('error.html', 
                             message=f"Topic '{topic}' not found"), 404
    
    scores = topic_scores[topic]
    summary = calculate_topic_summary(scores)
    
    # Load full article content for each score
    for score in scores:
        article_file = score.get('article_file')
        if article_file:
            article = load_article_content(article_file)
            if article:
                score['full_content'] = article.get('content', '')
    
    return render_template(
        'topic_detail.html',
        topic=topic,
        scores=scores,
        summary=summary
    )


@app.route('/config')
@app.route('/config/')
def config_page():
    """Configuration and management page."""
    config = load_config_file()
    
    # Get list of available topics from data directory
    data_dir = get_data_directory()
    available_topics = []
    
    scores_dir = data_dir / "llm_scores"
    if scores_dir.exists():
        available_topics = sorted([d.name for d in scores_dir.iterdir() if d.is_dir()])
    
    return render_template(
        'config.html',
        config=config,
        available_topics=available_topics,
        data_dir=str(data_dir)
    )


@app.route('/api/topics')
def api_topics():
    """API endpoint to get all topics with their summaries."""
    data_dir = get_data_directory()
    topic_scores = load_sentiment_scores(data_dir)
    
    result = {}
    for topic, scores in topic_scores.items():
        result[topic] = calculate_topic_summary(scores)
    
    return jsonify(result)


@app.route('/api/topics/<topic>')
def api_topic_detail(topic: str):
    """API endpoint to get detailed scores for a specific topic."""
    data_dir = get_data_directory()
    topic_scores = load_sentiment_scores(data_dir)
    
    if topic not in topic_scores:
        return jsonify({'error': f"Topic '{topic}' not found"}), 404
    
    return jsonify({
        'topic': topic,
        'scores': topic_scores[topic],
        'summary': calculate_topic_summary(topic_scores[topic])
    })


@app.route('/api/execute', methods=['POST'])
def api_execute_command():
    """API endpoint to execute vuts commands."""
    try:
        data = request.get_json()
        command = data.get('command')
        args = data.get('args', {})
        
        if not command:
            return jsonify({'success': False, 'error': 'No command specified'}), 400
        
        # Validate command
        valid_commands = ['fetch', 'analyze', 'market']
        if command not in valid_commands:
            return jsonify({'success': False, 'error': f'Invalid command: {command}'}), 400
        
        # Build vuts command
        vuts_path = Path(__file__).parent.parent.parent / "vuts"
        cmd = [str(vuts_path), command]
        
        # Add command-specific arguments
        if command == 'fetch':
            config_path = args.get('config')
            output_dir = args.get('output_dir', 'output')
            
            if not config_path:
                return jsonify({'success': False, 'error': 'Config file is required for fetch command'}), 400
            
            # Resolve config path relative to scratch directory
            config_full_path = Path(__file__).parent.parent.parent / config_path
            if not config_full_path.exists():
                return jsonify({'success': False, 'error': f'Config file not found: {config_path}'}), 400
            
            cmd.extend(['--config', str(config_full_path)])
            if output_dir:
                output_full_path = Path(__file__).parent.parent.parent / output_dir
                cmd.extend(['--output-dir', str(output_full_path)])
        
        elif command == 'analyze':
            data_dir = args.get('data_dir', 'output')
            max_articles = args.get('max_articles', 10)
            model = args.get('model', 'gpt-4o-mini')
            market_data_dir = args.get('market_data_dir', '')
            
            data_full_path = Path(__file__).parent.parent.parent / data_dir
            cmd.extend(['--data-dir', str(data_full_path)])
            cmd.extend(['--max-articles', str(max_articles)])
            cmd.extend(['--model', model])
            
            if market_data_dir:
                market_full_path = Path(__file__).parent.parent.parent / market_data_dir
                cmd.extend(['--market-data-dir', str(market_full_path)])
        
        elif command == 'market':
            symbols = args.get('symbols', '')
            days = args.get('days', 30)
            output_dir = args.get('output_dir', 'output/market_data')
            
            if not symbols:
                return jsonify({'success': False, 'error': 'Stock symbols are required for market command'}), 400
            
            # Split symbols by comma or space
            symbol_list = [s.strip().upper() for s in symbols.replace(',', ' ').split() if s.strip()]
            if not symbol_list:
                return jsonify({'success': False, 'error': 'No valid stock symbols provided'}), 400
            
            cmd.extend(symbol_list)
            cmd.extend(['--days', str(days)])
            
            output_full_path = Path(__file__).parent.parent.parent / output_dir
            cmd.extend(['--output-dir', str(output_full_path)])
        
        # Execute command
        print(f"Executing command: {' '.join(cmd)}")
        
        # Run command and capture output
        result = subprocess.run(
            cmd,
            cwd=str(Path(__file__).parent.parent.parent),
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        return jsonify({
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None,
            'returncode': result.returncode
        })
    
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Command execution timed out (5 minutes)'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.template_filter('format_datetime')
def format_datetime_filter(value):
    """Format datetime for display."""
    if not value:
        return 'N/A'
    
    try:
        dt = ensure_datetime(value)
        return dt.strftime('%Y-%m-%d %H:%M')
    except Exception:
        return str(value)


@app.template_filter('sentiment_color')
def sentiment_color_filter(score):
    """Get color class for sentiment score."""
    try:
        score = float(score)
        if score >= 4:
            return 'very-positive'
        elif score >= 2:
            return 'positive'
        elif score >= 0.5:
            return 'slightly-positive'
        elif score > -0.5:
            return 'neutral'
        elif score > -2:
            return 'slightly-negative'
        elif score > -4:
            return 'negative'
        else:
            return 'very-negative'
    except (ValueError, TypeError):
        return 'neutral'


@app.template_filter('score_arrow')
def score_arrow_filter(score):
    """Get arrow symbol for score direction."""
    try:
        score = float(score)
        if score > 0.5:
            return '↑'
        elif score < -0.5:
            return '↓'
        else:
            return '→'
    except (ValueError, TypeError):
        return '→'


def main():
    """Run the Flask development server."""
    import argparse
    
    parser = argparse.ArgumentParser(description='VUTS Web UI Server')
    parser.add_argument('--host', default='127.0.0.1', 
                       help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000,
                       help='Port to bind to (default: 5000)')
    parser.add_argument('--debug', action='store_true',
                       help='Run in debug mode')
    parser.add_argument('--data-dir', type=Path,
                       help='Data directory (default: scratch/output or scratch/demo_output)')
    
    args = parser.parse_args()
    
    # Set data directory if provided
    if args.data_dir:
        os.environ['VUTS_DATA_DIR'] = str(args.data_dir)
    
    print("=" * 70)
    print("VUTS - Web UI Server")
    print("=" * 70)
    print(f"Starting server at http://{args.host}:{args.port}")
    print(f"Data directory: {get_data_directory()}")
    print()
    print("Available routes:")
    print(f"  - http://{args.host}:{args.port}/")
    print(f"  - http://{args.host}:{args.port}/reports")
    print(f"  - http://{args.host}:{args.port}/reports/topics")
    print(f"  - http://{args.host}:{args.port}/config")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 70)
    
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
