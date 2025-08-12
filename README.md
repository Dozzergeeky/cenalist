# Cenalist - John Cena Match Tracker

A comprehensive web application for tracking and analyzing John Cena's wrestling career matches, with data verification capabilities.

## Features

### 📊 Interactive Match Visualization
- **Complete Match History**: 313+ matches from 2003-2023
- **Interactive Charts**: Year-by-year statistics and trends
- **Advanced Filtering**: By year, match type, event, and opponent
- **Real-time Search**: Find specific matches instantly

### 🔍 Data Verification System
- **ProFightDB Integration**: Verify match accuracy against external sources
- **Automated Comparison**: Identify missing or inconsistent match data
- **Detailed Reports**: Generate comprehensive verification reports
- **Mock Data Support**: Test functionality when external sources are unavailable

### 📱 Modern Interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Clean UI**: Easy-to-use interface with intuitive controls
- **Fast Performance**: Client-side processing for instant results

## Quick Start

### View Match Data
Simply open `index.html` in your web browser to explore John Cena's match history.

### Verify Data Accuracy
1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run verification:
   ```bash
   python verify_cena_matches_demo.py
   ```

3. View generated reports:
   - `cena_match_verification_report.md` - Human-readable report
   - `cena_match_comparison_data.json` - Machine-readable data

## Documentation

- **[Verification System](VERIFICATION_README.md)** - Complete guide to the data verification tools
- **[Match Data Structure](#match-data-structure)** - How match data is organized
- **[Contributing](#contributing)** - How to contribute to the project

## Match Data Structure

Each match in the dataset includes:
- **Year**: Year the match took place
- **Type**: PPV, TV, Live Event, or Special
- **Date**: Specific date (YYYY-MM-DD format)
- **Event**: Name of the wrestling event
- **Opponent**: Opponent(s) faced

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Charts**: Chart.js for data visualization
- **Verification**: Python with BeautifulSoup and Requests
- **Data Format**: JSON embedded in JavaScript

## Project Structure

```
cenalist/
├── index.html                          # Main web application
├── README.md                           # Project documentation
├── VERIFICATION_README.md              # Verification system guide
├── requirements.txt                    # Python dependencies
├── verify_cena_matches_demo.py         # Main verification script
├── verify_cena_matches.py              # Original verification script
├── test_verification.py               # Test suite
└── .github/                           # GitHub workflows and templates
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python test_verification.py`
5. Submit a pull request

## Data Sources

- **Primary**: Manual compilation from WWE.com, wrestling databases
- **Verification**: ProFightDB (http://www.profightdb.com)
- **Updates**: Community contributions and corrections

## License

This project is open source. See the repository for license details.
