"""
Table generation module for Report 3.

This module contains functions for generating various tables used in Report 3,
including loan officer efficiency tables, closed pulls tables, and closed pulls
by branch tables.
"""


def generate_loan_officer_by_efficiency_table(df):
    """
    Generates a table of loan officer efficiency.

    Args:
            df (pd.DataFrame): The DataFrame containing loan data.

    Returns:
            pandas.DataFrame: A DataFrame containing the loan officer efficiency table.
    """
    top30_table = df[df["Credit Pulls"] > 0].copy()
    top30_table = top30_table.sort_values(by="Loans per Pull", ascending=False).head(30)

    # Replace NaN in 'ORGID' with '-'
    top30_table["ORGID"] = top30_table["ORGID"].fillna("-")

    # Rename ORGID to Branch for display
    top30_table = top30_table.rename(columns={"ORGID": "Branch"})

    # Reorder columns with Branch first
    top30_table = top30_table.rename(columns={"ORGID": "Branch"})
    top30_table = top30_table[
        ["Branch", "Loan Officer", "Closed Loans", "Credit Pulls", "Loan Amount", "Loans per Pull"]
    ]
    top30_table["Loan Amount"] = top30_table["Loan Amount"].apply(lambda x: f"${x:,.0f}")
    return top30_table


def generate_closed_pulls_table(df):
    """
    Generates a table of closed pulls.

    Args:
            df (pd.DataFrame): The DataFrame containing loan data.

    Returns:
            pandas.DataFrame: A DataFrame containing the closed pulls table.
    """
    top30 = df.sort_values(by="Closed Loans", ascending=False).head(30)
    return top30


def generate_closed_pulls_by_branch_table(df):
    """
    Generates a table of closed pulls by branch.

    Args:
            df (pd.DataFrame): The DataFrame containing loan data.

    Returns:
            pandas.DataFrame: A DataFrame containing the closed pulls by branch table.
    """
    branch_summary = (
        df.groupby("ORGID").agg({"Closed Loans": "sum", "Credit Pulls": "sum"}).reset_index()
    )
    branch_summary["Loans per Pull"] = (
        branch_summary["Closed Loans"] / branch_summary["Credit Pulls"]
    ).round(2)

    sorted_branch = branch_summary.sort_values(by="Closed Loans", ascending=False)
    return sorted_branch


def get_graph_tables(merged_df):
    """
    Generates a list of tables for the graphs.

    Args:
            merged_df (pd.DataFrame): The DataFrame containing loan data.

    Returns:
            tuple: A tuple containing the loan officer by efficiency table, closed pulls table, and closed pulls by branch table.
    """
    loan_officer_by_efficiency_table = generate_loan_officer_by_efficiency_table(merged_df)
    closed_pulls_table = generate_closed_pulls_table(merged_df)
    closed_pulls_by_branch_table = generate_closed_pulls_by_branch_table(merged_df)
    return loan_officer_by_efficiency_table, closed_pulls_table, closed_pulls_by_branch_table
