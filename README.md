# Sales Report Automation

Python script that automates weekly sales reporting across Postgres, Shopify, and WooCommerce.

## Problem
Every Monday, analysts manually export CSVs from 3 platforms, clean mismatched columns, remove duplicates, and merge them in Excel. 
This took 4-5 hours and introduced errors.

## Solution
This script connects to all 3 sources, standardizes schemas, deduplicates orders, flags missing data, and outputs a single Excel workbook with a summary sheet.

## Features
- Handles Shopify and WooCommerce REST APIs with exponential backoff for rate limits
- Normalizes timestamps to UTC
- Validates data: checks for missing SKUs, negative quantities, duplicate order IDs
- Outputs clean Excel with formatted summary sheet
- Full logging for debugging

## Tech Stack
Python 3.9+, Pandas, SQLAlchemy, Requests, OpenPyXL, python-dotenv

## Setup
1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your credentials
4. Run: `python sales_report.py`

## Example Output
Generates `weekly_sales_report.xlsx` with:
- Raw data sheet per source
- Merged, deduplicated data
- Summary sheet with totals by platform, SKU, and date

## Why This Matters
Shows ability to identify manual bottlenecks, build reliable ETL pipelines, handle real-world API edge cases, and deliver production-ready code with docs.
