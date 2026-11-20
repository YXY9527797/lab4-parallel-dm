#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成实验四使用的购物篮事务数据集.

输出格式：每行一条事务，商品之间用英文逗号分隔，无空格。
生成方式：按“购物场景”模板抽样，使商品之间产生真实的关联关系，
这样频繁项集和关联规则才有可解释的意义（而不是纯随机噪声）。
"""
import random

ITEMS = [
    "Bread", "Milk", "Eggs", "Cheese", "Butter", "Yogurt", "Apple", "Banana",
    "Orange", "Grape", "Chicken", "Beef", "Pork", "Fish", "Shrimp", "Rice",
    "Pasta", "Noodles", "Flour", "Sugar", "Salt", "Pepper", "Oil", "Vinegar",
    "Soy_Sauce", "Coffee", "Tea", "Juice", "Beer", "Wine", "Chips", "Nuts",
    "Chocolate", "Cookie", "Ice_Cream", "Detergent", "Soap", "Shampoo", "Towel", "Napkin",
]

# 购物场景模板：一组经常一起购买的商品
SCENARIOS = [
    ["Bread", "Milk", "Eggs", "Butter"],
    ["Bread", "Cheese", "Butter", "Milk"],
    ["Coffee", "Milk", "Sugar", "Cookie"],
    ["Tea", "Sugar", "Cookie", "Chocolate"],
    ["Beef", "Salt", "Pepper", "Oil"],
    ["Chicken", "Oil", "Salt", "Soy_Sauce"],
    ["Fish", "Shrimp", "Soy_Sauce", "Rice"],
    ["Pasta", "Cheese", "Oil", "Vinegar"],
    ["Rice", "Noodles", "Soy_Sauce", "Eggs"],
    ["Apple", "Banana", "Orange", "Yogurt"],
    ["Chips", "Beer", "Nuts"],
    ["Wine", "Cheese", "Grape"],
    ["Detergent", "Soap", "Towel", "Napkin"],
    ["Shampoo", "Soap", "Towel"],
    ["Flour", "Sugar", "Eggs", "Butter"],
    ["Ice_Cream", "Chocolate", "Cookie"],
    ["Juice", "Orange", "Apple"],
    ["Milk", "Yogurt", "Banana"],
]


def main():
    rng = random.Random(2026)
    n_tx = 1500
    lines = []
    for _ in range(n_tx):
        scen = rng.choice(SCENARIOS)
        # 场景内商品按 65%~100% 的概率被一起买走
        keep = [it for it in scen if rng.random() < 0.85]
        if not keep:
            keep = [rng.choice(scen)]
        # 少量随机补充商品，模拟计划外购买
        for _ in range(rng.randint(0, 2)):
            extra = rng.choice(ITEMS)
            if extra not in keep:
                keep.append(extra)
        keep = sorted(set(keep))
        lines.append(",".join(keep))

    with open("transactions.txt", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

    sizes = [len(l.split(",")) for l in lines]
    print("事务数     : %d" % n_tx)
    print("商品种类   : %d" % len(ITEMS))
    print("平均事务长度: %.2f" % (sum(sizes) / len(sizes)))
    print("最长事务   : %d" % max(sizes))


if __name__ == "__main__":
    main()
