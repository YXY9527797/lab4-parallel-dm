#!/bin/bash
# 对比两版结果：必须逐字节相同
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

echo "== 频繁项集对比 =="
if diff -q results/serial_itemsets.txt results/spark_itemsets.txt >/dev/null 2>&1; then
    echo "完全一致（逐字节相同）"
else
    echo "存在差异:"
    diff results/serial_itemsets.txt results/spark_itemsets.txt | head -20
fi

echo
echo "== 关联规则对比 =="
if diff -q results/serial_rules.txt results/spark_rules.txt >/dev/null 2>&1; then
    echo "完全一致（逐字节相同）"
else
    echo "存在差异:"
    diff results/serial_rules.txt results/spark_rules.txt | head -20
fi

echo
echo "== SHA256 =="
sha256sum results/serial_itemsets.txt results/spark_itemsets.txt \
          results/serial_rules.txt results/spark_rules.txt

echo
echo "== 规模 =="
echo "频繁项集行数: $(grep -vc '^#' results/serial_itemsets.txt)"
echo "关联规则行数: $(grep -vc '^#' results/serial_rules.txt)"
