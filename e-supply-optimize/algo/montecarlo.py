from multiprocessing import Pool, cpu_count
from tqdm import tqdm
from algo.models.mc_mat import MonteCarloMatrix

def run_once(args):
  hourly_prices, processes = args
  mc_mat = MonteCarloMatrix(hourly_prices, processes)
  while mc_mat.next():
    continue
  if mc_mat.constrain_power_demand():
    return (mc_mat.calculate_peak_power(), mc_mat.calculate_electric_cost(), mc_mat.get_result())
  else:
    return (None, None, None)

def select_best(monte_carlo_res, best):
  monte_carlo_res = [x for x in monte_carlo_res if x[0] is not None]
  if len(monte_carlo_res) == 0:
    return best
  new_result = sorted(monte_carlo_res, key=lambda x: x[1])[0]
  new_best_score = new_result[1]
  best_score = best[1] if best else None
  if best_score is None or new_best_score < best_score:
    best = new_result
    print('发现新的最优计划方案')
    print('峰值电量:', best[0], '总电费：', best[1])
  return best

def optimize_electic_cost_single(hourly_prices, processes):
  res = run_once((hourly_prices, [processes[0]]))
  print(res)

def optimize_electric_cost(hourly_prices, processes):
  best = None
  epoch = 100
  i = 0
  batch_size = 1000
  progress_bar = tqdm(total=epoch)
  
  while i < epoch:
    pool = Pool(cpu_count())
    monte_carlo_res = pool.map(
      run_once, 
      [(hourly_prices, processes)] * batch_size
    )

    best = select_best(monte_carlo_res, best)
    progress_bar.update(1)
    i += 1
    pool.close()
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
