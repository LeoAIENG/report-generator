from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaFileUpload
import io
import os
import pickle

class GoogleDriveConverter:
    def __init__(self, credentials_path):
        """
        Initialize the Google Drive Converter.
        
        Args:
            credentials_path (str): Path to the credentials.json file from Google Cloud Console
        """
        self.SCOPES = ['https://www.googleapis.com/auth/drive.file']
        self.credentials_path = credentials_path
        self.service = self._get_drive_service()

    def _get_drive_service(self):
        """Get or create Google Drive service instance."""
        creds = None
        
        # Load credentials from token.pickle if it exists
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If credentials are not valid or don't exist, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for future use
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return build('drive', 'v3', credentials=creds)

    def convert_local_docx_to_pdf(self, input_path, output_path):
        """
        Convert a local DOCX file to PDF using Google Drive API and save it locally.
        
        Args:
            input_path (str): Local path to the DOCX file
            output_path (str): Local path where the PDF should be saved
            
        Returns:
            str: The local path of the saved PDF file
        """
        try:
            # Upload the DOCX file to Google Drive
            file_metadata = {
                'name': os.path.basename(input_path),
                'mimeType': 'application/vnd.google-apps.document'  # Convert to Google Doc
            }
            
            media = MediaFileUpload(
                input_path,
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            doc_id = file.get('id')
            
            # Export as PDF
            request = self.service.files().export_media(
                fileId=doc_id,
                mimeType='application/pdf'
            )
            
            # Download and save the PDF
            pdf_content = request.execute()
            with open(output_path, 'wb') as f:
                f.write(pdf_content)
                
            # Clean up - delete the uploaded doc from Google Drive
            self.service.files().delete(fileId=doc_id).execute()
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Error converting file to PDF: {str(e)}")