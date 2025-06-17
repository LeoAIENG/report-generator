"""
Report generation module for Report 1.

This module handles the complete generation process for Report 1,
including image creation, document rendering, and file management.
"""

from docxtpl import DocxTemplate
from src.utils import get_report_paths

import config as cfg

from .context import get_df_by_status, get_template_context
from .plots import (
    plot_loan_officer_pareto,
    plot_projected_closings,
    plot_volume_by_branch,
    plot_volume_by_channel_and_product,
    plot_volume_by_state,
)
from .preprocess import preprocess_json


def gen_images_report(images_path, loan_df, report_prefix, status_label, time_label):
    """
    Generates and saves all required report images for a given loan DataFrame and report configuration.

    Args:
            images_path (Path): Path object to the directory where images will be saved.
            loan_df (pd.DataFrame): DataFrame containing loan data.
            report_prefix (str): Prefix identifying the report type (e.g., "report_1").
            status_label (str): Status label to filter the DataFrame (e.g., "Active").
            time_label (str): String label for the reporting period (e.g., "June 2025").
    """
    status_df = get_df_by_status(loan_df, status_label)
    images_path = images_path.as_posix() + "/"
    title_prefix = getattr(cfg.report.title_label, report_prefix)
    if report_prefix == "report_1":
        title_prefix = title_prefix.format(time_label=time_label, status_label=status_label)
    suffix = status_label.lower()

    plot_volume_by_channel_and_product(
        status_df, title_prefix=title_prefix, suffix=suffix, images_path=images_path
    )
    plot_volume_by_state(
        status_df, title_prefix=title_prefix, suffix=suffix, images_path=images_path
    )
    plot_loan_officer_pareto(
        status_df, status_label=title_prefix, suffix=suffix, images_path=images_path
    )
    plot_projected_closings(
        status_df, suffix=suffix, images_path=images_path
    ) if status_label == "Active" else None
    plot_volume_by_branch(
        status_df, title_prefix=title_prefix, suffix=suffix, images_path=images_path
    )


def remove_images(images_path):
    """
    Removes all files in the specified images directory.

    Args:
            images_path (Path): Path object to the directory containing images to remove.
    """
    for path in sorted((images_path).glob("*")):
        path.unlink()


def gen_docx_report(
    report_prefix,
    doc_template_path,
    appendix_template_path,
    images_path,
    output_path,
    loan_df,
    status_label,
    month_label,
    year_label,
    show_appendix=True,
):
    """
    Generates a DOCX report by rendering a template with the provided context.

    Args:
            report_prefix (str): Prefix identifying the report type.
            doc_template_path (str or Path): Path to the main DOCX template.
            appendix_template_path (str or Path): Path to the appendix DOCX template.
            images_path (Path): Path to the directory containing images for the report.
            output_path (str or Path): Path where the rendered DOCX will be saved.
            loan_df (pd.DataFrame): DataFrame containing loan data.
            status_label (str): Status label for filtering and context.
            month_label (str): Month label for the report.
            year_label (str): Year label for the report.
            show_appendix (bool, optional): Whether to include the appendix. Defaults to True.

    Returns:
            str or Path: The path to the saved DOCX report.
    """
    tpl = DocxTemplate(doc_template_path)
    appendix_sd = tpl.new_subdoc(appendix_template_path) if show_appendix else None
    context = get_template_context(
        images_path=images_path,
        report_prefix=report_prefix,
        loan_df=loan_df,
        status_label=status_label,
        tpl=tpl,
        appendix_sd=appendix_sd,
        show_appendix=show_appendix,
        month_label=month_label,
        year_label=year_label,
    )
    tpl.render(context, autoescape=True)
    tpl.save(output_path)

    return output_path


def run(report_prefix, month_label, year_label, show_appendix):
    """
    Orchestrates the full report generation process: prepares data, generates images,
    renders the DOCX report, and cleans up images.

    Args:
            report_prefix (str): Prefix identifying the report type.
            month_label (str): Month label for the report.
            year_label (str): Year label for the report.
            show_appendix (bool): Whether to include the appendix in the report.

    Returns:
            str or Path: The path to the generated DOCX report.
    """
    report_paths = get_report_paths(report_prefix, month_label, year_label)
    time_label = cfg.report.time_label.format(month_label=month_label, year_label=year_label)
    status_label = getattr(cfg.report.status_label, report_prefix)
    loan_df = preprocess_json(
        loan_json_path=report_paths["loan_json_path"],
    )
    gen_images_report(
        images_path=report_paths["images_path"],
        report_prefix=report_prefix,
        loan_df=loan_df,
        status_label=status_label,
        time_label=time_label,
    )
    output_path = gen_docx_report(
        report_prefix=report_prefix,
        doc_template_path=report_paths["doc_template_path"],
        appendix_template_path=report_paths["appendix_template_path"],
        images_path=report_paths["images_path"],
        output_path=report_paths["output_path"],
        month_label=month_label,
        year_label=year_label,
        loan_df=loan_df,
        status_label=status_label,
        show_appendix=show_appendix,
    )
    remove_images(images_path=report_paths["images_path"])
    return output_path
