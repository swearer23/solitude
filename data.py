import pandas as pd

def bom_sales_weight_monthly(sku_all, ref):
  ret = []
  group = ref.copy().groupby('month')
  for month, ref_monthly in group:
    sku = sku_all.copy()
    sales = []
    for bom_id in sku['物料'].values.tolist():
      ref_record = ref_monthly[
        (ref_monthly['物料'] == bom_id)
        &
        (ref_monthly['交易类型'] == '销售出库')
      ]
      if ref_record.empty:
        sales.append(0)
      else:
        sales.append(-ref_record['数量'].sum())
    sku['history_sales'] = sales
    sku['weight'] = sku['history_sales'] / sku['history_sales'].sum()
    sku['month'] = month
    sku = sku[sku['history_sales'] != 0]
    sku['物料'] = sku['物料'].apply(lambda x: x.strip()).astype(str)
    sku.to_csv(f'data/monthly.sku.{month}.csv', index=False, encoding='utf-8-sig')
    ret.append(sku)
  return pd.concat(ret)

def bom_sales_weight_anually(sku, ref):
  sku = sku.copy()
  sales = []

  for bom_id in sku['物料'].values.tolist():
    sales2021 = ref[
      (ref['物料'] == bom_id)
      &
      (ref['交易类型'] == '销售出库')
    ]['数量'].sum()
    sales.append(-sales2021)

  # sku['物料'] = sku['物料'].apply(lambda x: x.strip()).astype(str)
  sku['history_sales'] = sales
  sku['weight'] = sku['history_sales'] / sku['history_sales'].sum()
  sku.to_csv('data/annual.sku.csv', index=False, encoding='utf-8-sig')
  return sku

def almost_equal(a, b):
  return abs(a - b) < 1e-6

# channel = pd.read_excel('raw_docs/md.xlsx', sheet_name='渠道信息')
sku = pd.read_excel('raw_docs/md.xlsx', sheet_name='物料基本信息')
# sku['物料'] = sku['物料'].astype(str)
# sku['物料'] = sku['物料'].apply(lambda x: x.replace('00000000', ''))
sku.index = sku['物料']

ref = pd.read_excel('raw_docs/2020.xlsx')
ref.columns = [x.strip() for x in ref.columns]
ref['dt'] = pd.to_datetime(ref['输入日期'])
ref['month'] = ref['dt'].dt.month

annually = bom_sales_weight_anually(sku, ref)
all_month = bom_sales_weight_monthly(sku, ref)
for bom_id in sku['物料'].values.tolist():
  annually_record = annually[annually['物料'] == bom_id]
  all_month_record = all_month[all_month['物料'] == bom_id]
  try:
    assert almost_equal(annually_record['history_sales'].values[0], all_month_record['history_sales'].sum())
  except:
    print(bom_id)
    print(annually_record['history_sales'].values[0])
    print(all_month_record['history_sales'].sum())
    print('===========================')
    raise