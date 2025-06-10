import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.colors as mcolors
import pandas as pd

def plot_volume_by_channel_and_product(df, title_prefix, images_path=None, suffix="", show_plots=False):
	category_matrix = df.groupby(["channel", "product_category"]).agg(
		loan_volume=("loan_amount", "sum"),
		loan_count=("loanId", "count")
	).reset_index()

	category_matrix["loan_volume_fmt"] = category_matrix["loan_volume"].apply(lambda x: f"${x:,.0f}")
	category_matrix["loan_count_fmt"] = category_matrix["loan_count"].apply(lambda x: f"{x:,}")

	for ch in category_matrix["channel"].unique():
		subset = category_matrix[category_matrix["channel"] == ch][["product_category", "loan_volume_fmt", "loan_count_fmt"]]

		# Table
		fig, ax = plt.subplots(figsize=(8, 1 + 0.4 * len(subset)))
		ax.axis('off')
		table = ax.table(
			cellText=subset.values,
			colLabels=["Product Type", "Loan Volume", "Loan Count"],
			cellLoc='left',
			loc='center',
			colColours=["#c25c4b"] * 3
		)
		table.auto_set_font_size(False)
		table.set_fontsize(12)
		table.scale(1.5, 2)
		for key, cell in table.get_celld().items():
			if key[0] == 0:
				cell.get_text().set_color("white")
				cell.get_text().set_weight("bold")
				cell.get_text().set_ha("left")

		fig.subplots_adjust(top=0.85)
		fig.text(0.5, 0.91, f"{title_prefix} Loan Volume and Count by Product Type\nChannel: {ch.upper()}",
						 ha='center', fontsize=13, weight='bold')
		if show_plots:
			plt.show()
		if images_path:
			fig.savefig(
				f"{images_path}final_table_{suffix}_{ch.lower().replace(' ', '_').replace('_-_', '_')}.png",
				bbox_inches='tight',
			)
		plt.close(fig)

		# Chart
		subset_chart = df[df["channel"] == ch].copy()
		grouped = subset_chart.groupby("product_category").agg(
			loan_volume=("loan_amount", "sum"),
			loan_count=("loanId", "count")
		).sort_values(by="loan_volume", ascending=False)
		grouped["loan_volume_m"] = grouped["loan_volume"] / 1_000_000
		colors = generate_shades("#d4af37", len(grouped))

		fig, ax = plt.subplots(figsize=(4, 6))
		bars = ax.bar(grouped.index, grouped["loan_volume_m"], color=colors)
		ax.set_title(f"{title_prefix} Loan Volume by Product Type\nChannel: {ch.upper()}",
								 fontsize=13, weight='bold', pad=15)
		ax.set_ylabel("Loan Volume ($M)", fontsize=12)
		ax.set_xlabel("Product Type", fontsize=12)
		ax.tick_params(axis='x', labelsize=10)
		ax.tick_params(axis='y', labelsize=10)
		ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}M'))
		ax.grid(True, axis='y', linestyle='--', linewidth=0.7)
		ax.set_ylim(top=grouped["loan_volume_m"].max() * 1.10)

		for bar, count in zip(bars, grouped["loan_count"]):
			height = bar.get_height()
			ax.annotate(f'{count:,}',
									xy=(bar.get_x() + bar.get_width() / 2, height),
									xytext=(0, 4), textcoords="offset points",
									ha='center', va='bottom', fontsize=9)

		plt.xticks(rotation=45, ha="right")
		plt.tight_layout()
		if show_plots:
			plt.show()
		if images_path:
			fig.savefig(
				f"{images_path}final_chart_{suffix}_{ch.lower().replace(' ', '_').replace('_-_', '_')}.png",
				bbox_inches='tight',
			)
		plt.close(fig)

	return category_matrix

def plot_volume_by_state(df, title_prefix="Closed", color_base="#d2042d", suffix=None, images_path=None, show_plots=False):
	import matplotlib.pyplot as plt
	import matplotlib.ticker as mtick

	grouped = df.groupby("state").agg(
		loan_volume=("loan_amount", "sum"),
		loan_count=("loanId", "count")
	).sort_values(by="loan_volume", ascending=False)
	grouped["loan_volume_m"] = grouped["loan_volume"] / 1_000_000
	colors = generate_shades(color_base, len(grouped))

	fig, ax = plt.subplots(figsize=(8, 6))
	bars = ax.bar(grouped.index, grouped["loan_volume_m"], color=colors)
	ax.set_title(f"{title_prefix} Loan Volume by State", fontsize=13, weight='bold')
	ax.set_ylabel("Loan Amount", fontsize=12)
	ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}M'))
	ax.tick_params(axis='x', labelrotation=45, labelsize=10)
	ax.grid(True, axis='y', linestyle='--', linewidth=0.7)

	for bar, count in zip(bars, grouped["loan_count"]):
		height = bar.get_height()
		ax.annotate(f'{count:,}',
								xy=(bar.get_x() + bar.get_width() / 2, height),
								xytext=(0, 3),
								textcoords="offset points",
								ha='center', va='bottom', fontsize=9)

	plt.tight_layout()
	if show_plots:
		plt.show()
	if images_path and suffix:
		fig.savefig(f"{images_path}volume_by_state_{suffix.replace(' ', '_').replace('_-_', '_')}.png")
	plt.close(fig)

def plot_volume_by_branch(df, title_prefix="Closed", color_base="#e6970c", suffix=None, images_path=None, show_plots=False):
  df = df.copy()
  df["branch"] = df["branch"].fillna("Unassigned").astype(str).str.strip()
  df["branch"] = df["branch"].replace("", "Unassigned")

  grouped = df.groupby("branch").agg(
    loan_volume=("loan_amount", "sum"),
    loan_count=("loanId", "count")
  ).sort_values(by="loan_volume", ascending=False)
  grouped["loan_volume_m"] = grouped["loan_volume"] / 1_000_000
  colors = generate_shades(color_base, len(grouped))

  fig, ax = plt.subplots(figsize=(8, 6))
  bars = ax.bar(grouped.index, grouped["loan_volume_m"], color=colors)
  ax.set_title(f"{title_prefix} Loan Volume by Branch", fontsize=13, weight='bold')
  ax.set_ylabel("Loan Amount", fontsize=12)
  ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}M'))
  ax.tick_params(axis='x', labelrotation=45, labelsize=10)
  ax.grid(True, axis='y', linestyle='--', linewidth=0.7)

  for bar, count in zip(bars, grouped["loan_count"]):
    height = bar.get_height()
    ax.annotate(f'{count:,}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=9)

  plt.xticks(rotation=45, ha="right")
  plt.tight_layout()
  if show_plots:
    plt.show()
  if images_path and suffix:
    fig.savefig(f"{images_path}volume_by_branch_{suffix.replace(' ', '_').replace('_-_', '_')}.png")
  plt.close(fig)


# def plot_volume_by_branch_processor(df, title_prefix="Closed", color_base="#a191ff", suffix=None, images_path=None, show_plots=False):
# 	import matplotlib.pyplot as plt
# 	import matplotlib.ticker as mtick

# 	df = df.copy()
# 	df["branch_processor"] = df["LoanTeamMember.Name.Branch Processor"].fillna("").str.strip()
# 	df["branch_processor"] = df["branch_processor"].replace("", "Unassigned")

# 	grouped = df.groupby("branch_processor").agg(
# 		loan_volume=("loan_amount", "sum"),
# 		loan_count=("loanId", "count")
# 	).sort_values(by="loan_volume", ascending=False)
# 	grouped["loan_volume_m"] = grouped["loan_volume"] / 1_000_000
# 	colors = generate_shades(color_base, len(grouped))

# 	fig, ax = plt.subplots(figsize=(8, 6))
# 	bars = ax.bar(grouped.index, grouped["loan_volume_m"], color=colors)
# 	ax.set_title(f"{title_prefix} Loan Volume by Branch Processor", fontsize=13, weight='bold')
# 	ax.set_ylabel("Loan Volume ($M)", fontsize=12)
# 	ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}M'))
# 	ax.tick_params(axis='x', labelrotation=45, labelsize=10)
# 	ax.grid(True, axis='y', linestyle='--', linewidth=0.7)

# 	for bar, count in zip(bars, grouped["loan_count"]):
# 		height = bar.get_height()
# 		ax.annotate(f'{count:,}',
# 								xy=(bar.get_x() + bar.get_width() / 2, height),
# 								xytext=(0, 3),
# 								textcoords="offset points",
# 								ha='center', va='bottom', fontsize=9)

# 	plt.xticks(rotation=45, ha="right")
# 	plt.tight_layout()
# 	if show_plots:
# 		plt.show()
# 	if images_path and suffix:
# 		fig.savefig(f"{images_path}volume_by_branch_processor_{suffix.replace(' ', '_').replace('_-_', '_')}.png")
# 	plt.close(fig)


def plot_projected_closings(
	df,
	date_field="Log.MS.Date.Clear to Close",
	title="Estimated Loan Closings",
	days_ahead=30,
	images_path=None,
	suffix=None,
	show_plots=False
):
	df = df.copy()
	df[date_field] = df[date_field].replace(["//", "...", ""], pd.NA)
	df[date_field] = pd.to_datetime(df[date_field], format="%m/%d/%Y", errors="coerce")

	today = pd.Timestamp.today().normalize()
	horizon = today + pd.Timedelta(days=days_ahead)

	filtered = df[df[date_field].notna()].copy()
	filtered["week"] = filtered[date_field].dt.to_period("W").apply(lambda r: r.start_time)

	grouped = filtered.groupby("week").agg(
		loan_volume=("loan_amount", "sum"),
		loan_count=("loanId", "count")
	).sort_index()

	if grouped.empty:
		print("No loans with valid 'Clear to Close' dates found.")
		return

	grouped["loan_volume_m"] = grouped["loan_volume"] / 1_000_000
	avg_volume = grouped["loan_volume_m"].mean()
	colors = generate_shades("#00d387", len(grouped))

	fig, ax = plt.subplots(figsize=(5, 6))
	bars = ax.bar(
		grouped.index.astype(str),
		grouped["loan_volume_m"],
		color=colors
	)

	ax.set_title(f"{title} – Next {days_ahead} Days", fontsize=13, weight='bold', pad=10)
	ax.set_ylabel("Loan Volume ($M)", fontsize=12)
	ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}M'))
	ax.tick_params(axis='x', rotation=45, labelsize=10)
	ax.grid(True, axis='y', linestyle='--', linewidth=0.7)

	ax.axhline(avg_volume, color="red", linestyle=':', linewidth=2)
	ax.annotate(f'Avg: ${avg_volume:.1f}M',
							xy=(0.99, avg_volume),
							xycoords=('axes fraction', 'data'),
							xytext=(-10, -10),
							textcoords='offset points',
							ha='right', fontsize=9, color="red")

	for bar, count in zip(bars, grouped["loan_count"]):
		height = bar.get_height()
		ax.annotate(f'{count:,}',
								xy=(bar.get_x() + bar.get_width() / 2, height),
								xytext=(0, 4), textcoords="offset points",
								ha='center', va='bottom', fontsize=9)

	plt.tight_layout()
	if show_plots:
		plt.show()
	if images_path and suffix:
		fig.savefig(f"{images_path}projected_closings_{suffix.replace(' ', '_').replace('_-_', '_')}.png")
	plt.close(fig)

	return grouped.reset_index()

def plot_loan_officer_pareto(df, status_label, images_path=None, suffix=None, show_plots=False):
  df = df.copy()
  df["loan_officer"] = df["loan_officer"].fillna("Unassigned").astype(str).str.strip()
  df["loan_officer"] = df["loan_officer"].replace("", "Unassigned")
  df["loan_officer"] = df["loan_officer"].apply(lambda x: " ".join(x.split()))

  grouped = df.groupby("loan_officer").agg(
    loan_volume=("loan_amount", "sum"),
    loan_count=("loanId", "count")
  ).sort_values(by="loan_volume", ascending=False)

  top30 = grouped.head(30).copy()
  top30["loan_volume_m"] = top30["loan_volume"] / 1_000_000
  top30["cum_pct"] = top30["loan_volume"].cumsum() / top30["loan_volume"].sum() * 100

  fig, ax1 = plt.subplots(figsize=(10, 12))

  y = np.arange(len(top30))
  colors = generate_shades("#347cff", len(top30))

  bars = ax1.barh(y, top30["loan_volume_m"], color=colors)
  ax1.set_xlabel("Loan Volume ($M)", fontsize=12)
  ax1.xaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}M'))
  ax1.set_yticks(y)
  ax1.set_yticklabels(top30.index, fontsize=10)
  ax1.invert_yaxis()
  ax1.grid(True, axis='x', linestyle='--', linewidth=0.7)

  for yi, bar, count in zip(y, bars, top30["loan_count"]):
    width = bar.get_width()
    ax1.annotate(f'{count:,}',
      xy=(width, yi),
      xytext=(5, 0),
      textcoords="offset points",
      ha='left', va='center', fontsize=10)

  plt.title(f"{status_label} Loan Volume by Loan Officer – Top 30", fontsize=13, weight='bold', pad=10)
  plt.tight_layout(pad=2)
  if show_plots:
    plt.show()
  if images_path and suffix:
    fig.savefig(f"{images_path}pareto_loan_officer_{suffix.replace(' ', '_').replace('_-_', '_')}.png")
  plt.close(fig)

def generate_shades(base_hex, n_shades):
	base_rgb = mcolors.to_rgb(base_hex)
	shades = []
	for i in range(n_shades):
		factor = 0.6 + 0.4 * (i / max(1, n_shades - 1))
		shade = tuple(min(1, c * factor) for c in base_rgb)
		shades.append(mcolors.to_hex(shade))
	return shades[::-1]