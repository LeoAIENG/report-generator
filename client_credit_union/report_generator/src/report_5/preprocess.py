"""
Data preprocessing module for Report 5.

This module handles the preprocessing of loan data from JSON format,
including data flattening, field mapping, and product type categorization.
"""

import pandas as pd
from src.utils import parse_date


def map_product_type(value):
    """
    Map loan product type values to standardized categories.

    Converts various product type strings to standardized categories:
    - FHA: Federal Housing Administration loans
    - VA: Veterans Affairs loans
    - Non-QM: Non-qualified mortgage loans
    - Conventional: Conventional mortgage loans
    - Other: All other product types

    Args:
            value: Product type value (string or other type)

    Returns:
            str: Standardized product category

    Example:
            >>> map_product_type("FHA 30 Year Fixed")
            'FHA'
            >>> map_product_type("VA LOAN")
            'VA'
            >>> map_product_type("CONV 15 YEAR")
            'Conventional'
            >>> map_product_type("NON QM JUMBO")
            'Non-QM'
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
    Preprocess loan data from JSON format for Report 5 analysis.

    Loads loan data from JSON file, flattens nested structure, maps fields
    to standardized names, and filters for closed loans only.

    Args:
            loan_json_path: Path to the JSON file containing loan data

    Returns:
            pd.DataFrame: Preprocessed DataFrame containing only closed loans with columns:
                    - loanId: Unique loan identifier
                    - folder: Loan folder/status
                    - loan_amount: Loan amount in dollars
                    - product_type: Original product type string
                    - product_category: Standardized product category
                    - submittal_date: Parsed submittal date
                    - clear_to_close: Parsed clear to close date
                    - status: Loan status (Active/Closed)
                    - branch_processor: Branch processor name (defaults to "Unassigned" if empty)

    Example:
            >>> df = preprocess("loans.json")
            >>> print(f"Total closed loans: {len(df)}")
            >>> print(f"Product categories: {df['product_category'].unique()}")
            >>> print(f"Branch processors: {df['branch_processor'].unique()}")
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
    df["submittal_date"] = df["Log.MS.Date.Submittal"].apply(parse_date)
    df["clear_to_close"] = df["Log.MS.Date.Clear to Close"].apply(parse_date)
    df["status"] = df["folder"].str.extract(r"(Active|Closed)", expand=False)
    df["branch_processor"] = df["LoanTeamMember.Name.Branch Processor"]
    df["branch_processor"] = df["LoanTeamMember.Name.Branch Processor"].fillna("").str.strip()
    df["branch_processor"] = df["branch_processor"].replace("", "Unassigned")
    closed_df = df[df["status"] == "Closed"].copy()
    return closed_df
