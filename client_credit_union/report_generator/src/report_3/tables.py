def generate_loan_officer_by_efficiency_table(df):
	top30_table = df[df['Credit Pulls'] > 0].copy()
	top30_table = top30_table.sort_values(by='Loans per Pull', ascending=False).head(30)

	# Replace NaN in 'ORGID' with '-'
	top30_table['ORGID'] = top30_table['ORGID'].fillna('-')

	# Rename ORGID to Branch for display
	top30_table = top30_table.rename(columns={'ORGID': 'Branch'})

	# Reorder columns with Branch first
	top30_table = top30_table.rename(columns={'ORGID': 'Branch'})
	top30_table = top30_table[['Branch', 'Loan Officer', 'Closed Loans', 'Credit Pulls', 'Loan Amount', 'Loans per Pull']]
	top30_table['Loan Amount'] = top30_table['Loan Amount'].apply(lambda x: f"${x:,.0f}")
	return top30_table

def generate_closed_pulls_table(df):
	top30 = df.sort_values(by='Closed Loans', ascending=False).head(30)
	return top30

def generate_closed_pulls_by_branch_table(df):
	branch_summary = df.groupby('ORGID').agg({
		'Closed Loans': 'sum',
		'Credit Pulls': 'sum'
	}).reset_index()
	branch_summary['Loans per Pull'] = (branch_summary['Closed Loans'] / branch_summary['Credit Pulls']).round(2)

	sorted_branch = branch_summary.sort_values(by='Closed Loans', ascending=False)
	return sorted_branch

def get_graph_tables(merged_df):
	loan_officer_by_efficiency_table = generate_loan_officer_by_efficiency_table(merged_df)
	closed_pulls_table = generate_closed_pulls_table(merged_df)
	closed_pulls_by_branch_table = generate_closed_pulls_by_branch_table(merged_df)
	return loan_officer_by_efficiency_table, closed_pulls_table, closed_pulls_by_branch_table