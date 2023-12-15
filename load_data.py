import pandas as pd
from const import dp_kit_sku_ids, ljq_kit_sku_ids
def load_data():
  sku_list = pd.read_csv('data/annual.sku.csv')
  channel_list = pd.read_csv('data/channel.csv')
  data = []

  def is_channel_online(channel_type):
    return '线上' in channel_type

  for month in range(1, 13):
    for index, channel_row in channel_list.iterrows():
      for index, sku_row in sku_list.iterrows():
        if not is_channel_online(channel_row['渠道大类']) and sku_row['是否仅线上销售'] == 'Y':
          continue
        if channel_row['渠道名称'] == '大漂亮药妆' and sku_row['物料'] not in dp_kit_sku_ids:
          continue
        if channel_row['渠道名称'] == '李佳琦直播间' and sku_row['物料'] not in ljq_kit_sku_ids:
          continue
        data.append({
          'unique_id': f"{sku_row['物料']}_{channel_row['渠道名称']}_month_{month}",
          'bom_id': sku_row['物料'],
          'channel_id': channel_row['渠道名称'],
          'month': month,
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