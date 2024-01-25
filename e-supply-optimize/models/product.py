import shortuuid
from models.process import TechProcess

class Product:
  def __init__(
      self,
      pid
    ):
    self.batch_id = shortuuid.uuid()
    self.process = TechProcess.from_id(pid, self.batch_id)
    self.batch_name = f'{self.batch_id}_{self.process.id}'
