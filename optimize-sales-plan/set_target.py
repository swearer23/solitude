import pulp

def set_target(uk, dm, revenue_target):
  # 创建问题
  problem = pulp.LpProblem("Maximize Sales Revenue", pulp.LpMaximize)

  # 创建变量，sr -> solver result
  # sr_list = pulp.LpVariable.dicts("SKU_Sales", uk, lowBound=0, cat='Integer')  # 每个SKU的销售数量}
  sr_list = pulp.LpVariable.dicts("SKU_Sales", uk, lowBound=0, cat='Continuous')  # 每个SKU的销售数量}
  # 设置目标函数
  problem += sum([
    sr_list[id] * dm[id]['sku_price']
    for id in uk
  ]), "Total Revenue"
  problem += problem.objective <= revenue_target
  return problem, sr_list