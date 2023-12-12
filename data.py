import random
import pandas as pd

def gen_sku(amount):
  skus = []
  for i in range(amount):
    cost_seed = random.randint(1, 9)
    cost = random.randint(1, 100) * cost_seed
    profit_rate = random.random() + 1
    storage = random.randint(100, 1000)
    skus.append({
      'sku_id': i,
      'sku_name': 'sku_name_' + str(i),
      'sku_cost': cost,
      'sku_price': cost * profit_rate,
      'sku_profit_rate': profit_rate,
      'sku_profit': cost * profit_rate - cost,
      'sku_storage': storage
    })
  df = pd.DataFrame(skus)
  df.to_csv('data/sku.csv', index=False)
  return df

if __name__ == '__main__':
  df = gen_sku(1000)
  print(df)