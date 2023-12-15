import math
import pulp
import pandas as pd

def calculate_monthly_weight():
  monthly_sku_list = [pd.read_csv(f'data/monthly.sku.{x}.csv') for x in range(1, 13)]
  for x in monthly_sku_list:
    x['revenue'] = x['history_sales'] * x['成本'] * (1 + x['最低毛利要求'])
  monthly_revenue = [
    x['revenue'].sum()
    for x in monthly_sku_list
  ]
  monthly_weight = [
    x / sum(monthly_revenue)
    for x in monthly_revenue
  ]
  return monthly_weight, pd.concat(monthly_sku_list)

def set_month_revenue_constraint(problem, uk, dm, sr_list, monthly_weight, monthly_sku_list):
  for month in range(1, 13):
    
    monthly_rev = pulp.lpSum([
      sr_list[x] * dm[x]['sku_price']
      for x in uk if dm[x]['month'] == month
    ])
    uk_list_list = []
    for _, row in monthly_sku_list[monthly_sku_list['month'] == month].iterrows():
      uk_list = [
        x for x in uk
        if dm[x]['bom_id'] == row['物料'] and dm[x]['month'] == month
      ]
      ref_record = row['history_sales']
      if ref_record >= 0:
        problem += max(math.ceil(ref_record * 0.5), 1) <= sum([sr_list[x] for x in uk_list]) <= max(math.ceil(ref_record * 1.5), 2) + 1
        uk_list_list.append(uk_list)
    # if month == 4:
    #   from pprint import pprint
    #   print(monthly_sku_list[monthly_sku_list['month'] == month])
    #   print(len(uk_list_list))
    #   print(uk_list_list)
    #   raise
    problem += monthly_rev >= (problem.objective * monthly_weight[month - 1] * 0.99)
  return problem

def set_monthly_constraint(problem, uk, dm, sr_list):
  monthly_weight, monthly_sku_list = calculate_monthly_weight()
  problem = set_month_revenue_constraint(problem, uk, dm, sr_list, monthly_weight, monthly_sku_list)
  return problem
  