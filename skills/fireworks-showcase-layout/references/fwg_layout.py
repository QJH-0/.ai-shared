"""fireworks-tech-graph 的版式辅助模块（本项目共用）。

存在意义：`fireworks-tech-graph` 的 `render` 在 `quality_profile="showcase"` 下有一组硬门禁
（文本必须放得下、边不得出现 <16px 微段、桥接交叉数必须为 0、单边折点 ≤2、节点间距 ≥40px），
手填坐标极易反复撞门禁。本模块把四条最容易踩的规则固化下来：

1. **节点尺寸按文本反算** —— 渲染器给节点的文本预算是 `width - 24`，度量走
   `fireworks_geometry.estimate_text_width`（CJK=1.0 单位、空格 0.36、其余 0.58，乘 weight 1.08）。
   宽度不够会先缩字号，缩到下限仍放不下就在 strict 模式下直接报错。高度则按行数走
   `NODE_LINE_HEIGHT`（与渲染器同一常量），行数越多节点越高。
2. **同行节点共享 y 与高度** —— 水平连线天然端口对齐，不会产生微段。
3. **容器内芯片与主链节点垂直居中** —— 芯片中心若与主链中心差几像素，进出容器的连线就会出现微段。
4. **多行正文用 `body`** —— 节点的 title/subtitle/body 三部分在渲染器里作为一个整块垂直居中，
   行距固定 `NODE_LINE_HEIGHT`。本模块的 `natural_height` 必须与之同源，否则末行会压出节点下沿。
5. **同排高度不等就按中心对齐** —— 一律顶对齐会让水平连线的端口差出半个高度差，
   几像素的落差就是一条微段（`emit_centered` 负责这件事）。

另注两条契约限制：容器不能作为连线端点（须接到容器内的真实节点）；容器标签会被强制转大写。
容器**只有标题头**是路由障碍（`container_header_bounds`），容器本体不是——所以边可以自由穿越容器边框，
但任何从容器顶部进入首芯片的连线都要给标题头让路（见 `panel_pad_for`）。
"""

import importlib.util
import math
import pathlib
import sys

SKILL_ROOT = pathlib.Path(r"C:\Users\20448\.ai-shared\skills\fireworks-tech-graph")

_spec = importlib.util.spec_from_file_location(
    "fwg_geometry", SKILL_ROOT / "scripts" / "fireworks_geometry.py"
)
geo = importlib.util.module_from_spec(_spec)
sys.modules["fwg_geometry"] = geo  # dataclass 装饰器需要能从 sys.modules 取回本模块
_spec.loader.exec_module(geo)

# 渲染器的样式表是边色的唯一来源：图例色块与线色都从它取，图例才不会说谎。
# 顺带解决一个静默回落——`arrow_colors` 里没有的 flow 名会被当成 control 上色，
# 而箭头 marker 是按色值反查的，色值不在表里就退化成 control 的箭头。
_style_path = SKILL_ROOT / "scripts" / "generate-from-template.py"
sys.path.insert(0, str(_style_path.parent))
_style_spec = importlib.util.spec_from_file_location("fwg_template", _style_path)
template = importlib.util.module_from_spec(_style_spec)
sys.modules["fwg_template"] = template
_style_spec.loader.exec_module(template)

# 与渲染器 generate-from-template.py 的 NODE_LINE_HEIGHT 必须一致（多行正文的行距）
NODE_LINE_HEIGHT = 17.0
HEIGHT_PADDING = 30.0
MIN_NODE_HEIGHT = 56

TEXT_PADDING = 24.0
WEIGHT = 1.08
# 节点标题的渲染 preferred 由 node["title_size"] 决定，这里统一钉成同一字号，
# 否则宽度富余的节点会渲染成 18px、紧的渲染成 16px，同一行里字号不齐。
TITLE_SIZE = 16.0
SUB_PREF = 12.0
BODY_PREF = 11.5

GAP_LABELED = 75   # 连线上要放 badge 标签
GAP_PLAIN = 40     # showcase 构图合约的最小节点间距
PANEL_PAD = 30

# 语义角色 → (fill, stroke)，沿用原文档的配色语义
ROLES = {
    "io":      ("#eff6ff", "#3b82f6"),  # 输入输出
    "encoder": ("#fff7ed", "#f97316"),  # 编码器 / 降维卷积
    "sep":     ("#f0fdf4", "#16a34a"),  # 分离器 / TCN 主干
    "spk":     ("#faf5ff", "#8b5cf6"),  # 说话人分支
    "decoder": ("#fefce8", "#eab308"),  # 解码器
    "adapt":   ("#f7fee7", "#84cc16"),  # 乘法自适应
    "quant":   ("#fef2f2", "#dc2626"),  # 量化模块
    "norm":    ("#f9fafb", "#9ca3af"),  # 归一化 / 相加
    "skip":    ("#faf5ff", "#8b5cf6"),  # Skip / 残差
    "out":     ("#fefce8", "#f59e0b"),  # 输出级
}

# 语义 flow → 调色板键。teacher（教师 / 蒸馏）在调色板里没有同名项，借 write 的绿色；
# quant（量化机制标注）借 neutral 的灰——标注边是次要信息，灰底虚线读起来最不抢戏。
FLOW_KEYS = {
    "control":  "control",
    "data":     "data",
    "feedback": "feedback",
    "teacher":  "write",
    "quant":    "neutral",
}


def flow_color(style, flow):
    palette = template.STYLE_PROFILES[int(style)]["arrow_colors"]
    return palette[FLOW_KEYS.get(flow, "control")]


CONTAINER_FILL = "#fbfcfe"
CONTAINER_STROKE = "#dbeafe"

# 深色样式的节点配色（边色不在这里，边色一律取渲染器样式表的 arrow_colors）
DARK_PALETTES = {
    3: dict(canvas="#0a1628", container=("#0b1a30", "#1b3a5c"),
            roles={k: ("#0d1f3c", s) for k, (_, s) in ROLES.items()}),
    4: dict(canvas="#ffffff", container=("#ffffff", "#d1d5db"),
            roles={k: ("#f9fafb", "#e5e7eb") for k in ROLES}),
}


def spec_parts(spec):
    """节点描述可写 3/4/5 元组：(id, role, title[, sublabel[, body]])。

    body 允许是字符串（单行）或字符串序列；两者都归一成 list，空值归一成 []。
    """
    nid, role, title = spec[0], spec[1], spec[2]
    sub = spec[3] if len(spec) > 3 else None
    body = spec[4] if len(spec) > 4 else None
    if isinstance(body, str):
        body = [body]
    return nid, role, title, sub, [str(line) for line in (body or []) if str(line).strip()]


def natural_width(title, sublabel=None, body=None):
    """渲染器在 width-24 的预算内放不下就会截断，故宽度由此反算（取各行的最大值）。

    末尾 +2 是安全余量：度量是启发式的，贴着预算边缘容易在真实字体下被截断。
    """
    width = geo.estimate_text_width(title, TITLE_SIZE, weight=WEIGHT) + TEXT_PADDING
    if sublabel:
        width = max(width, geo.estimate_text_width(sublabel, SUB_PREF, weight=WEIGHT) + TEXT_PADDING)
    for line in (body or []):
        width = max(width, geo.estimate_text_width(line, BODY_PREF, weight=WEIGHT) + TEXT_PADDING)
    return int(math.ceil(width)) + 2


def verbatim(nid, role, lines):
    """原图节点的多行文字 → 节点描述元组：首行进 title，其余行全部进 body。

    逐行一一对应，不合并、不省略——这是「保持原图文字一致」的落点。
    """
    text = [str(line).strip() for line in lines if str(line).strip()]
    return (nid, role, text[0], None, text[1:])


def shift_row(placed, node_id, target_center):
    """整行平移，使 node_id 的水平中心落在 target_center 上。

    平移量保持浮点：竖直连线两端若差 0.5px 就会被判成微段，取整反而会引入这个差值。
    """
    anchor = next(item for item in placed if item["id"] == node_id)
    dx = target_center - (anchor["x"] + anchor["width"] / 2)
    for item in placed:
        item["x"] += dx
    return dx


def natural_height(sublabel=None, body=None):
    """行数 → 高度。与渲染器的整块居中公式同源（见 NODE_LINE_HEIGHT 注释）。"""
    lines = 1 + (1 if sublabel else 0) + len(body or [])
    return max(MIN_NODE_HEIGHT, int(math.ceil(NODE_LINE_HEIGHT * lines + HEIGHT_PADDING)))


def place_row(nodes, x0, gaps):
    """把一行节点按自然宽度横向摆开。

    nodes: 3/4/5 元组序列；gaps 长度为 len(nodes)-1。
    返回 (placed, 行总宽)；placed 每项含 x / width / height，y 由调用方统一指定。
    """
    placed, cursor = [], x0
    for i, spec in enumerate(nodes):
        nid, role, title, sub, body = spec_parts(spec)
        w = natural_width(title, sub, body)
        placed.append(dict(id=nid, role=role, title=title, sub=sub, body=body,
                           x=cursor, width=w, height=natural_height(sub, body)))
        cursor += w
        if i < len(nodes) - 1:
            cursor += gaps[i]
    return placed, cursor - x0


def row_height(placed):
    """一行统一高度：取该行最大自然高度，水平连线才能端口对齐。"""
    return max(item["height"] for item in placed)


def gap_for(label=None):
    """带 badge 标签的连线要留出标签宽度，否则 render 报 no collision-free label position。"""
    if not label:
        return GAP_PLAIN
    badge = geo.estimate_text_width(label, 11, weight=WEIGHT) + 14
    return max(GAP_LABELED, int(math.ceil(badge)) + 18)


def align_row_under(nodes, parent, gaps):
    """把一行放到某节点下方，并保证**首个节点**的水平中心与 parent 完全一致。

    节点宽度是文本反算出来的整数，奇偶性不匹配时中心会差 0.5px，
    渲染器就会在竖直连线上判出 <16px 的微段。这里把首节点宽度调成与父节点同奇偶。
    """
    first = spec_parts(nodes[0])
    base = natural_width(first[2], first[3], first[4])
    first_w = base + 1 if (base % 2) != (int(parent["width"]) % 2) else base
    x0 = int(parent["x"] + (parent["width"] - first_w) / 2)
    placed, cursor = [], x0
    for i, spec in enumerate(nodes):
        nid, role, title, sub, body = spec_parts(spec)
        w = first_w if i == 0 else natural_width(title, sub, body)
        placed.append(dict(id=nid, role=role, title=title, sub=sub, body=body,
                           x=cursor, width=w, height=natural_height(sub, body)))
        cursor += w
        if i < len(nodes) - 1:
            cursor += gaps[i]
    return placed, x0


def centered_row(nodes, center_x, gaps):
    """整行水平居中到 center_x（宽度按自然值求和）。用于独立成排的分支。"""
    placed, total = place_row(nodes, 0, gaps)
    x0 = int(center_x - total / 2)
    for item in placed:
        item["x"] += x0
    return placed, total


def same_parity(width, reference):
    """把 width 调成与 reference 同奇偶，竖直连线的端口偏移才不会出现 0.5px 微段。"""
    return width + 1 if (width % 2) != (reference % 2) else width


PANEL_HEADER = 44
HEADER_CLEARANCE = 8.0
# 渲染器把标题/副标题画在画布顶部固定位置（副标题基线 y=82、字号 14），且**不是**路由障碍，
# 所以构图门禁查不出「容器标题头压到副标题」。按字形盒估下界：副标题底 ≈ 86，
# 标题头文字高 ≈ 10，留 6px 间隙 ⇒ 标题头基线 ≥ 102；标题头基线 = 容器顶 + 24 ⇒ 容器顶 ≥ 78。
# 这里取 90（多留 12px 余量），既是摆放值也是校验下界——含容器的带据此下移。
CONTAINER_TOP_MIN = 90.0


def panel_pad_for(label, first_chip_width, base=PANEL_PAD):
    """容器标题头在左上角占一块路由障碍（起于 x+8、宽为标签宽+30、高 30，另有 6px 间隙）。

    从容器**顶部**进入首芯片的连线必须落在障碍右侧，否则路由器会先绕到障碍边上、
    再横移一小段扎进芯片——表现就是折点超标 + 竖线上一段几像素的微段。
    把左内边距顶到障碍右侧即可；只有确实从顶部进线的容器才需要调用它。
    """
    reserved = geo.estimate_text_width(str(label), 13) + 30
    need = 8 + reserved + 6 + HEADER_CLEARANCE - first_chip_width / 2
    return int(max(base, math.ceil(need)))


def band(x0, items, gap=GAP_PLAIN, pad=PANEL_PAD, header=PANEL_HEADER):
    """按顺序摆放普通节点与容器，返回 (nodes, boxes, 总宽)。

    items 元素为 `("node", spec)` 或 `("box", box_id, label, [spec, ...], {opts})`；
    opts 目前支持 `top_entry`（有连线从容器顶部进入首芯片 → 自动放宽左内边距）。
    返回的 x 已定位；y 由调用方按带顶统一给（见 emit_band）。
    """
    cursor, nodes, boxes = x0, [], []
    for item in items:
        if item[0] == "node":
            nid, role, title, sub, body = spec_parts(item[1])
            width = natural_width(title, sub, body)
            nodes.append(dict(id=nid, role=role, title=title, sub=sub, body=body,
                              x=cursor, width=width, height=natural_height(sub, body)))
            cursor += width + gap
        else:
            _, box_id, label, specs = item[0], item[1], item[2], item[3]
            opts = item[4] if len(item) > 4 else {}
            first = spec_parts(specs[0])
            box_pad = (panel_pad_for(label, natural_width(first[2], first[3], first[4]), pad)
                       if opts.get("top_entry") else pad)
            chips, inner_w = place_row(specs, cursor + box_pad, [gap] * (len(specs) - 1))
            boxes.append(dict(id=box_id, label=label, x=cursor, pad=box_pad, header=header,
                              width=inner_w + 2 * box_pad, chips=chips))
            cursor += boxes[-1]["width"] + gap
    return nodes, boxes, cursor - gap - x0


def band_height(nodes, boxes):
    """一条带的高度：普通节点与容器芯片取最大自然高度，横向连线才端口对齐。"""
    heights = [n["height"] for n in nodes]
    for box in boxes:
        heights.extend(chip["height"] for chip in box["chips"])
    return max(heights)


def emit_band(fig, nodes, boxes, y, height):
    """把一条带落到画布：节点与容器芯片共用 y，容器向上留出标题头。"""
    for n in nodes:
        fig.node(n["id"], n["role"], n["x"], y, n["width"], height,
                 n["title"], n["sub"], n["body"])
    for box in boxes:
        fig.container(box["id"], None, box["label"], box["x"], y - box["header"],
                      box["width"], box["header"] + height + box["pad"])
        for chip in box["chips"]:
            fig.node(chip["id"], chip["role"], chip["x"], y, chip["width"], height,
                     chip["title"], chip["sub"], chip["body"], parent=box["id"])


def emit_centered(fig, placed, center_y, parent=None):
    """按各自自然高度、以 center_y 为垂直中心落成节点。

    同排节点高度不等时（例如掩码侧的三级节点）必须按中心对齐，
    否则水平连线两端端口会差半个高度差，被判成微段。
    """
    for item in placed:
        item["y"] = center_y - item["height"] / 2
        fig.node(item["id"], item["role"], item["x"], item["y"],
                 item["width"], item["height"], item["title"], item["sub"], item["body"], parent)


def center_of(placed, node_id):
    node = next(item for item in placed if item["id"] == node_id)
    return node["x"] + node["width"] / 2


def stack(placed, x, top, gap=GAP_PLAIN):
    """把一批节点竖直堆在同一列（容器内 direction TB 的子图用它）。

    宽度取最大值并统一，堆叠高度 = Σheight + gap×(n-1)。
    """
    width = max(item["width"] for item in placed)
    cursor = top
    for item in placed:
        item["x"], item["width"], item["y"] = x, width, cursor
        cursor += item["height"] + gap
    return cursor - gap - top



class Figure:
    """按显式坐标拼装 fireworks-tech-graph 的契约 JSON。"""

    def __init__(self, name, title, subtitle, style=1):
        self.name = name
        self.title = title
        self.subtitle = subtitle
        self.style = style
        self.containers = []
        self.nodes = []
        self.arrows = []
        self.legend = []

    # ---- 结构 ----
    def panel(self, pid, label, x, y, width, height):
        # preserve_case：渲染器默认把容器标签转大写，会让原图文案（如 Stage1）失真。
        self.containers.append(dict(id=pid, x=x, y=y, width=width, height=height,
                                    label=label, preserve_case=True))
        return pid

    def container(self, cid, parent, label, x, y, width, height):
        self.containers.append(dict(id=cid, parent=parent, x=x, y=y,
                                    width=width, height=height, label=label,
                                    preserve_case=True))
        return cid

    def node(self, nid, role, x, y, width, height, title, sub=None, body=None, parent=None):
        fill, stroke = ROLES[role]
        item = dict(id=nid, kind="round", x=x, y=y, width=width, height=height,
                    label=title, fill=fill, stroke=stroke, flat=True,
                    title_size=TITLE_SIZE)
        if sub:
            item["sublabel"] = sub
        if body:
            item["body"] = list(body)
        if parent:
            item["parent"] = parent
        self.nodes.append(item)
        return nid

    def row(self, nodes, x0, y, gaps, parent=None, height=None):
        """摆一行并落成节点，返回 placed 列表（含 x / width / height）。"""
        placed, _ = place_row(nodes, x0, gaps)
        h = height or row_height(placed)
        for item in placed:
            self.node(item["id"], item["role"], item["x"], y, item["width"], h,
                      item["title"], item["sub"], item["body"], parent)
        return placed

    def place(self, placed, y, height=None, parent=None):
        """落成一批已摆好 x 的节点（placed 来自 place_row / centered_row）。"""
        h = height or row_height(placed)
        for item in placed:
            self.node(item["id"], item["role"], item["x"], y, item["width"], h,
                      item["title"], item["sub"], item["body"], parent)
        return placed

    def shift(self, dx=0, dy=0):
        """整体平移（用于负坐标归位）。容器与节点同步移动，相对关系不变。"""
        if not dx and not dy:
            return
        for node in self.nodes:
            node["x"] += dx
            node["y"] += dy
        for box in self.containers:
            box["x"] += dx
            box["y"] += dy

    def bounds(self):
        """所有节点的 x 区间，用于负坐标检测与画布宽度推算。"""
        left = min(n["x"] for n in self.nodes)
        right = max(n["x"] + n["width"] for n in self.nodes)
        return left, right

    # ---- 连线 ----
    def edge(self, eid, src, dst, flow="control", label=None,
             sp="right", tp="left", **kw):
        # 显式写 color：线色与图例色块同源，箭头 marker 也才查得到对应色值
        item = dict(id=eid, source=src, target=dst, flow=flow, color=flow_color(self.style, flow),
                    source_port=sp, target_port=tp)
        if label:
            item["label"] = label
        item.update(kw)
        self.arrows.append(item)

    def chain(self, prefix, ids, flow="control", labels=None):
        for i in range(len(ids) - 1):
            self.edge(f"{prefix}{i + 1}", ids[i], ids[i + 1], flow,
                      labels[i] if labels else None)

    # ---- 装配 ----
    def add_legend(self, entries):
        """entries: [(flow, 中文说明), ...]"""
        for flow, text in entries:
            self.legend.append(dict(flow=flow, label=text, color=flow_color(self.style, flow)))

    def build(self, width, height, legend_xy, footer_text):
        palette = DARK_PALETTES.get(self.style)
        containers = [dict(c) for c in self.containers]
        if palette:
            cf, cs = palette["container"]
            for c in containers:
                c["fill"], c["stroke"] = cf, cs
            for n in self.nodes:
                n["fill"], n["stroke"] = palette["roles"][_role_of(n)]
        lx, ly = legend_xy
        footer_w = geo.estimate_text_width(footer_text, 12) + 40
        return {
            "schema_version": 1,
            "mode": "architecture",
            "template_type": "architecture",
            "style": self.style,
            "quality_profile": "showcase",
            "text_policy": "strict",
            "width": width,
            "height": height,
            "title": self.title,
            "subtitle": self.subtitle,
            "containers": containers,
            "nodes": self.nodes,
            "arrows": self.arrows,
            "legend_orientation": "horizontal",
            "legend_x": lx,
            "legend_y": ly,
            "legend_locked": True,
            "legend": self.legend,
            "footer": footer_text,
            "footer_x": width - footer_w,
            "footer_y": ly + 4,
        }


def _role_of(node):
    for role, (fill, stroke) in ROLES.items():
        if node.get("fill") == fill and node.get("stroke") == stroke:
            return role
    return "norm"


def write(fig, out_dir, width, height, legend_xy, footer_text):
    import json
    data = fig.build(width, height, legend_xy, footer_text)
    path = pathlib.Path(out_dir) / f"{fig.name}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path, data


def render_and_check(out_dir, names, python=None):
    """渲染 + 跑 5 项 check + 读排版报告，返回 {name: (render_ok, check_ok, 摘要)}。

    摘要里带 `text=完整/截断`：截断会被 strict 模式拦下，但 report 模式能列出具体是哪几行，
    排查时先看这里再去改宽度。
    """
    import json
    import subprocess

    exe = python or sys.executable
    fw = SKILL_ROOT / "scripts" / "fireworks.py"
    results = {}
    for name in names:
        src = pathlib.Path(out_dir) / f"{name}.json"
        svg = pathlib.Path(out_dir) / f"{name}.svg"
        report_path = pathlib.Path(out_dir) / f"{name}.report.json"
        r = subprocess.run([exe, str(fw), "render", "architecture", str(src), str(svg),
                            "--report", str(report_path)],
                           capture_output=True, text=True, encoding="utf-8")
        if r.returncode != 0:
            results[name] = (False, False, (r.stdout or "") + (r.stderr or ""))
            continue
        text_state = "?"
        try:
            typography = json.loads(report_path.read_text(encoding="utf-8")).get("typography", {})
            text_state = "完整" if typography.get("complete_text") else \
                "截断:" + ",".join(item["role"] for item in typography.get("truncated", []))
        except Exception:
            pass
        c = subprocess.run([exe, str(fw), "check", str(svg)],
                           capture_output=True, text=True, encoding="utf-8")
        try:
            report = json.loads(c.stdout)
            checks = report.get("checks", {})
            summary = ", ".join(f"{k}={'ok' if v['ok'] else 'FAIL'}"
                                for k, v in sorted(checks.items()))
            results[name] = (True, bool(report.get("ok")), f"text={text_state} | {summary}")
        except Exception:
            results[name] = (True, False, (c.stdout or "") + (c.stderr or ""))
    return results
