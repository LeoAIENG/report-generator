import pandas as pd

def preprocess_json(loan_json_path):
    """
    Preprocesses loan data from a JSON file into a pandas DataFrame with flattened and transformed fields.
    
    Args:
        loan_json_path: Path to JSON file containing loan data
        
    Returns:
        pandas.DataFrame: DataFrame containing flattened loan records with the following columns:
            - loanId: Unique identifier for the loan
            - folder: Folder status of the loan
            - loan_amount: Loan amount as float, stripped of $ and commas
            - product_type: Product type from field 1401
            - title_company: Title company from field 411  
            - channel: Channel from field 2626
            - state: State from field 14
            - loan_officer: Loan officer from field 317
            - status: Active/Closed status extracted from folder name
            - product_category: Mapped product category based on product_type
            - branch: Branch processor name
    """
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
    df["title_company"] = df["411"]
    df["channel"] = df["2626"]
    df["state"] = df["14"]
    df["loan_officer"] = df["317"]
    df["status"] = df["folder"].str.extract(r'(Active|Closed)', expand=False)
    df["product_category"] = df["product_type"].apply(map_product_type)
    df["branch"] = df["ORGID"]
    return df

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