import pandas as pd
import json
from collections import Counter

def first_last(name):
  parts = name.strip().lower().split()
  return f"{parts[0]} {parts[-1]}" if len(parts) > 1 else parts[0]

def loan_df_from_records(loan_json_path):
	df = pd.read_json(loan_json_path)
	
	records = []
	for loan in df.to_dict(orient='records'):
		flat_record = {"loanId": loan["loanId"], "folder": loan["folder"]}
		flat_record.update(loan["fields"])
		records.append(flat_record)

	df = pd.DataFrame(records)
	return df

def preprocess(loan_json_path, credit_excel_path):
	
	# Open Credit Excel File
	xls = pd.ExcelFile(credit_excel_path)
	credit_df = xls.parse('Sheet0') # credit_df = xls.parse('Export Worksheet')
	credit_df.columns = [col.strip() for col in credit_df.columns]
	credit_df = credit_df.rename(columns={'OPERATOR_NAME': 'Loan Officer'})
	credit_df['Loan Officer'] = credit_df['Loan Officer'].str.strip().str.lower()

	# Melt Excel to long format
	credit_long = credit_df.melt(id_vars='Loan Officer',
								var_name='Scenario',
								value_name='Credit Pulls').dropna()
	credit_totals = credit_long.groupby('Loan Officer')['Credit Pulls'].sum().reset_index()
	

	# Load the JSON file with loan data
	with open(loan_json_path, 'r') as f:
		loan_data = json.load(f)

	# Filter only closed loans
	closed_loans = [loan for loan in loan_data if loan.get('folder') == 'Closed 2025']

	# === Normalize and Count Closed Loans per Officer ===
	closed_officers = [first_last(loan['fields']['317']) for loan in closed_loans if loan['fields'].get('317')]
	closed_per_officer = pd.Series(closed_officers).value_counts().reset_index()
	closed_per_officer.columns = ['Loan Officer', 'Closed Loans']

	# === Merge Loan Officer Data ===
	credit_totals['Normalized Name'] = credit_totals['Loan Officer'].apply(first_last)
	closed_per_officer['Normalized Name'] = closed_per_officer['Loan Officer'].apply(first_last)

	credit_totals_grouped = credit_totals.groupby('Normalized Name')['Credit Pulls'].sum().reset_index()
	closed_grouped = closed_per_officer.groupby('Normalized Name')['Closed Loans'].sum().reset_index()

	merged = pd.merge(credit_totals_grouped, closed_grouped, on='Normalized Name', how='outer').fillna(0)
	merged['Credit Pulls'] = merged['Credit Pulls'].astype(int)
	merged['Closed Loans'] = merged['Closed Loans'].astype(int)
	merged['Close Rate (%)'] = merged.apply(lambda r: round((r['Closed Loans']/r['Credit Pulls'])*100, 1) if r['Credit Pulls'] > 0 else None, axis=1)
	merged['Loans per Pull'] = merged.apply(lambda r: round((r['Closed Loans']/r['Credit Pulls']), 2) if r['Credit Pulls'] > 0 else None, axis=1)
	merged['Loan Officer'] = merged['Normalized Name'].apply(lambda x: ' '.join([w.capitalize() for w in x.split()]))

	# === Map ORGID (Branch) for Each Loan Officer ===
	officer_branch_amount_triplets = [
	(
		first_last(loan['fields'].get('317')),
		loan['fields'].get('ORGID'),
		float(str(loan['fields'].get('2')).replace('$', '').replace(',', '').strip())
	)
	for loan in closed_loans
	if loan['fields'].get('317') and loan['fields'].get('ORGID') and loan['fields'].get('2')
	]

	officer_branch_amount_df = pd.DataFrame(officer_branch_amount_triplets, columns=['Normalized Name', 'ORGID', 'Loan Amount'])

	officer_branch_map = officer_branch_amount_df.groupby('Normalized Name')['ORGID'] \
		.agg(lambda x: Counter(x).most_common(1)[0][0]).reset_index()
	officer_amount_map = officer_branch_amount_df.groupby('Normalized Name')['Loan Amount'].sum().reset_index()

	merged = pd.merge(merged, officer_branch_map, on='Normalized Name', how='left')
	merged = pd.merge(merged, officer_amount_map, on='Normalized Name', how='left')
	merged['Loan Amount'] = merged['Loan Amount'].fillna(0).astype(float)

	return merged