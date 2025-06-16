from docxtpl import InlineImage
from docx.shared import Inches
from datetime import datetime
import config as cfg

def get_df_by_status(df, status_label):
	return df[df["status"] == status_label].copy()

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

def get_template_context(images_path, report_prefix, loan_df, status_label, tpl, appendix_sd=None, show_appendix=True, month_label=None, year_label=None):
	df = get_df_by_status(loan_df, status_label)
	cl_qtd = len(df)
	cl_report_m = datetime.now().strftime("%B")
	cl_report_d = "1"
	cl_report_yr = datetime.now().strftime("%Y")
	report_v = getattr(cfg.report.report_v, report_prefix)
	report_n = getattr(cfg.report.report_n, report_prefix)
	
	context = {
		'cl_report_num': report_n,
		'cl_report_v': report_v,
		'cl_report_m' : cl_report_m,
		'cl_report_d' : cl_report_d,
		'cl_report_yr' : cl_report_yr,
		'cl_qtd' : cl_qtd,
		'cl_yr': year_label,
		'cl_fund_m' : month_label,
		'cl_fund_yr' : year_label,
		'appendix_sd': appendix_sd,
		"show_appendix": str(show_appendix)
	}
	context = add_images_context(images_path, report_prefix, tpl, context)
	return context