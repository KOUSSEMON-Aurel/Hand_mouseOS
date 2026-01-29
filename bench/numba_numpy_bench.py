import time
import numpy as np
import math
import sys
import os

# Ajout du path pour trouver rust_core
sys.path.insert(0, os.getcwd())

from numba import jit

# 1. SETUP DATA
n_hands = 100
landmarks_list = [np.random.rand(21, 3).astype(np.float32) for _ in range(n_hands)]
landmarks_np = np.array(landmarks_list) # (100, 21, 3)

iterations = 500 # Réduit pour éviter les timeouts

print("="*60)
print(f"🔬 BENCHMARK: OPTIMISATION DE LA GÉOMÉTRIE (Batch)")
print(f"Calcul de distance entre Thumb Tip (4) et Index Tip (8)")
print(f"Traitement de {n_hands} mains x {iterations} répétitions")
print("="*60)

# 2. IMPLEMENTATIONS

def py_pinch_dist(hands):
    results = []
    for hand in hands:
        p1 = hand[4]
        p2 = hand[8]
        dist = math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)
        results.append(dist)
    return results

def np_pinch_dist(hands_np):
    p1 = hands_np[:, 4, :]
    p2 = hands_np[:, 8, :]
    return np.sqrt(np.sum((p1 - p2)**2, axis=1))

@jit(nopython=True)
def numba_pinch_dist(hands_np):
    n = hands_np.shape[0]
    results = np.empty(n, dtype=np.float32)
    for i in range(n):
        p1 = hands_np[i, 4]
        p2 = hands_np[i, 8]
        results[i] = math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)
    return results

try:
    from rust_core import distance_3d
    def rust_multi_dist(hands):
        results = []
        for hand in hands:
            p1 = hand[4]
            p2 = hand[8]
            results.append(distance_3d(p1[0], p1[1], p1[2], p2[0], p2[1], p2[2]))
        return results
    rust_available = True
except ImportError:
    rust_available = False

# 3. RUN BENCHMARKS

def bench(name, func, data, baseline=None):
    # Warmup
    func(data)
    start = time.perf_counter()
    for _ in range(iterations):
        func(data)
    duration = (time.perf_counter() - start) * 1000
    speedup = baseline / duration if baseline else 1.0
    print(f"{name:<15} | {duration:>10.2f} ms | {speedup:>8.2f}x")
    return duration

base_dur = bench("Python Pur", py_pinch_dist, landmarks_list)
bench("NumPy (Vect)", np_pinch_dist, landmarks_np, base_dur)
bench("Numba (JIT)", numba_pinch_dist, landmarks_np, base_dur)

if rust_available:
    bench("Rust (Fils)", rust_multi_dist, landmarks_list, base_dur)
else:
    print("Rust (Fils)     | Non disponible")

print("\n" + "="*60)
print("📌 COMPARAISON RUST DIRECT (BATCH)")
print("="*60)

try:
    import rust_core
    # Simulation d'une fonction Rust qui prend TOUS les points d'un coup
    # Si on avait implémenté une fonction batch_pinch_distance en Rust
    print("Version Rust optimisée (théorique):")
    print("Rust Batch      | ~0.10 ms    | ~200x (Estimation si tout est en Rust)")
except:
    pass
