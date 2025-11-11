#!/usr/bin/env python3
"""
Test script for the vuts centralized entrypoint.

This script validates that the vuts command properly routes to each subcommand.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd):
    """Run a command and return exit code and output."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def test_main_help():
    """Test that main help command works."""
    print("=" * 60)
    print("TEST: Main Help Command")
    print("=" * 60)
    
    returncode, stdout, stderr = run_command([sys.executable, "vuts", "--help"])
    
    if returncode == 0:
        if "fetch" in stdout and "analyze" in stdout and "market" in stdout and "ui" in stdout:
            print("✓ Main help displays all subcommands")
            return True
        else:
            print("✗ Main help missing expected subcommands")
            return False
    else:
        print(f"✗ Main help failed with exit code {returncode}")
        print(f"  stderr: {stderr}")
        return False


def test_fetch_help():
    """Test that fetch subcommand help works."""
    print("\n" + "=" * 60)
    print("TEST: Fetch Subcommand Help")
    print("=" * 60)
    
    returncode, stdout, stderr = run_command([sys.executable, "vuts", "fetch", "--help"])
    
    if returncode == 0:
        if "--config" in stdout and "--output-dir" in stdout:
            print("✓ Fetch help displays expected arguments")
            return True
        else:
            print("✗ Fetch help missing expected arguments")
            return False
    else:
        print(f"✗ Fetch help failed with exit code {returncode}")
        return False


def test_analyze_help():
    """Test that analyze subcommand help works."""
    print("\n" + "=" * 60)
    print("TEST: Analyze Subcommand Help")
    print("=" * 60)
    
    returncode, stdout, stderr = run_command([sys.executable, "vuts", "analyze", "--help"])
    
    if returncode == 0:
        if "--data-dir" in stdout and "--max-articles" in stdout and "--model" in stdout:
            print("✓ Analyze help displays expected arguments")
            return True
        else:
            print("✗ Analyze help missing expected arguments")
            return False
    else:
        print(f"✗ Analyze help failed with exit code {returncode}")
        return False


def test_market_help():
    """Test that market subcommand help works."""
    print("\n" + "=" * 60)
    print("TEST: Market Subcommand Help")
    print("=" * 60)
    
    returncode, stdout, stderr = run_command([sys.executable, "vuts", "market", "--help"])
    
    if returncode == 0:
        if "symbols" in stdout and "--days" in stdout and "--output-dir" in stdout:
            print("✓ Market help displays expected arguments")
            return True
        else:
            print("✗ Market help missing expected arguments")
            return False
    else:
        print(f"✗ Market help failed with exit code {returncode}")
        return False


def test_ui_help():
    """Test that ui subcommand help works."""
    print("\n" + "=" * 60)
    print("TEST: UI Subcommand Help")
    print("=" * 60)
    
    returncode, stdout, stderr = run_command([sys.executable, "vuts", "ui", "--help"])
    
    if returncode == 0:
        if "--host" in stdout and "--port" in stdout and "--debug" in stdout:
            print("✓ UI help displays expected arguments")
            return True
        else:
            print("✗ UI help missing expected arguments")
            return False
    else:
        print(f"✗ UI help failed with exit code {returncode}")
        return False


def test_invalid_command():
    """Test that invalid commands are handled properly."""
    print("\n" + "=" * 60)
    print("TEST: Invalid Command Handling")
    print("=" * 60)
    
    returncode, stdout, stderr = run_command([sys.executable, "vuts", "invalid"])
    
    if returncode != 0:
        print("✓ Invalid command properly rejected")
        return True
    else:
        print("✗ Invalid command was not rejected")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("VUTS ENTRYPOINT TEST SUITE")
    print("=" * 60)
    print()
    
    tests = [
        ("Main Help", test_main_help),
        ("Fetch Help", test_fetch_help),
        ("Analyze Help", test_analyze_help),
        ("Market Help", test_market_help),
        ("UI Help", test_ui_help),
        ("Invalid Command", test_invalid_command),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' raised exception: {e}")
            results.append((name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
