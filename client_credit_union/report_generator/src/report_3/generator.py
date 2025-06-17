"""
Report generation module for Report 3.

This module handles the complete generation process for Report 3,
including image creation, document rendering, and file management.
"""

from docxtpl import DocxTemplate
from src.utils import get_report_paths

import config as cfg

from .context import get_template_context
from .plots import plot_closed_pulls, plot_closed_pulls_by_branch, plot_loan_officer_by_efficiency
from .preprocess import loan_df_from_records, preprocess
from .tables import get_graph_tables


def gen_images_report(images_path, merged_df, report_prefix, time_label):
    """
    Generates and saves all required report images for a given loan DataFrame and report configuration.

    Args:
            images_path (Path): Path object to the directory where images will be saved.
            merged_df (pd.DataFrame): DataFrame containing loan data.
            report_prefix (str): Prefix identifying the report type (used to access layout config).
            time_label (str): String label for the reporting period (e.g., "June 2025").
    """
    loan_officer_by_efficiency_table, closed_pulls_table, closed_pulls_by_branch_table = (
        get_graph_tables(merged_df)
    )
    plot_loan_officer_by_efficiency(
        table=loan_officer_by_efficiency_table,
        graph_name="loan_officer_by_efficiency_top30",
        image_path=images_path,
        prefix=report_prefix,
        time_label=time_label,
        show_plots=False,
    )

    plot_closed_pulls(
        table=closed_pulls_table,
        graph_name="closed_pulls_top30",
        image_path=images_path,
        prefix=report_prefix,
        time_label=time_label,
        show_plots=False,
    )
    plot_closed_pulls_by_branch(
        table=closed_pulls_by_branch_table,
        graph_name="closed_pulls_by_branch",
        image_path=images_path,
        prefix=report_prefix,
        time_label=time_label,
        show_plots=False,
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
    merged_df,
    loan_df,
    closed_loans,
    month_label,
    year_label,
    show_appendix=True,
):
    tpl = DocxTemplate(doc_template_path)
    appendix_sd = tpl.new_subdoc(appendix_template_path) if show_appendix else None
    context = get_template_context(
        report_prefix=report_prefix,
        merged_df=merged_df,
        loan_df=loan_df,
        closed_loans=closed_loans,
        images_path=images_path,
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
    merged_df, closed_loans = preprocess(
        loan_json_path=report_paths["loan_json_path"],
        credit_excel_path=report_paths["credit_excel_path"],
    )
    loan_df = loan_df_from_records(report_paths["loan_json_path"])

    gen_images_report(
        images_path=report_paths["images_path"],
        merged_df=merged_df,
        report_prefix=report_prefix,
        time_label=time_label,
    )
    output_path = gen_docx_report(
        report_prefix=report_prefix,
        doc_template_path=report_paths["doc_template_path"],
        appendix_template_path=report_paths["appendix_template_path"],
        images_path=report_paths["images_path"],
        output_path=report_paths["output_path"],
        merged_df=merged_df,
        loan_df=loan_df,
        closed_loans=closed_loans,
        month_label=month_label,
        year_label=year_label,
        show_appendix=show_appendix,
    )
    remove_images(images_path=report_paths["images_path"])
    return output_path
