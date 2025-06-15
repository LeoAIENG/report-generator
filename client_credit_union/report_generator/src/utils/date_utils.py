from datetime import datetime, timedelta

def get_last_month_year_labels():
    last_month = (datetime.now() - timedelta(days=30)).strftime("%B") 
    last_year = (datetime.now() - timedelta(days=30)).strftime("%Y")
    return last_month, last_year

def parse_date(date_str):
    try:
      return datetime.strptime(date_str, "%m/%d/%Y")
    except Exception:
      return None