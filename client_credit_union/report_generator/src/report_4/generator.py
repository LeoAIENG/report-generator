from docxtpl import DocxTemplate, InlineImage
from src.utils import get_report_paths
from .preprocess import preprocess
from .plots import (
	plot_closed_loan_volume,
	plot_product_type_distribution,
	plot_avg_days_to_close,
	plot_loans_missing_submittal,
	generate_product_type_summary_table
)
import config as cfg
from .context import get_template_context
 
def gen_images_report_4(report_prefix, closed_df, images_path, time_label):
	plot_closed_loan_volume(
		df=closed_df,
		title_prefix=time_label,
		image_path=images_path,
		prefix=report_prefix,
		show_plots=False
	)
	plot_product_type_distribution(
		df=closed_df,
		title_prefix=time_label,
		image_path=images_path,
		prefix=report_prefix,
		show_plots=False
	)
	plot_avg_days_to_close(
		df=closed_df,
		title_prefix=time_label,
		image_path=images_path,
		prefix=report_prefix,
		show_plots=False
	)
	plot_loans_missing_submittal(
		df=closed_df,
		title_prefix=time_label,
		image_path=images_path,
		prefix=report_prefix,
		show_plots=False
	)
	generate_product_type_summary_table(
		df=closed_df,
		title_prefix=time_label,
		image_path=images_path,
		prefix=report_prefix,
		show_plots=False
	)

def remove_images(images_path):
	for path in sorted((images_path).glob("*")):
		path.unlink()

def gen_docx_report(report_prefix, doc_template_path, appendix_template_path, images_path, output_path, closed_df, month_label, year_label, show_appendix=True):
	tpl = DocxTemplate(doc_template_path)
	appendix_sd = tpl.new_subdoc(appendix_template_path) if show_appendix else None
	context = get_template_context(
		report_prefix=report_prefix,
		closed_df=closed_df,
		images_path=images_path,
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
	closed_df = preprocess(
		loan_json_path=report_paths["loan_json_path"]
	)
	
	gen_images_report_4(
		images_path=report_paths["images_path"],
		closed_df=closed_df,
		report_prefix=report_prefix,
		time_label=time_label
	)
	output_path = gen_docx_report(
		report_prefix=report_prefix,
		doc_template_path=report_paths["doc_template_path"],
		appendix_template_path=report_paths["appendix_template_path"],
		images_path=report_paths["images_path"],
		output_path=report_paths["output_path"],
		closed_df=closed_df,
		month_label=month_label,
		year_label=year_label,
		show_appendix=show_appendix
	)
	remove_images(images_path=report_paths["images_path"])
	return output_path

