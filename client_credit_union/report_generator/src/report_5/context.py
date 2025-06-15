from docx.shared import Inches
from datetime import datetime
from docxtpl import InlineImage
import config as cfg
import pandas as pd

def add_images_context(images_path, report_prefix, tpl, context):
	for path in images_path.glob("*.png"):
		context_img = f"{path.stem}_img"
		report_layout = getattr(cfg.layout, report_prefix)
		if context_img in report_layout.images.full_width_imgs:
			width = Inches(cfg.layout.metrics.full)
		elif context_img in report_layout.images.half_width_imgs:
			width = Inches(cfg.layout.metrics.half)
		elif context_img in report_layout.images.custom_width_imgs:
			custom = getattr(cfg.layout.metrics.custom, context_img)
			width = Inches(custom)
		context[context_img] = InlineImage(tpl=tpl, image_descriptor=path.as_posix(), width=width)
	return context

def get_template_context(report_prefix, closed_df, tpl, images_path, appendix_sd=None, show_appendix=True, month_label=None, year_label=None):
	# Quantity of Loans
	closed_df = closed_df[closed_df["folder"] == "Closed 2025"]
	cl_qtd = len(closed_df)

	# Branch Processors Unique
	branch_processors = closed_df["branch_processor"].dropna().unique()
	cl_branch_procs_qtd = len(branch_processors)

	# loans where the submittal date field "fields.Log.MS.Date.Submittal" is empty (""), null, or set to "//"
	cl_nosubdate_qtd = len(closed_df[closed_df["submittal_date"].isna() | (closed_df["submittal_date"] == "") | (closed_df["submittal_date"] == "//")])
	cl_nosubdate_per = round(cl_nosubdate_qtd / cl_qtd * 100, 2)

	# Average days to close
	close_c_df = closed_df.copy()
	close_c_df["submittal_date"] = pd.to_datetime(close_c_df["submittal_date"])
	close_c_df["clear_to_close"] = pd.to_datetime(close_c_df["clear_to_close"])
	close_c_df = close_c_df[close_c_df["submittal_date"].notna() & close_c_df["clear_to_close"].notna()]
	close_c_df["days_to_close"] = (close_c_df["clear_to_close"] - close_c_df["submittal_date"]).dt.days
	cl_avg_sub_days = round(close_c_df["days_to_close"].mean(), 1)

	# Unnamed Branch Processors
	cl_unnamed_branch_procs_qtd = len(closed_df[closed_df["LoanTeamMember.Name.Branch Processor"].isna() | (closed_df["LoanTeamMember.Name.Branch Processor"] == "") | (closed_df["LoanTeamMember.Name.Branch Processor"] == "//")])
	cl_unnamed_branch_procs_per  = round(cl_unnamed_branch_procs_qtd / cl_qtd * 100, 1)

	# Report Date
	cl_report_m = datetime.now().strftime("%B")
	cl_report_d = "1"
	cl_report_yr = datetime.now().strftime("%Y")

	report_n = getattr(cfg.report.report_n, report_prefix)
	report_v = getattr(cfg.report.report_v, report_prefix)

	context = {
		'appendix_sd': appendix_sd,
		'cl_fund_m' : month_label,
		'cl_fund_yr' : year_label,
		'cl_qtd' : cl_qtd,
		'cl_report_num': report_n,
		'cl_report_v': report_v,
		'cl_report_m' : cl_report_m,
		'cl_report_d' : cl_report_d,
		'cl_report_yr' : cl_report_yr,
		'cl_yr': year_label,
		'cl_avg_sub_days': cl_avg_sub_days,
		'cl_branch_procs_qtd': cl_branch_procs_qtd,
		'cl_unnamed_branch_procs_qtd': cl_unnamed_branch_procs_qtd,
		'cl_unnamed_branch_procs_per': cl_unnamed_branch_procs_per,
		'cl_nosubdate_qtd': cl_nosubdate_qtd,
		'cl_nosubdate_per': cl_nosubdate_per,
		"show_appendix": str(show_appendix)
	}
	context = add_images_context(images_path, report_prefix, tpl, context)

	return context