import pulp
from split_to_month import calculate_monthly_weight

def annual_target_expression(sr_month_revenue):
  return pulp.lpSum([
    sr_month_revenue[f'{x}_month_revenue']
    for x in range(1, 13)
  ])

def get_monthly_variables():
  sr_month_revenue = pulp.LpVariable.dicts("SKU_Month_Revenue", [
    f'{x}_month_revenue'
    for x in range(1, 13)
  ], lowBound=0, cat='Continuous')
  return sr_month_revenue

problem = pulp.LpProblem("Maximize Sales Revenue", pulp.LpMaximize)
sr_monthly_revenue = get_monthly_variables()
problem += annual_target_expression(sr_monthly_revenue)

def resolve(target, months=(1, 12)):
  monthly_target = [percentage * target for percentage  in calculate_monthly_weight()]