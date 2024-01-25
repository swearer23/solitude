from models.demand import Demand

class Graph:
  def __init__(self, demand: Demand):
    self.demand = demand
    self.flatten_pb = []

  def expand(self):
    for prod in self.demand.production:
      for power_block in prod.process.power_line:
        self.flatten_pb.append(power_block)
    