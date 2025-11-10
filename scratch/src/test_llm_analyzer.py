#!/usr/bin/env python3
"""
Test script for LLM sentiment analyzer.

This script validates the analyzer's functionality without making actual API calls.
"""

import json
import tempfile
from pathlib import Path
import datetime
import sys

# Add parent directory to path to import the analyzer
sys.path.insert(0, str(Path(__file__).parent))

from llm_sentiment_analyzer import (
    load_prompt_template,
    format_prompt,
    parse_llm_response,
    find_article_files,
    save_llm_score
)


def test_prompt_loading():
    """Test loading the prompt template."""
    print("=" * 60)
    print("TEST: Prompt Template Loading")
    print("=" * 60)
    
    prompt_path = Path(__file__).parent / "llm_sentiment_prompt.txt"
    
    try:
        template = load_prompt_template(prompt_path)
        assert len(template) > 0, "Prompt template is empty"
        assert "{title}" in template, "Prompt missing {title} placeholder"
        assert "{content}" in template, "Prompt missing {content} placeholder"
        assert "{topic}" in template, "Prompt missing {topic} placeholder"
        print("✓ Prompt template loaded successfully")
        print(f"  Length: {len(template)} characters")
        print(f"  Contains required placeholders")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def test_prompt_formatting():
    """Test formatting the prompt with article data."""
    print("\n" + "=" * 60)
    print("TEST: Prompt Formatting")
    print("=" * 60)
    
    template = """
Title: {title}
Topic: {topic}
Source: {source}
Published: {published_at}
Content: {content}
"""
    
    article = {
        "title": "Test Article",
        "topic": "TSLA",
        "source": "test_source",
        "published_at": "2024-11-10T12:00:00Z",
        "content": "This is test content."
    }
    
    try:
        formatted = format_prompt(template, article)
        assert "Test Article" in formatted, "Title not in formatted prompt"
        assert "TSLA" in formatted, "Topic not in formatted prompt"
        assert "test content" in formatted, "Content not in formatted prompt"
        print("✓ Prompt formatting works correctly")
        print(f"  Formatted length: {len(formatted)} characters")
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def test_response_parsing():
    """Test parsing LLM response with score and explanation."""
    print("\n" + "=" * 60)
    print("TEST: Response Parsing")
    print("=" * 60)
    
    test_cases = [
        (
            "SCORE: 5.50\nEXPLANATION: Strong earnings beat expectations.",
            5.50,
            "Strong earnings beat expectations.",
            True
        ),
        (
            "SCORE: +7.25\nEXPLANATION: Revenue growth. Positive outlook. Market share gains.",
            7.25,
            "Revenue growth. Positive outlook. Market share gains.",
            True
        ),
        (
            "SCORE: -3.75\nEXPLANATION: Missed guidance. Concerns about competition.",
            -3.75,
            "Missed guidance. Concerns about competition.",
            True
        ),
        (
            "SCORE: 0.00\nEXPLANATION: Neutral reporting with no clear direction.",
            0.00,
            "Neutral reporting with no clear direction.",
            True
        ),
        (
            "SCORE: -10.00\nEXPLANATION: Bankruptcy filing announced.",
            -10.00,
            "Bankruptcy filing announced.",
            True
        ),
        (
            "Invalid response without proper format",
            None,
            None,
            False
        ),
        (
            "SCORE: 15.00\nEXPLANATION: Out of range",
            None,
            None,
            False
        ),
    ]
    
    all_passed = True
    for response_text, expected_score, expected_explanation, should_pass in test_cases:
        score, explanation = parse_llm_response(response_text)
        
        if should_pass:
            if score == expected_score and explanation == expected_explanation:
                print(f"✓ Score: {score:+.2f}, Explanation: {explanation[:40]}...")
            else:
                print(f"✗ Expected ({expected_score}, {expected_explanation}), got ({score}, {explanation})")
                all_passed = False
        else:
            if score is None:
                print(f"✓ Invalid response correctly rejected")
            else:
                print(f"✗ Should be rejected but got score={score}")
                all_passed = False
    
    return all_passed


def test_article_finding():
    """Test finding article files."""
    print("\n" + "=" * 60)
    print("TEST: Article File Discovery")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create test article structure
        source_dir = tmpdir / "test_source" / "TSLA"
        source_dir.mkdir(parents=True)
        
        # Create a recent article
        recent_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=12)
        article1 = {
            "title": "Recent Article",
            "content": "Test content",
            "published_at": recent_date.isoformat(),
            "topic": "TSLA",
            "source": "test_source"
        }
        
        with open(source_dir / "001_recent.json", "w") as f:
            json.dump(article1, f)
        
        # Create an old article
        old_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=5)
        article2 = {
            "title": "Old Article",
            "content": "Test content",
            "published_at": old_date.isoformat(),
            "topic": "TSLA",
            "source": "test_source"
        }
        
        with open(source_dir / "002_old.json", "w") as f:
            json.dump(article2, f)
        
        # Create an article without content (should be skipped)
        article3 = {
            "title": "No Content Article",
            "published_at": recent_date.isoformat(),
            "topic": "TSLA",
            "source": "test_source"
        }
        
        with open(source_dir / "003_nocontent.json", "w") as f:
            json.dump(article3, f)
        
        # Find articles
        try:
            found_files = find_article_files(tmpdir, max_age_days=1)
            
            if len(found_files) == 1:
                print(f"✓ Found {len(found_files)} recent article (correct)")
                print(f"  File: {found_files[0].name}")
                return True
            else:
                print(f"✗ Expected 1 file, found {len(found_files)}")
                return False
                
        except Exception as e:
            print(f"✗ Failed: {e}")
            return False


def test_score_saving():
    """Test saving score results."""
    print("\n" + "=" * 60)
    print("TEST: Score Saving")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        article_file = tmpdir / "test_article.json"
        article = {
            "title": "Test Article",
            "topic": "TSLA",
            "source": "test_source",
            "url": "https://example.com",
            "published_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        
        llm_scores_dir = tmpdir / "llm_scores"
        
        try:
            save_llm_score(
                article_file,
                article,
                score=5.50,
                explanation="Strong earnings beat. Positive outlook.",
                llm_scores_dir=llm_scores_dir,
                model_used="test-model"
            )
            
            # Check if file was created
            expected_file = llm_scores_dir / "TSLA" / "test_article_score.json"
            
            if expected_file.exists():
                with open(expected_file, "r") as f:
                    saved_data = json.load(f)
                
                if saved_data["llm_score"] == 5.50 and "llm_explanation" in saved_data:
                    print("✓ Score and explanation saved successfully")
                    print(f"  Location: {expected_file.relative_to(tmpdir)}")
                    print(f"  Score: {saved_data['llm_score']}")
                    print(f"  Explanation: {saved_data['llm_explanation'][:50]}...")
                    return True
                else:
                    print(f"✗ Data mismatch in saved file")
                    return False
            else:
                print(f"✗ Score file not created at {expected_file}")
                return False
                
        except Exception as e:
            print(f"✗ Failed: {e}")
            return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("LLM SENTIMENT ANALYZER - TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Prompt Loading", test_prompt_loading),
        ("Prompt Formatting", test_prompt_formatting),
        ("Response Parsing", test_response_parsing),
        ("Article Finding", test_article_finding),
        ("Score Saving", test_score_saving),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
