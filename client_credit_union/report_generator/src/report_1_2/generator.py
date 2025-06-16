from docxtpl import DocxTemplate
from .preprocess import preprocess_json
from src.utils import get_report_paths
from .plots import (
	plot_volume_by_channel_and_product,
	plot_volume_by_state,
	plot_volume_by_branch,
	plot_loan_officer_pareto,
	plot_projected_closings
)
from .context import get_df_by_status, get_template_context
import config as cfg


def gen_images_report(images_path, loan_df, report_prefix, status_label, time_label):
	status_df = get_df_by_status(loan_df, status_label)
	images_path = images_path.as_posix() + '/'
	title_prefix = getattr(cfg.report.title_label, report_prefix)
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
	report_paths = get_report_paths(report_prefix, month_label, year_label)
	time_label = cfg.report.time_label.format(
        month_label=month_label,
        year_label=year_label
    )
	status_label = getattr(cfg.report.status_label, report_prefix)
	loan_df = preprocess_json(
		loan_json_path=report_paths["loan_json_path"],
	)	
	gen_images_report(
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

