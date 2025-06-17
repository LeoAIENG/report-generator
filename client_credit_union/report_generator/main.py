import logging
from typing import Optional

from src import (
    DataRetriever,
    check_credit_data_file,
    check_loan_data_file,
    get_last_month_year_labels,
    run_report_1_2,
    run_report_3,
    run_report_4,
    run_report_5,
)
from src.utils import GoogleDriveConverter
import typer

import config as cfg

logging.basicConfig(level=logging.INFO)
app = typer.Typer(help="Generate reports from loan data")


def validate_report_number(report_n: Optional[int]) -> Optional[int]:
    if report_n is not None and report_n not in [1, 2, 3, 4, 5]:
        raise typer.BadParameter("Report number must be either 1, 2, 3, 4 or 5")
    return report_n


@app.command()
def main(
    report_n: Optional[int] = typer.Argument(
        None,
        help="Report number (1, 2, 3, 4, 5). Leave empty to run all reports.",
        callback=validate_report_number,
        show_default=False,
    ),
    all_reports: bool = typer.Option(cfg.app.all_reports, "--all", help="Run all reports"),
    show_appendix: bool = typer.Option(
        cfg.app.show_appendix, "--no-appendix", help="Include appendix in report"
    ),
    data_retrieve: bool = typer.Option(
        cfg.app.data_retrieve, "--data-retrieve", help="Run loan data retriever"
    ),
):
    """Generate one or all loan reports with optional appendix."""
    loan_data_path = cfg.path.loan_json
    credit_data_path = cfg.path.credit_excel
    month_label, year_label = get_last_month_year_labels()

    if data_retrieve:
        logging.info("Starting data retrieval process...")
        data_retriever = DataRetriever()
        data_retriever.run()
        logging.info("Data retrieval completed")

    if check_loan_data_file(loan_data_path):
        if all_reports:
            logging.info("Generating all reports...")
            # Run all reports
            logging.info("Generating Report 1...")
            run_report_1_2("report_1", month_label, year_label, show_appendix)
            logging.info("Generating Report 2...")
            run_report_1_2("report_2", month_label, year_label, show_appendix)
            if check_credit_data_file(credit_data_path):
                logging.info("Generating Report 3...")
                run_report_3("report_3", month_label, year_label, show_appendix)
            logging.info("Generating Report 4...")
            run_report_4("report_4", month_label, year_label, show_appendix)
            logging.info("Generating Report 5...")
            run_report_5("report_5", month_label, year_label, show_appendix)
            logging.info("All reports generated successfully")
        else:
            # Run single report
            report_prefix = cfg.report.report_prefix.format(report_n=report_n)
            logging.info(f"Generating Report {report_n}...")
            if report_n in [1, 2]:
                run_report_1_2(report_prefix, month_label, year_label, show_appendix)
            elif report_n == 3:
                if check_credit_data_file(credit_data_path):
                    run_report_3(report_prefix, month_label, year_label, show_appendix)
            elif report_n == 4:
                run_report_4(report_prefix, month_label, year_label, show_appendix)
            elif report_n == 5:
                run_report_5(report_prefix, month_label, year_label, show_appendix)
            logging.info(f"Report {report_n} generated successfully")

    ## Save as pdf
    logging.info("Converting DOCX files to PDF...")
    credentials_path = cfg.path.credentials
    if credentials_path.exists():
        converter = GoogleDriveConverter(credentials_path)
        for path in cfg.path.output.glob("*.docx"):
            input_path = path.as_posix()
            output_path = path.with_suffix(".pdf").as_posix()
            logging.info(f"Converting {input_path} to PDF...")
            converter.convert_local_docx_to_pdf(input_path, output_path)
            logging.info(f"Successfully converted {input_path} to {output_path}")
    else:
        logging.error(f"Credentials file not found at {credentials_path}")
        logging.info("Please create a credentials.json file in the config directory")
        logging.info("You can use the credentials.json.example file as a template")

    logging.info("All conversions completed")


if __name__ == "__main__":
    app()
