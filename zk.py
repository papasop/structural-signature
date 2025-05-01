import time
import math
import hashlib

# 模拟结构函数 φ(x)
def phi(x, A=2.0, t=3.0, theta=0.5):
    return A * math.cos(t * math.log(x + 1) + theta)

# 模拟 ZKP 生成（100~150ms）
def generate_zkp(phi_x, tau, epsilon):
    time.sleep(0.12)  # 模拟生成耗时
    return f"zkp_proof_for_{phi_x:.4f}"

# 模拟 ZKP 验证（5~10ms，非必须测）
def verify_zkp(proof):
    time.sleep(0.007)
    return True

# 不带 ZKP 的结构签名
def structure_signature_without_zkp(x, tau, epsilon):
    start = time.time()
    phi_x = phi(x)
    delta = abs(phi_x - tau)
    signature = hashlib.sha256(f"{x}|{phi_x:.6f}|{delta:.6f}".encode()).hexdigest()
    return signature, time.time() - start

# 带 ZKP 的结构签名
def structure_signature_with_zkp(x, tau, epsilon):
    start = time.time()
    phi_x = phi(x)
    delta = abs(phi_x - tau)
    proof = generate_zkp(phi_x, tau, epsilon)
    signature = hashlib.sha256(f"{x}|{phi_x:.6f}|{delta:.6f}".encode()).hexdigest()
    return signature, proof, time.time() - start

# 运行测试
if __name__ == "__main__":
    x_val = 123456
    tau = 1.5
    epsilon = 0.05

    print("Running benchmark over 100 signatures...\n")
    zkp_total, no_zkp_total = 0, 0

    for _ in range(100):
        _, t1 = structure_signature_without_zkp(x_val, tau, epsilon)
        _, _, t2 = structure_signature_with_zkp(x_val, tau, epsilon)
        no_zkp_total += t1
        zkp_total += t2

    print(f"平均不带ZKP签名时间：{no_zkp_total / 100:.8f} 秒")
    print(f"平均带ZKP签名时间：{zkp_total / 100:.3f} 秒")
    print(f"合计总耗时（ZKP）：{zkp_total:.2f} 秒")
