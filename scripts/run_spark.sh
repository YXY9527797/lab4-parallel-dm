#!/bin/bash
# 并行化版：数据放 HDFS，用 Spark RDD 在 local[4] 上并行统计
# 用法: bash scripts/run_spark.sh [最小支持度计数] [分区数]
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export HADOOP_HOME=/opt/hadoop-3.3.6
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export SPARK_HOME=/opt/spark-3.5.9-bin-hadoop3
export PATH=$HADOOP_HOME/bin:$SPARK_HOME/bin:$PATH

MIN_SUP=${1:-15}
NPART=${2:-4}
mkdir -p results

echo "== 上传数据集到 HDFS =="
hdfs dfs -rm -r -f /lab4/input >/dev/null 2>&1
hdfs dfs -mkdir -p /lab4/input
hdfs dfs -put -f data/transactions.txt /lab4/input/
hdfs dfs -ls /lab4/input

echo
echo "== Spark Apriori (min_sup=${MIN_SUP}, partitions=${NPART}) =="
time spark-submit --master "local[${NPART}]" \
    spark/apriori_spark.py \
    hdfs://localhost:9000/lab4/input/transactions.txt \
    "$MIN_SUP" results/spark "$NPART"

echo
echo "结果: results/spark_itemsets.txt / results/spark_rules.txt"
