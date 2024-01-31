import numpy as np
from scipy.optimize import linprog
from models.process import TechProcess

process = TechProcess.from_id(1, 1)
process = [pb.power for pb in process.power_line]

# 生产计划
output_count = 50

# 假设参数
M = 10  # 反应炉数量
K = 1  # 工艺种类数量
Q = 69000 # 电费限制

# 假设的电费单价和工艺耗电量
c = np.random.rand(744, M)  # 744小时，M个反应炉的电费单价
d = np.random.rand(K)  # 工艺种类数量

# 电价分段
p = np.array([1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 2, 2, 2, 3, 3, 3, 3, 2, 2, 2, 2, 1, 1] * 31)

# 定义目标函数的系数
c_flat = c.flatten()

# 定义约束矩阵
A_eq = np.zeros((len(p), M))
for j in range(M):
    for k in range(K):
        for i in range(len(p)):
            for p in process:
                A_eq[j, i] = p

# 定义等式右侧
b_eq = np.ones(M * K) * 8

# 定义电费约束
A_ub = np.zeros((744, 744 * M))
for i in range(744):
    for j in range(M):
        for k in range(K):
            A_ub[i, i * M + j + K * 744] = c[i, j]

# 定义电费上限
b_ub = np.ones(744) * Q

# 定义变量的上下界
x_bounds = [(0, None)] * (744 * M)

# 使用线性规划求解器
result = linprog(p, A_eq=A_eq, b_eq=b_eq, A_ub=A_ub, b_ub=b_ub, bounds=x_bounds, method='highs')

# 输出结果
x_optimal = result.x.reshape((744, M))
print("Optimal schedule:\n", x_optimal)
print("Optimal cost:", result.fun)
