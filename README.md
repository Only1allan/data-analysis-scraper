
# Manager Filings and Holdings Scraper

## Overview

**Hector-Scrapy** is a Python-based web scraping tool built using the Scrapy framework. It automates the collection of financial data, focusing on fund managers, their filings, and holdings from the following website. [https://13f.info/](url)

The scraping logic is divided into three main spiders:

- **Managers Spider**: Scrapes fund manager details.
- **Filings Spider**: Extracts 13F filing data for managers.
- **Holdings Spider**: Collects detailed holdings data from filings.

Additional utility files handle checkpoints, data models, and configuration settings.

## Data Storage

- **Checkpoint Data**: Manager, filings and holdings information is stored in `/checkpoint/13info.json`.
- **Final Output**: Processed CSV files are saved in the `/data/processed_csv` directory.


## Installation and Setup

### Prerequisites

Ensure the following are installed:

- Python 3.8 or higher
- `pip` (Python package installer)
- Git

### Setting up a Virtual Environment

It is recommended to use a virtual environment:

**Create a Virtual Environment:**

```bash
python -m venv venv
```

**Activate the Virtual Environment:**

On Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

**Install Dependencies:**

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
BASE_URL=https://13f.info
CHECKPOINT_PATH=path/to/checkpoint.json
HOLDING_LIST_BASE_URL=https://13f.info/holdings
MANAGER_LIST_BASE_URL=https://13f.info/managers
```

## Running the Scrapers

Use the following command to run a specific spider:

```bash
python3 -m scraper.main
```
- note the creation of the following files as the crawler work `13f-info.json` in the checkpoints folder containing all the data we need and `processed_data.csv` with the final data

## Spiders and Their Inner Workings

### 1. Managers Spider

- **File**: `managers_spider.py`
- **Purpose**: Scrapes fund manager details.

**Key Features**:

- Iterates through alphabetical pages using `MANAGER_LIST_BASE_URL`
- Extracts manager names, IDs, and links
- Uses checkpoints to avoid duplicates

**Yields**:

- `id`: Manager identifier
- `name`: Manager's name
- `link`: URL to filings

### 2. Filings Spider

- **File**: `filings_spider.py`
- **Purpose**: Scrapes 13F filings

**Key Features**:

- Extracts form type, quarter, top holdings
- Filters only `13F-HR` forms
- Limits processed filings per manager

**Yields**:

- `manager_id`, `quarter`, `filing_url`, `holdings`, `value`, `top_holdings`

### 3. Holdings Spider

- **File**: `holdings_spider.py`
- **Purpose**: Extracts detailed holdings

**Key Features**:

- Processes JSON data
- Uses checkpoints

**Yields**:

- `symbol`, `issuer`, `value`, `shares`, `percentage`

## Other Files

### `__init__.py`

- Marks `scraper/spiders` as a Python package.

## Data Flow Between Spiders

1. Managers Spider scrapes manager details.
2. Filings Spider uses this data to extract filing info.
3. Holdings Spider processes and outputs holding details.

## Advanced Configuration

### Logging

- Logs scraping progress and errors.
- Configurable in Scrapy settings.

### Error Recovery

- Checkpoint system allows resuming scraping without reprocessing.

## Contribution

Contributions are welcome!

1. Fork the repository.
2. Create a new feature/bugfix branch.
3. Submit a pull request with a detailed description.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
