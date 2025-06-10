from docx.shared import Inches
from datetime import datetime
from docxtpl import InlineImage
import config as cfg

def add_images_context(images_path, report_prefix, tpl, context):
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

def get_template_context(report_prefix, merged_df, loan_df, tpl, images_path, appendix_sd=None, show_appendix=True, month_label=None, year_label=None):
	# Quantity of Loans
	cl_qtd = len(loan_df)
	
	# Quantity of Closed Loans and Credit Pulls
	cl_cleared_qtd = merged_df["Closed Loans"].sum()
	cl_cred_pulls_qtd = merged_df["Credit Pulls"].sum()
	
	# Min and Max Close Rate
	min_idx = merged_df[merged_df["Close Rate (%)"]>0]["Close Rate (%)"].idxmin()
	max_idx = merged_df[merged_df["Close Rate (%)"]>0]["Close Rate (%)"].idxmax()
	min_name, min_rate = merged_df.iloc[min_idx]["Loan Officer"], merged_df.iloc[min_idx]["Close Rate (%)"]
	max_name, max_rate = merged_df.iloc[max_idx]["Loan Officer"], merged_df.iloc[max_idx]["Close Rate (%)"]
	cl_pulltoc_name_max = max_name
	cl_pulltoc_name_min = min_name
	cl_pulltoc_ratio_max = max_rate
	cl_pulltoc_ratio_min = min_rate

	# Report Date
	cl_report_m = datetime.now().strftime("%B")
	cl_report_d = datetime.now().strftime("%-d")
	cl_report_yr = datetime.now().strftime("%Y")
	
	# TODO:
	cl_sent_branch_qtd = 8

	context = {
		'appendix_sd': appendix_sd,
		'cl_cleared_qtd': cl_cleared_qtd,
		'cl_cred_pulls_qtd': cl_cred_pulls_qtd,
		'cl_fund_m' : month_label,
		'cl_fund_yr' : year_label,
		'cl_pulltoc_name_max': cl_pulltoc_name_max,
		'cl_pulltoc_name_min': cl_pulltoc_name_min,
		'cl_pulltoc_ratio_max': cl_pulltoc_ratio_max,
		'cl_pulltoc_ratio_min': cl_pulltoc_ratio_min,
		'cl_qtd' : cl_qtd,
		'cl_report_num': cfg.app.report_n.report_3,
		'cl_report_v': cfg.app.report_v,
		'cl_report_m' : cl_report_m,
		'cl_report_d' : cl_report_d,
		'cl_report_yr' : cl_report_yr,
		'cl_sent_branch_qtd': cl_sent_branch_qtd,
		'cl_yr': year_label,
		"show_appendix": str(show_appendix)
	}
	context = add_images_context(images_path, report_prefix, tpl, context)

	return context