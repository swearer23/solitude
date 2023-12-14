import pandas as pd

sku = pd.read_excel('raw_docs/md.xlsx', sheet_name='物料基本信息')
sku.index = sku['物料']

data2020 = pd.read_excel('raw_docs/2020.xlsx')
data2020.columns = [x.strip() for x in data2020.columns]
data2021 = pd.read_excel('raw_docs/2021.xlsx')
data2021.columns = [x.strip() for x in data2021.columns]

sales = []

for bom_id in sku['物料'].values.tolist():
  sales2020 = data2020[
    (data2020['物料'] == bom_id)
    &
    (data2020['交易类型'] == '销售出库')
  ]['数量'].sum()
  sales2021 = data2021[
    (data2021['物料'] == bom_id)
    &
    (data2021['交易类型'] == '销售出库')
  ]['数量'].sum()
  sales.append(-(sales2020 + sales2021))
  
sku['history_sales'] = sales 
sku['weight'] = sku['history_sales'] / sku['history_sales'].sum()

sku.to_csv('data/sku.csv', index=False, encoding='utf-8-sig')