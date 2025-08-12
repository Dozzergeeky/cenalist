#!/usr/bin/env python3
"""
John Cena PPV Match Verification Script - Demo Version

This script demonstrates how to verify John Cena's PPV matches by comparing
existing data with scraped data. Since ProFightDB is not accessible in this
environment, it includes mock data for demonstration purposes.
"""

import re
import json
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from dateutil import parser


@dataclass
class Match:
    """Represents a wrestling match."""
    year: int
    type: str
    date: str
    event: str
    opponent: str
    
    def __eq__(self, other):
        """Custom equality check for matches."""
        if not isinstance(other, Match):
            return False
        return (
            self.year == other.year and
            self.event.lower().strip() == other.event.lower().strip() and
            self.date == other.date
        )
    
    def __hash__(self):
        """Hash based on unique identifiers."""
        return hash((self.year, self.event.lower().strip(), self.date))
    
    def to_dict(self):
        """Convert match to dictionary for JSON serialization."""
        return {
            'year': self.year,
            'type': self.type,
            'date': self.date,
            'event': self.event,
            'opponent': self.opponent
        }


class CenaMatchVerifier:
    """Handles verification of John Cena's match data."""
    
    def __init__(self, use_mock_data=False):
        self.profightdb_url = "http://www.profightdb.com/wrestler-ppv/john-cena-350.html"
        self.existing_matches = []
        self.scraped_matches = []
        self.use_mock_data = use_mock_data
        
    def get_mock_profightdb_data(self) -> List[Match]:
        """Return mock data simulating ProFightDB for demonstration purposes."""
        mock_matches = [
            # Some matches that should match existing data
            Match(2003, "PPV", "2003-01-19", "Royal Rumble", "Participated in Royal Rumble Match"),
            Match(2003, "PPV", "2003-04-27", "Backlash", "Brock Lesnar"),
            Match(2004, "PPV", "2004-03-14", "WrestleMania XX", "Big Show"),
            Match(2005, "PPV", "2005-04-03", "WrestleMania 21", "John 'Bradshaw' Layfield"),
            Match(2006, "PPV", "2006-04-02", "WrestleMania 22", "Triple H"),
            Match(2007, "PPV", "2007-04-01", "WrestleMania 23", "Shawn Michaels"),
            
            # Some matches with slight differences (testing fuzzy matching)
            Match(2008, "PPV", "2008-03-28", "WrestleMania XXIV", "Randy Orton & Triple H"),  # Should match existing
            Match(2009, "PPV", "2009-04-05", "WrestleMania 25", "Edge & Big Show"),  # Different format
            
            # Some completely new matches (not in existing data)
            Match(2023, "PPV", "2023-12-30", "New Year's Revolution", "Roman Reigns"),  # New match
            Match(2024, "PPV", "2024-01-27", "Royal Rumble", "LA Knight"),  # Future match
            
            # Some matches missing from existing data
            Match(2015, "PPV", "2015-11-22", "Survivor Series", "Alberto Del Rio"),  # Missing from existing
        ]
        
        return mock_matches
        
    def extract_existing_matches(self, html_file_path: str) -> List[Match]:
        """Extract existing match data from the index.html file."""
        print("📁 Extracting existing match data from index.html...")
        
        with open(html_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Find the JavaScript array containing match data
        pattern = r'const allMatches = \[(.*?)\];'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            raise ValueError("Could not find allMatches array in index.html")
        
        matches_text = match.group(1)
        
        # Parse each match object
        match_pattern = r'\{\s*year:\s*(\d+),\s*type:\s*"([^"]*)",\s*date:\s*"([^"]*)",\s*event:\s*"([^"]*)",\s*opponent:\s*"([^"]*)"[^}]*\}'
        
        matches = []
        for match_obj in re.finditer(match_pattern, matches_text):
            year, match_type, date, event, opponent = match_obj.groups()
            matches.append(Match(
                year=int(year),
                type=match_type,
                date=date,
                event=event,
                opponent=opponent
            ))
        
        print(f"✅ Found {len(matches)} existing matches")
        return matches
    
    def scrape_profightdb_matches(self) -> List[Match]:
        """Scrape PPV matches from ProFightDB website or return mock data."""
        if self.use_mock_data:
            print("🧪 Using mock data for demonstration (ProFightDB not accessible)")
            return self.get_mock_profightdb_data()
        
        print(f"🌐 Scraping PPV matches from {self.profightdb_url}...")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(self.profightdb_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the table containing match data
            matches = []
            
            # Look for tables or divs containing match information
            # The structure may vary, so we'll try multiple approaches
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header row
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        # Try to extract match information
                        match_data = self._parse_match_row(cells)
                        if match_data:
                            matches.append(match_data)
            
            # If no tables found, look for other structures
            if not matches:
                # Look for div elements or other containers
                match_divs = soup.find_all('div', class_=re.compile(r'match|event|ppv', re.I))
                for div in match_divs:
                    match_data = self._parse_match_div(div)
                    if match_data:
                        matches.append(match_data)
            
            print(f"✅ Scraped {len(matches)} PPV matches from ProFightDB")
            return matches
            
        except requests.RequestException as e:
            print(f"❌ Error scraping ProFightDB: {e}")
            print("🧪 Falling back to mock data for demonstration...")
            self.use_mock_data = True
            return self.get_mock_profightdb_data()
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print("🧪 Falling back to mock data for demonstration...")
            self.use_mock_data = True
            return self.get_mock_profightdb_data()
    
    def _parse_match_row(self, cells) -> Optional[Match]:
        """Parse a table row to extract match information."""
        try:
            # Common patterns for ProFightDB tables
            # This is a best guess implementation that may need adjustment
            # based on the actual website structure
            
            date_text = cells[0].get_text(strip=True) if cells else ""
            event_text = cells[1].get_text(strip=True) if len(cells) > 1 else ""
            opponent_text = cells[2].get_text(strip=True) if len(cells) > 2 else ""
            
            if not all([date_text, event_text]):
                return None
            
            # Parse date
            try:
                parsed_date = parser.parse(date_text)
                year = parsed_date.year
                formatted_date = parsed_date.strftime("%Y-%m-%d")
            except:
                # Try to extract year from text
                year_match = re.search(r'(\d{4})', date_text)
                if year_match:
                    year = int(year_match.group(1))
                    formatted_date = date_text
                else:
                    return None
            
            return Match(
                year=year,
                type="PPV",  # ProFightDB page is specifically for PPV matches
                date=formatted_date,
                event=event_text,
                opponent=opponent_text
            )
            
        except Exception as e:
            print(f"⚠️  Error parsing row: {e}")
            return None
    
    def _parse_match_div(self, div) -> Optional[Match]:
        """Parse a div element to extract match information."""
        try:
            text = div.get_text(strip=True)
            
            # Look for date patterns
            date_pattern = r'(\d{1,2}[-/]\d{1,2}[-/]\d{4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})'
            date_match = re.search(date_pattern, text)
            
            if not date_match:
                return None
            
            date_text = date_match.group(1)
            try:
                parsed_date = parser.parse(date_text)
                year = parsed_date.year
                formatted_date = parsed_date.strftime("%Y-%m-%d")
            except:
                return None
            
            # Extract event and opponent from remaining text
            # This is a simplified approach and may need refinement
            remaining_text = text.replace(date_text, "").strip()
            
            # Look for "vs" or "vs." to separate event from opponent
            vs_match = re.search(r'(.*?)\s+vs\.?\s+(.*)', remaining_text, re.I)
            if vs_match:
                event = vs_match.group(1).strip()
                opponent = vs_match.group(2).strip()
            else:
                event = remaining_text
                opponent = "Unknown"
            
            return Match(
                year=year,
                type="PPV",
                date=formatted_date,
                event=event,
                opponent=opponent
            )
            
        except Exception as e:
            print(f"⚠️  Error parsing div: {e}")
            return None
    
    def fuzzy_match_events(self, event1: str, event2: str) -> bool:
        """Check if two event names are likely the same with fuzzy matching."""
        # Normalize the event names
        norm1 = re.sub(r'[^\w\s]', '', event1.lower().strip())
        norm2 = re.sub(r'[^\w\s]', '', event2.lower().strip())
        
        # Direct match
        if norm1 == norm2:
            return True
        
        # Check for common variations
        variations = {
            'wrestlemania': ['wrestlemania', 'wm'],
            'royal rumble': ['royal rumble', 'rumble'],
            'summerslam': ['summerslam', 'summer slam'],
            'survivor series': ['survivor series', 'ss'],
        }
        
        for canonical, variants in variations.items():
            if any(v in norm1 for v in variants) and any(v in norm2 for v in variants):
                return True
        
        # Check if one contains the other (for cases like "WrestleMania 21" vs "WrestleMania XXI")
        return norm1 in norm2 or norm2 in norm1
    
    def compare_matches(self) -> Dict[str, List[Match]]:
        """Compare existing matches with scraped matches using fuzzy matching."""
        print("🔍 Comparing existing data with scraped data...")
        
        # Filter existing matches to only PPV events
        existing_ppv = [m for m in self.existing_matches if m.type == "PPV"]
        
        # Perform fuzzy matching
        matched = []
        only_in_existing = []
        only_in_scraped = list(self.scraped_matches)  # Start with all scraped matches
        
        for existing_match in existing_ppv:
            found_match = False
            for scraped_match in self.scraped_matches[:]:  # Use slice to allow modification during iteration
                if (existing_match.year == scraped_match.year and 
                    self.fuzzy_match_events(existing_match.event, scraped_match.event)):
                    matched.append(existing_match)
                    if scraped_match in only_in_scraped:
                        only_in_scraped.remove(scraped_match)
                    found_match = True
                    break
            
            if not found_match:
                only_in_existing.append(existing_match)
        
        print(f"✅ Matched: {len(matched)} PPV matches")
        print(f"⚠️  Only in existing data: {len(only_in_existing)} matches")
        print(f"🆕 Only in scraped data: {len(only_in_scraped)} matches")
        
        return {
            'matched': matched,
            'only_in_existing': only_in_existing,
            'only_in_scraped': only_in_scraped
        }
    
    def generate_report(self, comparison: Dict[str, List[Match]]) -> str:
        """Generate a detailed verification report."""
        report = []
        report.append("# John Cena PPV Match Verification Report")
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if self.use_mock_data:
            report.append("⚠️ **Note: This report uses mock data for demonstration purposes**")
        report.append("")
        
        # Summary
        total_existing_ppv = len([m for m in self.existing_matches if m.type == "PPV"])
        total_scraped = len(self.scraped_matches)
        matched_count = len(comparison['matched'])
        
        report.append("## Summary")
        report.append(f"- **Total PPV matches in existing data:** {total_existing_ppv}")
        report.append(f"- **Total PPV matches scraped from ProFightDB:** {total_scraped}")
        report.append(f"- **Matched matches:** {matched_count}")
        if total_existing_ppv > 0:
            accuracy_rate = (matched_count / total_existing_ppv) * 100
            report.append(f"- **Accuracy rate:** {accuracy_rate:.1f}%")
        report.append("")
        
        # Data source info
        report.append("## Data Source Information")
        report.append(f"- **ProFightDB URL:** {self.profightdb_url}")
        report.append(f"- **Using mock data:** {'Yes' if self.use_mock_data else 'No'}")
        report.append("")
        
        # Detailed findings
        if comparison['only_in_existing']:
            report.append("## ⚠️ Matches in existing data but NOT found on ProFightDB")
            report.append("*These matches might be missing from ProFightDB or have different naming conventions.*")
            report.append("")
            for match in sorted(comparison['only_in_existing'], key=lambda x: x.date):
                report.append(f"- **{match.date}** - {match.event} vs {match.opponent}")
            report.append("")
        
        if comparison['only_in_scraped']:
            report.append("## 🆕 Matches found on ProFightDB but NOT in existing data")
            report.append("*These might be new matches that should be added to the existing dataset.*")
            report.append("")
            for match in sorted(comparison['only_in_scraped'], key=lambda x: x.date):
                report.append(f"- **{match.date}** - {match.event} vs {match.opponent}")
            report.append("")
        
        if comparison['matched']:
            report.append("## ✅ Successfully matched PPV matches")
            report.append(f"Found {len(comparison['matched'])} matches that appear in both datasets:")
            report.append("")
            for match in sorted(comparison['matched'], key=lambda x: x.date)[:10]:  # Show first 10
                report.append(f"- **{match.date}** - {match.event} vs {match.opponent}")
            if len(comparison['matched']) > 10:
                report.append(f"- ... and {len(comparison['matched']) - 10} more matches")
            report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        if comparison['only_in_existing']:
            report.append("- 🔍 **Review unmatched existing matches**: These might have different naming on ProFightDB or be missing from their database")
        if comparison['only_in_scraped']:
            report.append("- 📝 **Consider adding new matches**: Update the existing dataset with matches found only on ProFightDB")
        if matched_count == total_existing_ppv:
            report.append("- ✅ **Perfect match**: All existing PPV matches were verified against ProFightDB!")
        else:
            report.append(f"- 📊 **{accuracy_rate:.1f}% accuracy**: Consider investigating discrepancies for better data quality")
        
        if self.use_mock_data:
            report.append("")
            report.append("## For Production Use")
            report.append("- Ensure ProFightDB website is accessible")
            report.append("- Review and adjust the scraping logic based on actual website structure")
            report.append("- Implement rate limiting to be respectful to the website")
            report.append("- Add more sophisticated fuzzy matching for event names and opponent names")
        
        return "\n".join(report)
    
    def save_comparison_data(self, comparison: Dict[str, List[Match]]) -> None:
        """Save comparison data as JSON for further analysis."""
        data = {
            'timestamp': datetime.now().isoformat(),
            'use_mock_data': self.use_mock_data,
            'source_url': self.profightdb_url,
            'summary': {
                'total_existing_ppv': len([m for m in self.existing_matches if m.type == "PPV"]),
                'total_scraped': len(self.scraped_matches),
                'matched_count': len(comparison['matched']),
                'only_in_existing_count': len(comparison['only_in_existing']),
                'only_in_scraped_count': len(comparison['only_in_scraped'])
            },
            'matched_matches': [m.to_dict() for m in comparison['matched']],
            'only_in_existing': [m.to_dict() for m in comparison['only_in_existing']],
            'only_in_scraped': [m.to_dict() for m in comparison['only_in_scraped']]
        }
        
        with open('cena_match_comparison_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print("💾 Detailed comparison data saved to: cena_match_comparison_data.json")
    
    def run_verification(self, html_file_path: str = "index.html") -> None:
        """Run the complete verification process."""
        print("🚀 Starting John Cena PPV Match Verification")
        print("=" * 60)
        
        try:
            # Extract existing matches
            self.existing_matches = self.extract_existing_matches(html_file_path)
            
            # Scrape ProFightDB matches
            self.scraped_matches = self.scrape_profightdb_matches()
            
            if not self.scraped_matches:
                print("❌ No matches could be scraped. Verification cannot proceed.")
                return
            
            # Compare matches
            comparison = self.compare_matches()
            
            # Generate and save report
            report = self.generate_report(comparison)
            
            report_file = "cena_match_verification_report.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            # Save detailed comparison data
            self.save_comparison_data(comparison)
            
            print("")
            print("📄 Files generated:")
            print(f"  - {report_file} (verification report)")
            print(f"  - cena_match_comparison_data.json (detailed data)")
            print("")
            print("=" * 60)
            print("VERIFICATION COMPLETE")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main function to run the verification."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Verify John Cena PPV match data against ProFightDB')
    parser.add_argument('--mock', action='store_true', help='Use mock data for demonstration')
    parser.add_argument('--html', default='index.html', help='Path to HTML file with existing match data')
    
    args = parser.parse_args()
    
    verifier = CenaMatchVerifier(use_mock_data=args.mock)
    verifier.run_verification(args.html)


if __name__ == "__main__":
    main()