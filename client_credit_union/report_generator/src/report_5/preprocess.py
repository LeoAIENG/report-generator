import pandas as pd
from datetime import datetime

def map_product_type(value):
  val = str(value).upper()

  if "FHA" in val:
    return "FHA"
  elif "VA" in val:
    return "VA"
  elif "NON QM" in val or "NON-QM" in val:
    return "Non-QM"
  elif "CONV" in val or "CONVENTIONAL" in val:
    return "Conventional"
  else:
    return "Other"
  
def parse_date(date_str):
    try:
      return datetime.strptime(date_str, "%m/%d/%Y")
    except Exception:
      return None
    
def preprocess(loan_json_path):
	df = pd.read_json(loan_json_path)

	# Flatten records
	records = []
	for loan in df.to_dict(orient='records'):
		flat_record = {"loanId": loan["loanId"], "folder": loan["folder"]}
		flat_record.update(loan["fields"])
		records.append(flat_record)

	df = pd.DataFrame(records)

	df["loan_amount"] = df["2"].replace('[\$,]', '', regex=True).astype(float)
	df["product_type"] = df["1401"]
	df["product_category"] = df["product_type"].apply(map_product_type)
	df["submittal_date"] = df["Log.MS.Date.Submittal"].apply(parse_date)
	df["clear_to_close"] = df["Log.MS.Date.Clear to Close"].apply(parse_date)
	df["status"] = df["folder"].str.extract(r'(Active|Closed)', expand=False)
	df["branch_processor"] = df["LoanTeamMember.Name.Branch Processor"]
	df["branch_processor"] = df["LoanTeamMember.Name.Branch Processor"].fillna("").str.strip()
	df["branch_processor"] = df["branch_processor"].replace("", "Unassigned")
	closed_df = df[df["status"] == "Closed"].copy()
	return closed_df