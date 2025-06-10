from docx import Document
from docx.oxml.ns import qn
import config as cfg

def get_image_alt_texts(docx_path):
    """
    Extracts alt text from images within a .docx file.

    Args:
        docx_path (str): The path to the .docx file.

    Returns:
        list: A list of dictionaries, where each dictionary contains
              the image's alt text ('title' and/or 'description') and its index.
    """

    document = Document(docx_path)
    image_alt_texts = {}
    image_index = 0

    for paragraph in document.paragraphs:
        for run in paragraph.runs:
            for inline_shape in run._element.findall('.//' + qn('wp:anchor')) + run._element.findall('.//' + qn('wp:inline')):
                docPr = inline_shape.find(qn('wp:docPr'))
                if docPr is not None:
                    alt_text_descr = docPr.get('descr')
                    if alt_text_descr:
                        image_alt_texts[image_index] = alt_text_descr
                    image_index += 1
    return image_alt_texts

def get_report_paths(report_prefix):
    output_path = cfg.path.output / cfg.path.output_file.format(
        report_prefix=report_prefix,
        month_label=cfg.app.month_label,
        year_label=cfg.app.year_label
    )
    doc_template_path = cfg.path.templates / cfg.path.doc_template_file.format(
        report_prefix=report_prefix
    )
    appendix_template_path = cfg.path.templates / cfg.path.appendix_template_file.format(
        report_prefix=report_prefix
    )
    images_path = cfg.path.images
    loan_json_path = cfg.path.loan_json
    credit_excel_path = cfg.path.credit_excel
    return {
        "output_path": output_path,
        "doc_template_path": doc_template_path,
        "appendix_template_path": appendix_template_path,
        "images_path": images_path,
        "loan_json_path": loan_json_path,
        "credit_excel_path": credit_excel_path
    }