"""
Data preprocessing module for Report 4.

This module handles the preprocessing of loan data from JSON format,
including data flattening, field mapping, and product type categorization.
"""

from datetime import datetime

from docx.shared import Inches
from docxtpl import InlineImage
import pandas as pd

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
        elif context_img in report_layout.images.custom_width_imgs:
            custom = getattr(cfg.layout.metrics.custom, context_img)
            width = Inches(custom)
        context[context_img] = InlineImage(tpl=tpl, image_descriptor=path.as_posix(), width=width)
    return context


def get_template_context(
    report_prefix,
    closed_df,
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
    - Number of underwriters
    - Number of loans where the submittal date field is empty
    - Average days to close
    - Number of unnamed underwriters
    - Report date

    Args:
            report_prefix (str): The prefix of the report.
            closed_df (pd.DataFrame): The DataFrame containing closed loans.
            tpl (DocxTemplate): The docxtpl template object.
            images_path (Path): The path to the directory containing PNG images.
            appendix_sd (str): The appendix SD.
            show_appendix (bool): Whether to show the appendix.
            month_label (str): The month label.
            year_label (str): The year label.

    Returns:
            dict: The context dictionary for rendering the report template.
    """

    # Quantity of Loans
    closed_df = closed_df[closed_df["folder"] == "Closed 2025"]
    cl_qtd = len(closed_df)

    # Underwriters Unique
    underwriters = closed_df["underwriter"].dropna().unique()
    cl_underw_qtd = len(underwriters)

    # loans where the submittal date field "fields.Log.MS.Date.Submittal" is empty (""), null, or set to "//"
    cl_nosubdate_qtd = len(
        closed_df[
            closed_df["submittal_date"].isna()
            | (closed_df["submittal_date"] == "")
            | (closed_df["submittal_date"] == "//")
        ]
    )
    cl_nosubdate_per = round(cl_nosubdate_qtd / cl_qtd * 100, 2)

    # Average days to close
    close_c_df = closed_df.copy()
    close_c_df["submittal_date"] = pd.to_datetime(close_c_df["submittal_date"])
    close_c_df["clear_to_close"] = pd.to_datetime(close_c_df["clear_to_close"])
    close_c_df = close_c_df[
        close_c_df["submittal_date"].notna() & close_c_df["clear_to_close"].notna()
    ]
    close_c_df["days_to_close"] = (
        close_c_df["clear_to_close"] - close_c_df["submittal_date"]
    ).dt.days
    cl_avg_sub_days = round(close_c_df["days_to_close"].mean(), 1)

    # Unnamed Underwriters
    cl_unnamed_underw_qtd = len(
        closed_df[
            closed_df["LoanTeamMember.Name.Underwriter"].isna()
            | (closed_df["LoanTeamMember.Name.Underwriter"] == "")
        ]
    )
    cl_unnamed_underw_per = round(cl_unnamed_underw_qtd / cl_qtd * 100, 1)

    # Report Date
    cl_report_m = datetime.now().strftime("%B")
    cl_report_d = "1"
    cl_report_yr = datetime.now().strftime("%Y")

    report_n = getattr(cfg.report.report_n, report_prefix)
    report_v = getattr(cfg.report.report_v, report_prefix)

    context = {
        "appendix_sd": appendix_sd,
        "cl_fund_m": month_label,
        "cl_fund_yr": year_label,
        "cl_qtd": cl_qtd,
        "cl_report_num": report_n,
        "cl_report_v": report_v,
        "cl_report_m": cl_report_m,
        "cl_report_d": cl_report_d,
        "cl_report_yr": cl_report_yr,
        "cl_yr": year_label,
        "cl_avg_sub_days": cl_avg_sub_days,
        "cl_underw_qtd": cl_underw_qtd,
        "cl_unnamed_underw_qtd": cl_unnamed_underw_qtd,
        "cl_unnamed_underw_per": cl_unnamed_underw_per,
        "cl_nosubdate_qtd": cl_nosubdate_qtd,
        "cl_nosubdate_per": cl_nosubdate_per,
        "show_appendix": str(show_appendix),
    }
    context = add_images_context(images_path, report_prefix, tpl, context)

    return context
