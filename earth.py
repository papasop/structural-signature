import numpy as np
import pandas as pd
from itertools import combinations
from scipy.optimize import minimize_scalar

# 基本单位
AU = 1.496e8

# 近似前 20 个 ζ 零点
t_values = np.array([
    14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
    37.586178, 40.918719, 43.327073, 48.005150, 49.773832,
    52.970321, 56.446248, 59.347045, 60.831780, 65.112544,
    67.079811, 69.546402, 72.067158, 75.704690, 77.144840
])

# 相位范围
theta_pool = np.linspace(0, 2 * np.pi, 20)

# 行星数据 (AU)
planet_au = {
    "Mercury": 0.39,
    "Venus": 0.72,
    "Earth": 1.0,
    "Mars": 1.52,
    "Jupiter": 5.2,
    "Saturn": 9.58,
    "Uranus": 19.2,
    "Neptune": 30.1
}

# 结构语言 ψ-path 残差计算函数
def compute_delta(t_set, theta_set, au):
    log_x = np.log(au * AU)
    psi = sum(0.01 * np.cos(t * log_x + th) for t, th in zip(t_set, theta_set))
    rho = 1 / log_x + psi
    pi_over_x = 1 / log_x
    return abs(pi_over_x - rho)

# 搜索最优 ψ-path 的 ζ 零点组合
def find_best_path(au, t_pool, theta_pool):
    best_combo = None
    best_theta = None
    min_delta = float('inf')
    for t_set in combinations(t_pool, 3):
        for theta_set in combinations(theta_pool, 3):
            delta = compute_delta(t_set, theta_set, au)
            if delta < min_delta:
                min_delta = delta
                best_combo = t_set
                best_theta = theta_set
    return best_combo, best_theta, min_delta

# 精细搜索 ψ-path 最佳共振位置（预测 AU）
def find_predicted_au(t_set, theta_set, au_actual, step=1000, search_range=0.3):
    x_vals = np.linspace(au_actual - search_range, au_actual + search_range, step)
    min_delta = float('inf')
    best_au = None
    for x in x_vals:
        delta = compute_delta(t_set, theta_set, x)
        if delta < min_delta:
            min_delta = delta
            best_au = x
    error = abs(best_au - au_actual)
    return best_au, error, min_delta

# 主程序
results = []
for planet, au in planet_au.items():
    t_set, th_set, _ = find_best_path(au, t_values, theta_pool)
    pred_au, err_au, delta_min = find_predicted_au(t_set, th_set, au)
    results.append({
        "Planet": planet,
        "Actual AU": au,
        "Predicted AU": round(pred_au, 6),
        "Error (AU)": round(err_au, 6),
        "Error (%)": round(100 * err_au / au, 2),
        "Min δ(x)": format(delta_min, ".6e"),
        "Optimal t_n": t_set,
        "θ_n": tuple(round(th, 2) for th in th_set)
    })

# 输出表格
df = pd.DataFrame(results)
print(df.to_string(index=False))
df.to_csv("zeta_orbital_predictions.csv", index=False)
