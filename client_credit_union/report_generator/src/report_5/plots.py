"""
Data visualization module for Report 5.

This module contains functions for creating various charts and visualizations
used in Report 5, including loan volume charts, product distribution plots,
and summary tables.
"""

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import seaborn as sns


def generate_shades(base_hex, n_shades):
    """
    Generate a range of color shades from a base hex color.

    Creates n_shades variations of the base color, from lighter to darker.

    Args:
            base_hex (str): Base hex color code (e.g., "#d4af37")
            n_shades (int): Number of shades to generate

    Returns:
            list: List of hex color codes representing the shades

    Example:
            >>> shades = generate_shades("#d4af37", 5)
            >>> print(shades)
            ['#d4af37', '#b89a2e', '#9c8525', '#80701c', '#645b13']
    """
    base_rgb = mcolors.to_rgb(base_hex)
    shades = []
    for i in range(n_shades):
        factor = 0.6 + 0.4 * (i / max(1, n_shades - 1))
        shade = tuple(min(1, c * factor) for c in base_rgb)
        shades.append(mcolors.to_hex(shade))
    return shades[::-1]


def plot_closed_loan_volume(df, title_prefix, image_path, prefix, show_plots=False):
    """
    Create a bar chart showing closed loan volume by branch processor.

    Generates a horizontal bar chart displaying total loan volume in millions
    of dollars for each branch processor, with loan counts annotated on bars.

    Args:
            df (pd.DataFrame): DataFrame containing loan data with columns:
                    - branch_processor: Name of the branch processor
                    - loan_amount: Loan amount in dollars
                    - loanId: Unique loan identifier
            title_prefix (str): Prefix for the chart title
            image_path: Path object where the image will be saved
            prefix (str): Prefix for the output filename
            show_plots (bool): Whether to display the plot (default: False)

    Returns:
            None: Saves the chart as a PNG file

    Example:
            >>> plot_closed_loan_volume(df, "January 2025", Path("./images"), "report_5")
            >>> # Creates report_5_closed_loan_volume.png
    """
    grouped = (
        df.groupby("branch_processor")
        .agg(loan_volume=("loan_amount", "sum"), loan_count=("loanId", "count"))
        .sort_values(by="loan_volume", ascending=False)
    )
    grouped["loan_volume_m"] = grouped["loan_volume"] / 1_000_000
    colors = generate_shades("#d4af37", len(grouped))

    fig, ax = plt.subplots(figsize=(8, 8))
    bars = ax.bar(grouped.index, grouped["loan_volume_m"], color=colors)
    ax.set_title(
        f"{title_prefix} Closed Loan Volume by Branch Processor", fontsize=13, weight="bold"
    )
    ax.set_ylabel("Loan Volume ($M)", fontsize=12)
    plt.xlabel("Processor", fontsize=12)
    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.0f}M"))
    ax.tick_params(axis="x", labelrotation=45, labelsize=10)
    ax.grid(True, axis="y", linestyle="--", linewidth=0.7)

    for bar, count in zip(bars, grouped["loan_count"]):
        height = bar.get_height()
        ax.annotate(
            f"{count:,}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    if show_plots:
        plt.show()
    if image_path and prefix:
        plt.savefig(image_path / f"{prefix}_closed_loan_volume.png")
    plt.close(fig)


def plot_product_type_distribution(df, title_prefix, image_path, prefix, show_plots=False):
    """
    Create a stacked bar chart showing product type distribution by branch processor.

    Generates a stacked bar chart displaying the distribution of different
    loan product types (FHA, VA, Conventional, etc.) for each branch processor.

    Args:
            df (pd.DataFrame): DataFrame containing loan data with columns:
                    - branch_processor: Name of the branch processor
                    - product_category: Category of the loan product
            title_prefix (str): Prefix for the chart title
            image_path: Path object where the image will be saved
            prefix (str): Prefix for the output filename
            show_plots (bool): Whether to display the plot (default: False)

    Returns:
            None: Saves the chart as a PNG file

    Example:
            >>> plot_product_type_distribution(df, "January 2025", Path("./images"), "report_5")
            >>> # Creates report_5_product_type_distribution.png
    """
    product_distribution = (
        df.groupby(["branch_processor", "product_category"]).size().unstack(fill_value=0)
    )

    fig, ax = plt.subplots(figsize=(12, 8))
    bottom = np.zeros(len(product_distribution))

    for column in product_distribution.columns:
        values = product_distribution[column].values
        for i, (val, btm) in enumerate(zip(values, bottom)):
            if val > 0:
                ax.text(
                    i, btm + val / 2, str(val), ha="center", va="center", fontsize=9, color="black"
                )
        bottom += values

    ax.set_title(
        f"{title_prefix} Closed Loan Product Type Distribution by Branch Processor",
        fontsize=13,
        weight="bold",
    )
    ax.set_xlabel("Processor", fontsize=12)
    ax.set_ylabel("Number of Loans", fontsize=12)
    ax.set_xticklabels(product_distribution.index, rotation=45, ha="right")
    ax.legend(title="Product Type")
    ax.grid(axis="y")
    plt.tight_layout()
    if show_plots:
        plt.show()
    if image_path and prefix:
        plt.savefig(image_path / f"{prefix}_product_type_distribution.png")
    plt.close(fig)


def generate_product_type_summary_table(df, title_prefix, image_path, prefix, show_plots=False):
    """
    Create a summary table showing product type distribution by branch processor.

    Generates a formatted table displaying the count of each product type
    for each branch processor, with totals and professional styling.

    Args:
            df (pd.DataFrame): DataFrame containing loan data with columns:
                    - branch_processor: Name of the branch processor
                    - product_category: Category of the loan product
            title_prefix (str): Prefix for the table title
            image_path: Path object where the image will be saved
            prefix (str): Prefix for the output filename
            show_plots (bool): Whether to display the plot (default: False)

    Returns:
            None: Saves the table as a PNG file

    Example:
            >>> generate_product_type_summary_table(df, "January 2025", Path("./images"), "report_5")
            >>> # Creates report_5_product_type_summary_table.png
    """
    product_distribution = (
        df.groupby(["branch_processor", "product_category"]).size().unstack(fill_value=0)
    )
    product_distribution["TOTAL"] = product_distribution.sum(axis=1)
    product_distribution = product_distribution.sort_values(by="TOTAL", ascending=False)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.axis("off")

    header_color = "#c25c4b"
    row_colors = ["#ffffff", "#f2f2f2"]
    header_text_color = "white"

    table = ax.table(
        cellText=product_distribution.values,
        rowLabels=product_distribution.index,
        colLabels=product_distribution.columns,
        cellLoc="center",
        rowLoc="center",
        loc="center",
    )

    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight="bold", color=header_text_color)
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[(row - 1) % 2])

    table.scale(1.5, 1.8)

    plt.subplots_adjust(top=0.85)
    ax.text(
        0.5,
        0.85,
        f"{title_prefix} Closed Loan Product Type Distribution by Branch Processor",
        ha="center",
        va="bottom",
        fontsize=13,
        weight="bold",
        transform=ax.transAxes,
    )
    if show_plots:
        plt.show()
    if image_path and prefix:
        plt.savefig(image_path / f"{prefix}_product_type_summary_table.png", bbox_inches="tight")
    plt.close(fig)


def plot_avg_days_to_close(df, title_prefix, image_path, prefix, show_plots=False):
    """
    Create a bar chart showing average days to close by branch processor.

    Generates a bar chart displaying the average number of days from
    submittal to clear-to-close for each branch processor.

    Args:
            df (pd.DataFrame): DataFrame containing loan data with columns:
                    - branch_processor: Name of the branch processor
                    - clear_to_close: Clear to close date
                    - submittal_date: Submittal date
            title_prefix (str): Prefix for the chart title
            image_path: Path object where the image will be saved
            prefix (str): Prefix for the output filename
            show_plots (bool): Whether to display the plot (default: False)

    Returns:
            None: Saves the chart as a PNG file

    Example:
            >>> plot_avg_days_to_close(df, "January 2025", Path("./images"), "report_5")
            >>> # Creates report_5_avg_days_to_close.png
    """
    valid = df[(df["clear_to_close"].notnull()) & (df["submittal_date"].notnull())].copy()
    valid["days_to_close"] = (valid["clear_to_close"] - valid["submittal_date"]).dt.days
    avg_days = (
        valid.groupby("branch_processor")["days_to_close"]
        .mean()
        .reset_index()
        .rename(columns={"days_to_close": "avg_days_to_close"})
    )

    plt.figure(figsize=(8, 8))
    colors = generate_shades("#33e468", len(avg_days))
    ax = sns.barplot(
        data=avg_days,
        x="branch_processor",
        y="avg_days_to_close",
        palette=colors,
        legend=False,
        hue="branch_processor",
    )

    plt.title(
        f"{title_prefix} Average Days from Submission to Clear to Close per Branch Processor",
        fontsize=13,
        weight="bold",
    )
    plt.ylabel("Average Days", fontsize=12)
    plt.xlabel("Processor", fontsize=12)

    plt.xticks(rotation=45, ha="right", va="top")

    for bar, value in zip(ax.patches, avg_days["avg_days_to_close"]):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.5,
            f"{round(value)} days",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    plt.grid(axis="y")
    plt.tight_layout()
    if show_plots:
        plt.show()
    if image_path and prefix:
        plt.savefig(image_path / f"{prefix}_avg_days_to_close.png")
    plt.close()


def plot_loans_missing_submittal(df, title_prefix, image_path, prefix, show_plots=False):
    """
    Create a bar chart showing loans with missing submittal dates by branch processor.

    Generates a bar chart displaying the count of loans that have missing
    or invalid submittal dates for each branch processor.

    Args:
            df (pd.DataFrame): DataFrame containing loan data with columns:
                    - branch_processor: Name of the branch processor
                    - submittal_date: Submittal date (may contain null/empty values)
            title_prefix (str): Prefix for the chart title
            image_path: Path object where the image will be saved
            prefix (str): Prefix for the output filename
            show_plots (bool): Whether to display the plot (default: False)

    Returns:
            None: Saves the chart as a PNG file

    Example:
            >>> plot_loans_missing_submittal(df, "January 2025", Path("./images"), "report_5")
            >>> # Creates report_5_loans_missing_submittal.png
    """
    missing = df[df["submittal_date"].isnull()]
    count_by_branch_processor = missing["branch_processor"].value_counts()

    plt.figure(figsize=(8, 8))
    colors = generate_shades("#a191ff", len(count_by_branch_processor))
    ax = sns.barplot(
        x=count_by_branch_processor.index,
        y=count_by_branch_processor.values,
        palette=colors,
        hue=count_by_branch_processor.index,
        legend=False,
    )
    plt.title(
        f"{title_prefix} Missing Submittal Date by Branch Processor", fontsize=13, weight="bold"
    )
    plt.xlabel("Processor", fontsize=12)
    plt.ylabel("Number of Loans", fontsize=12)
    plt.xticks(rotation=45, ha="right")

    for bar, value in zip(ax.patches, count_by_branch_processor.values):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.2,
            str(value),
            ha="center",
            va="bottom",
            fontsize=10,
        )

    y_max = count_by_branch_processor.values.max()
    ax.set_ylim(0, y_max * 1.15)

    plt.grid(axis="y")
    plt.tight_layout()
    if show_plots:
        plt.show()
    if image_path and prefix:
        plt.savefig(image_path / f"{prefix}_loans_missing_submittal.png")
    plt.close()
