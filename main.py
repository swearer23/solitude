import pulp
import pandas as pd

def set_kit_constraint(problem, sr_list):
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
  return problem

def set_channel_new_sku_constraint(problem, uk, dm, sr_list, new_sku_ids, min_new_sku_portion_by_channel):
  # 渠道新品推广要求
  total_new_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in new_sku_ids])
  # 天猫旗舰店新品占比不低于 20%
  tm_sku_ids = [x for x in uk if dm[x]['channel_id'] == '天猫旗舰店']
  tm_new_sku_ids = [x for x in tm_sku_ids if dm[x]['is_new'] == 'Y' and dm[x]['channel_id'] == '天猫旗舰店']
  tm_new_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in tm_new_sku_ids])
  problem += tm_new_sku_sales >= min_new_sku_portion_by_channel.get('天猫旗舰店', 0.2) * total_new_sku_sales
  # 新天地旗舰店新品占比不低于 30%
  xtd_sku_ids = [x for x in uk if dm[x]['channel_id'] == '上海新天地旗舰店']
  xtd_new_sku_ids = [x for x in xtd_sku_ids if dm[x]['is_new'] == 'Y' and dm[x]['channel_id'] == '上海新天地旗舰店']
  xtd_new_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in xtd_new_sku_ids])
  problem += xtd_new_sku_sales >= min_new_sku_portion_by_channel.get('上海新天地旗舰店', 0.3) * total_new_sku_sales 
  # 大漂亮药妆新品占比不低于 5%
  dp_sku_ids = [x for x in uk if dm[x]['channel_id'] == '大漂亮药妆']
  dp_new_sku_ids = [x for x in dp_sku_ids if dm[x]['is_new'] == 'Y' and dm[x]['channel_id'] == '大漂亮药妆']
  dp_new_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in dp_new_sku_ids])
  problem += dp_new_sku_sales >= min_new_sku_portion_by_channel.get('大漂亮药妆', 0.05) * total_new_sku_sales
  # 李佳琦直播间新品占比不低于 30%
  ljq_sku_ids = [x for x in uk if dm[x]['channel_id'] == '李佳琦直播间']
  ljq_new_sku_ids = [x for x in ljq_sku_ids if dm[x]['is_new'] == 'Y' and dm[x]['channel_id'] == '李佳琦直播间']
  ljq_new_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in ljq_new_sku_ids])
  problem += ljq_new_sku_sales >= min_new_sku_portion_by_channel.get('李佳琦直播间', 0.3) * total_new_sku_sales
  return problem

def set_channel_min_profit_rate_constraint(problem, uk, dm, sr_list, min_profit_rate_by_channel):
  # 渠道毛利率要求
  # 天猫旗舰店毛利率不低于 30%
  tm_sku_ids = [x for x in uk if dm[x]['channel_id'] == '天猫旗舰店']
  tm_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in tm_sku_ids])
  tm_sku_cost = pulp.lpSum([sr_list[id] * dm[id]['sku_cost'] for id in tm_sku_ids])
  problem += tm_sku_sales * min_profit_rate_by_channel.get('天猫旗舰店') <= (tm_sku_sales - tm_sku_cost)
  # # 新天地旗舰店毛利率不低于 25%
  xtd_sku_ids = [x for x in uk if dm[x]['channel_id'] == '上海新天地旗舰店']
  xtd_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in xtd_sku_ids])
  xtd_sku_cost = pulp.lpSum([sr_list[id] * dm[id]['sku_cost'] for id in xtd_sku_ids])
  problem += xtd_sku_sales * min_profit_rate_by_channel.get('上海新天地旗舰店') <= (xtd_sku_sales - xtd_sku_cost)
  # # 大漂亮药妆毛利率不低于 15%
  dp_sku_ids = [x for x in uk if dm[x]['channel_id'] == '大漂亮药妆']
  dp_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in dp_sku_ids])
  dp_sku_cost = pulp.lpSum([sr_list[id] * dm[id]['sku_cost'] for id in dp_sku_ids])
  problem += dp_sku_sales * min_profit_rate_by_channel.get('大漂亮药妆') <= (dp_sku_sales - dp_sku_cost)
  # # 李佳琦直播间毛利率不低于 20%
  ljq_sku_ids = [x for x in uk if dm[x]['channel_id'] == '李佳琦直播间']
  ljq_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in ljq_sku_ids])
  ljq_sku_cost = pulp.lpSum([sr_list[id] * dm[id]['sku_cost'] for id in ljq_sku_ids])
  problem += ljq_sku_sales * min_profit_rate_by_channel.get('李佳琦直播间') <= (ljq_sku_sales - ljq_sku_cost)
  return problem

def set_channel_revenue_constraint(problem, uk, dm, sr_list, min_revenue_by_channel):
  # 渠道销售额要求
  # 天猫旗舰店销售额不低于 500万
  tm_sku_ids = [x for x in uk if dm[x]['channel_id'] == '天猫旗舰店']
  tm_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in tm_sku_ids])
  problem += tm_sku_sales >= min_revenue_by_channel.get('天猫旗舰店', 3000000)
  # # 新天地旗舰店销售额不低于 300万
  xtd_sku_ids = [x for x in uk if dm[x]['channel_id'] == '上海新天地旗舰店']
  xtd_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in xtd_sku_ids])
  problem += xtd_sku_sales >= min_revenue_by_channel.get('上海新天地旗舰店', 2000000)
  # # 大漂亮药妆销售额不低于 100万
  dp_sku_ids = [x for x in uk if dm[x]['channel_id'] == '大漂亮药妆']
  dp_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in dp_sku_ids])
  problem += dp_sku_sales >= min_revenue_by_channel.get('大漂亮药妆', 1000000)
  # # 李佳琦直播间销售额不低于 400万
  ljq_sku_ids = [x for x in uk if dm[x]['channel_id'] == '李佳琦直播间']
  ljq_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in ljq_sku_ids])
  problem += ljq_sku_sales >= min_revenue_by_channel.get('李佳琦直播间', 2000000)
  return problem

def set_dtc_constraint(problem, uk, dm, sr_list, portion=0.6):
  # DTC 占比 60%
  dtc_sku_ids = [x for x in uk if 'DTC' in dm[x]['channel_type']]
  dtc_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in dtc_sku_ids])
  problem += dtc_sku_sales >= portion * pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in uk])
  return problem

def set_hot_sku_constraint(problem, uk, dm, sr_list, portion=0.1):
  # 爆款占比大于10%
  hot_sku_ids = [x for x in uk if dm[x]['is_hot'] == 'Y']
  hot_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in hot_sku_ids])
  problem += hot_sku_sales >= portion * pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in uk])
  return problem

def set_new_sku_constraint(problem, uk, dm, sr_list, portion=0.1):
  # 新品占比大于15%
  new_sku_ids = [x for x in uk if dm[x]['is_new'] == 'Y']
  new_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in new_sku_ids])
  problem += new_sku_sales >= portion * pulp.lpSum([
    sr_list[id] * dm[id]['sku_price']
    for id in uk 
  ])
  return problem, new_sku_ids

def set_storage_constraint(problem, uk, dm, sr_list, sku_map):
  for id in uk:
    same_sku_uk = [x for x in uk if dm[x]['bom_id'] == dm[id]['bom_id']]
    total_sales = pulp.lpSum([sr_list[x] for x in same_sku_uk])
    sku_id = dm[id]['bom_id']
    problem += total_sales <= sku_map[sku_id]['库存']
  return problem

def set_target(uk, dm):
  # 创建问题
  problem = pulp.LpProblem("Maximize Sales Revenue", pulp.LpMaximize)

  # 创建变量，sr -> solver result
  sr_list = pulp.LpVariable.dicts("SKU_Sales", uk, lowBound=0, cat='Integer')  # 每个SKU的销售数量}

  # 设置目标函数
  problem += sum([
    sr_list[id] * dm[id]['sku_price']
    for id in uk
  ]), "Total Revenue"
  return problem, sr_list

def load_data():
  sku_list = pd.read_csv('data/sku.csv')
  channel_list = pd.read_csv('data/channel.csv')
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
  return dm, uk, sku_map

def linear_optimize(**kwargs):
  new_sku_portion = kwargs.get('new_sku_portion', 0.15)
  hot_sku_portion = kwargs.get('hot_sku_portion', 0.1)
  dtc_sku_portion = kwargs.get('dtc_sku_portion', 0.6)
  min_profit_rate_by_channel = kwargs.get('min_profit_rate_by_channel', {
    '天猫旗舰店': 0.3,
    '上海新天地旗舰店': 0.25,
    '大漂亮药妆': 0.15,
    '李佳琦直播间': 0.2,
  })
  min_new_sku_portion_by_channel = kwargs.get('min_new_sku_portion_by_channel', {
    '天猫旗舰店': 0.2,
    '上海新天地旗舰店': 0.3,
    '大漂亮药妆': 0.05,
    '李佳琦直播间': 0.3,
  })
  min_revenue_by_channel = kwargs.get('min_revenue_by_channel', {
    '天猫旗舰店': 3000000,
    '上海新天地旗舰店': 2000000,
    '大漂亮药妆': 1000000,
    '李佳琦直播间': 2000000,
  })
  dm, uk, sku_map = load_data()
  problem, sr_list = set_target(uk, dm)
  problem = set_storage_constraint(problem, uk, dm, sr_list, sku_map)
  # 约束条件
  # 爆款占比大于10%
  problem, new_sku_ids = set_new_sku_constraint(problem, uk, dm, sr_list, portion=new_sku_portion)
  problem = set_hot_sku_constraint(problem, uk, dm, sr_list, portion=hot_sku_portion)
  problem = set_dtc_constraint(problem, uk, dm, sr_list, portion=dtc_sku_portion)
  problem = set_channel_min_profit_rate_constraint(problem, uk, dm, sr_list, min_profit_rate_by_channel)
  problem = set_channel_new_sku_constraint(problem, uk, dm, sr_list, new_sku_ids, min_new_sku_portion_by_channel)
  problem = set_channel_revenue_constraint(problem, uk, dm, sr_list, min_revenue_by_channel)
  problem = set_kit_constraint(problem, sr_list)
  solver = pulp.get_solver('PULP_CBC_CMD', timeLimit=5)
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
        '渠道类型': dm[id]['channel_type'],
        '成本': dm[id]['sku_cost'],
      })
    result_df = pd.DataFrame(result)
    print(result_df[result_df['qty'] > 0])
    # print('Total Revenue: ', pd.DataFrame(result)['合计'].sum())
    print(f"Total Revenue: {pulp.value(problem.objective)}")
    # print(f"Total Cost: {pulp.value(total_cost)}")
    # assert_new_portion(result)
    print(result_df.groupby('渠道')['销售额'].sum())
    return True, result, pulp.value(problem.objective)
  else:
    print("No optimal solution found.")
    return False, None, None

if __name__ == '__main__':
  linear_optimize()