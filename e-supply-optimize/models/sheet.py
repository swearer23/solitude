import pandas as pd
from models.calendar import Calendar, PEAK_HOURS, NORMAL_HOURS, TROUGH_HOURS
from models.eprice import PriceType

class Sheet:
  def __init__(self, calendar: Calendar) -> None:
    self.calendar = calendar
    self.df = self.__make_calendar()

  def __make_calendar(self):
    df = pd.DataFrame(columns=['day' ,'proc_id'] + list(range(1, 25)))

    df.loc[0] = [None, 'Price'] + [self.__get_price_type(x) for x in range(1, 25)]
    df.set_index(['day', 'proc_id'], inplace=True)
    return df
  
  def __get_price_type(self, hour):
    if hour in PEAK_HOURS:
      return PriceType.PEAK.value
    elif hour in NORMAL_HOURS:
      return PriceType.NORMAL.value
    elif hour in TROUGH_HOURS:
      return PriceType.TROUGH.value
    
  def fill_process(self, df: pd.DataFrame):
    if 'Unnamed: 0' in df.columns:
      df = df.drop(columns=['Unnamed: 0'])
    df = df.set_index('ProdID')
    for col in df.columns[1:]:
      for index, cell in df[col].items():
        if cell > 1:
          day = int(col.split('_')[1])
          hour = int(col.split('_')[3])
          self.fill_cell(index, day, hour, cell)
    print(self.df)
          
  def fill_cell(self, proc_id, day, hour, value):
    self.df.loc[(day, proc_id), hour] = value
    