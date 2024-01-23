import json
from models.calendar import Calendar
from models.product import Product

calendar = Calendar()

with open('./localdata/process.json', 'r') as f:
  processes = json.load(f)

for p in processes:
  product = Product(
    p['id'],
    p['init_power'],
    p['work_duration'],
    p['steps']
  )
  print(product)