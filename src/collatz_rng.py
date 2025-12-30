#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

MASK32 = 0xFFFFFFFF
WEYL_C = 0x61C88647  # Weyl increment


def collatz_step(x: int) -> int:
    return x // 2 if (x % 2 == 0) else (3 * x + 1)


def mix32(x: int) -> int:
    """
    32-bit karıştırma (dağılımı iyileştirmek için).
    Kriptografik amaçla tasarlanmamıştır.
    """
    x &= MASK32
    x ^= (x >> 16)
    x = (x * 0x7FEB352D) & MASK32
    x ^= (x >> 15)
    x = (x * 0x846CA68B) & MASK32
    x ^= (x >> 16)
    return x & MASK32


def collatz_rng(seed: int, n: int) -> list[int]:
    x = seed
    out = []
    for _ in range(n):
        x = collatz_step(x)
        out.append(mix32(x))
    return out


def collatz_weyl_rng(seed: int, n: int) -> list[int]:
    x = seed
    w = 0
    out = []
    for _ in range(n):
        x = collatz_step(x)
        w = (w + WEYL_C) & MASK32
        out.append(mix32((x + w) & MASK32))
    return out


def generate_key(seed: int, key_len_bytes: int, mode: str = "weyl") -> bytes:
    need_words = (key_len_bytes + 3) // 4
    nums = collatz_weyl_rng(seed, need_words) if mode == "weyl" else collatz_rng(seed, need_words)

    b = bytearray()
    for v in nums:
        b += v.to_bytes(4, byteorder="little", signed=False)
    return bytes(b[:key_len_bytes])


def main():
    p = argparse.ArgumentParser(description="Collatz tabanlı pseudo-random sayı üreteci (basic/weyl).")
    p.add_argument("--seed", type=int, required=True, help="Başlangıç tohumu (pozitif tamsayı önerilir).")
    p.add_argument("--n", type=int, default=10, help="Üretilecek 32-bit sayı adedi.")
    p.add_argument("--mode", choices=["basic", "weyl"], default="weyl", help="basic=V0, weyl=V1")
    p.add_argument("--hex", action="store_true", help="Çıktıyı hex yazdır.")
    p.add_argument("--key", type=int, default=0, help="0 değilse belirtilen byte uzunluğunda anahtar üretir.")
    args = p.parse_args()

    if args.key > 0:
        k = generate_key(args.seed, args.key, mode=args.mode)
        print(k.hex())
        return

    nums = collatz_weyl_rng(args.seed, args.n) if args.mode == "weyl" else collatz_rng(args.seed, args.n)
    for v in nums:
        print(hex(v) if args.hex else v)


if __name__ == "__main__":
    main()
