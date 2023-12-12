import random
import pulp
import pandas as pd

"""
问题描述：
分渠道SKU的销售利润最大化
目标：
分渠道SKU的销售利润最大化，因此操作数据的最细粒度是SKU-Channel
约束条件：
"""

# channel = pd.read_excel('raw_docs/md.xlsx', sheet_name='渠道信息')
# channel.to_csv('data/channel.csv', index=False)
# print(channel)
# exit()
# sku_list['库存'] = [random.randint(100, 1000) for i in range(len(sku_list))]
# sku_list['sku_price'] = sku_list['成本'] * (1 + sku_list['最低毛利要求'])
# sku_list.to_csv('data/sku.csv', index=False)
# exit()

sku_list = pd.read_csv('data/sku.csv')
channel_list = pd.read_csv('data/channel.csv')

# 映射SKU到Channel

data = []

def is_channel_online(channel_type):
  return '线上' in channel_type

for index, channel_row in channel_list.iterrows():
  for index, sku_row in sku_list.iterrows():
    if not is_channel_online(channel_row['渠道大类']) and sku_row['是否仅线上销售'] == 'Y':
      continue
    data.append({
      'unique_id': f"{sku_row['物料']}_{channel_row['渠道名称']}",
      'bom_id': sku_row['物料'],
      'channel_id': channel_row['渠道名称'],
      'channel_type': channel_row['渠道大类'],
      'sku_cost': sku_row['成本'],
      'sku_price': sku_row['成本'] * (1 + sku_row['最低毛利要求']),
      'is_new': sku_row['是否新品'],
      'is_hot': sku_row['是否爆款'],
    })

df = pd.DataFrame(data)

# 将SKU List转为字典，方便后续使用 
sku_map = sku_list.set_index('物料').to_dict(orient='index')
# sku_ids = sku_list['物料'].tolist()

# 将SKU-Channel List转为字典，方便后续使用
dm = df.set_index('unique_id').to_dict(orient='index')
uk = df['unique_id'].tolist()

# 创建问题
problem = pulp.LpProblem("Maximize Sales Revenue", pulp.LpMaximize)

# 创建变量，sr -> solver result
sr_list = pulp.LpVariable.dicts("SKU_Sales", uk, lowBound=0, cat='Integer')  # 每个SKU的销售数量}

# 设置目标函数
problem += sum([
  sr_list[id] * dm[id]['sku_price']
  for id in uk
]), "Total Revenue"

# 新品占比大于15%
new_sku_ids = [x for x in uk if dm[x]['is_new'] == 'Y']
new_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in new_sku_ids])
problem += new_sku_sales >= 0.1 * pulp.lpSum([
  sr_list[id] * dm[id]['sku_price']
  for id in uk 
])

# 爆款占比大于10%
hot_sku_ids = [x for x in uk if dm[x]['is_hot'] == 'Y']
hot_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in hot_sku_ids])
problem += hot_sku_sales >= 0.1 * pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in uk])

# DTC 占比 60%
dtc_sku_ids = [x for x in uk if 'DTC' in dm[x]['channel_type']]
dtc_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in dtc_sku_ids])
problem += dtc_sku_sales >= 0.6 * pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in uk])

# 渠道毛利率要求
# 天猫旗舰店毛利率不低于 30%
tm_sku_ids = [x for x in uk if dm[x]['channel_id'] == '天猫旗舰店']
tm_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in tm_sku_ids])
tm_sku_cost = pulp.lpSum([sr_list[id] * dm[id]['sku_cost'] for id in tm_sku_ids])
problem += tm_sku_cost * 0.30 <= (tm_sku_sales - tm_sku_cost)
# # 新天地旗舰店毛利率不低于 25%
xtd_sku_ids = [x for x in uk if dm[x]['channel_id'] == '上海新天地旗舰店']
xtd_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in xtd_sku_ids])
xtd_sku_cost = pulp.lpSum([sr_list[id] * dm[id]['sku_cost'] for id in xtd_sku_ids])
problem += xtd_sku_cost * 0.25 <= (xtd_sku_sales - xtd_sku_cost)
# # 大漂亮药妆毛利率不低于 15%
dp_sku_ids = [x for x in uk if dm[x]['channel_id'] == '大漂亮药妆']
dp_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in dp_sku_ids])
dp_sku_cost = pulp.lpSum([sr_list[id] * dm[id]['sku_cost'] for id in dp_sku_ids])
problem += dp_sku_cost * 0.15 <= (dp_sku_sales - dp_sku_cost)
# # 李佳琦直播间毛利率不低于 20%
ljq_sku_ids = [x for x in uk if dm[x]['channel_id'] == '李佳琦直播间']
ljq_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in ljq_sku_ids])
ljq_sku_cost = pulp.lpSum([sr_list[id] * dm[id]['sku_cost'] for id in ljq_sku_ids])
problem += ljq_sku_cost * 0.2 <= (ljq_sku_sales - ljq_sku_cost)

# 渠道业绩要求
# 天猫旗舰店销售额不低于 500万
problem += tm_sku_sales >= 3000000
# 新天地旗舰店销售额不低于 300万
problem += xtd_sku_sales >= 2000000
# 大漂亮药妆销售额不低于 100万
problem += dp_sku_sales >= 1000000
# 李佳琦直播间销售额不低于 400万
problem += ljq_sku_sales >= 2000000

# 渠道新品推广要求
total_new_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in new_sku_ids])
# 天猫旗舰店新品占比不低于 20%
tm_new_sku_ids = [x for x in tm_sku_ids if dm[x]['is_new'] == 'Y' and dm[x]['channel_id'] == '天猫旗舰店']
tm_new_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in tm_new_sku_ids])
problem += tm_new_sku_sales >= 0.2 * total_new_sku_sales
# 新天地旗舰店新品占比不低于 30%
xtd_new_sku_ids = [x for x in xtd_sku_ids if dm[x]['is_new'] == 'Y' and dm[x]['channel_id'] == '上海新天地旗舰店']
xtd_new_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in xtd_new_sku_ids])
problem += xtd_new_sku_sales >= 0.3 * total_new_sku_sales 
# 大漂亮药妆新品占比不低于 5%
dp_new_sku_ids = [x for x in dp_sku_ids if dm[x]['is_new'] == 'Y' and dm[x]['channel_id'] == '大漂亮药妆']
dp_new_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in dp_new_sku_ids])
problem += dp_new_sku_sales >= 0.05 * total_new_sku_sales
# 李佳琦直播间新品占比不低于 30%
ljq_new_sku_ids = [x for x in ljq_sku_ids if dm[x]['is_new'] == 'Y' and dm[x]['channel_id'] == '李佳琦直播间']
ljq_new_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in ljq_new_sku_ids])
problem += ljq_new_sku_sales >= 0.3 * total_new_sku_sales 

# 套件约束
# 大漂亮套件约束
dp_kit_sku_ids = [
  '000000003103900055',
  '1006A02010',
  '1302A00034',
  '3105A11293',
  '3105A13024',
  '3105A16253'
]
dp_kit_sku_ids = [f'{x}_大漂亮药妆' for x in dp_kit_sku_ids]
first_sku_id = dp_kit_sku_ids[0]
for id in dp_kit_sku_ids[1:]:
  problem += sr_list[id] == sr_list[first_sku_id]

# 李佳琦套件约束
ljq_kit_sku_ids = [
  '3808A10534',
  '3808A11359',
  '3808A11369',
  '3808A11878'
]
ljq_kit_sku_ids = [f'{x}_李佳琦直播间' for x in ljq_kit_sku_ids]
first_sku_id = ljq_kit_sku_ids[0]
for id in ljq_kit_sku_ids[1:]:
  problem += sr_list[id] == sr_list[first_sku_id]


# 添加约束条件
# problem += pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in uk]) >= 6000000 # 总销售额达到1亿
# 其他可能的约束条件，比如每个SKU的最小/最大销售数量等
# total_cost = pulp.lpSum([df['sku_cost'][i] * sku_sales[i] for i in skus])
# problem += total_cost  # 成本作为约束条件

# problem += pulp.LpConstraint(
#     e=pulp.lpSum([sku_sales[i] * sku_list['sku_profit'][i] for i in sku_list]),
#     sense=pulp.LpConstraintGE,
#     rhs=80000,
#     name='Minimum Profit'
# )  # 利润达到2千万

# 添加约束条件，每个sku的销售数量小于等于各自的库存

def assert_new_portion(df):
  df = df.copy()
  new_sku_ids = [x for x in uk if dm[x]['is_new'] == 'Y']
  df['new_sales'] = df[df['id'].isin(new_sku_ids)]['qty'] * df[df['id'].isin(new_sku_ids)]['定价']
  # print(df[df['id'].isin(new_sku_ids)][['id', 'is_new', 'new_sales']])
  df['sku_id'] = df['id'].apply(lambda x: x.split('_')[0])
  # print(df[df['id'].isin(new_sku_ids)].groupby('sku_id')['qty'].sum())
  new_sku_sales = df[df['id'].isin(new_sku_ids)].groupby('sku_id')['qty'].sum()
  for row in new_sku_sales.items():
    sku_id, qty = row
    print(sku_id, qty, sku_map[sku_id]['库存'])
    assert qty <= sku_map[sku_id]['库存']

for id in uk:
  same_sku_uk = [x for x in uk if dm[x]['bom_id'] == dm[id]['bom_id']]
  total_sales = pulp.lpSum([sr_list[x] for x in same_sku_uk])
  sku_id = dm[id]['bom_id']
  problem += total_sales <= sku_map[sku_id]['库存']

# 求解
# solver_list = pulp.listSolvers(onlyAvailable=True)
# print(solver_list)
# exit()
solver = pulp.get_solver('PULP_CBC_CMD', timeLimit=60)
problem.solve(solver=solver)

# 输出结果
if pulp.LpStatus[problem.status] == 'Optimal':
  result = []
  for id in uk:
    result.append({
      'id': id,
      "qty": sr_list[id].value(),
      'is_new': dm[id]['is_new'],
      '是否爆款': dm[id]['is_hot'],
      '定价': dm[id]['sku_price'],
      '销售额': sr_list[id].value() * dm[id]['sku_price'],
      '渠道': dm[id]['channel_id'],
    })
  result = pd.DataFrame(result)
  print(result[result['qty'] > 0])
  # print('Total Revenue: ', pd.DataFrame(result)['合计'].sum())
  print(f"Total Revenue: {pulp.value(problem.objective)}")
  # print(f"Total Cost: {pulp.value(total_cost)}")
  # assert_new_portion(result)
  print(result.groupby('渠道')['销售额'].sum())
else:
  print("No optimal solution found.")
