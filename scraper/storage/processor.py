import logging
from pathlib import Path
from typing import Dict, Any
import pandas as pd

logger = logging.getLogger(__name__)

def parse_int(val):
    try:
        return int(str(val).replace(',', ''))
    except (TypeError, ValueError):
        return 0


def process_data(checkpoint_data: Dict[str, Any], output_path: str = "data/processed_data.csv"):
    """
    Process the scraped data to generate useful insights.
    This function would be called from the DataProcessingPipeline.

    Args:
        checkpoint_data: Dictionary of all scraped data
        output_path: Path to save the processed data
    """
    logger.info("Processing collected data...")

    processed_data = []
    # Extract data from checkpoint
    for manager_id, manager_data in checkpoint_data.items():
        if 'filings' not in manager_data or len(list(manager_data.get("filings").values())) == 0:
            continue

        fund_name = manager_data.get('name', 'Unknown')
        filings = manager_data.get("filings", {})

        latest_filing = list(filings.values())[0]
        prev_filing = list(filings.values())[1] if len(filings) > 1 else None
        print("prev_filing", prev_filing)
        # Process holdings in latest filing
        for symbol, holding in latest_filing.get('holdings', {}).items():
            entry = {
                'fund_name': fund_name,
                'filing_date': latest_filing.get('filing_date', ''),
                'quarter': latest_filing.get('quarter', ''),
                'stock_symbol': symbol,
                'cl': holding.get('cl', ''),
                'value_($000)': parse_int(holding.get('value')),
                'shares': parse_int(holding.get('shares'))
            }

            # Find previous holding data if exists
            prev_shares = 0
            if prev_filing:
                prev_holding = prev_filing.get('holdings', {}).get(symbol, {})
                prev_shares = parse_int(prev_holding.get('shares'))

            # Calculate metrics
            current_shares = entry['shares']
            entry['change'] = current_shares - prev_shares

            try:
                entry['pct_change'] = round((entry['change'] / prev_shares) * 100, 2) if prev_shares != 0 else 0.0
            except ZeroDivisionError:
                entry['pct_change'] = 0.0

            # Determine transaction type
            if prev_shares == 0:
                entry['inferred_transaction_type'] = 'new'
            elif entry['change'] > 0:
                entry['inferred_transaction_type'] = 'buy'
            elif entry['change'] < 0:
                entry['inferred_transaction_type'] = 'sell'
            else:
                entry['inferred_transaction_type'] = 'hold'

            processed_data.append(entry)

    # Save processed data
    output_file = Path("data/processed_data.csv")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(processed_data)[[
        'fund_name', 'filing_date', 'quarter', 'stock_symbol', 'cl',
        'value_($000)', 'shares', 'change', 'pct_change', 'inferred_transaction_type'
    ]]

    df.to_csv(output_file, index=False)

    logger.info(f"Processed data saved to {output_file}")
    return processed_data
