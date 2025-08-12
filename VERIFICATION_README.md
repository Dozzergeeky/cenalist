# John Cena PPV Match Verification

This directory contains tools to verify the accuracy of John Cena's PPV match data by comparing it against external sources like ProFightDB.

## Overview

The verification system scrapes PPV match data from [ProFightDB](http://www.profightdb.com/wrestler-ppv/john-cena-350.html) and compares it with the existing match data in `index.html` to identify:

- ✅ **Matched matches**: Events that appear in both datasets
- ⚠️ **Missing matches**: Events in existing data but not found on ProFightDB
- 🆕 **New matches**: Events found on ProFightDB but not in existing data

## Files

### Core Scripts

- **`verify_cena_matches_demo.py`** - Main verification script with fallback to mock data
- **`verify_cena_matches.py`** - Original script (requires ProFightDB access)
- **`test_verification.py`** - Test suite to validate functionality

### Generated Reports

- **`cena_match_verification_report.md`** - Human-readable verification report
- **`cena_match_comparison_data.json`** - Machine-readable comparison data

### Configuration

- **`requirements.txt`** - Python dependencies

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Dependencies include:**
   - `requests` - For web scraping
   - `beautifulsoup4` - For HTML parsing
   - `python-dateutil` - For date parsing
   - `lxml` - For XML/HTML processing

## Usage

### Basic Verification

Run the verification with automatic fallback to mock data:

```bash
python verify_cena_matches_demo.py
```

### Using Mock Data (Demo Mode)

For testing or when ProFightDB is not accessible:

```bash
python verify_cena_matches_demo.py --mock
```

### Custom HTML File

Specify a different HTML file containing match data:

```bash
python verify_cena_matches_demo.py --html path/to/your/file.html
```

### Running Tests

Validate the verification system:

```bash
python test_verification.py
```

## Features

### Intelligent Matching

The system uses fuzzy matching to handle variations in event names:

- **WrestleMania 21** ↔ **WrestleMania XXI**
- **Royal Rumble** ↔ **Royal Rumble 2023**
- **SummerSlam** ↔ **Summer Slam**

### Comprehensive Reporting

- **Summary statistics** with accuracy percentages
- **Detailed match listings** for all categories
- **Recommendations** for data improvements
- **Data source information** and processing notes

### Data Export

- **Markdown report** for human reading
- **JSON export** for programmatic analysis
- **Structured data** with timestamps and metadata

## Sample Output

```
🚀 Starting John Cena PPV Match Verification
============================================================
📁 Extracting existing match data from index.html...
✅ Found 313 existing matches
🌐 Scraping PPV matches from ProFightDB...
✅ Scraped 45 PPV matches from ProFightDB
🔍 Comparing existing data with scraped data...
✅ Matched: 42 PPV matches
⚠️  Only in existing data: 3 matches
🆕 Only in scraped data: 3 matches

📄 Files generated:
  - cena_match_verification_report.md (verification report)
  - cena_match_comparison_data.json (detailed data)
```

## Data Structure

### Match Object

Each match is represented with:

```python
@dataclass
class Match:
    year: int          # Year of the match
    type: str          # Match type (e.g., "PPV")
    date: str          # Date in YYYY-MM-DD format
    event: str         # Event name
    opponent: str      # Opponent(s)
```

### Comparison Results

The verification produces:

```json
{
  "timestamp": "2023-12-01T12:00:00",
  "summary": {
    "total_existing_ppv": 163,
    "total_scraped": 45,
    "matched_count": 42,
    "only_in_existing_count": 3,
    "only_in_scraped_count": 3
  },
  "matched_matches": [...],
  "only_in_existing": [...],
  "only_in_scraped": [...]
}
```

## Limitations & Considerations

### Network Access

- Requires internet connection to scrape ProFightDB
- Falls back to mock data when website is inaccessible
- Implements respectful scraping with proper headers

### Data Quality

- ProFightDB structure may change over time
- Some events may have different naming conventions
- Date formats may vary between sources

### Fuzzy Matching

- Handles common event name variations
- May miss some valid matches with very different naming
- Can be improved with more sophisticated matching algorithms

## Troubleshooting

### Common Issues

1. **"No matches could be scraped"**
   - Check internet connection
   - Verify ProFightDB website is accessible
   - Use `--mock` flag for demonstration

2. **"Could not find allMatches array"**
   - Ensure `index.html` contains the expected JavaScript structure
   - Check file path is correct

3. **Import errors**
   - Install requirements: `pip install -r requirements.txt`
   - Ensure Python 3.7+ is being used

### Debug Mode

Add debug prints by modifying the script or using Python's logging module:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Production Deployment

For production use:

1. **Rate Limiting**: Add delays between requests to respect ProFightDB
2. **Error Handling**: Implement more robust error recovery
3. **Caching**: Cache scraped data to reduce load on external sites
4. **Scheduling**: Set up periodic verification (e.g., weekly)
5. **Monitoring**: Add alerts for verification failures or significant discrepancies

## Contributing

When modifying the verification system:

1. Run the test suite: `python test_verification.py`
2. Test with both real and mock data
3. Update documentation for any new features
4. Consider backward compatibility with existing data formats

## License

This verification tool is part of the Cenalist project and follows the same license terms.