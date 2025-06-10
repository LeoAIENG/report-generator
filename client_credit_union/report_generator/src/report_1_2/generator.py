from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches
from datetime import datetime
from src.report_1_2.preprocess import preprocess_json
import config as cfg
from src.utils import get_report_paths
from .plots import (
	plot_volume_by_channel_and_product,
	plot_volume_by_state,
	plot_volume_by_branch,
	plot_loan_officer_pareto,
	plot_projected_closings
)

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
	cl_report_d = datetime.now().strftime("%-d")
	cl_report_yr = datetime.now().strftime("%Y")

	context = {
		'cl_report_num': cfg.app.report_n.__dict__[report_prefix],
		'cl_report_v': cfg.app.report_v,
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

def gen_images_report_1_2(images_path, loan_df, report_prefix, status_label, time_label):
	status_df = get_df_by_status(loan_df, status_label)
	images_path = images_path.as_posix() + '/'
	title_prefix = getattr(cfg.app.title_label, report_prefix)
	if report_prefix == "report_1":
		title_prefix = title_prefix.format(
			time_label=time_label,
			status_label=status_label
		)
	suffix = status_label.lower()
	
	plot_volume_by_channel_and_product(status_df, title_prefix=title_prefix, suffix=suffix, images_path=images_path)
	plot_volume_by_state(status_df, title_prefix=title_prefix, suffix=suffix, images_path=images_path)
	plot_loan_officer_pareto(status_df, status_label=title_prefix, suffix=suffix, images_path=images_path)
	plot_projected_closings(status_df, suffix=suffix, images_path=images_path) if status_label == "Active" else None
	plot_volume_by_branch(status_df, title_prefix=title_prefix, suffix=suffix, images_path=images_path)

def remove_images(images_path):
	for path in sorted((images_path).glob("*")):
		path.unlink()

def gen_docx_report(report_prefix, doc_template_path, appendix_template_path, images_path, output_path, loan_df, status_label, month_label, year_label, show_appendix=True):
	tpl = DocxTemplate(doc_template_path)
	appendix_sd = tpl.new_subdoc(appendix_template_path) if show_appendix else None
	context = get_template_context(
		images_path=images_path,
		report_prefix=report_prefix,
		loan_df=loan_df,
		status_label=status_label,
		tpl=tpl,
		appendix_sd=appendix_sd,
		show_appendix=show_appendix,
		month_label=month_label,
		year_label=year_label
	)
	tpl.render(context, autoescape=True)
	tpl.save(output_path)
	
	
	return output_path

def run(report_prefix, month_label, year_label, show_appendix):
	report_paths = get_report_paths(report_prefix)
	time_label = cfg.app.time_label.format(
        month_label=month_label,
        year_label=year_label
    )
	status_label = getattr(cfg.app.status_label, report_prefix)
	loan_df = preprocess_json(
		loan_json_path=report_paths["loan_json_path"],
	)	
	gen_images_report_1_2(
		images_path=report_paths["images_path"],
		report_prefix=report_prefix,
		loan_df=loan_df,
		status_label=status_label,
		time_label=time_label
	)
	output_path = gen_docx_report(
		report_prefix=report_prefix,
		doc_template_path=report_paths["doc_template_path"],
		appendix_template_path=report_paths["appendix_template_path"],
		images_path=report_paths["images_path"],
		output_path=report_paths["output_path"],
		month_label=month_label,
		year_label=year_label,
		loan_df=loan_df,
		status_label=status_label,
		show_appendix=show_appendix
	)
	remove_images(images_path=report_paths["images_path"])
	return output_path

