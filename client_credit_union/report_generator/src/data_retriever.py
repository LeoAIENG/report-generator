import json
import requests
from tqdm import tqdm
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Any, Optional, Tuple
import config as cfg

class DataRetriever:
    """A class to handle loan data retrieval from Encompass API."""
    
    def __init__(self):
        """Initialize the LoanDataRetriever with API configuration.
        
        Args:
            api_server (str): The base URL for the Encompass API
        """
        self.api_server = cfg.retriever.api_server
        self.access_token = None
        
        # API endpoints
        self.token_url = cfg.retriever.token_url.format(api_server=self.api_server)
        self.pipeline_url = cfg.retriever.pipeline_url.format(api_server=self.api_server)
        
        # Field definitions
        self.fields = cfg.retriever.fields
        self.sort_order = cfg.retriever.sort_order
        self.field_ids = cfg.retriever.field_ids
        self.date_fields = cfg.retriever.date_fields
        
        # Folders to process
        self.folders = cfg.retriever.folders

    def get_access_token(self, username: str, password: str, client_id: str, client_secret: str) -> str:
        """Get OAuth2 access token using password credentials flow.
        
        Args:
            username (str): Encompass username
            password (str): Encompass password
            client_id (str): OAuth client ID
            client_secret (str): OAuth client secret
            
        Returns:
            str: Access token
            
        Raises:
            Exception: If token request fails
        """
        payload = {
            "grant_type": "password",
            "username": username,
            "password": password,
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "lp"
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        response = requests.post(self.token_url, data=payload, headers=headers)
        
        if response.status_code == 200:
            self.access_token = response.json()["access_token"]
            return self.access_token
        else:
            raise Exception(f"Failed to get access token: {response.text}")

    def get_loan_ids_by_folder(self, folder_name: str) -> List[str]:
        """Get loan IDs for a specific folder.
        
        Args:
            folder_name (str): Name of the folder to query
            
        Returns:
            List[str]: List of loan IDs
            
        Raises:
            Exception: If API request fails
        """
        if not self.access_token:
            raise Exception("Access token not set. Call get_access_token first.")
            
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        body = {
            "fields": self.fields,
            "sortOrder": self.sort_order,
            "filter": {
                "canonicalName": "Loan.LoanFolder",
                "value": folder_name,
                "matchType": "exact",
                "precision": "Day"
            },
            "orgType": "Internal",
            "loanOwnership": "AllLoans"
        }
        
        response = requests.post(self.pipeline_url, headers=headers, json=body)
        response.raise_for_status()
        return [loan["loanId"] for loan in response.json()]

    def get_last_month_date_range(self, month: Optional[int] = None, year: Optional[int] = None) -> Tuple[datetime, datetime]:
        """Get date range for last month.
        
        Args:
            month (Optional[int]): Reference month (1-12)
            year (Optional[int]): Reference year
            
        Returns:
            Tuple[datetime, datetime]: Start and end dates of last month
        """
        today = datetime.today()
        
        if month:
            if not year:
                year = today.year
            reference_date = datetime(year, month, 1)
        else:
            reference_date = today
            
        first_day_this_month = reference_date.replace(day=1)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        first_day_last_month = last_day_last_month.replace(day=1)
        
        return first_day_last_month, last_day_last_month

    def is_funded_last_month(self, funding_date_str: str, start_date: datetime, end_date: datetime) -> bool:
        """Check if loan was funded in the specified date range.
        
        Args:
            funding_date_str (str): Funding date string
            start_date (datetime): Start date of range
            end_date (datetime): End date of range
            
        Returns:
            bool: True if funded in range, False otherwise
        """
        if not funding_date_str:
            return False
        try:
            funding_date = datetime.strptime(funding_date_str.split()[0], "%m/%d/%Y")
            return start_date <= funding_date <= end_date
        except Exception as e:
            print(f"⚠️ Error parsing funding date: {funding_date_str} - {e}")
            return False

    def retrieve_loan_field_data(self, folders: List[str], output_path: str) -> List[Dict[str, Any]]:
        """Retrieve and save loan field data for specified folders.
        
        Args:
            folders (List[str]): List of folder names to process
            output_path (str): Path to save the JSON output
            
        Returns:
            List[Dict[str, Any]]: Retrieved loan field data
        """
        if not self.access_token:
            raise Exception("Access token not set. Call get_access_token first.")
            
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        loan_field_data = []
        start_date, end_date = self.get_last_month_date_range()
        
        for folder in folders:
            loan_ids = self.get_loan_ids_by_folder(folder)
            print(f"✅ {folder}: {len(loan_ids)} loan(s) found")
            
            for loan_id in tqdm(loan_ids, desc=f"Fetching fields from '{folder}'"):
                url = f"{self.api_server}/encompass/v3/loans/{loan_id}/fieldReader?invalidFieldBehavior=Include"
                response = requests.post(url, headers=headers, json=self.field_ids)
                
                if response.status_code == 200:
                    loan_data = response.json()
                    
                    # Apply funding date filter only for Closed 2025
                    if folder == "Closed 2025":
                        funding_date_str = loan_data.get("1997")
                        if not self.is_funded_last_month(funding_date_str, start_date, end_date):
                            continue
                            
                    loan_field_data.append({
                        "loanId": loan_id,
                        "folder": folder,
                        "fields": loan_data
                    })
                else:
                    print(f"❌ Failed for loanId: {loan_id} | Status: {response.status_code}")
        
        # Save to file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(loan_field_data, f, indent=2, ensure_ascii=False)
            
        return loan_field_data
    
    def extract_month_year(self, date_str: str) -> Optional[str]:
            try:
                date = datetime.strptime(date_str.split()[0], "%m/%d/%Y")
                return date.strftime("%Y-%m")
            except:
                return None

    def analyze_date_fields(self, loan_field_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, set]]:
        """Analyze date fields in loan data.
        
        Args:
            loan_field_data (List[Dict[str, Any]]): Loan field data to analyze
            
        Returns:
            Dict[str, Dict[str, set]]: Analysis results by folder and field
        """
        months_by_folder_and_field = defaultdict(lambda: defaultdict(set))
        
        for entry in loan_field_data:
            folder = entry["folder"]
            fields = entry["fields"]
            
            for field_id in self.date_fields:
                date_str = fields.get(field_id)
                if date_str:
                    month = self.extract_month_year(date_str)
                    if month:
                        months_by_folder_and_field[folder][field_id].add(month)
                        
        return months_by_folder_and_field
    
    def print_analysis(self, analysis: Dict[str, Dict[str, set]]):
        print("\n📅 Months detected by folder and date field:")
        for folder, field_months in analysis.items():
            print(f"\n📁 {folder}:")
            for field_id, months in field_months.items():
                month_list = sorted(months)
                print(f"  - {field_id}: {', '.join(month_list)}")
    
    def run(self):

        
        # Get access token
        username = cfg.app.secrets.encompass.username
        password = cfg.app.secrets.encompass.password
        client_id = cfg.app.secrets.encompass.client_id
        client_secret = cfg.app.secrets.encompass.client_secret
        
        try:
            self.get_access_token(username, password, client_id, client_secret)
            print("✅ Successfully obtained access token")
            
            # Define folders to process
            folders = ["Active Pipeline", "Closed 2025"]
            
            # Retrieve and save loan field data
            output_path = cfg.path.loan_json
            loan_field_data = self.retrieve_loan_field_data(folders, output_path)
            print(f"✅ Successfully saved loan field data to {output_path}")
            
            # Analyze date fields
            analysis = self.analyze_date_fields(loan_field_data)
            
            # Print analysis results
            self.print_analysis(analysis)
                    
        except Exception as e:
            print(f"❌ Error: {str(e)}")