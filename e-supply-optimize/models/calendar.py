from models.eprice import PriceType

PEAK_HOURS = [11, 12, 16, 17, 18, 19, 20, 22]
NORMAL_HOURS = [9, 10, 13, 14, 15, 21, 23, 0]
TROUGH_HOURS = [1, 2, 3, 4, 5, 6, 7, 8]

class Calendar:
  def __init__(self) -> None:
    self.slots = self.__gen_slots()

  def __gen_slots(self):
    slots = []
    for day in range(1, 30):
      for hour in range(0, 24):
        slots.append({
          'day': day,
          'hour': hour,
          'price_type': self.__calculate_price_type(hour)
        })
    return slots

  def __calculate_price_type(self, hour):
    if hour in PEAK_HOURS:
      return PriceType.PEAK
    elif hour in NORMAL_HOURS:
      return PriceType.NORMAL
    elif hour in TROUGH_HOURS:
      return PriceType.TROUGH
  