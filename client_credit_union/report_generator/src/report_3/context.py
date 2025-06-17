"""
Context generation module for Report 3.

This module handles the creation of template context data for Report 3,
including loan statistics, image processing, and report metadata.
"""

from datetime import datetime

from docx.shared import Inches
from docxtpl import InlineImage

import config as cfg


def add_images_context(images_path, report_prefix, tpl, context):
    """
    Adds image objects to the context dictionary for use in a docxtpl template.

    Iterates through all PNG images in the specified images_path, determines the appropriate width
    for each image based on the report layout configuration, and adds an InlineImage object to the context
    with a key based on the image filename.

    Args:
            images_path (Path): Path object to the directory containing PNG images.
            report_prefix (str): Prefix identifying the report type (used to access layout config).
            tpl (DocxTemplate): The docxtpl template object.
            context (dict): The context dictionary to update.

    Returns:
            dict: The updated context dictionary with image keys and InlineImage objects.
    """
    for path in images_path.glob("*.png"):
        context_img = f"{path.stem}_img"
        report_layout = getattr(cfg.layout, report_prefix)
        if context_img in report_layout.images.full_width_imgs:
            width = Inches(cfg.layout.metrics.full)
        elif context_img in report_layout.images.half_width_imgs:
            width = Inches(cfg.layout.metrics.half)
        else:
            width = Inches(cfg.layout.metrics.custom.config[context_img])
        context[context_img] = InlineImage(tpl=tpl, image_descriptor=path.as_posix(), width=width)
    return context


def get_template_context(
    report_prefix,
    merged_df,
    loan_df,
    closed_loans,
    tpl,
    images_path,
    appendix_sd=None,
    show_appendix=True,
    month_label=None,
    year_label=None,
):
    """
    Generates the context dictionary for rendering a report template.

    Calculates and collects various statistics and values required for the report, such as:
    - Number of closed loans
    - Number of closed loans with a "Clear to Close" date
    - Number of credit pulls
    - Loan officers with minimum and maximum close rates
    - Report date and version information
    - Number of loans sent to branch
    - Appendix and display options

    Adds image objects to the context using add_images_context.

    Args:
            report_prefix (str): Prefix identifying the report type (used for config lookups).
            merged_df (pd.DataFrame): DataFrame containing merged loan/credit pull data.
            loan_df (pd.DataFrame): DataFrame containing all loan data (not directly used here).
            closed_loans (list): List of closed loan records (dicts).
            tpl (DocxTemplate): The docxtpl template object.
            images_path (Path): Path object to the directory containing PNG images.
            appendix_sd (any, optional): Appendix data to include in the context.
            show_appendix (bool, optional): Whether to show the appendix in the report.
            month_label (str, optional): Month label for the report.
            year_label (str, optional): Year label for the report.

    Returns:
            dict: The context dictionary for rendering the report template.
    """
    # Quantity of Loans
    closed_loans_f = [i for i in closed_loans if i["folder"] == "Closed 2025"]
    cl_qtd = len(closed_loans_f)

    # Quantity of Closed Loans and Credit Pulls
    #  loans with "fields.Log.MS.Date.Clear to Close" ≠ "//", empty or null
    cl_cleared_qtd = [
        i
        for i in closed_loans_f
        if i["fields"]["Log.MS.Date.Clear to Close"] not in ["//", "", None]
    ]
    cl_cleared_qtd = len(cl_cleared_qtd)

    cl_cred_pulls_qtd = merged_df["Credit Pulls"].sum()

    # Min and Max Close Rate
    min_idx = merged_df[merged_df["Close Rate (%)"] > 0]["Close Rate (%)"].idxmin()
    max_idx = merged_df[merged_df["Close Rate (%)"] > 0]["Close Rate (%)"].idxmax()
    min_name, min_rate = (
        merged_df.iloc[min_idx]["Loan Officer"],
        merged_df.iloc[min_idx]["Close Rate (%)"],
    )
    max_name, max_rate = (
        merged_df.iloc[max_idx]["Loan Officer"],
        merged_df.iloc[max_idx]["Close Rate (%)"],
    )
    cl_pulltoc_name_max = max_name
    cl_pulltoc_name_min = min_name
    cl_pulltoc_ratio_max = max_rate
    cl_pulltoc_ratio_min = min_rate

    # Report Date
    cl_report_m = datetime.now().strftime("%B")
    cl_report_d = "1"
    cl_report_yr = datetime.now().strftime("%Y")

    # Number of loans sent to branch
    cl_sent_branch_qtd = [
        i
        for i in closed_loans_f
        if i["fields"]["Log.MS.Date.Sent to Branch LP"] not in ["//", "", None]
    ]
    cl_sent_branch_qtd = len(cl_sent_branch_qtd)
    report_n = getattr(cfg.report.report_n, report_prefix)
    report_v = getattr(cfg.report.report_v, report_prefix)

    context = {
        "appendix_sd": appendix_sd,
        "cl_cleared_qtd": cl_cleared_qtd,
        "cl_cred_pulls_qtd": cl_cred_pulls_qtd,
        "cl_fund_m": month_label,
        "cl_fund_yr": year_label,
        "cl_pulltoc_name_max": cl_pulltoc_name_max,
        "cl_pulltoc_name_min": cl_pulltoc_name_min,
        "cl_pulltoc_ratio_max": cl_pulltoc_ratio_max,
        "cl_pulltoc_ratio_min": cl_pulltoc_ratio_min,
        "cl_qtd": cl_qtd,
        "cl_report_num": report_n,
        "cl_report_v": report_v,
        "cl_report_m": cl_report_m,
        "cl_report_d": cl_report_d,
        "cl_report_yr": cl_report_yr,
        "cl_sent_branch_qtd": cl_sent_branch_qtd,
        "cl_yr": year_label,
        "show_appendix": str(show_appendix),
    }
    context = add_images_context(images_path, report_prefix, tpl, context)

    return context
