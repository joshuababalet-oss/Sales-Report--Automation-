import os
import pandas as pd
import requests
import logging
import time
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(filename='report_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

DB_CONN = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
API_URLS = {
    "shopify": os.getenv('SHOPIFY_API_URL'),
    "woocommerce": os.getenv('WOOCOMMERCE_API_URL')
}

def fetch_postgres_data():
    engine = create_engine(DB_CONN)
    query = "SELECT * FROM orders WHERE order_date >= CURRENT_DATE - 7"
    df = pd.read_sql(query, engine)
    logging.info(f"Pulled {len(df)} rows from Postgres")
    return df

def fetch_api_data(url, source_name):
    retries = 3
    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            df = pd.DataFrame(resp.json())
            df['source'] = source_name
            logging.info(f"Pulled {len(df)} rows from {source_name}")
            return df
        except requests.exceptions.RequestException as e:
            wait = 2 ** attempt
            logging.warning(f"{source_name} failed, retrying in {wait}s: {e}")
            time.sleep(wait)
    logging.error(f"{source_name} failed after {retries} retries")
    return pd.DataFrame()

def validate_schema(df, required_cols):
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        logging.warning(f"Missing columns: {missing}")
        return False
    return True

def clean_and_merge(dfs):
    for df in dfs:
        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
        df['order_date'] = pd.to_datetime(df['order_date'], utc=True, errors='coerce')

    merged = pd.concat(dfs, ignore_index=True)
    merged = merged.drop_duplicates(subset=['order_id'])

    missing_sku = merged[merged['sku'].isna()]
    if not missing_sku.empty:
        missing_sku.to_excel('missing_sku_flagged.xlsx', index=False)
        logging.warning(f"Flagged {len(missing_sku)} rows with missing SKU")
        merged = merged.dropna(subset=['sku'])

    return merged

def main():
    required_cols = ['order_id', 'sku', 'order_date', 'amount']
    df_pg = fetch_postgres_data()
    df_shopify = fetch_api_data(API_URLS['shopify'], 'shopify')
    df_woo = fetch_api_data(API_URLS['woocommerce'], 'woocommerce')
    dfs = [df for df in [df_pg, df_shopify, df_woo] if not df.empty and validate_schema(df, required_cols)]

    if not dfs:
        logging.error("No valid data sources. Exiting.")
        return

    final_df = clean_and_merge(dfs)
    with pd.ExcelWriter('weekly_sales_report.xlsx', engine='openpyxl') as writer:
        final_df.to_excel(writer, sheet_name='Sales', index=False)
        final_df.groupby('source')['amount'].sum().to_excel(writer, sheet_name='Summary')

    logging.info(f"Report generated with {len(final_df)} rows")
    print(f"Done. Report has {len(final_df)} rows.")

if __name__ == "__main__":
    main()