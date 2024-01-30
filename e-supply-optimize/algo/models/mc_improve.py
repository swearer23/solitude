import pandas as pd
from algo.models.mc_mat import LEAP_PUNISHMENT

class MonteCarloImprove:
  def __init__(self, df: pd.DataFrame, hourly_prices: list) -> None:
    self.df = df
    self.hourly_prices = hourly_prices

  def find_improvement_chances(self):

    for y_idx, row in self.df.iterrows():
      for x_idx, cell in enumerate(row[1:]):
        print(x_idx, self.hourly_prices[x_idx], cell)
      # for idx, cell in enumerate(row[1:]):
      #   if self.hourly_prices[idx - 1] in [2, 3] and int(cell) > 0:
      #     print(self.hourly_prices[idx - 1], cell)

  def __track_left(self, y_idx, x_idx):
    df = self.df.copy()
    far_left = x_idx
    while self.hourly_prices[far_left] <= self.hourly_prices[x_idx] and df.iloc[y_idx, far_left] == 0:
      # 找到为空的最左端单元格
      far_left -= 1
    if far_left < x_idx:
      # 从最左端开始，尝试将当前值与左端单元格交换，如果更优则替换当前df
      pass

  def __track_reverse(self, y_idx, far_left):
    pass

  def __move_right(self):
    pass