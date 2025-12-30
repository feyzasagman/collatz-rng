from __future__ import annotations
from typing import List
from collatz_rng import collatz_weyl_rng

# JPEG standart "luminance" quantization tablosu (baseline)
STD_LUMA_Q = [
    16,11,10,16,24,40,51,61,
    12,12,14,19,26,58,60,55,
    14,13,16,24,40,57,69,56,
    14,17,22,29,51,87,80,62,
    18,22,37,56,68,109,103,77,
    24,35,55,64,81,104,113,92,
    49,64,78,87,103,121,120,101,
    72,92,95,98,112,100,103,99
]

def clamp(v: int, lo: int, hi: int) -> int:
    return lo if v < lo else hi if v > hi else v

def qtable_from_seed(seed: int, strength: float = 0.35) -> List[int]:
    """
    Standart JPEG tablosunu RNG ile hafif perturbe eder.
    strength küçük olmalı; tamamen rastgele tablo genelde kaliteyi bozar.
    """
    r = collatz_weyl_rng(seed, 64)
    out: List[int] = []
    for base, rv in zip(STD_LUMA_Q, r):
        t = ((rv & 0xFFFF) / 65535.0) * 2.0 - 1.0  # [-1, +1]
        scaled = round(base * (1.0 + strength * t))
        out.append(clamp(int(scaled), 1, 255))
    return out
