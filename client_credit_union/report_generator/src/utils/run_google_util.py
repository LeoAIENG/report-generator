from google_util import GoogleDriveConverter

# Initialize the converter with your credentials file
converter = GoogleDriveConverter("credentials.json")

# Convert a DOCX file to PDF using its file ID
input_path = "data/output/report_1_May_2025.docx"
output_path = "data/output/report_1_May_2025.pdf"
output_path = converter.convert_local_docx_to_pdf(input_path, output_path)
print(output_path)

# # Or convert using a file path
# file_path = 'folder/subfolder/document.docx'
# file_id = converter.get_file_id_from_path(file_path)
# pdf_file_id = converter.convert_docx_to_pdf(file_id)

# # Optionally specify a different output folder
# output_folder_id = 'your_output_folder_id'
# pdf_file_id = converter.convert_docx_to_pdf(file_id, output_folder_id)
