# 实验四 并行化数据挖掘算法设计

大数据管理与分析 课程实验 · 山东大学计算机科学与技术学院

以 **Apriori 关联规则挖掘（频繁项集）** 为对象，分别实现**单机非并行版**与 **Spark 并行化版**，
在伪分布式 Hadoop 环境（HDFS）上运行，两版输出**逐字节完全一致**。

## 实验环境

| 组件 | 版本 |
|---|---|
| 操作系统 | Ubuntu 22.04.5 LTS（VirtualBox 虚拟机，4 vCPU / 4 GB） |
| JDK | OpenJDK 11.0.33 |
| Hadoop | 3.3.6（伪分布式，HDFS） |
| Spark | 3.5.9（local[4]） |
| Python | 3.10 |

## 数据集

`data/transactions.txt`：1500 条购物篮事务，40 种商品，平均事务长度 4.06。
由 `data/gen_transactions.py` 按 18 种"购物场景"模板抽样生成（固定随机种子 2026），
使商品之间存在真实的关联关系，关联规则才具备可解释性。

## 算法

Apriori 逐层挖掘频繁项集：

- 支持度 `support(X) = count(X) / N`，本实验最小支持度计数 `min_sup = 15`（即 1%）；
- 由 k-1 频繁项集**连接 + 剪枝**生成 k 候选集（Apriori-gen）；
- 扫描事务统计候选集计数，保留 `count >= min_sup` 的项集；
- 由频繁项集导出关联规则 `A => B`，置信度 `conf = support(A∪B) / support(A) ≥ 0.6`。

### 并行化设计

Spark 版每一轮迭代：

1. driver 端用 Apriori-gen 生成候选集，`sc.broadcast()` 广播到所有 executor；
2. 事务 RDD 被划分为 4 个分区，各分区**并行**枚举本地事务的 k 元子集，
   过滤出落在候选集中的组合，映射为 `(itemset, 1)` 并做 map 端预聚合；
3. `reduceByKey` 跨分区汇总计数，过滤得到本轮频繁项集；
4. 结果收集回 driver，继续下一轮。

## 运行

```bash
# 1. 生成数据集
cd data && python3 gen_transactions.py && cd ..

# 2. 单机非并行版
bash scripts/run_serial.sh 15

# 3. Spark 并行版（数据先上传 HDFS）
bash scripts/run_spark.sh 15 4

# 4. 对比两版结果
bash scripts/compare.sh
```

## 实验结果

| 指标 | 单机版 | Spark 版 |
|---|---|---|
| 频繁项集总数 | 190 | 190 |
| 1-项集 / 2-项集 / 3-项集 / 4-项集 | 40 / 85 / 53 / 12 | 40 / 85 / 53 / 12 |
| 关联规则数（conf ≥ 0.6） | 257 | 257 |
| 输出文件 SHA256 | `99ffa467…` | `99ffa467…` |

两版输出经 `diff` 比对与 SHA256 校验，**完全一致**。

部分高置信度规则：

```
Chicken,Salt,Soy_Sauce => Oil      sup=49  conf=0.9423
Apple,Banana,Orange    => Yogurt   sup=42  conf=0.9130
Eggs,Flour,Sugar       => Butter   sup=41  conf=0.9111
Bread,Cheese,Milk      => Butter   sup=50  conf=0.9091
```

### 运行耗时

| 实现 | 墙钟时间 |
|---|---|
| 单机版（纯 Python） | 0.13 s |
| Spark 版（local[4]） | 63 s |

数据集体量很小（39 KB），Spark 的时间几乎全部消耗在 JVM 启动、SparkContext 初始化与
任务调度上（约 50–60 s），真正用于计数计算的时间不足 1 s。这说明**并行化的收益取决于数据规模**，
在小数据上并行的固定开销远大于收益；同时 Apriori 的候选集生成在 driver 端串行完成，
也是该实现难以随规模线性扩展的原因之一。

## 目录结构

```
lab4-parallel-dm/
├── data/
│   ├── gen_transactions.py     # 数据集生成
│   └── transactions.txt
├── serial/
│   └── apriori_serial.py       # 单机非并行实现
├── spark/
│   └── apriori_spark.py        # Spark RDD 并行实现
├── scripts/
│   ├── run_serial.sh
│   ├── run_spark.sh
│   └── compare.sh              # diff + SHA256 对比
└── results/
    ├── serial_itemsets.txt  / spark_itemsets.txt
    └── serial_rules.txt     / spark_rules.txt
```

## 正确性说明

两版能够做到逐字节一致，关键在于：

1. **候选生成逻辑完全相同**（同一套 Apriori-gen 连接 + 剪枝规则）；
2. **计数全部使用整数**，不涉及浮点累加，避免了分布式归约顺序带来的误差；
3. 输出前统一按 `(项集长度, 项集字典序)` 排序，规则按 `(置信度降序, 支持度降序, 前件, 后件)` 排序。

## License

MIT
