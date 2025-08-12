#!/usr/bin/env python3
"""
John Cena PPV Match Verification Script

This script crawls the ProFightDB page for John Cena's PPV matches and compares
them against the existing data in the index.html file to verify accuracy.
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


class CenaMatchVerifier:
    """Handles verification of John Cena's match data."""
    
    def __init__(self):
        self.profightdb_url = "http://www.profightdb.com/wrestler-ppv/john-cena-350.html"
        self.existing_matches = []
        self.scraped_matches = []
        
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
        """Scrape PPV matches from ProFightDB website."""
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
            return []
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return []
    
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
    
    def compare_matches(self) -> Dict[str, List[Match]]:
        """Compare existing matches with scraped matches."""
        print("🔍 Comparing existing data with scraped data...")
        
        # Filter existing matches to only PPV events
        existing_ppv = [m for m in self.existing_matches if m.type == "PPV"]
        
        # Convert to sets for comparison
        existing_set = set(existing_ppv)
        scraped_set = set(self.scraped_matches)
        
        # Find matches in different states
        matched = existing_set & scraped_set
        only_in_existing = existing_set - scraped_set
        only_in_scraped = scraped_set - existing_set
        
        print(f"✅ Matched: {len(matched)} PPV matches")
        print(f"⚠️  Only in existing data: {len(only_in_existing)} matches")
        print(f"🆕 Only in scraped data: {len(only_in_scraped)} matches")
        
        return {
            'matched': list(matched),
            'only_in_existing': list(only_in_existing),
            'only_in_scraped': list(only_in_scraped)
        }
    
    def generate_report(self, comparison: Dict[str, List[Match]]) -> str:
        """Generate a detailed verification report."""
        report = []
        report.append("# John Cena PPV Match Verification Report")
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary
        total_existing_ppv = len([m for m in self.existing_matches if m.type == "PPV"])
        total_scraped = len(self.scraped_matches)
        matched_count = len(comparison['matched'])
        
        report.append("## Summary")
        report.append(f"- **Total PPV matches in existing data:** {total_existing_ppv}")
        report.append(f"- **Total PPV matches scraped from ProFightDB:** {total_scraped}")
        report.append(f"- **Matched matches:** {matched_count}")
        report.append(f"- **Accuracy rate:** {(matched_count / max(total_existing_ppv, 1)) * 100:.1f}%")
        report.append("")
        
        # Detailed findings
        if comparison['only_in_existing']:
            report.append("## ⚠️ Matches in existing data but NOT found on ProFightDB")
            for match in sorted(comparison['only_in_existing'], key=lambda x: x.date):
                report.append(f"- **{match.date}** - {match.event} vs {match.opponent}")
            report.append("")
        
        if comparison['only_in_scraped']:
            report.append("## 🆕 Matches found on ProFightDB but NOT in existing data")
            for match in sorted(comparison['only_in_scraped'], key=lambda x: x.date):
                report.append(f"- **{match.date}** - {match.event} vs {match.opponent}")
            report.append("")
        
        if comparison['matched']:
            report.append("## ✅ Successfully matched PPV matches")
            report.append(f"Found {len(comparison['matched'])} matches that appear in both datasets:")
            for match in sorted(comparison['matched'], key=lambda x: x.date)[:10]:  # Show first 10
                report.append(f"- **{match.date}** - {match.event} vs {match.opponent}")
            if len(comparison['matched']) > 10:
                report.append(f"... and {len(comparison['matched']) - 10} more matches")
            report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        if comparison['only_in_existing']:
            report.append("- Review matches that appear only in existing data - they may be missing from ProFightDB or have different naming")
        if comparison['only_in_scraped']:
            report.append("- Consider adding newly discovered matches from ProFightDB to the existing dataset")
        if matched_count == total_existing_ppv:
            report.append("- ✅ All existing PPV matches were verified against ProFightDB!")
        
        return "\n".join(report)
    
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
                print("❌ No matches could be scraped from ProFightDB. Please check the website structure.")
                return
            
            # Compare matches
            comparison = self.compare_matches()
            
            # Generate and save report
            report = self.generate_report(comparison)
            
            report_file = "cena_match_verification_report.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"📄 Verification report saved to: {report_file}")
            print("")
            print("Report Summary:")
            print("-" * 40)
            print(report[:500] + "..." if len(report) > 500 else report)
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main function to run the verification."""
    verifier = CenaMatchVerifier()
    verifier.run_verification()


if __name__ == "__main__":
    main()