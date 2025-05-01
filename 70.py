import numpy as np
import random
from collections import defaultdict
import hashlib

# ==== 参数设置 ====
NUM_NODES = 100                # 节点总数
MALICIOUS_RATIO = 0.6         # 拜占庭节点比例（60%）
EPSILON = 0.1                 # 残差阈值
NUM_ROUNDS = 10               # 总共运行轮数
CHALLENGE_POINTS = 5          # 每轮的结构挑战点数量

# ==== 结构函数 ====
def structure_function(x, params):
    return sum(A * np.cos(t * np.log(x + 1) + theta) for A, t, theta in params)

# ==== 节点私钥派生结构参数 ====
def generate_node_params(seed):
    random.seed(seed)
    return [(random.uniform(0.5, 2.0),
             random.uniform(1.0, 5.0),
             random.uniform(0, 2 * np.pi)) for _ in range(3)]

# ==== 残差计算 ====
def compute_residual(phi_x, tau):
    return abs(phi_x - tau)

# ==== ZKP 验证模拟（实际可扩展） ====
def zkp_verify(residual, epsilon):
    return residual < epsilon

# ==== DAG 节点结构 ====
class DAGNode:
    def __init__(self, node_id, x, phi_x, residual, zkp_valid, references):
        self.node_id = node_id
        self.x = x
        self.phi_x = phi_x
        self.residual = residual
        self.zkp_valid = zkp_valid
        self.references = references

# ==== 主模拟函数 ====
def simulate_porcdag():
    nodes = []
    malicious_nodes = set(random.sample(range(NUM_NODES), int(NUM_NODES * MALICIOUS_RATIO)))
    node_params = {i: generate_node_params(i) for i in range(NUM_NODES)}
    dag = {}
    reference_counts = defaultdict(int)

    for round in range(NUM_ROUNDS):
        print(f"\nRound {round + 1}")
        challenge_points = [random.uniform(1, 100) for _ in range(CHALLENGE_POINTS)]

        for node_id in range(NUM_NODES):
            is_malicious = node_id in malicious_nodes
            params = node_params[node_id]
            x = random.choice(challenge_points)
            phi_x = structure_function(x, params)
            tau = np.median([structure_function(x, node_params[i]) for i in range(NUM_NODES)])
            residual = compute_residual(phi_x, tau)

            if is_malicious:
                phi_x += random.uniform(-0.2, 0.2)  # 模拟结构伪造扰动
                residual = compute_residual(phi_x, tau)

            zkp_valid = zkp_verify(residual, EPSILON)

            valid_refs = [
                n_id for n_id, node in dag.items()
                if node.zkp_valid and abs(node.phi_x - phi_x) < EPSILON
            ]
            references = random.sample(valid_refs, min(len(valid_refs), 3)) if valid_refs else []
            dag_node = DAGNode(node_id, x, phi_x, residual, zkp_valid, references)
            dag[(round, node_id)] = dag_node

            if zkp_valid:
                for ref in references:
                    reference_counts[ref] += 1

        # 主路径判断：引用最多者
        if dag:
            canonical = max(dag.keys(), key=lambda k: reference_counts.get(k, 0), default=None)
            ref_count = reference_counts.get(canonical, 0)
            print(f"Canonical path node: {canonical}, References: {ref_count}")
            if canonical and canonical[1] in malicious_nodes:
                print("⚠️  Warning: Canonical path controlled by malicious node!")
            else:
                print("✅ Consensus path maintained by honest node.")

    # 统计合法节点最终引用
    honest_control = sum(1 for k in dag if reference_counts.get(k, 0) > 0 and k[1] not in malicious_nodes)
    print(f"\n📊 Final result: {honest_control} honest nodes in high-reference paths.")

# ==== 启动模拟 ====
if __name__ == "__main__":
    random.seed(42)
    np.random.seed(42)
    simulate_porcdag()
