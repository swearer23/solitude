import pulp
from models.process import PowerBlock
from models.calendar import Calendar

class Resolvor:
  def __init__(self, calendar: Calendar, power_blocks: list[PowerBlock]) -> None:
    self.calendar = calendar
    self.power_blocks = power_blocks
    self.problem = None
    self.pb_index_list = None
    self.__set_target()
    self.__set_constraints()

  def __set_target(self):
    self.problem = pulp.LpProblem("Minimize_Electric_Cost", pulp.LpMinimize)
    # 创建变量，sr -> solver result
    self.pb_cal_slots = pulp.LpVariable.dicts("pb_slot_index", [
      (pb, slot)
      for pb in self.power_blocks
      for slot in self.calendar.slots
    ], lowBound=0, cat='Binary')  # 每个power block 所在的calendar slot index

    # 设置目标函数
    self.problem += pulp.lpSum([
      key[0].power * key[1].price
      for key, value in self.pb_cal_slots.items() if value.value() == 1.0
    ]), "Total_Cost"

  def __set_constraints(self):
    demand_total_power = sum([x.power for x in self.power_blocks])
    print(demand_total_power)
    output_total_power = pulp.lpSum([
      key[0].power
      for key, value in self.pb_cal_slots.items() if value.value() == 1.0
    ])
    self.problem += output_total_power >= demand_total_power, "Total_Power_Constraint"

  def run(self):
    solver = pulp.get_solver('PULP_CBC_CMD', timeLimit=600)
    self.problem.solve(solver=solver)
    if pulp.LpStatus[self.problem.status] == 'Optimal':
      print("Optimal solution found.")
      print(f"Total Power Cost: {pulp.value(self.problem.objective)}")
      # for key, value in self.pb_cal_slots.items():
      #   if value is not None:
      #     print(value)
    else:
      print("No optimal solution found.")
      print("Solver status:", self.problem.solver)
      print("Solver message:", pulp.LpSolverDefault.msg)
      return False, None, None
