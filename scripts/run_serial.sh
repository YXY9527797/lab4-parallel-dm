#!/bin/bash
# 非并行（单机）版：直接在本机跑纯 Python Apriori
# 用法: bash scripts/run_serial.sh [最小支持度计数]
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

MIN_SUP=${1:-15}
mkdir -p results

echo "== 单机 Apriori (min_sup=${MIN_SUP}) =="
time python3 serial/apriori_serial.py data/transactions.txt "$MIN_SUP" results/serial
echo
echo "结果: results/serial_itemsets.txt / results/serial_rules.txt"
