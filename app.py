import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from retirement import compute_projection


st.set_page_config(layout="wide")
st.title("Retirement Income Projection")


def sidebar_inputs():
	st.sidebar.header("Retirement assumptions")
	current_year = st.sidebar.number_input("Current year", value=2025, step=1)
	current_age = st.sidebar.number_input("Current age", value=35, min_value=18, max_value=100, step=1)
	current_savings = st.sidebar.number_input("Current savings ($)", value=200000.0, step=1000.0, format="%.2f")
	retirement_start_year = st.sidebar.number_input("Retirement start year", value=2059, step=1)
	retirement_years = st.sidebar.number_input("Retirement length (years)", value=25, min_value=1, step=1)
	base_income_need = st.sidebar.number_input("Base income need (2025 $)", value=100000.0, step=1000.0, format="%.2f")
	inflation = st.sidebar.number_input("Inflation rate", value=0.03, step=0.005, format="%.3f")
	cola = st.sidebar.number_input("COLA (pensions/SS)", value=0.03, step=0.005, format="%.3f")
	investment_return = st.sidebar.number_input("Investment return (annual)", value=0.05, step=0.005, format="%.3f")

	st.sidebar.header("Pensions & Social Security")
	p1_start_age = st.sidebar.number_input("Pension 1 start age", value=62, min_value=40, max_value=120, step=1)
	p1_start_value = st.sidebar.number_input("Pension 1 start value ($/yr)", value=30000.0, step=500.0, format="%.2f")
	p2_start_age = st.sidebar.number_input("Pension 2 start age", value=62, min_value=40, max_value=120, step=1)
	p2_start_value = st.sidebar.number_input("Pension 2 start value ($/yr)", value=29400.0, step=500.0, format="%.2f")
	ss_start_age = st.sidebar.number_input("Social Security start age", value=62, min_value=62, max_value=70, step=1)
	ss_start_value = st.sidebar.number_input("Social Security annual value ($/yr)", value=1000.0 * 12, step=100.0, format="%.2f")

	return {
		'current_year': int(current_year),
		'current_age': int(current_age),
		'current_savings': float(current_savings),
		'retirement_start_year': int(retirement_start_year),
		'retirement_years': int(retirement_years),
		'base_income_need': float(base_income_need),
		'inflation': float(inflation),
		'cola': float(cola),
		'investment_return': float(investment_return),
		'p1_start_age': int(p1_start_age),
		'p1_start_value': float(p1_start_value),
		'p2_start_age': int(p2_start_age),
		'p2_start_value': float(p2_start_value),
		'ss_start_age': int(ss_start_age),
		'ss_start_value': float(ss_start_value),
	}


inputs = sidebar_inputs()

# Compute projection
(
	df,
	total_needed_at_retirement,
	fv_current_savings,
	remaining_needed,
	annual_savings_needed,
	years_to_retirement,
	retirement_age,
) = compute_projection(
	current_year=inputs['current_year'],
	current_age=inputs['current_age'],
	current_savings=inputs['current_savings'],
	retirement_start_year=inputs['retirement_start_year'],
	retirement_years=inputs['retirement_years'],
	base_income_need=inputs['base_income_need'],
	inflation=inputs['inflation'],
	cola=inputs['cola'],
	investment_return=inputs['investment_return'],
	p1_start_value=inputs['p1_start_value'],
	p1_start_age=inputs['p1_start_age'],
	p2_start_value=inputs['p2_start_value'],
	p2_start_age=inputs['p2_start_age'],
	ss_start_value=inputs['ss_start_value'],
	ss_start_age=inputs['ss_start_age'],
)


col1, col2 = st.columns([2, 1])

with col1:
	st.subheader("Income projection")
	fig, ax = plt.subplots(figsize=(10, 5))
	sns.lineplot(data=df, x='Year', y='Target_Income', label='Target Income', ax=ax)
	sns.lineplot(data=df, x='Year', y='Total_Fixed_Income', label='Total Fixed Income', ax=ax)
	ax.set_title('Income Projection')
	ax.set_xlabel('Year')
	ax.set_ylabel('Income ($)')
	ax.legend()
	st.pyplot(fig)

	st.markdown("### Projection table")
	st.dataframe(df)

with col2:
	st.subheader("Summary")
	st.metric("Total needed at retirement", f"${total_needed_at_retirement:,.2f}")
	st.metric("Future value of current savings", f"${fv_current_savings:,.2f}")
	st.metric("Remaining needed", f"${remaining_needed:,.2f}")
	st.metric("Annual savings required", f"${annual_savings_needed:,.2f}")

	st.markdown("---")
	st.write(f"Years to retirement: {years_to_retirement} (retirement age ≈ {retirement_age})")
	st.write("Adjust the inputs in the left sidebar to see how the projection changes.")