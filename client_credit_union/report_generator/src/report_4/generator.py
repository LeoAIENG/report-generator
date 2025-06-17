"""
Report generation module for Report 4.

This module handles the complete generation process for Report 4,
including image creation, document rendering, and file management.
"""

from docxtpl import DocxTemplate
from src.utils import get_report_paths

import config as cfg

from .context import get_template_context
from .plots import (
    generate_product_type_summary_table,
    plot_avg_days_to_close,
    plot_closed_loan_volume,
    plot_loans_missing_submittal,
    plot_product_type_distribution,
)
from .preprocess import preprocess


def gen_images_report(report_prefix, closed_df, images_path, time_label):
    """
    Generates and saves all required report images for a given loan DataFrame and report configuration.

    Args:
            report_prefix (str): Prefix identifying the report type (used to access layout config).
            closed_df (pd.DataFrame): DataFrame containing closed loan data.
            images_path (Path): Path to the directory where images will be saved.
            time_label (str): String label for the reporting period (e.g., "June 2025").
    """
    plot_closed_loan_volume(
        df=closed_df,
        title_prefix=time_label,
        image_path=images_path,
        prefix=report_prefix,
        show_plots=False,
    )
    plot_product_type_distribution(
        df=closed_df,
        title_prefix=time_label,
        image_path=images_path,
        prefix=report_prefix,
        show_plots=False,
    )
    plot_avg_days_to_close(
        df=closed_df,
        title_prefix=time_label,
        image_path=images_path,
        prefix=report_prefix,
        show_plots=False,
    )
    plot_loans_missing_submittal(
        df=closed_df,
        title_prefix=time_label,
        image_path=images_path,
        prefix=report_prefix,
        show_plots=False,
    )
    generate_product_type_summary_table(
        df=closed_df,
        title_prefix=time_label,
        image_path=images_path,
        prefix=report_prefix,
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
    closed_df,
    month_label,
    year_label,
    show_appendix=True,
):
    """
    Generates a Word document report using a template and context.

    Args:
            report_prefix (str): Prefix identifying the report type (used to access layout config).
            doc_template_path (Path): Path to the main Word document template.
            appendix_template_path (Path): Path to the appendix Word document template.
            images_path (Path): Path to the directory containing PNG images.
            output_path (Path): Path to the output Word document.
            closed_df (pd.DataFrame): DataFrame containing closed loan data.
            month_label (str): String label for the reporting period (e.g., "June 2025").
            year_label (str): String label for the reporting period (e.g., "2025").
            show_appendix (bool): Whether to show the appendix.

    Returns:
            Path: Path to the output Word document.
    """
    tpl = DocxTemplate(doc_template_path)
    appendix_sd = tpl.new_subdoc(appendix_template_path) if show_appendix else None
    context = get_template_context(
        report_prefix=report_prefix,
        closed_df=closed_df,
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
    report_paths = get_report_paths(report_prefix, month_label, year_label)
    time_label = cfg.report.time_label.format(month_label=month_label, year_label=year_label)
    closed_df = preprocess(loan_json_path=report_paths["loan_json_path"])

    gen_images_report(
        images_path=report_paths["images_path"],
        closed_df=closed_df,
        report_prefix=report_prefix,
        time_label=time_label,
    )
    output_path = gen_docx_report(
        report_prefix=report_prefix,
        doc_template_path=report_paths["doc_template_path"],
        appendix_template_path=report_paths["appendix_template_path"],
        images_path=report_paths["images_path"],
        output_path=report_paths["output_path"],
        closed_df=closed_df,
        month_label=month_label,
        year_label=year_label,
        show_appendix=show_appendix,
    )
    remove_images(images_path=report_paths["images_path"])
    return output_path
