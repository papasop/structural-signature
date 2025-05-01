import hashlib
import hmac
import math
import os
import time
from typing import List, Tuple
import matplotlib.pyplot as plt

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

def generate_signature(message: str, A: List[float], t: List[float], theta: List[float], D: int = 2**24) -> Tuple[str, float]:
    m_bytes = message.encode()
    xm = structure_hash(m_bytes) % D
    phi_xm = phi(xm, A, t, theta)
    challenge_xs = [101, 211, 307]
    phi_values = [phi(x, A, t, theta) for x in challenge_xs]
    tau = sorted(phi_values)[1]
    delta = abs(phi_xm - tau)
    data = f"{xm}|{phi_xm}|{delta}".encode()
    sig = hashlib.sha256(data).hexdigest()
    return sig, delta

def verify_signature(message: str, signature: str, A: List[float], t: List[float], theta: List[float], D: int = 2**24, alpha: float = 0.1) -> Tuple[bool, float]:
    m_bytes = message.encode()
    xm = structure_hash(m_bytes) % D
    phi_xm = phi(xm, A, t, theta)
    challenge_xs = [101, 211, 307]
    phi_values = [phi(x, A, t, theta) for x in challenge_xs]
    tau = sorted(phi_values)[1]
    sigma_phi = math.sqrt(sum((v - tau)**2 for v in phi_values) / 3)
    epsilon = alpha * sigma_phi
    delta = abs(phi_xm - tau)
    data = f"{xm}|{phi_xm}|{delta}".encode()
    expected_sig = hashlib.sha256(data).hexdigest()
    return (delta < epsilon and expected_sig == signature), delta

def main():
    message = "Test 123"
    num_trials = 50
    best_result = {"delta": float("inf")}
    results_all = []

    print(f"Trying {num_trials} random seeds for message: '{message}'...")

    for i in range(num_trials):
        seed_i = os.urandom(16)
        A_i, t_i, theta_i = derive_parameters(seed_i)
        sig_i, delta_i = generate_signature(message, A_i, t_i, theta_i)
        results_all.append((i, delta_i))
        if delta_i < best_result["delta"]:
            best_result = {
                "seed": seed_i,
                "delta": delta_i,
                "A": A_i,
                "t": t_i,
                "theta": theta_i,
                "signature": sig_i
            }

    print(f"Best delta found: {best_result['delta']:.6f}")
    print(f"Best signature: {best_result['signature']}")

    valid, delta_check = verify_signature(message, best_result['signature'],
                                          best_result['A'], best_result['t'], best_result['theta'], alpha=0.1)

    print(f"Verification: {'VALID ✅' if valid else 'INVALID ❌'} (delta = {delta_check:.6f})")

    try:
        plt.figure(figsize=(10, 5))
        plt.plot([i for i, _ in results_all], [d for _, d in results_all], marker='o')
        plt.axhline(0.2, color='red', linestyle='--', label='ε = 0.2')
        plt.title("Delta vs. Key Trial")
        plt.xlabel("Trial Number")
        plt.ylabel("Delta")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("delta_vs_trials.png")
        print("Plot saved as delta_vs_trials.png")
    except Exception as e:
        print("Plot generation failed:", e)

if __name__ == '__main__':
    main()
