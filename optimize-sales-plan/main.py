import pulp
import pandas as pd
import math
from const import dp_kit_sku_ids, ljq_kit_sku_ids
from load_data import load_data
from set_target import set_target
from split_to_month import set_monthly_constraint

def set_kit_constraint(problem, uk, dm, sr_list):
  # 套件约束
  # 大漂亮套件约束
  dp_sku_ids = dp_kit_sku_ids
  dp_sku_ids = [f'{x}_大漂亮药妆' for x in dp_sku_ids]
  for month in range(1, 13):
    first_sku_id = f'{dp_sku_ids[0]}_month_{month}'
    for id in dp_sku_ids[1:]:
      problem += sr_list[f'{id}_month_{month}'] == sr_list[first_sku_id]

  # 李佳琦套件约束
  ljq_sku_ids = ljq_kit_sku_ids
  ljq_sku_ids = [f'{x}_李佳琦直播间' for x in ljq_sku_ids]
  for month in range(1, 13):
    first_sku_id = f'{ljq_sku_ids[0]}_month_{month}'
    for id in ljq_sku_ids[1:]:
      problem += sr_list[f'{id}_month_{month}'] == sr_list[first_sku_id]

  return problem

def set_channel_new_sku_constraint(problem, uk, dm, sr_list, new_sku_revenue, min_new_sku_portion_by_channel):
  # 渠道新品推广要求
  # 天猫旗舰店新品占比不低于 20%
  tm_new_sku_portion = min_new_sku_portion_by_channel.get('天猫旗舰店', 0.2)
  tm_new_sku_ids = [x for x in uk if dm[x]['is_new'] == 'Y' and dm[x]['channel_id'] == '天猫旗舰店']
  tm_new_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in tm_new_sku_ids])
  problem += tm_new_sku_sales >= tm_new_sku_portion * new_sku_revenue 
  # 新天地旗舰店新品占比不低于 30%
  xtd_new_sku_portion = min_new_sku_portion_by_channel.get('上海新天地旗舰店', 0.3)
  xtd_new_sku_ids = [x for x in uk if dm[x]['is_new'] == 'Y' and dm[x]['channel_id'] == '上海新天地旗舰店']
  xtd_new_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in xtd_new_sku_ids])
  problem += xtd_new_sku_sales >= xtd_new_sku_portion * new_sku_revenue 
  # 大漂亮药妆新品占比不低于 5%
  dp_new_sku_portion = min_new_sku_portion_by_channel.get('大漂亮药妆', 0.05)
  dp_new_sku_ids = [x for x in uk if dm[x]['is_new'] == 'Y' and dm[x]['channel_id'] == '大漂亮药妆']
  dp_new_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in dp_new_sku_ids])
  problem += dp_new_sku_sales >= dp_new_sku_portion * new_sku_revenue
  # 李佳琦直播间新品占比不低于 30%
  ljq_new_sku_portion = min_new_sku_portion_by_channel.get('李佳琦直播间', 0.3)
  ljq_new_sku_ids = [x for x in uk if dm[x]['is_new'] == 'Y' and dm[x]['channel_id'] == '李佳琦直播间']
  ljq_new_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in ljq_new_sku_ids])
  problem += ljq_new_sku_sales >= ljq_new_sku_portion * new_sku_revenue
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

def set_new_sku_constraint(problem, uk, dm, sr_list, revenue):
  # 新品占比大于15%
  new_sku_ids = [x for x in uk if dm[x]['is_new'] == 'Y']
  new_sku_sales = pulp.lpSum([sr_list[id] * dm[id]['sku_price'] for id in new_sku_ids])
  problem += new_sku_sales >= revenue
  return problem, new_sku_ids

def set_history_sales_constraint(problem, uk, dm, sr_list, sku_map):
  # 历史销量约束
  for id in uk:
    same_sku_uk = [x for x in uk if dm[x]['bom_id'] == dm[id]['bom_id']]
    sku_total_sales = pulp.lpSum([sr_list[x] for x in same_sku_uk])
    sku_id = dm[id]['bom_id']
    upper_limit = sku_map[sku_id]['history_sales'] * 1.5
    lower_limit = sku_map[sku_id]['history_sales'] * 0.5
    problem += sku_total_sales <= math.ceil(upper_limit) + 1
    problem += sku_total_sales >= math.ceil(lower_limit)
  return problem

def linear_optimize(**kwargs):
  revenue_target = kwargs.get('revenue_target')
  new_sku_revenue = kwargs.get('new_sku_revenue', 10000000)
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
  problem, sr_list = set_target(uk, dm, revenue_target)
  # 设置约束，新品销售额
  problem, new_sku_ids = set_new_sku_constraint(problem, uk, dm, sr_list, revenue=new_sku_revenue)
  # 设置约束，根据SKU历史销量预估未来销量
  problem = set_hot_sku_constraint(problem, uk, dm, sr_list, portion=hot_sku_portion)
  # 设置约束，DTC占比
  problem = set_dtc_constraint(problem, uk, dm, sr_list, portion=dtc_sku_portion)
  # 设置约束，每月历史销量约束
  problem = set_monthly_constraint(problem, uk, dm, sr_list)
  # 设置约束，各渠道利润率约束
  problem = set_channel_min_profit_rate_constraint(problem, uk, dm, sr_list, min_profit_rate_by_channel)
  # 设置约束，各渠道新品销售额占比约束
  problem = set_channel_new_sku_constraint(problem, uk, dm, sr_list, new_sku_revenue, min_new_sku_portion_by_channel)
  # 设置约束，各渠道销售额约束
  problem = set_channel_revenue_constraint(problem, uk, dm, sr_list, min_revenue_by_channel)
  # 设置约束，套件销售
  problem = set_kit_constraint(problem, uk, dm, sr_list)
  solver = pulp.get_solver('PULP_CBC_CMD', timeLimit=600)
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
        'month': dm[id]['month'],
      })
    result_df = pd.DataFrame(result)
    print(result_df[result_df['qty'] > 0])
    # print('Total Revenue: ', pd.DataFrame(result)['合计'].sum())
    print(f"Total Revenue: {pulp.value(problem.objective)}")
    # print(f"Total Cost: {pulp.value(total_cost)}")
    # assert_new_portion(result)
    print(result_df.groupby('渠道')['销售额'].sum())

    for month in range(1, 13):
      total = sum([sr_list[x].value() * dm[x]['sku_price'] for x in uk])
      monthly = sum([sr_list[x].value() * dm[x]['sku_price'] for x in uk if dm[x]['month'] == month])
      print(f"Month {month} Revenue: {monthly}, Portion: {monthly / total}")
    return True, result, pulp.value(problem.objective)
  else:
    print("No optimal solution found.")
    print("Solver status:", problem.solver)
    print("Solver message:", pulp.LpSolverDefault.msg)
    return False, None, None

if __name__ == '__main__':
  linear_optimize()