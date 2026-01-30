#!/usr/bin/env python3
"""Benchmark SIMD Batch Filter vs Loop Filter"""

import time
import numpy as np
from rust_core import BatchOneEuroFilter, OneEuroFilter

# Configuration
NUM_ITERATIONS = 10000
NUM_LANDMARKS = 21

# Générer des landmarks aléatoires (21 × 3)
np.random.seed(42)
landmarks_batch = np.random.rand(NUM_ITERATIONS, NUM_LANDMARKS, 3).astype(np.float32)

print("🔬 Benchmark SIMD vs Loop Filter")
print(f"Iterations: {NUM_ITERATIONS}")
print(f"Landmarks: {NUM_LANDMARKS} × 3 coords\n")

# ========================================
# Test 1: Filtre Batch SIMD (ZERO-COPY NumPy)
# ========================================
print("1️⃣  Test Batch SIMD Filter (Zero-Copy NumPy)...")
batch_filter = BatchOneEuroFilter(min_cutoff=1.0, beta=0.007, d_cutoff=1.0)

start = time.perf_counter()
for i, lm_frame in enumerate(landmarks_batch):
    t = i * 0.016  # 60 FPS
    # NumPy array direct - zero copy!
    batch_filter.filter_batch(lm_frame, t)
batch_time = time.perf_counter() - start

print(f"   ✅ Temps: {batch_time:.4f}s")
print(f"   📊 Throughput: {NUM_ITERATIONS/batch_time:.0f} frames/sec\n")

# ========================================
# Test 2: Filtre Loop (63 appels)
# ========================================
print("2️⃣  Test Loop Filter (63 appels par frame)...")
loop_filters = [OneEuroFilter(min_cutoff=1.0, beta=0.007, d_cutoff=1.0) for _ in range(63)]

start = time.perf_counter()
for i, lm_frame in enumerate(landmarks_batch):
    t = i * 0.016
    flat = lm_frame.flatten()  # 63 floats
    for j, val in enumerate(flat):
        loop_filters[j].filter(val, t)
loop_time = time.perf_counter() - start

print(f"   ✅ Temps: {loop_time:.4f}s")
print(f"   📊 Throughput: {NUM_ITERATIONS/loop_time:.0f} frames/sec\n")

# ========================================
# Résultats
# ========================================
speedup = loop_time / batch_time
print("=" * 50)
print(f"🚀 SPEEDUP SIMD: {speedup:.1f}x")
print("=" * 50)

if speedup > 50:
    print("✅ EXCELLENT! SIMD超高速化成功！")
elif speedup > 10:
    print("✅ Très bon gain de performance")
elif speedup > 5:
    print("⚠️  Gain modéré, vérifier optimisations compilateur")
else:
    print("❌ Gain faible, possible problème SIMD")

print(f"\n📈 Détails:")
print(f"   Batch SIMD: {batch_time*1000/NUM_ITERATIONS:.3f} ms/frame")
print(f"   Loop:       {loop_time*1000/NUM_ITERATIONS:.3f} ms/frame")
print(f"   Gain absolu: {(loop_time - batch_time)*1000:.1f} ms total")

