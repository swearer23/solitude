import json
from models.product import Product

class Demand:
  def __init__(self) -> None:
    self.production: list[Product] = []
    with open('./localdata/demand.json', 'r') as f:
      demand = json.load(f)
      for d in demand:
        for _ in range(d['amount']):
          self.production.append(Product(
            d['pid'],
          ))
