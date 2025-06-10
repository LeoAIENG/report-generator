import typer
import config as cfg
from src.report_1_2.generator import run as run_report_1_2
from src.report_3.generator import run as run_report_3
from src.report_4.generator import run as run_report_4
from src.report_5.generator import run as run_report_5

app = typer.Typer(help="Generate reports from loan data")

def validate_report_number(report_n: int) -> int:
    if report_n not in [1, 2, 3, 4, 5]:
        raise typer.BadParameter("Report number must be either 1, 2, 3, 4 or 5")
    return report_n

@app.command()
def main(
    report_n: int = typer.Argument(..., callback=validate_report_number, help="Report number (1, 2, 3, 4, 5)"),
    show_appendix: bool = typer.Option(
        cfg.app.show_appendix,
        "--show-appendix/--no-appendix",
        help="Include appendix in report"
    ),
    month_label: str = typer.Option(
        cfg.app.month_label,
        "--month",
        "-m",
        help="Month label for report"
    ),
    year_label: str = typer.Option(
        cfg.app.year_label,
        "--year",
        "-y", 
        help="Year label for report"
    )
):
    """Generate a loan report with optional appendix."""
    report_prefix = cfg.app.report_prefix.format(report_n=report_n)

    if report_n in [1, 2]:
        run_report_1_2(report_prefix, month_label, year_label, show_appendix)
    elif report_n == 3:
        run_report_3(report_prefix, month_label, year_label, show_appendix)
    elif report_n == 4:
        run_report_4(report_prefix, month_label, year_label, show_appendix)
    elif report_n == 5:
        run_report_5(report_prefix, month_label, year_label, show_appendix)
if __name__ == "__main__":
    app()
