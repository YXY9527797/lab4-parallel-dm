#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apriori 频繁项集挖掘 —— 并行化（Spark RDD）实现.

用法:
    spark-submit apriori_spark.py <hdfs_input> <min_sup_count> <out_prefix> [partitions]

并行点：
    每一轮迭代中，事务集合被划分到多个分区，各分区并行地把「本地事务的子集」
    映射成 (候选项集, 1) 并做 map 端预聚合，再按 key 做 reduceByKey 汇总计数。
    候选集由 driver 端按 Apriori-gen 生成后广播到所有 executor。

输出与串行版完全相同的两个文件：
    <out_prefix>_itemsets.txt / <out_prefix>_rules.txt
"""
import sys
from collections import Counter
from itertools import combinations

from pyspark import SparkContext

MIN_CONF = 0.6


def gen_candidates(prev_freq, k):
    """与串行版完全一致的 Apriori-gen：连接 + 剪枝"""
    prev = sorted(prev_freq)
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
            if all(tuple(c) in prev_freq for c in combinations(cand, k - 1)):
                candidates.add(cand)
    return sorted(candidates)


def build_rules(all_freq, min_conf=MIN_CONF):
    from itertools import combinations as comb
    rules = []
    for itemset, sup in all_freq.items():
        if len(itemset) < 2:
            continue
        for r in range(1, len(itemset)):
            for ant in comb(itemset, r):
                cons = tuple(sorted(set(itemset) - set(ant)))
                if not cons:
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
        print("usage: apriori_spark.py <input> <min_sup_count> <out_prefix> [partitions]", file=sys.stderr)
        sys.exit(1)

    src, min_sup, prefix = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    npart = int(sys.argv[4]) if len(sys.argv) > 4 else 4

    sc = SparkContext(appName="Apriori-Spark")
    sc.setLogLevel("WARN")

    txs = (
        sc.textFile(src, minPartitions=npart)
        .map(lambda l: l.strip())
        .filter(lambda l: len(l) > 0)
        .map(lambda l: tuple(sorted(set(l.split(",")))))
        .cache()
    )
    n_tx = txs.count()

    freq_by_size = {}

    # ---- 第 1 轮：单项计数（完全并行）----
    l1 = dict(
        txs.flatMap(lambda t: [(i,) for i in t])
        .map(lambda kv: (kv, 1))
        .reduceByKey(lambda a, b: a + b)
        .filter(lambda kv: kv[1] >= min_sup)
        .collect()
    )
    if not l1:
        print("没有满足支持度的频繁项集", file=sys.stderr)
        sc.stop()
        sys.exit(2)
    freq_by_size[1] = l1

    # ---- 第 k 轮：广播候选集，各分区并行统计 ----
    k = 2
    prev = l1
    while prev:
        candidates = gen_candidates(set(prev.keys()), k)
        if not candidates:
            break
        cand_set = set(candidates)
        bc = sc.broadcast(cand_set)

        counts = dict(
            txs.flatMap(lambda t: [c for c in combinations(t, k) if c in bc.value])
            .map(lambda c: (c, 1))
            .reduceByKey(lambda a, b: a + b)
            .filter(lambda kv: kv[1] >= min_sup)
            .collect()
        )
        if not counts:
            break
        freq_by_size[k] = counts
        prev = counts
        k += 1

    all_freq = {}
    for kk in freq_by_size:
        all_freq.update(freq_by_size[kk])

    rules = build_rules(all_freq)

    # ---- 输出：与串行版格式逐字节一致 ----
    with open(prefix + "_itemsets.txt", "w", encoding="utf-8", newline="\n") as f:
        f.write("# 事务数=%d 最小支持度计数=%d 频繁项集总数=%d\n"
                % (n_tx, min_sup, len(all_freq)))
        for kk in sorted(freq_by_size):
            for itemset in sorted(freq_by_size[kk]):
                f.write("%d\t%s\t%d\n" % (kk, ",".join(itemset), freq_by_size[kk][itemset]))

    with open(prefix + "_rules.txt", "w", encoding="utf-8", newline="\n") as f:
        f.write("# 关联规则数=%d 最小置信度=0.60\n" % len(rules))
        for ant, cons, sup, conf in rules:
            f.write("%s=>%s\t%d\t%.6f\n" % (",".join(ant), ",".join(cons), sup, conf))

    print("事务数: %d (分区数 %d)" % (n_tx, npart))
    print("频繁项集: %d 个" % len(all_freq))
    for kk in sorted(freq_by_size):
        print("  %d-项集: %d" % (kk, len(freq_by_size[kk])))
    print("关联规则: %d 条" % len(rules))

    sc.stop()


if __name__ == "__main__":
    main()
