from models.eprice import PriceType

PEAK_HOURS = [11, 12, 16, 17, 18, 19, 20, 22]
NORMAL_HOURS = [9, 10, 13, 14, 15, 21, 23, 24]
TROUGH_HOURS = [1, 2, 3, 4, 5, 6, 7, 8]

class CalendarSlot:
  def __init__(self, day, hour, price):
    self.day = day
    self.hour = hour
    self.price = price

  def __str__(self) -> str:
    return f'{self.day} {self.hour} {self.price}'

class Calendar:
  def __init__(self) -> None:
    self.slots: list[CalendarSlot] = self.__gen_slots()

  def __gen_slots(self):
    slots = []
    for day in range(1, 32):
      for hour in range(1, 25):
        slots.append(
          CalendarSlot(
            day,
            hour,
            self.__calculate_price_type(hour)
          )
        )
    return slots

  def __calculate_price_type(self, hour):
    if hour in PEAK_HOURS:
      return PriceType.PEAK.value
    elif hour in NORMAL_HOURS:
      return PriceType.NORMAL.value
    elif hour in TROUGH_HOURS:
      return PriceType.TROUGH.value
  