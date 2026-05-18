Weekly Sales Report Automation

PROBLEM
Team manually exported CSVs from 3 platforms and cleaned in Excel every Monday.
Took 4-5 hours with frequent copy-paste errors.

SOLUTION
Python script using pandas and SQLAlchemy that:
- Pulls data from Postgres and two REST APIs
- Standardizes column names and merges on order ID
- Validates schema before processing
- Deduplicates records
- Logs missing fields to a separate sheet
- Outputs clean Excel with charts

EDGE CASES
1. API rate limits - exponential backoff and retries
2. Mismatched date formats - standardized to UTC
3. Missing SKUs - flagged, not dropped

HOW TO RUN
1. pip install -r requirements.txt
2. cp.env.example.env and fill credentials
3. python sales_report.py