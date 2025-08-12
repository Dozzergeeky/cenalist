#!/usr/bin/env python3
"""
Test script for John Cena match verification functionality.
"""

import os
import json
from verify_cena_matches_demo import CenaMatchVerifier, Match

def test_match_extraction():
    """Test extraction of matches from index.html"""
    print("🧪 Testing match extraction from index.html...")
    
    verifier = CenaMatchVerifier()
    matches = verifier.extract_existing_matches("index.html")
    
    # Basic assertions
    assert len(matches) > 0, "Should extract some matches"
    assert all(isinstance(m, Match) for m in matches), "All items should be Match objects"
    
    # Check we have PPV matches
    ppv_matches = [m for m in matches if m.type == "PPV"]
    assert len(ppv_matches) > 0, "Should have PPV matches"
    
    print(f"✅ Extracted {len(matches)} total matches, {len(ppv_matches)} PPV matches")
    return matches

def test_fuzzy_matching():
    """Test fuzzy event matching functionality"""
    print("🧪 Testing fuzzy event matching...")
    
    verifier = CenaMatchVerifier()
    
    # Test cases
    test_cases = [
        ("WrestleMania 21", "WrestleMania XXI", True),
        ("Royal Rumble", "Royal Rumble 2023", True),
        ("SummerSlam", "Summer Slam", True),
        ("Backlash", "Completely Different Event", False),
        ("WrestleMania", "Royal Rumble", False),
    ]
    
    for event1, event2, expected in test_cases:
        result = verifier.fuzzy_match_events(event1, event2)
        assert result == expected, f"Expected {expected} for '{event1}' vs '{event2}', got {result}"
        print(f"✅ '{event1}' vs '{event2}' -> {result}")
    
    print("✅ Fuzzy matching tests passed")

def test_mock_data_verification():
    """Test the complete verification process with mock data"""
    print("🧪 Testing complete verification with mock data...")
    
    verifier = CenaMatchVerifier(use_mock_data=True)
    verifier.existing_matches = verifier.extract_existing_matches("index.html")
    verifier.scraped_matches = verifier.scrape_profightdb_matches()
    
    comparison = verifier.compare_matches()
    
    # Check we have expected keys
    expected_keys = ['matched', 'only_in_existing', 'only_in_scraped']
    for key in expected_keys:
        assert key in comparison, f"Missing key: {key}"
        assert isinstance(comparison[key], list), f"Key {key} should be a list"
    
    print(f"✅ Comparison results:")
    print(f"   - Matched: {len(comparison['matched'])}")
    print(f"   - Only in existing: {len(comparison['only_in_existing'])}")
    print(f"   - Only in scraped: {len(comparison['only_in_scraped'])}")
    
    return comparison

def test_report_generation():
    """Test report generation"""
    print("🧪 Testing report generation...")
    
    verifier = CenaMatchVerifier(use_mock_data=True)
    verifier.existing_matches = verifier.extract_existing_matches("index.html")
    verifier.scraped_matches = verifier.scrape_profightdb_matches()
    
    comparison = verifier.compare_matches()
    report = verifier.generate_report(comparison)
    
    # Check report contains expected sections
    assert "# John Cena PPV Match Verification Report" in report
    assert "## Summary" in report
    assert "## Data Source Information" in report
    
    print("✅ Report generation test passed")
    print(f"   Report length: {len(report)} characters")
    
    return report

def test_json_export():
    """Test JSON data export"""
    print("🧪 Testing JSON data export...")
    
    verifier = CenaMatchVerifier(use_mock_data=True)
    verifier.existing_matches = verifier.extract_existing_matches("index.html")
    verifier.scraped_matches = verifier.scrape_profightdb_matches()
    
    comparison = verifier.compare_matches()
    verifier.save_comparison_data(comparison)
    
    # Check file was created
    assert os.path.exists("cena_match_comparison_data.json"), "JSON file should be created"
    
    # Load and validate JSON structure
    with open("cena_match_comparison_data.json", 'r') as f:
        data = json.load(f)
    
    expected_keys = ['timestamp', 'use_mock_data', 'source_url', 'summary', 'matched_matches', 'only_in_existing', 'only_in_scraped']
    for key in expected_keys:
        assert key in data, f"Missing key in JSON: {key}"
    
    print("✅ JSON export test passed")
    print(f"   Summary: {data['summary']}")

def main():
    """Run all tests"""
    print("🚀 Running John Cena Match Verification Tests")
    print("=" * 60)
    
    try:
        # Run tests
        test_match_extraction()
        test_fuzzy_matching()
        test_mock_data_verification()
        test_report_generation()
        test_json_export()
        
        print("")
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("The verification system is working correctly.")
        print("You can now use it to verify John Cena's PPV match data.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main()