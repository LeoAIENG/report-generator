from matplotlib.table import Table
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches

def generate_shades(base_hex, n_shades):
	base_rgb = mcolors.to_rgb(base_hex)
	shades = []
	for i in range(n_shades):
		factor = 0.6 + 0.4 * (i / max(1, n_shades - 1))
		shade = tuple(min(1, c * factor) for c in base_rgb)
		shades.append(mcolors.to_hex(shade))
	return shades[::-1]

def plot_loan_officer_by_efficiency(table, image_path, prefix, time_label, show_plots=False, graph_name = "loan_officer_by_efficiency"):
	top30_table = table
	# Plot styled table
	fig, ax = plt.subplots(figsize=(10, 10))
	ax.set_axis_off()
	tbl = Table(ax, bbox=[0, 0.1, 1, 0.85])
	data = [top30_table.columns.tolist()] + top30_table.values.tolist()

	tbl.auto_set_font_size(False)
	tbl.set_fontsize(12)

	n_rows, n_cols = len(data), len(data[0])
	width, height = 1.0 / n_cols, 0.85 / n_rows

	for i, row in enumerate(data):
		for j, val in enumerate(row):
			cell = tbl.add_cell(i, j, width, height, text=str(val), loc='center',
								facecolor='#c25c4b' if i == 0 else 'white')
			cell.set_edgecolor('black')
			cell.set_linewidth(0.5)
			if i == 0:
				cell.get_text().set_color('white')
				cell.get_text().set_weight('bold')

	ax.add_table(tbl)

	fig.text(0.5, 0.975, f"{time_label} Loan Officers by Efficiency – Top 30", ha='center', fontsize=13, weight='bold')
	fig.text(0.5, 0.02, "Efficiency is measured by Loans per Pull (Closed Loans / Credit Pulls)", ha='center', fontsize=12, style='italic')

	plt.tight_layout()
	if show_plots:
		plt.show()
	if image_path and prefix:
		fig.savefig(image_path / f"{prefix}_{graph_name}.png")
	plt.close(fig)

def plot_closed_pulls(table, image_path, prefix, time_label, show_plots=False, graph_name = "closed_pulls_top30"):
	# === 3. Graph – Closed Loans vs. Credit Pulls (Top 30) with custom shades ===
	top_30 = table
	x = range(len(top_30))
	bar_width = 0.35

	closed_shades = generate_shades("#ff782c", len(top_30))
	pulls_shades = generate_shades("#84c0d6", len(top_30))

	fig, ax = plt.subplots(figsize=(12, 8))
	for i in x:
		ax.bar(i, top_30['Closed Loans'].iloc[i], width=bar_width, color=closed_shades[i])
		ax.bar(i + bar_width, top_30['Credit Pulls'].iloc[i], width=bar_width, color=pulls_shades[i])
		ax.text(i, top_30['Closed Loans'].iloc[i] + 1,
					f"{top_30['Closed Loans'].iloc[i]}", ha='center', fontsize=9)

		ax.text(i + bar_width, top_30['Credit Pulls'].iloc[i] + 1,
					f"{top_30['Credit Pulls'].iloc[i]}", ha='center', fontsize=9)

	ax.set_xticks([i + bar_width / 2 for i in x])
	ax.set_xticklabels(top_30['Loan Officer'], rotation=40, ha='right', fontsize=11)
	ax.set_xlabel("Loan Officer", fontsize=12)
	ax.set_ylabel("Count", fontsize=12)
	ax.set_title(f"{time_label} Closed Loans vs. Credit Pulls – Top 30 Loan Officers", fontsize=13, weight='bold')

	closed_patch = mpatches.Patch(color="#ff782c", label='Closed Loans')
	pulls_patch = mpatches.Patch(color="#84c0d6", label='Credit Pulls')
	ax.legend(handles=[closed_patch, pulls_patch], loc='upper right')

	plt.tight_layout()
	if show_plots:
		plt.show()
	if image_path and prefix:
		fig.savefig(image_path / f"{prefix}_{graph_name}.png")
	plt.close(fig)

def plot_closed_pulls_by_branch(table, image_path, prefix, time_label, show_plots=False, graph_name = "closed_pulls_by_branch"):
	sorted_branch = table
	fig, ax = plt.subplots(figsize=(12, 6))
	x = range(len(sorted_branch))
	bar_width = 0.4

	closed_shades = generate_shades("#e6970c", len(sorted_branch))
	pulls_shades = generate_shades("#d2042d", len(sorted_branch))

	# Plot bars for Closed Loans and Credit Pulls
	for i in x:
		ax.bar(i, sorted_branch['Closed Loans'].iloc[i], width=bar_width, color=closed_shades[i])
		ax.bar(i + bar_width, sorted_branch['Credit Pulls'].iloc[i], width=bar_width, color=pulls_shades[i])

		# Add value labels
		ax.text(i, sorted_branch['Closed Loans'].iloc[i] + 1,
				f"{sorted_branch['Closed Loans'].iloc[i]}", ha='center', fontsize=9)
		ax.text(i + bar_width, sorted_branch['Credit Pulls'].iloc[i] + 1,
				f"{sorted_branch['Credit Pulls'].iloc[i]}", ha='center', fontsize=9)

	# X-axis labels and styling
	ax.set_xticks([i + bar_width / 2 for i in x])
	ax.set_xticklabels(sorted_branch['ORGID'], rotation=30, ha='right', fontsize=10)
	ax.set_xlabel("Branch", fontsize=12)
	ax.set_ylabel("Volume", fontsize=12)
	ax.set_title(f"{time_label} Closed Loans vs. Credit Pulls by Branch", fontsize=14, weight='bold')

	closed_patch = mpatches.Patch(color="#e6970c", label='Closed Loans')
	pulls_patch = mpatches.Patch(color="#d2042d", label='Credit Pulls')
	ax.legend(handles=[closed_patch, pulls_patch], loc='upper right')

	plt.tight_layout()
	if show_plots:
		plt.show()
	if image_path and prefix:
		fig.savefig(image_path / f"{prefix}_{graph_name}.png")
	plt.close(fig)