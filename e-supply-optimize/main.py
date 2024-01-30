from pprint import pprint
import pandas as pd
from models.demand import Demand
from models.calendar import Calendar
from models.sheet import Sheet
from algo.montecarlo import optimize_electric_cost, optimize_electic_cost_single
from algo.models.mc_improve import MonteCarloImprove

calendar = Calendar()
demand = Demand()

processes = [{
  'id': x.batch_name,
  'process': x.process.get_power_line_num()
} for x in demand.production]

hourly_prices = [x.price for x in calendar.slots]

best = optimize_electric_cost(
  hourly_prices,
  processes
)

# TODO: delete this, just for test
# best = optimize_electic_cost_single(hourly_prices, processes)

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
print(df)
df.to_csv('./localdata/elec_cost.csv')

# df = pd.read_csv('./localdata/elec_cost.csv')
# df = df.drop(columns=['Unnamed: 0'])
# mci = MonteCarloImprove(df, [x.price for x in calendar.slots])
# mci.find_improvement_chances()
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