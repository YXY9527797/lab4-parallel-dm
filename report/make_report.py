# -*- coding: utf-8 -*-
"""生成实验四 并行化数据挖掘算法设计 的实验报告 DOCX"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SONG = "宋体"
MONO = "Consolas"
REPO = "https://github.com/YXY9527797/lab4-parallel-dm"

STU_NO = "202400390056"
NAME = "于昕杨"
CLASS = "24级人工智能1班"
EMAIL = "1849932646@qq.com"


def set_font(run, name=SONG, size=12, bold=False):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:eastAsia"), name)
    rFonts.set(qn("w:ascii"), name)
    rFonts.set(qn("w:hAnsi"), name)


def style_paragraph(p, size=12, spacing=1.25, first_indent=True, space_after=0):
    pf = p.paragraph_format
    pf.line_spacing = spacing
    pf.space_before = Pt(0)
    pf.space_after = Pt(space_after)
    if first_indent:
        pf.first_line_indent = Pt(size * 2)


def add_body(doc, text, size=12, indent=True):
    p = doc.add_paragraph()
    style_paragraph(p, size=size, first_indent=indent)
    r = p.add_run(text)
    set_font(r, SONG, size)
    return p


def add_heading(doc, text, level=1):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing = 1.25
    pf.space_before = Pt(6)
    pf.space_after = Pt(3)
    r = p.add_run(text)
    set_font(r, SONG, 14 if level == 1 else 12, bold=True)
    return p


def add_code(doc, text, size=9):
    for line in text.rstrip("\n").split("\n"):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.line_spacing = 1.0
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        pf.left_indent = Cm(0.6)
        r = p.add_run(line if line else " ")
        set_font(r, MONO, size)


def shade(cell, color="D9E2F3"):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def fixed_widths(table, widths):
    table.autofit = False
    tblPr = table._tbl.tblPr
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tblPr.append(layout)
    for row in table.rows:
        for idx, w in enumerate(widths):
            row.cells[idx].width = w
    for idx, w in enumerate(widths):
        table.columns[idx].width = w


def cell_text(cell, text, bold=False, size=10.5, align=WD_ALIGN_PARAGRAPH.LEFT):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(text)
    set_font(r, SONG, size, bold=bold)


def make_table(doc, headers, rows, widths, size=10.5, center_cols=None):
    center_cols = center_cols or []
    t = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(headers):
        c = t.cell(0, j)
        cell_text(c, h, bold=True, size=size, align=WD_ALIGN_PARAGRAPH.CENTER)
        shade(c)
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            align = WD_ALIGN_PARAGRAPH.CENTER if j in center_cols else WD_ALIGN_PARAGRAPH.LEFT
            cell_text(t.cell(i, j), str(val), size=size, align=align)
    fixed_widths(t, widths)
    return t


def build(path):
    doc = Document()
    for s in doc.sections:
        s.page_width = Cm(21.0)
        s.page_height = Cm(29.7)
        s.top_margin = Cm(2.54)
        s.bottom_margin = Cm(2.54)
        s.left_margin = Cm(3.17)
        s.right_margin = Cm(3.17)

    normal = doc.styles["Normal"]
    normal.font.name = SONG
    normal.font.size = Pt(12)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), SONG)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("计算机科学与技术学院")
    set_font(r, SONG, 16, bold=True)
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.paragraph_format.space_after = Pt(8)
    r2 = p2.add_run("大数据管理与分析  课程实验报告")
    set_font(r2, SONG, 16, bold=True)

    info = [
        ("实验题目", "实验四  并行化数据挖掘算法设计", "学号", STU_NO),
        ("日期", "2026 年 11 月 20 日", "班级", CLASS),
        ("姓名", NAME, "Email", EMAIL),
    ]
    t = doc.add_table(rows=3, cols=4)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    widths = [Cm(2.4), Cm(5.2), Cm(1.8), Cm(5.2)]
    fixed_widths(t, widths)
    for i, row in enumerate(info):
        for j, val in enumerate(row):
            c = t.cell(i, j)
            cell_text(c, val, bold=(j % 2 == 0))
            if j % 2 == 0:
                shade(c)

    doc.add_paragraph()

    # 一、实验目的
    add_heading(doc, "一、实验目的")
    for s in [
        "掌握关联规则挖掘的基本原理，理解支持度、置信度与 Apriori 性质的含义。",
        "掌握把一个串行数据挖掘算法改造成分布式并行算法的方法：找出可并行化的计算部分，"
        "明确哪些状态必须在 driver 端维护。",
        "使用 Spark RDD 实现并行化的 Apriori 频繁项集挖掘，并与单机实现对比，"
        "验证两者结果完全一致。",
        "通过实测运行时间，理解并行化的收益与固定开销之间的关系。",
    ]:
        add_body(doc, s)

    # 二、环境
    add_heading(doc, "二、实验软件和硬件环境")
    env = [
        ("主机环境", "Windows 11，VirtualBox 7.1.8 虚拟机"),
        ("操作系统", "Ubuntu 22.04.5 LTS（4 vCPU / 4 GB 内存 / 25 GB 磁盘）"),
        ("JDK", "OpenJDK 11.0.33"),
        ("Hadoop", "3.3.6，伪分布式部署（HDFS，端口 9000）"),
        ("Spark", "3.5.9（bin-hadoop3），local[4] 模式运行"),
        ("编程语言", "Python 3.10（单机版纯 Python；并行版 PySpark RDD API）"),
    ]
    t = doc.add_table(rows=len(env), cols=2)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    fixed_widths(t, [Cm(3.2), Cm(11.4)])
    for i, (k, v) in enumerate(env):
        c0, c1 = t.cell(i, 0), t.cell(i, 1)
        cell_text(c0, k, bold=True)
        shade(c0)
        cell_text(c1, v)

    doc.add_paragraph()

    # 三、原理和方法
    add_heading(doc, "三、实验原理和方法")
    add_heading(doc, "3.1  关联规则挖掘与 Apriori 算法", level=2)
    add_body(doc, "设 I 为全部商品的集合，D 为事务数据库，每条事务 T 是 I 的一个子集。"
                  "项集 X 的支持度计数 count(X) 是包含 X 的事务条数，支持度为 count(X)/|D|；"
                  "规则 X⇒Y 的置信度为 count(X∪Y)/count(X)。挖掘任务即找出所有支持度不低于"
                  "最小支持度（本实验取计数 15，约 1%）的频繁项集，并由此导出置信度不低于 0.6 的规则。")
    add_body(doc, "Apriori 的核心是反单调性：一个项集频繁，则它的所有子集必然频繁；"
                  "反之，若某项集的某个子集不频繁，该项集一定不频繁。据此逐层搜索：")
    add_code(doc, "L1 = {频繁 1-项集}\n"
                  "for k = 2, 3, ... :\n"
                  "    Ck = apriori_gen(L(k-1))        # 连接 + 剪枝\n"
                  "    for 每条事务 t in D:            # 计数（可并行）\n"
                  "        for 每个 t 的 k 元子集 s:\n"
                  "            if s in Ck: count[s] += 1\n"
                  "    Lk = {s in Ck | count[s] >= min_sup}\n"
                  "    if Lk 为空: break", size=9)

    add_heading(doc, "3.2  单机实现", level=2)
    add_body(doc, "单机版把所有事务读入内存，逐层扫描：对每条事务枚举其 k 元子集，"
                  "只要该子集出现在候选集中就累加计数。候选集用集合（set）组织，"
                  "因此单次判断是 O(1)；相比“对每个候选去扫描所有事务”的朴素写法，"
                  "枚举事务子集在候选集较大时效率高得多。")

    add_heading(doc, "3.3  Spark 并行化设计", level=2)
    add_body(doc, "观察 3.1 的伪代码可以发现：候选集生成必须串行（它依赖上一轮的完整结果，"
                  "且规模不大），而计数是对每条事务的独立操作，天然可并行。"
                  "据此把算法拆成 driver 端与 executor 端两部分：")
    add_body(doc, "driver 端负责 apriori_gen 生成候选集，并通过 broadcast 广播到所有 executor；"
                  "executor 端把本地分区内的事务展开成 k 元子集，与广播的候选集求交，"
                  "产出 (候选项集, 1) 并做 map 端预聚合；最后由 reduceByKey 跨分区汇总计数：")
    add_code(doc, "candidates = apriori_gen(L[k-1], k)          # driver 端串行\n"
                  "bc = sc.broadcast(set(candidates))            # 广播到所有 executor\n"
                  "counts = (txs.flatMap(lambda t: [c for c in combinations(t, k)\n"
                  "                                 if c in bc.value])\n"
                  "             .map(lambda c: (c, 1))\n"
                  "             .reduceByKey(lambda a, b: a + b)     # 跨分区汇总\n"
                  "             .filter(lambda kv: kv[1] >= min_sup)\n"
                  "             .collect())\n"
                  "L[k] = dict(counts)", size=9)
    add_body(doc, "第一轮（单项计数）不需要候选集，直接用 flatMap + reduceByKey 完成，"
                  "并行度更高。")

    # 四、步骤
    add_heading(doc, "四、实验步骤")
    add_heading(doc, "4.1  构造数据集", level=2)
    add_body(doc, "实验允许自备数据集。为避免纯随机数据挖不出有意义的规则，"
                  "按 18 种“购物场景”模板抽样生成事务：每个场景是一组经常一起购买的商品，"
                  "场景内商品以 85% 的概率被同时买走，再随机补充 0~2 件计划外商品。"
                  "最终数据集包含 1500 条事务、40 种商品，平均事务长度 4.06，最长 6。")
    add_code(doc, "Cookie,Tea\n"
                  "Banana,Milk,Shampoo,Yogurt\n"
                  "Bread,Butter,Eggs,Flour,Sugar\n"
                  "Chocolate,Cookie,Ice_Cream,Soy_Sauce", size=9)

    add_heading(doc, "4.2  运行单机版", level=2)
    add_body(doc, "直接在本机用 python3 运行，不依赖任何分布式组件：")
    add_code(doc, "python3 serial/apriori_serial.py data/transactions.txt 15 results/serial", size=9)
    add_body(doc, "耗时约 0.13 秒，得到 190 个频繁项集和 257 条关联规则。")

    add_heading(doc, "4.3  运行并行版", level=2)
    add_body(doc, "先把数据集上传到 HDFS 伪分布式集群，再用 spark-submit 提交，"
                  "数据从 HDFS 读入并划分成 4 个分区并行处理：")
    add_code(doc, "hdfs dfs -put data/transactions.txt /lab4/input/\n"
                  "spark-submit --master \"local[4]\" spark/apriori_spark.py \\\n"
                  "    hdfs://localhost:9000/lab4/input/transactions.txt 15 results/spark 4", size=9)
    add_body(doc, "整机墙钟时间约 63 秒（其中绝大部分为 JVM 启动与 SparkContext 初始化）。")

    add_heading(doc, "4.4  一致性验证", level=2)
    add_body(doc, "两版实现输出的文件格式完全相同，直接做字节级比对：先 diff，再用 SHA256 校验摘要。"
                  "由于计数全部为整数、输出前统一排序，理论上应当逐字节相同，"
                  "任何一处不一致都会在 diff 中暴露。")

    # 五、结果
    add_heading(doc, "五、实验结果与分析")
    add_heading(doc, "5.1  频繁项集挖掘结果", level=2)
    make_table(doc,
               ["项集长度", "频繁项集个数", "示例项集（支持度计数）"],
               [["1", "40", "Bread (166)、Banana (174)"],
                ["2", "85", "Cookie,Sugar (140)、Rice,Soy_Sauce (139)"],
                ["3", "53", "Bread,Cheese,Milk (50)、Apple,Banana,Orange (42)"],
                ["4", "12", "Bread,Butter,Cheese,Milk (50)、Eggs,Noodles,Rice,Soy_Sauce (61)"],
                ["合计", "190", "—"]],
               [Cm(2.2), Cm(3.0), Cm(9.4)], center_cols=[0, 1])

    doc.add_paragraph()
    add_body(doc, "一个有意思的验证：挖出的 12 个频繁 4-项集，恰好对应生成数据时使用的 18 个购物场景"
                  "模板中支持度足够高的那些（如「面包+黄油+奶酪+牛奶」「鸡蛋+面条+米+酱油」），"
                  "说明算法确实还原出了数据中潜藏的结构，而不是随机噪声。")

    add_heading(doc, "5.2  关联规则", level=2)
    add_body(doc, "在 190 个频繁项集基础上，枚举所有非空真子集作为前件，计算置信度并筛选 ≥ 0.6，"
                  "共得到 257 条规则，其中置信度 ≥ 0.9 的有 8 条。置信度最高的 5 条如下：")
    make_table(doc,
               ["关联规则", "支持度计数", "置信度"],
               [["Chicken,Salt,Soy_Sauce ⇒ Oil", "49", "0.9423"],
                ["Apple,Banana,Orange ⇒ Yogurt", "42", "0.9130"],
                ["Eggs,Flour,Sugar ⇒ Butter", "41", "0.9111"],
                ["Bread,Cheese,Milk ⇒ Butter", "50", "0.9091"],
                ["Apple,Banana ⇒ Yogurt", "49", "0.9074"]],
               [Cm(7.6), Cm(3.2), Cm(3.6)], center_cols=[1, 2])
    doc.add_paragraph()
    add_body(doc, "这些规则与购物场景模板高度吻合（例如「鸡肉+盐+酱油 ⇒ 食用油」对应炒菜场景），"
                  "规则的可解释性反过来印证了挖掘结果的合理性。")

    add_heading(doc, "5.3  两版结果一致性", level=2)
    make_table(doc,
               ["文件", "行数", "SHA256"],
               [["serial_itemsets.txt", "190", "99ffa467…e2839e"],
                ["spark_itemsets.txt", "190", "99ffa467…e2839e"],
                ["serial_rules.txt", "257", "781d4afc…969f7"],
                ["spark_rules.txt", "257", "781d4afc…969f7"]],
               [Cm(5.0), Cm(2.2), Cm(7.4)], center_cols=[1])
    doc.add_paragraph()
    add_body(doc, "diff 显示两个文件逐字节相同，SHA256 摘要完全一致，满足实验“两种结果需完全一致”的要求。"
                  "能做到这一点的原因有三：候选集生成逻辑完全一致；计数全部使用整数，"
                  "不存在浮点归约顺序带来的误差；输出前统一按 (项集长度, 项集字典序) 排序，"
                  "而规则的排序键是 (置信度降序, 支持度降序, 前件, 后件)。")

    add_heading(doc, "5.4  运行时间与并行化分析", level=2)
    make_table(doc,
               ["实现方式", "运行环境", "墙钟时间", "说明"],
               [["单机版", "本机 Python，单进程", "0.13 s", "纯计算"],
                ["Spark 版", "local[4]，数据在 HDFS", "63 s", "其中约 50–60 s 为 JVM 启动与调度"]],
               [Cm(2.6), Cm(4.6), Cm(2.6), Cm(4.8)], center_cols=[0, 2])
    doc.add_paragraph()
    add_body(doc, "并行版反而慢了近 500 倍，这个结果乍看反直觉，但原因很清楚："
                  "数据集只有 39 KB、1500 条事务，单机完成全部计算只需 0.13 秒；"
                  "而 Spark 光是启动 JVM、初始化 SparkContext、启动 SparkUI 就要几十秒，"
                  "这部分是与数据规模无关的固定开销。当数据规模放大到单机内存放不下、"
                  "或单轮计算需要数分钟以上时，这部分开销才会被摊薄，并行收益才会显现。")
    add_body(doc, "另一方面也要看到，Apriori 本身并不适合“完全并行化”：候选集生成依赖上一轮的完整结果，"
                  "必须在 driver 端串行完成，随着 k 增大候选集规模指数增长，这部分会成为瓶颈。"
                  "真正能线性扩展的只是“计数”这一步。如果要在大规模数据上取得更好的加速比，"
                  "应当考虑 FP-Growth 这类只需两次扫描、不需要候选集的算法，"
                  "或把数据划分与本地频繁项集挖掘结合的两阶段并行方案。")

    # 六、问题
    add_heading(doc, "六、实验过程中的问题与解决")
    add_body(doc, "问题 1：如何保证两版结果“完全一致”而不是“差不多一致”？", indent=True)
    add_body(doc, "分析：分布式实现最容易出问题的地方有三处——候选集生成顺序不同导致结果集不同、"
                  "浮点累加顺序不同导致末位差异、输出顺序不同导致 diff 失败。", indent=True)
    add_body(doc, "解决：一是让两版共用完全相同的 apriori_gen 逻辑（连接时比较前 k-2 项、"
                  "并校验全部 k-1 子集频繁）；二是全程使用整数计数，从根上消除浮点误差；"
                  "三是输出前强制排序，并用 diff + SHA256 双重校验。最终两版文件逐字节相同。", indent=True)

    add_body(doc, "问题 2：朴素写法（对每个候选扫描全部事务）太慢，如何优化？", indent=True)
    add_body(doc, "分析：40 种商品会产生 780 个 2-候选集，若对每个候选都扫一遍 1500 条事务，"
                  "需要 117 万次集合包含判断，且每次判断都要构造事务的集合。", indent=True)
    add_body(doc, "解决：反转思路——不再“按候选找事务”，而是“按事务找候选”："
                  "预先枚举每条事务的 k 元子集（平均事务长度仅 4.06，子集数很少），"
                  "再判断该子集是否在候选集中。单机版耗时降到 0.13 秒，并行版也沿用同一策略，"
                  "保证了结果一致。", indent=True)

    add_body(doc, "问题 3：Spark 提交后报 “hostname resolves to a loopback address” 警告，是否影响运行？", indent=True)
    add_body(doc, "分析：虚拟机 /etc/hosts 中主机名映射到 127.0.1.1，Spark 检测到后会改用实际网卡地址"
                  "（10.0.2.15）绑定。这是 VirtualBox NAT 环境的正常现象。", indent=True)
    add_body(doc, "解决：不影响运行，任务正常完成。若要消除警告，可在 spark-env.sh 中显式设置 "
                  "SPARK_LOCAL_IP。本实验数据量小、只在单机内通信，保持默认即可。", indent=True)

    # 七、结论
    add_heading(doc, "七、结论分析与体会")
    add_body(doc, "本实验以 Apriori 关联规则挖掘为对象，分别实现了单机版和 Spark 并行版。"
                  "在 1500 条事务、40 种商品的数据集上（最小支持度计数 15、最小置信度 0.6），"
                  "两版都挖掘出 190 个频繁项集和 257 条关联规则，输出文件逐字节相同、SHA256 一致，"
                  "完全满足实验要求。")
    add_body(doc, "通过这次实验，我对“并行化”有了更具体的认识。并行化并不是简单地把代码搬到集群上跑："
                  "首先要识别算法中哪些步骤可以并行（这里的计数），哪些必须串行（候选集生成），"
                  "然后用广播、分区、归约等手段把可并行的部分真正拆开。"
                  "更重要的体会是，并行化有明确的适用边界——对于 39 KB 的数据，"
                  "Spark 的启动开销让总耗时从 0.13 秒涨到 63 秒。"
                  "只有当数据规模大到单机处理不动时，并行带来的收益才可能超过它的固定成本。")
    add_body(doc, "另外，把“两版结果完全一致”作为硬性验收标准，其实是非常有效的工程约束。"
                  "它逼着我去思考每一处可能引入差异的细节——候选生成、数值类型、输出排序，"
                  "从而写出更严谨的实现。这种“用另一种独立实现互相印证”的方法，"
                  "在调试分布式程序时尤其有价值。")

    # 八、仓库
    add_heading(doc, "八、代码仓库")
    add_body(doc, "本实验全部代码、数据集与运行结果已整理并上传至 GitHub 公开仓库：")
    p = doc.add_paragraph()
    style_paragraph(p, first_indent=False)
    r = p.add_run(REPO)
    set_font(r, SONG, 12)
    r.font.color.rgb = RGBColor(0x05, 0x63, 0xC1)
    r.font.underline = True

    doc.save(path)
    print("saved:", path)


if __name__ == "__main__":
    out = r"C:\Users\ASUS\Desktop\大数据\202400390056-于昕杨-实验四.docx"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    build(out)
