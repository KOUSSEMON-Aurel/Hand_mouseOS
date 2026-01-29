import time
import math
import ctypes
import numpy as np
from numba import jit

# -----------------------------------------------------------------------------
# 1. SETUP LIBRARIES
# -----------------------------------------------------------------------------

# C/C++ via ctypes
try:
    libc = ctypes.CDLL("./bench/libbench.so")
    class Point3D(ctypes.Structure):
        _fields_ = [("x", ctypes.c_float), ("y", ctypes.c_float), ("z", ctypes.c_float)]
    
    libc.c_distance_3d.restype = ctypes.c_float
    libc.c_distance_3d.argtypes = [ctypes.c_float, ctypes.c_float, ctypes.c_float, 
                                   ctypes.c_float, ctypes.c_float, ctypes.c_float]
    
    libc.c_batch_distances.argtypes = [ctypes.POINTER(Point3D), ctypes.POINTER(Point3D), 
                                       ctypes.POINTER(ctypes.c_float), ctypes.c_int]
except Exception as e:
    print(f"C/C++ Setup failed: {e}")
    libc = None

# Go via cgo
try:
    libgo = ctypes.CDLL("./bench/libgo_bench.so")
    libgo.GoDistance3D.restype = ctypes.c_float
    libgo.GoDistance3D.argtypes = [ctypes.c_float, ctypes.c_float, ctypes.c_float, 
                                   ctypes.c_float, ctypes.c_float, ctypes.c_float]
except Exception as e:
    print(f"Go Setup failed: {e}")
    libgo = None

# Rust via rust_core (from previous steps)
try:
    import rust_core
except ImportError:
    rust_core = None

# Numba JIT
@jit(nopython=True)
def numba_distance_3d(x1, y1, z1, x2, y2, z2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)

@jit(nopython=True)
def numba_batch_distances(p1s, p2s):
    n = len(p1s)
    results = np.empty(n, dtype=np.float32)
    for i in range(n):
        results[i] = math.sqrt((p1s[i][0]-p2s[i][0])**2 + (p1s[i][1]-p2s[i][1])**2 + (p1s[i][2]-p2s[i][2])**2)
    return results

# -----------------------------------------------------------------------------
# 2. DEFINITION DES TESTS
# -----------------------------------------------------------------------------

def py_distance_3d(x1, y1, z1, x2, y2, z2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)

def py_batch_distances(p1s, p2s):
    return [py_distance_3d(*p1, *p2) for p1, p2 in zip(p1s, p2s)]

# -----------------------------------------------------------------------------
# 3. RUN BENCHMARKS
# -----------------------------------------------------------------------------

N_SINGLE = 100000
N_BATCH = 1000 # Size of batch
ITER_BATCH = 100 # Number of times to run batch

print("="*80)
print(f"🔬 BENCHMARK MULTI-LANGAGES (Python {N_SINGLE:,} calls)")
print("="*80)

# --- SINGLE CALL TEST ---
print(f"\n[1] TEST APPELS UNIQUES ({N_SINGLE:,} itérations)")
print(f"{'Langage':<15} | {'Temps (ms)':<10} | {'Ops/sec':<15} | {'Speedup':<10}")
print("-" * 60)

def bench_single(name, func, baseline=None):
    start = time.perf_counter()
    for _ in range(N_SINGLE):
        func(0.1, 0.2, 0.3, 0.4, 0.5, 0.6)
    duration = (time.perf_counter() - start) * 1000
    ops = N_SINGLE / (duration / 1000)
    speedup = baseline / duration if baseline else 1.0
    print(f"{name:<15} | {duration:>10.2f} | {ops:>15,.0f} | {speedup:>8.2f}x")
    return duration

base_dur = bench_single("Python (math)", py_distance_3d)
bench_single("Numba (JIT)", numba_distance_3d, base_dur)

if libc:
    bench_single("C (ctypes)", lambda *a: libc.c_distance_3d(*a), base_dur)
if libgo:
    bench_single("Go (cgo)", lambda *a: libgo.GoDistance3D(*a), base_dur)
if rust_core:
    # Rust uses slightly different API in rust_core
    bench_single("Rust (PyO3)", lambda x1,y1,z1,x2,y2,z2: rust_core.distance_3d(x1,y1,z1,x2,y2,z2), base_dur)

# --- BATCH CALL TEST ---
print(f"\n[2] TEST BATCH ({N_BATCH} points, {ITER_BATCH} itérations)")
print(f"{'Langage':<15} | {'Temps (ms)':<10} | {'Points/sec':<15} | {'Speedup':<10}")
print("-" * 60)

# Prepare data
p1s_py = [(np.random.rand(), np.random.rand(), np.random.rand()) for _ in range(N_BATCH)]
p2s_py = [(np.random.rand(), np.random.rand(), np.random.rand()) for _ in range(N_BATCH)]

p1s_np = np.array(p1s_py, dtype=np.float32)
p2s_np = np.array(p2s_py, dtype=np.float32)

if libc:
    c_p1s = (Point3D * N_BATCH)(*[Point3D(*p) for p in p1s_py])
    c_p2s = (Point3D * N_BATCH)(*[Point3D(*p) for p in p2s_py])
    c_res = (ctypes.c_float * N_BATCH)()

def bench_batch(name, func, baseline=None):
    start = time.perf_counter()
    for _ in range(ITER_BATCH):
        func()
    duration = (time.perf_counter() - start) * 1000
    points_sec = (N_BATCH * ITER_BATCH) / (duration / 1000)
    speedup = baseline / duration if baseline else 1.0
    print(f"{name:<15} | {duration:>10.2f} | {points_sec:>15,.0f} | {speedup:>8.2f}x")
    return duration

base_batch = bench_batch("Python", lambda: py_batch_distances(p1s_py, p2s_py))
bench_batch("Numba", lambda: numba_batch_distances(p1s_np, p2s_np), base_batch)
bench_batch("Numpy (v)", lambda: np.sqrt(np.sum((p1s_np - p2s_np)**2, axis=1)), base_batch)

if libc:
    bench_batch("C (ctypes)", lambda: libc.c_batch_distances(c_p1s, c_p2s, c_res, N_BATCH), base_batch)

print("\n" + "="*80)
print("📌 CONCLUSIONS")
print("="*80)
print("1. Pour 1 seul calcul, Python/Numba sont souvent meilleurs car l'overhead FFI est lourd.")
print("2. Rust/C/Go brillent sur les BATCHS ou les algorithmes complexes (filtres).")
print("3. Numba est imbattable en facilité pour accélérer du Python pur.")
