"""
Data preprocessing module for Report 4.

This module handles the preprocessing of loan data from JSON format,
including data flattening, field mapping, and product type categorization.
"""

import pandas as pd
from src.utils import parse_date


def map_product_type(value):
    """
    Maps a product type string to a standardized product category.

    Args:
            value (str): The product type value to map.

    Returns:
            str: The standardized product category. One of:
                    - "FHA" for FHA loans
                    - "VA" for VA loans
                    - "Non-QM" for Non-QM loans
                    - "Conventional" for Conventional loans
                    - "Other" for all other types
    """
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


def preprocess(loan_json_path):
    """
    Preprocesses the loan data to create a DataFrame.

    Args:
            loan_json_path (str): The path to the loan JSON file.

    Returns:
            pandas.DataFrame: A DataFrame containing the loan data.
    """
    df = pd.read_json(loan_json_path)

    # Flatten records
    records = []
    for loan in df.to_dict(orient="records"):
        flat_record = {"loanId": loan["loanId"], "folder": loan["folder"]}
        flat_record.update(loan["fields"])
        records.append(flat_record)

    df = pd.DataFrame(records)

    df["loan_amount"] = df["2"].replace("[\$,]", "", regex=True).astype(float)
    df["product_type"] = df["1401"]
    df["product_category"] = df["product_type"].apply(map_product_type)
    df["underwriter"] = df["LoanTeamMember.Name.Underwriter"]
    df["submittal_date"] = df["Log.MS.Date.Submittal"].apply(parse_date)
    df["clear_to_close"] = df["Log.MS.Date.Clear to Close"].apply(parse_date)
    df["status"] = df["folder"].str.extract(r"(Active|Closed)", expand=False)
    df["underwriter"] = df["underwriter"].fillna("Unassigned").astype(str).str.strip()
    df["underwriter"] = df["underwriter"].replace("", "Unassigned")
    closed_df = df[df["status"] == "Closed"].copy()

    return closed_df
