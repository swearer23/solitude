import pulp

# 创建问题
problem = pulp.LpProblem("Maximize Production", pulp.LpMaximize)

# 创建变量
xa = pulp.LpVariable("Product_A", lowBound=0, cat='Continuous')
xb = pulp.LpVariable("Product_B", lowBound=0, cat='Continuous')

# 设置目标函数
problem += xa * 2 + xb * 3

# 添加约束条件
problem += 1 * xa + 2 * xb <= 8  # 生产时间限制
problem += 2 * xa + 1 * xb <= 10  # 原材料 X 限制

# 求解
problem.solve()

# 输出结果
if pulp.LpStatus[problem.status] == 'Optimal':
    print(f"Product A: {xa.value()}")
    print(f"Product B: {xb.value()}")
    print(f"Total Production: {pulp.value(problem.objective)}")
else:
    print("No optimal solution found.")