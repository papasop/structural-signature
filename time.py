import hashlib
import hmac
import math
import os
import time
from typing import List, Tuple

def derive_parameters(seed: bytes) -> Tuple[List[float], List[float], List[float]]:
    key = b'structkey'
    raw = b''.join([hmac.new(key, seed + bytes([i]), hashlib.sha256).digest() for i in range(3)])
    floats = [float.fromhex(hex(int.from_bytes(raw[i:i+4], 'big'))) for i in range(0, 48, 4)]
    A = [1 + abs(floats[i]) % 2 for i in range(3)]
    t = [0.5 + abs(floats[i]) % 20 for i in range(3, 6)]
    theta = [abs(floats[i]) % (2 * math.pi) for i in range(6, 9)]
    return A, t, theta

def phi(x: int, A: List[float], t: List[float], theta: List[float]) -> float:
    return sum(A[i] * math.cos(t[i] * math.log(x + 1) + theta[i]) for i in range(3))

def structure_hash(message: bytes) -> int:
    return int.from_bytes(hashlib.sha256(message).digest(), 'big')

def generate_signature(message: str, A, t, theta, D=2**24) -> Tuple[str, float, float]:
    m_bytes = message.encode()
    xm = structure_hash(m_bytes) % D
    phi_xm = phi(xm, A, t, theta)
    phi_values = [phi(x, A, t, theta) for x in [101, 211, 307]]
    tau = sorted(phi_values)[1]
    delta = abs(phi_xm - tau)
    data = f"{xm}|{phi_xm}|{delta}".encode()
    sig = hashlib.sha256(data).hexdigest()
    return sig, delta, tau

def verify_signature(message: str, signature: str, A, t, theta, D=2**24, alpha: float = 0.1) -> Tuple[bool, float, float]:
    m_bytes = message.encode()
    xm = structure_hash(m_bytes) % D
    phi_xm = phi(xm, A, t, theta)
    phi_values = [phi(x, A, t, theta) for x in [101, 211, 307]]
    tau = sorted(phi_values)[1]
    sigma_phi = math.sqrt(sum((v - tau)**2 for v in phi_values) / 3)
    epsilon = alpha * sigma_phi
    delta = abs(phi_xm - tau)
    data = f"{xm}|{phi_xm}|{delta}".encode()
    expected_sig = hashlib.sha256(data).hexdigest()
    return (delta < epsilon and expected_sig == signature), delta, epsilon

def find_valid_or_best_signature(message: str, max_attempts: int = 50, alpha: float = 0.1):
    best = {"delta": float("inf")}
    for i in range(max_attempts):
        seed = os.urandom(16)
        A, t, theta = derive_parameters(seed)

        start_sign = time.time()
        signature, delta, tau = generate_signature(message, A, t, theta)
        sign_time = (time.time() - start_sign) * 1000

        start_verify = time.time()
        is_valid, delta_check, epsilon = verify_signature(message, signature, A, t, theta, alpha=alpha)
        verify_time = (time.time() - start_verify) * 1000

        print(f"[尝试 {i+1}] Δ = {delta_check:.6f}, ε = {epsilon:.6f}, 签名 = {sign_time:.3f}ms, 验证 = {verify_time:.3f}ms => {'✅ VALID' if is_valid else '❌ INVALID'}")

        if delta_check < best["delta"]:
            best = {
                "seed": seed, "A": A, "t": t, "theta": theta,
                "signature": signature, "delta": delta_check,
                "valid": is_valid, "attempts": i + 1,
                "sign_time": sign_time, "verify_time": verify_time,
                "epsilon": epsilon
            }

        if is_valid:
            print("✔️ 成功找到有效签名！\n")
            return best

    print(f"⚠️ 未找到完全有效签名，返回残差最小版本（Δ = {best['delta']:.6f}）\n")
    return best

# 主程序
if __name__ == '__main__':
    message = "Test 123"
    alpha = 0.1
    max_attempts = 50

    start_total = time.time()
    result = find_valid_or_best_signature(message, max_attempts=max_attempts, alpha=alpha)
    end_total = time.time()

    print("最终签名:", result["signature"])
    print(f"残差 Δ = {result['delta']:.6f}")
    print(f"容差 ε = {result['epsilon']:.6f}")
    print(f"验证状态 = {'VALID ✅' if result['valid'] else '⚠️ BEST EFFORT'}")
    print(f"签名耗时 = {result['sign_time']:.3f} ms")
    print(f"验证耗时 = {result['verify_time']:.3f} ms")
    print(f"总耗时 = {(end_total - start_total)*1000:.3f} ms")
    print(f"尝试次数 = {result['attempts']}")
