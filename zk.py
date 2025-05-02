import math
import random

# === 结构函数定义 ===
def generate_phi_params(seed=0):
    random.seed(seed)
    return [(random.uniform(0.5, 2.0),
             random.uniform(1.0, 5.0),
             random.uniform(0, 2 * math.pi)) for _ in range(3)]

def phi(x, params):
    return sum(A * math.cos(t * math.log(x + 1) + theta) for A, t, theta in params)

def residual(phi_x, tau):
    return abs(phi_x - tau)

# === 模拟结构 ZKP ===
def zkp_prove(phi_x, tau, epsilon):
    delta = residual(phi_x, tau)
    return {
        "comm": f"commitment(delta={round(delta, 4)})",
        "phi_x": phi_x,
        "delta": delta,
        "epsilon": epsilon,
        "zkp_valid": delta < epsilon
    }

def zkp_verify(proof):
    return proof["zkp_valid"] and proof["delta"] < proof["epsilon"]

# === 签名查找器 ===
def find_valid_structure_signature(x, epsilon, max_trials=1000):
    for seed in range(max_trials):
        params = generate_phi_params(seed)
        phi_x = phi(x, params)
        for offset in [-epsilon * 0.5, 0, epsilon * 0.5]:
            tau = phi_x + offset
            delta = residual(phi_x, tau)
            proof = zkp_prove(phi_x, tau, epsilon)
            if zkp_verify(proof):
                return {
                    "seed": seed,
                    "x": x,
                    "phi(x)": round(phi_x, 6),
                    "tau": round(tau, 6),
                    "epsilon": epsilon,
                    "delta": round(delta, 6),
                    "zkp_valid": True,
                    "commitment": proof["comm"]
                }
    return {"zkp_valid": False, "message": "No valid structure signature found within trial limit."}

# === 测试运行 ===
if __name__ == "__main__":
    result = find_valid_structure_signature(x=42, epsilon=0.1)
    print("=== Structure ZKP Test Result ===")
    for k, v in result.items():
        print(f"{k}: {v}")
