class TechStep:
  def __init__(self, step) -> None:
    self.target_power = step['target_power']
    self.duration = step['duration']

class Product:
  def __init__(
      self,
      id,
      init_power: float,
      work_duration: float,
      steps: list
    ):
    self.id = id
    self.init_power = init_power
    self.work_duration = work_duration
    self.step_count = len(steps)
    self.steps = [TechStep(x) for x in steps]
    