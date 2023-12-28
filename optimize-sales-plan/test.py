# import pulp

# # 创建问题
# problem = pulp.LpProblem("Maximize Production", pulp.LpMaximize)

# # 创建变量
# xa = pulp.LpVariable("Product_A", lowBound=0, cat='Continuous')
# xb = pulp.LpVariable("Product_B", lowBound=0, cat='Continuous')

# # 设置目标函数
# problem += xa * 2 + xb * 3

# # # 添加约束条件
# # total = xa + xb
# problem += xa == xb
# # problem += total * 0.3 <= xa
# # problem += xa <= total * 0.8
# # problem += total * 0.2 <= xb
# # problem += xb <= total * 0.5
# problem += 1 * xa + 2 * xb <= 8  # 生产时间限制
# problem += 2 * xa + 1 * xb <= 10  # 原材料 X 限制

# # 求解
# problem.solve()

# # 输出结果
# if pulp.LpStatus[problem.status] == 'Optimal':
#     print(f"Product A: {xa.value()}")
#     print(f"Product B: {xb.value()}")
#     print(f"Total Production: {pulp.value(problem.objective)}")
# else:
#     print("No optimal solution found.")
import pandas as pd
sku_list = pd.read_csv('data/annual.sku.csv')
sku_list['profit'] = sku_list['history_sales'] * sku_list['成本'] * (1 + sku_list['最低毛利要求'])
ret = sku_list[sku_list['history_sales'] != 0]
print(ret[['物料', 'history_sales', 'profit']])