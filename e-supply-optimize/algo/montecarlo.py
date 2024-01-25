from pprint import pprint
from random import randint
from time import sleep
from multiprocessing import Pool, cpu_count, Manager, Process
from tqdm import tqdm

def find_last_non_zero_index(arr):
  for i in range(len(arr) - 1, -1, -1):
    if arr[i] > 0:
      return i
  return 0

def yes_or_no_prob():
  return randint(0, 1) == 1

def constrain_power_demand(arr, process_power):
  return sum([x for x in arr if x > 1]) == sum(process_power)

def calculate_electric_cost(arr, hourly_prices):
  return sum([arr[i] * hourly_prices[i] for i in range(len(arr))])

def calculate_peak_power(mat, hourly_prices):
  return max(
    [
      sum([
        mat[j][i] for j in range(len(mat))
      ])
      for i in range(len(hourly_prices))
    ]
  )

def monte_carlo(hourly_prices, process_power, start=0):
  # 1. 生成随机的电价序列
  # 2. 生成随机的工序序列
  # 3. 计算电费
  # 4. 返回电费
  time_table = [0] * len(hourly_prices)
  pp_index = 0
  tt_index = start
  while pp_index < len(process_power) and tt_index < len(time_table):
    if time_table[tt_index] == 0 and yes_or_no_prob():
      time_table[tt_index] = process_power[pp_index]
      pp_index += 1
    elif sum(time_table[:tt_index]) > 0:
      time_table[tt_index] = 1
    tt_index += 1
  if pp_index < len(process_power) - 1:
    return monte_carlo(hourly_prices, process_power, start=0)
  return time_table

def run_once(args):
  q, hourly_prices, processes = args
  calendar = []
  start = 0
  for process in processes:
    process_power = process['process']
    batch_id = process['id']
    res = monte_carlo(hourly_prices, process_power, start=start)
    start = find_last_non_zero_index(res) + 1
    if constrain_power_demand(res, process_power):
      elec_cost = calculate_electric_cost(res, hourly_prices)
      calendar.append((batch_id, elec_cost, res))
  peak_power = calculate_peak_power([x[2] for x in calendar], hourly_prices)
  total_elec_cost = sum([x[1] for x in calendar])
  q.put((peak_power, total_elec_cost, calendar))
  return (peak_power, total_elec_cost, calendar)

def select_best(monte_carlo_res, best):
  monte_carlo_res.sort(key=lambda x: x[0] + x[1])
  new_best_score = monte_carlo_res[0][0] + monte_carlo_res[0][1]
  best_score = best[0] + best[1] if best else None
  if best_score is None or new_best_score < best_score:
    best = monte_carlo_res[0]
    print('发现新的最优计划方案')
    print('峰值电量:', best[0], '总电费：', best[1])
  return best

def concurrent_run_once(queue, hourly_prices, processes):
  pool = Pool(cpu_count())
  pool.map(run_once, [(queue, hourly_prices, processes)] * 10000)

def optimize_electric_cost(hourly_prices, processes):
  best = None
  i = 0
  epoch = 100
  progress_bar = tqdm(total=epoch)
  m = Manager()
  queue = m.Queue()
  p = Process(target=concurrent_run_once, args=(queue, hourly_prices, processes))
  p.start()
  while True:
    if queue.empty():
      sleep(1)
      continue
    best = select_best(queue.get(), best)
    print(best)
  
  # while i < epoch:
  #   pool = Pool(cpu_count())
  #   monte_carlo_res = pool.map(
  #     run_once, 
  #     [(queue, hourly_prices, processes)] * 10000
  #   )

    # best = select_best(queue.get(), best)
    # best = select_best(monte_carlo_res, best)
    # progress_bar.update(1)
    # i += 1
  return best

if __name__ == '__main__':
  # 示例调用
  hourly_prices = [
      1, 1, 1, 1, 1, 1, 1, 1,
      2, 2, 2, 2,
      3, 3,
      2, 2, 2, 2,
      3, 3, 3, 3,
      2, 2,
  ] * 31

  process_power = [3000, 4000, 6000, 6000, 8000, 12000, 12000, 12000, 12000, 12000, 12000, 12000, 12000, 12000]

  optimize_electric_cost(hourly_prices, [
    process_power,
    process_power,
    process_power,
    process_power,
    process_power,
  ])
