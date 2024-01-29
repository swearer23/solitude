import json

class PowerBlock:
  def __init__(self, order, power, **kwargs):
    self.order = order
    self.power = int(power)
    self.process_ukey = kwargs['ukey']
    self.ukey = f'{kwargs["ukey"]}_{self.order}'

class PowerTarget:
  def __init__(self, **kwargs) -> None:
    self.target_power = kwargs['target_power']
    self.duration = kwargs['duration']
    self.order = kwargs['order']

class TechProcess:
  def __init__(
      self,
      id,
      batch_id,
      init_power: float,
      work_duration: float,
      steps: list
    ) -> None:
    self.id = id
    self.batch_id = batch_id
    self.init_power = init_power
    self.work_duration = work_duration
    self.step_count = len(steps)
    self.ukey = f'{self.batch_id}_{self.id}'
    self.steps = [PowerTarget(order=idx, **s) for idx, s in enumerate(steps)]
    self.power_line = self.__gen_power_line()
    self.total_power = self.__calc_total_power()

  @staticmethod
  def from_id(id, product_uid):
    with open('./localdata/process.json', 'r') as f:
      for p in json.load(f):
        if p['id'] == id:
          return TechProcess(
            id,
            product_uid,
            p['init_power'],
            p['work_duration'],
            p['steps']
          )
    return None

  def __gen_power_line(self):
    cost_line = [self.init_power]
    for step in self.steps:
      diff = step.target_power - cost_line[-1]
      hourly_step = diff / step.duration
      for _ in range(int(step.duration)):
        cost_line.append(cost_line[-1] + hourly_step)
    for _ in range(int(self.work_duration)):
      cost_line.append(cost_line[-1])
    return [
      PowerBlock(order=idx, power=p, ukey=self.ukey) for idx, p in
      enumerate(cost_line)
    ]
  
  def __calc_total_power(self):
    return sum([x.power for x in self.power_line])
  
  def get_power_line_num(self):
    return [x.power for x in self.power_line]
