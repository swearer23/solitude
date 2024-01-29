from pprint import pprint
import pandas as pd
from models.demand import Demand
from models.calendar import Calendar
from models.sheet import Sheet
from algo.montecarlo import optimize_electric_cost

calendar = Calendar()
demand = Demand()

processes = [{
  'id': x.batch_name,
  'process': x.process.get_power_line_num()
} for x in demand.production]

best = optimize_electric_cost(
  [x.price for x in calendar.slots],
  processes
)

# print(best[0], best[1], best[2])

cols = ['ProdID'] + [
  f'day_{i}_hour_{j}'
  for i in range(1, 32)
  for j in range(1, 25)
]

df = pd.DataFrame(
  best[2],
  columns=cols
)

df.to_csv('./localdata/elec_cost.csv')

# df = pd.read_csv('./localdata/elec_cost.csv')
# print(df)
sheet = Sheet(calendar)
sheet.fill_process(df)
sheet.df.to_excel('./localdata/elec_cost.xlsx')
# with open('./localdata/process.json', 'r') as f:
#   processes = json.load(f)

# for p in processes:
#   product = Product(
#     p['id'],
#     p['init_power'],
#     p['work_duration'],
#     p['steps']
#   )
#   print(product.tech_process.power_line)
#   print(product.tech_process.total_power)