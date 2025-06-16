from docxtpl import DocxTemplate, InlineImage
from .preprocess import preprocess, loan_df_from_records
from .tables import get_graph_tables
from src.utils import get_report_paths
from .plots import (
	plot_loan_officer_by_efficiency,
	plot_closed_pulls,
	plot_closed_pulls_by_branch
)
import config as cfg
from .context import get_template_context
 
def gen_images_report(images_path, merged_df, report_prefix, time_label):
	loan_officer_by_efficiency_table, closed_pulls_table, closed_pulls_by_branch_table = get_graph_tables(merged_df)
	plot_loan_officer_by_efficiency(
		table=loan_officer_by_efficiency_table,
		graph_name="loan_officer_by_efficiency_top30",
		image_path=images_path,
		prefix=report_prefix,
		time_label=time_label,
		show_plots=False
	)

	plot_closed_pulls(
		table=closed_pulls_table,
		graph_name="closed_pulls_top30",
		image_path=images_path,
		prefix=report_prefix,
		time_label=time_label,
		show_plots=False
	)
	plot_closed_pulls_by_branch(
		table=closed_pulls_by_branch_table,
		graph_name="closed_pulls_by_branch",
		image_path=images_path,
		prefix=report_prefix,
		time_label=time_label,
		show_plots=False
	)

def remove_images(images_path):
	for path in sorted((images_path).glob("*")):
		path.unlink()

def gen_docx_report(report_prefix, doc_template_path, appendix_template_path, images_path, output_path, merged_df, loan_df, closed_loans, month_label, year_label, show_appendix=True):
	tpl = DocxTemplate(doc_template_path)
	appendix_sd = tpl.new_subdoc(appendix_template_path) if show_appendix else None
	context = get_template_context(
		report_prefix=report_prefix,
		merged_df=merged_df,
		loan_df=loan_df,
		closed_loans=closed_loans,
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
	report_paths = get_report_paths(report_prefix, month_label, year_label)
	time_label = cfg.report.time_label.format(
        month_label=month_label,
        year_label=year_label
    )
	merged_df, closed_loans = preprocess(
		loan_json_path=report_paths["loan_json_path"],
		credit_excel_path=report_paths["credit_excel_path"]
	)
	loan_df = loan_df_from_records(report_paths["loan_json_path"])
	
	gen_images_report(
		images_path=report_paths["images_path"],
		merged_df=merged_df,
		report_prefix=report_prefix,
		time_label=time_label
	)
	output_path = gen_docx_report(
		report_prefix=report_prefix,
		doc_template_path=report_paths["doc_template_path"],
		appendix_template_path=report_paths["appendix_template_path"],
		images_path=report_paths["images_path"],
		output_path=report_paths["output_path"],
		merged_df=merged_df,
		loan_df=loan_df,
		closed_loans=closed_loans,
		month_label=month_label,
		year_label=year_label,
		show_appendix=show_appendix
	)
	remove_images(images_path=report_paths["images_path"])
	return output_path

