"""
Report generation module for Report 5.

This module handles the complete generation process for Report 5,
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
    Generate all visualization images for Report 5.

    Creates multiple charts and tables including loan volume, product distribution,
    average days to close, missing submittal data, and summary tables.

    Args:
            report_prefix (str): Prefix identifier for the report type
            closed_df (pd.DataFrame): DataFrame containing closed loan data
            images_path: Path object where images will be saved
            time_label (str): Time period label for chart titles

    Returns:
            None: Images are saved to the specified path

    Example:
            >>> gen_images_report("report_5", df, Path("./images"), "January 2025")
            >>> # Creates multiple PNG files in the images directory
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
    Remove all generated image files from the images directory.

    Cleans up temporary image files after report generation is complete.

    Args:
            images_path: Path object containing the images directory

    Returns:
            None: All files in the directory are deleted

    Example:
            >>> remove_images(Path("./images"))
            >>> # Deletes all files in the images directory
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
    Generate the final DOCX report from template and data.

    Renders the Word document template with all context data and saves
    the final report to the specified output path.

    Args:
            report_prefix (str): Prefix identifier for the report type
            doc_template_path: Path to the main document template
            appendix_template_path: Path to the appendix template
            images_path: Path object containing generated images
            output_path: Path where the final report will be saved
            closed_df (pd.DataFrame): DataFrame containing closed loan data
            month_label (str): Month label for the report period
            year_label (str): Year label for the report period
            show_appendix (bool): Whether to include appendix in the report

    Returns:
            str: Path to the generated report file

    Example:
            >>> output = gen_docx_report("report_5", "template.docx", "appendix.docx",
            ...                          Path("./images"), Path("./output/report.docx"), df, "January", "2025")
            >>> print(f"Report saved to: {output}")
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
    """
    Main function to generate Report 5.

    Orchestrates the complete report generation process including data preprocessing,
    image generation, document rendering, and cleanup.

    Args:
            report_prefix (str): Prefix identifier for the report type
            month_label (str): Month label for the report period
            year_label (str): Year label for the report period
            show_appendix (bool): Whether to include appendix in the report

    Returns:
            str: Path to the generated report file

    Example:
            >>> output_path = run("report_5", "January", "2025", True)
            >>> print(f"Report generated successfully: {output_path}")
    """
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
