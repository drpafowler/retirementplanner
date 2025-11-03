import pandas as pd
from typing import Tuple


def compute_projection(
    current_year: int = 2025,
    current_age: int = 51,
    current_savings: float = 20000.0,
    retirement_start_year: int = 2039,
    retirement_years: int = 25,
    base_income_need: float = 64000.0,
    inflation: float = 0.03,
    cola: float = 0.03,
    investment_return: float = 0.05,
    p1_start_value: float = 16000.0,
    p1_start_age: int = 55,
    p2_start_value: float = 29400.0,
    p2_start_age: int = 65,
    ss_start_value: float = 800 * 12,
    ss_start_age: int = 62,
) -> Tuple[pd.DataFrame, float, float, float, float, int, int]:
    """Compute retirement cash-flow projection and helper metrics.

    Returns:
      df: DataFrame with year-by-year projections
      total_needed_at_retirement: sum of PV of shortfalls
      fv_current_savings: future value of current savings at retirement start
      remaining_needed: remaining amount needed at retirement after FV of current savings
      annual_savings_needed: end-of-year annual contribution required
      years_to_retirement: years between current_year and retirement_start_year
      retirement_age: current_age + years_to_retirement
    """

    # Derived values
    retirement_end_year = retirement_start_year + retirement_years - 1
    retirement_years_range = list(range(retirement_start_year, retirement_end_year + 1))
    ret_index = list(range(len(retirement_years_range)))
    years_to_retirement = retirement_start_year - current_year

    # Build DataFrame
    df = pd.DataFrame({
        'Year': retirement_years_range,
        'Ret_Year_Index': ret_index,
    })
    df['Age'] = current_age + (df['Year'] - current_year)

    # Target income (inflated)
    df['Target_Income'] = base_income_need * (1 + inflation) ** (years_to_retirement + df['Ret_Year_Index'])

    # Pension 1 (age-based start)
    df['Pension_1'] = 0.0
    mask_p1 = df['Age'] >= p1_start_age
    df.loc[mask_p1, 'Pension_1'] = p1_start_value * (1 + cola) ** (df.loc[mask_p1, 'Age'] - p1_start_age)

    # Pension 2 (age-based start)
    df['Pension_2'] = 0.0
    mask_p2 = df['Age'] >= p2_start_age
    df.loc[mask_p2, 'Pension_2'] = p2_start_value * (1 + cola) ** (df.loc[mask_p2, 'Age'] - p2_start_age)

    # Social Security (age-based start)
    df['Social_Security'] = 0.0
    mask_ss = df['Age'] >= ss_start_age
    df.loc[mask_ss, 'Social_Security'] = ss_start_value * (1 + cola) ** (df.loc[mask_ss, 'Age'] - ss_start_age)

    # Totals and shortfall
    df['Total_Fixed_Income'] = df['Pension_1'] + df['Pension_2'] + df['Social_Security']
    df['Shortfall'] = (df['Target_Income'] - df['Total_Fixed_Income']).clip(lower=0)

    # Present Value of shortfall
    df['PV_of_Shortfall'] = df['Shortfall'] / (1 + investment_return) ** df['Ret_Year_Index']

    total_needed_at_retirement = df['PV_of_Shortfall'].sum()

    # Savings calculation
    if years_to_retirement <= 0:
        fv_current_savings = current_savings
        remaining_needed = max(0.0, total_needed_at_retirement - fv_current_savings)
        annual_savings_needed = 0.0
    else:
        fv_current_savings = current_savings * (1 + investment_return) ** years_to_retirement
        remaining_needed = max(0.0, total_needed_at_retirement - fv_current_savings)

        if remaining_needed == 0.0:
            annual_savings_needed = 0.0
        else:
            r = investment_return
            n = years_to_retirement
            if r == 0:
                annual_savings_needed = remaining_needed / n
            else:
                annuity_factor = ((1 + r) ** n - 1) / r
                annual_savings_needed = remaining_needed / annuity_factor

    retirement_age = current_age + years_to_retirement

    return (
        df,
        total_needed_at_retirement,
        fv_current_savings,
        remaining_needed,
        annual_savings_needed,
        years_to_retirement,
        retirement_age,
    )


if __name__ == '__main__':
    # When run directly, use the defaults and write CSV and print summary
    (
        df,
        total_needed_at_retirement,
        fv_current_savings,
        remaining_needed,
        annual_savings_needed,
        years_to_retirement,
        retirement_age,
    ) = compute_projection()

    # Save CSV
    df.to_csv('retirement_cash_flow.csv', index=False, float_format='%.2f')
    print(f"Successfully saved 'retirement_cash_flow.csv' to your directory.")
    print(f"Total needed at retirement ({df['Year'].iloc[0]}): ${total_needed_at_retirement:,.2f}")
    print()
    print(f"Current age: 51")
    print(f"Current savings: ${20000.00:,.2f}")
    print(f"Years to retirement: {years_to_retirement} (retirement age ≈ {retirement_age})")
    print(f"Future value of current savings at retirement: ${fv_current_savings:,.2f}")
    print(f"Remaining needed at retirement after current savings: ${remaining_needed:,.2f}")
    print(f"Estimated annual savings required (end of year deposits): ${annual_savings_needed:,.2f}")