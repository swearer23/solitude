from random import randint
from time import sleep
import pandas as pd
import numpy as np
from models.eprice import PriceType

PEAK_LIMIT = 69000
GAP_LIMIT = 5
REVERT_TIME_LIMIT = 1000

class MonteCarloMatrix:
  def __init__(self, hourly_prices, processes):
    self.hourly_prices = hourly_prices
    self.processes = [p.get('process') for p in processes]
    self.pp_index = 0
    self.matrix_index = [0, 0]
    self.matrix = np.array([[0] * len(self.hourly_prices)])
    self.process_id = [x.get('id') for x in processes]
    self.resolved = False
    self.reverting = (None, 0,)

  def next(self):
    if self.__gap_too_long():
      self.__revert_cur_line()
    if self.__within_peak_limit() and self.__montecarlo():
      self.__fill()
    self.__move_to_next()
    if self.__is_process_done():
      if self.__all_done():
        self.resolved = True
        return False
      else:
        self.__reset_revert()
        self.__append_new_line()
    if self.__out_of_range():
      self.__clear_line()
      self.pp_index = 0
      self.matrix_index[1] = 0
    if self.reverting[1] > REVERT_TIME_LIMIT:
      return False
    return True
  
  def get_result(self):
    return np.hstack((
      np.array(self.process_id).reshape(-1, 1),
      self.matrix
    ))

  def __all_done(self):
    # print(self.matrix_index[0], len(self.processes))
    return self.matrix_index[0] >= len(self.processes) - 1
  
  def __is_process_done(self):
    # print(self.pp_index, len(self.processes[self.matrix_index[0]]))
    return self.pp_index >= len(self.processes[self.matrix_index[0]])
  
  def __gap_too_long(self):
    filled_index = self.matrix[self.matrix_index[0], :].nonzero()[-1]
    if len(filled_index) == 0:
      return False
    gap = self.matrix_index[1] - filled_index[-1]
    if gap > GAP_LIMIT:
      # print(self.matrix[self.matrix_index[0], :])
      # print('gap too long', gap, self.matrix_index[1], filled_index[-1])
      return True
    return False
  
  def __revert_cur_line(self):
    times = self.reverting[1]
    self.reverting = (self.process_id[self.matrix_index[0]], times + 1)
    cur_line_head = self.matrix[self.matrix_index[0], :].nonzero()[0][0]
    # print(cur_line_head)
    self.matrix_index[1] = cur_line_head + 1
    self.pp_index = 0
    self.matrix[self.matrix_index[0], :] = np.array([0] * len(self.hourly_prices))

  def __reset_revert(self):
    self.reverting = (None, 0,)
  
  def __out_of_range(self):
    return self.matrix_index[1] >= len(self.hourly_prices)
  
  def __clear_line(self):
    self.matrix[self.matrix_index[0], :] = np.array([0] * len(self.hourly_prices))

  def __move_to_next(self):
    self.matrix_index[1] += 1
  
  def __append_new_line(self):
    self.matrix = np.vstack([
      self.matrix,
      np.array([[0] * len(self.hourly_prices)])
    ])
    self.pp_index = 0
    self.matrix_index[0] += 1
  
  def __within_peak_limit(self):
    cur_power = self.processes[self.matrix_index[0]][self.pp_index]
    return sum(self.matrix[:, self.matrix_index[1]]) + cur_power < PEAK_LIMIT
  
  def __montecarlo(self):
    # print(self.matrix)
    cur_cell = self.matrix[self.matrix_index[0], self.matrix_index[1]]
    cur_cell_price_type = self.hourly_prices[self.matrix_index[1]]
    fill_or_not = False
    # print(cur_cell)
    if cur_cell == 0:
      if cur_cell_price_type == PriceType.TROUGH.value:# and self.__yes_or_no_prob(base=1):
        fill_or_not = True
      elif cur_cell_price_type == PriceType.NORMAL.value:# and self.__yes_or_no_prob(base=2):
        fill_or_not = True
      elif cur_cell_price_type == PriceType.PEAK.value and self.__yes_or_no_prob(base=3):
        fill_or_not = True
    return fill_or_not
  
  def __fill(self):
    self.matrix[self.matrix_index[0], self.matrix_index[1]] = self.processes[self.matrix_index[0]][self.pp_index]
    self.pp_index += 1
  
  def __yes_or_no_prob(self, base=1):
    return randint(0, base) == base
  
  def calculate_electric_cost(self):
    return sum([
      self.matrix[j][i] * self.hourly_prices[i]
      for i in range(len(self.hourly_prices))
      for j in range(len(self.matrix))
      if self.matrix[j][i] > 0
    ])
  
  def calculate_peak_power(self):
    return max([
      sum([
        self.matrix[j][i]
        for j in range(len(self.matrix))
        if self.matrix[j][i] > 0
      ])
      for i in range(len(self.hourly_prices))
    ])
  
  def constrain_power_demand(self):
    deployed_power = np.sum(self.matrix[self.matrix > 0])
    planned_power = sum([
      sum([
        self.processes[i][j]
        for j in range(len(self.processes[i]))
      ])
      for i in range(len(self.processes))
    ])
    for i in range(len(self.matrix)):
      if sum([x for x in self.matrix[i, :] if x > 0]) != sum(self.processes[i]):
        print(f'line {i} ========================== {self.process_id[i]}')
        print(sum(self.matrix[i, :]))
        print(sum(self.processes[i]))
        print(self.matrix[i, :])
        print(self.processes[i])
    # print('====================================')
    # print(self.matrix[1, :])
    # print(deployed_power, planned_power)
    return deployed_power == planned_power
  