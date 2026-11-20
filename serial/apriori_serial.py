#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apriori 频繁项集挖掘 —— 非并行（单机）实现.

用法:
    python3 apriori_serial.py <transactions.txt> <min_sup_count> <out_prefix>

输出:
    <out_prefix>_itemsets.txt   频繁项集：k<TAB>item1,item2<TAB>count
    <out_prefix>_rules.txt      关联规则：A=>B<TAB>support<TAB>confidence
"""
import sys
from collections import Counter
from itertools import combinations


# --------------------------------------------------------------------------
# 候选生成（Apriori-gen）：由 k-1 频繁项集连接 + 剪枝得到 k 候选集
# 两个实现共用同一套逻辑，保证候选集完全一致
# --------------------------------------------------------------------------
def gen_candidates(prev_freq, k):
    prev = sorted(prev_freq)          # prev 中每个元素是排好序的 tuple
    candidates = set()
    n = len(prev)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = prev[i], prev[j]
            if a[:k - 2] != b[:k - 2]:
                continue
            cand = tuple(sorted(set(a) | set(b)))
            if len(cand) != k:
                continue
            # 剪枝：所有 k-1 子集必须都是频繁的
            if all(tuple(c) in prev_freq for c in combinations(cand, k - 1)):
                candidates.add(cand)
    return sorted(candidates)


def build_itemsets(transactions, min_sup):
    """返回 (freq_by_size, all_freq)，freq_by_size[k] = {tuple: count}"""
    txs = [sorted(set(t)) for t in transactions]
    freq_by_size = {}

    # 第 1 轮：直接统计单项
    counts = Counter()
    for t in txs:
        for item in t:
            counts[(item,)] += 1
    l1 = {k: v for k, v in counts.items() if v >= min_sup}
    if not l1:
        return freq_by_size, {}
    freq_by_size[1] = l1

    k = 2
    prev = l1
    while prev:
        candidates = gen_candidates(set(prev.keys()), k)
        if not candidates:
            break
        cand_set = set(candidates)
        counts = Counter()
        # 对每条事务枚举 k 元子集，只统计落在候选集里的组合
        for t in txs:
            if len(t) < k:
                continue
            for sub in combinations(t, k):
                if sub in cand_set:
                    counts[sub] += 1
        cur = {c: n for c, n in counts.items() if n >= min_sup}
        if not cur:
            break
        freq_by_size[k] = cur
        prev = cur
        k += 1

    all_freq = {}
    for kk in freq_by_size:
        all_freq.update(freq_by_size[kk])
    return freq_by_size, all_freq


def build_rules(all_freq, min_conf=0.6, min_len=2):
    """由频繁项集导出关联规则 A=>B，按置信度降序"""
    rules = []
    for itemset, sup in all_freq.items():
        if len(itemset) < min_len:
            continue
        total = len(itemset)
        for r in range(1, total):
            for ant in combinations(itemset, r):
                cons = tuple(sorted(set(itemset) - set(ant)))
                if len(cons) < 1:
                    continue
                ant_sup = all_freq.get(tuple(sorted(ant)))
                if not ant_sup:
                    continue
                conf = sup / ant_sup
                if conf >= min_conf:
                    rules.append((tuple(sorted(ant)), cons, sup, conf))
    rules.sort(key=lambda x: (-x[3], -x[2], x[0], x[1]))
    return rules


def main():
    if len(sys.argv) < 4:
        print("usage: apriori_serial.py <transactions> <min_sup_count> <out_prefix>", file=sys.stderr)
        sys.exit(1)

    src, min_sup, prefix = sys.argv[1], int(sys.argv[2]), sys.argv[3]

    transactions = []
    with open(src, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                transactions.append(line.split(","))

    freq_by_size, all_freq = build_itemsets(transactions, min_sup)
    rules = build_rules(all_freq)

    with open(prefix + "_itemsets.txt", "w", encoding="utf-8", newline="\n") as f:
        f.write("# 事务数=%d 最小支持度计数=%d 频繁项集总数=%d\n"
                % (len(transactions), min_sup, len(all_freq)))
        for k in sorted(freq_by_size):
            for itemset in sorted(freq_by_size[k]):
                f.write("%d\t%s\t%d\n" % (k, ",".join(itemset), freq_by_size[k][itemset]))

    with open(prefix + "_rules.txt", "w", encoding="utf-8", newline="\n") as f:
        f.write("# 关联规则数=%d 最小置信度=0.60\n" % len(rules))
        for ant, cons, sup, conf in rules:
            f.write("%s=>%s\t%d\t%.6f\n" % (",".join(ant), ",".join(cons), sup, conf))

    print("频繁项集: %d 个" % len(all_freq))
    for k in sorted(freq_by_size):
        print("  %d-项集: %d" % (k, len(freq_by_size[k])))
    print("关联规则: %d 条" % len(rules))
    print("Top5 规则:")
    for ant, cons, sup, conf in rules[:5]:
        print("  %s => %s  (sup=%d, conf=%.4f)" % (",".join(ant), ",".join(cons), sup, conf))


if __name__ == "__main__":
    main()
