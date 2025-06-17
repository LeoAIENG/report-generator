"""
Context generation module for Report 1.

This module handles the creation of template context data for Report 1,
including loan statistics, image processing, and report metadata.
"""

from datetime import datetime

from docx.shared import Inches
from docxtpl import InlineImage

import config as cfg


def get_df_by_status(df, status_label):
    """
    Filter the DataFrame by the given status label.

    Args:
        df (pd.DataFrame): The DataFrame to filter.
        status_label (str): The status value to filter by.

    Returns:
        pd.DataFrame: A copy of the filtered DataFrame where 'status' == status_label.
    """
    return df[df["status"] == status_label].copy()


def add_images_context(images_path, report_prefix, tpl, context):
    """
    Add image objects to the context dictionary for use in a docxtpl template.

    Args:
        images_path (Path): Path object to the directory containing PNG images.
        report_prefix (str): Prefix to select the report layout from config.
        tpl (DocxTemplate): The docxtpl template object.
        context (dict): The context dictionary to update.

    Returns:
        dict: The updated context dictionary with InlineImage objects.
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
    images_path,
    report_prefix,
    loan_df,
    status_label,
    tpl,
    appendix_sd=None,
    show_appendix=True,
    month_label=None,
    year_label=None,
):
    """
    Build the context dictionary for rendering a report template.

    Args:
        images_path (Path): Path to the directory containing images.
        report_prefix (str): Prefix to select the report configuration.
        loan_df (pd.DataFrame): DataFrame containing loan data.
        status_label (str): Status label to filter the DataFrame.
        tpl (DocxTemplate): The docxtpl template object.
        appendix_sd (Any, optional): Data for the appendix section. Defaults to None.
        show_appendix (bool, optional): Whether to show the appendix. Defaults to True.
        month_label (str, optional): Label for the month. Defaults to None.
        year_label (str, optional): Label for the year. Defaults to None.

    Returns:
        dict: The context dictionary for the template.
    """
    df = get_df_by_status(loan_df, status_label)
    cl_qtd = len(df)
    cl_report_m = datetime.now().strftime("%B")
    cl_report_d = "1"
    cl_report_yr = datetime.now().strftime("%Y")
    report_v = getattr(cfg.report.report_v, report_prefix)
    report_n = getattr(cfg.report.report_n, report_prefix)

    context = {
        "cl_report_num": report_n,
        "cl_report_v": report_v,
        "cl_report_m": cl_report_m,
        "cl_report_d": cl_report_d,
        "cl_report_yr": cl_report_yr,
        "cl_qtd": cl_qtd,
        "cl_yr": year_label,
        "cl_fund_m": month_label,
        "cl_fund_yr": year_label,
        "appendix_sd": appendix_sd,
        "show_appendix": str(show_appendix),
    }
    context = add_images_context(images_path, report_prefix, tpl, context)
    return context
