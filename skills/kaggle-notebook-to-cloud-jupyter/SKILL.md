---
name: kaggle-notebook-to-cloud-jupyter
description: >
  把原本跑在 Kaggle 的训练 notebook 迁移到租用的云 GPU 服务器（JupyterLab）上运行：
  模块源码「单源参数化」路径、加平台适配与开跑前自检 cell、本地 zip 直读打包上传、
  服务器端解压自检。适用于「脚本要挪到 XX 云服务器跑」「数据集/权重/检查点要上传到服务器」
  「复制一份改成服务器适配版本」这类需求。Triggers: 云服务器, 服务器版, 智川云, AutoDL,
  JupyterLab 上传, 迁移到服务器, 云上训练, cloud server training, server-adapted notebook,
  upload dataset to server.
---

# Kaggle Notebook → 云服务器 JupyterLab 迁移

把 Kaggle notebook 搬到租用云服务器跑。目标不是"复制一份改改路径"，而是
**让两版共用同一份源码、只让平台差异集中在一处**，并让"路径写错/上传不全"在开跑前就暴露。

参考实现（照抄结构即可）：
`D:\Code\00cursor_code\ConvtasnetTwo\` 下的
`build_spex_nb.py` + `deploy/{prepare_upload.py,server_setup.sh,SpExPlus云服务器部署操作文档.md,verify_*.py}`
以及对比参照的旧版 `NEW/ConvTasNet渐进位宽量化蒸馏训练_服务器版.ipynb`（手工改路径，不推荐）。

---

## 零、三条铁律（先读，违反必踩坑）

### 1. Windows 下无法创建 `aux.scp`——不要在 Windows 解压 Kaggle zip

`AUX` 与 `CON` / `NUL` / `PRN` / `COM1` / `LPT1` 同属 DOS 保留设备名。
实测：同目录写 `mix.scp`、`ref.scp` 正常，`aux.scp` 报 `FileNotFoundError`。

**别浪费时间试这些绕法**（都实测过，无效）：

| 尝试 | 结果 |
|---|---|
| `\\?\D:\path\aux.scp` 扩展长度前缀 | 改报 `PermissionError`（仍不可用） |
| 写成目录名 / 建 junction | 同样被名字解析拦下 |
| 找 WSL 跑 | 本机被安全策略阻止（且这是组织级黑名单，不可绕过） |
| 找 Docker 跑 | 守护进程常未启动 |

**后果**：Kaldi 风格索引（`mix.scp` / `ref.scp` / `aux.scp`）在 Windows 上一解压就丢 `aux.scp`，
训练时加载索引必崩——而且症状是"文件缺失"，容易被误判成索引坏了。

**对策**：打包脚本**从 zip 直接读成员、直接写 tar**，全程不落 Windows 文件系统：

```python
with zipfile.ZipFile(zip_path) as zf:
    with tarfile.open(out_tar, "w:gz") as tf:
        info = zf.getinfo(member)
        ti = tarfile.TarInfo(arcname); ti.size = info.file_size
        with zf.open(member) as fp:      # ZipExtFile 可直接喂给 addfile
            tf.addfile(ti, fp)
```

并且**只接受 zip 作为输入，不接受已解压目录**——否则半残索引（少了 aux.scp）会被当成完整索引打包出去，
错误被推迟到服务器上才炸。

**本地端到端测试怎么办**：目标平台是 Linux，本地 Windows 跑不了真文件名。采取的折中是
在测试子进程里把该**字节名**映射为安全名（`aux_scp.txt`），索引结构/解析/自检/DataLoader 全真实执行，
并让子进程上报 `shim_used`、测试**强制断言它必须为 True**——否则测试可能"悄悄没测到"却报 PASS。
这种让步必须写进交付文档，不能默认隐瞒。

### 2. 不要手工分叉 notebook

手工复制一份改路径，从那天起就是两份代码双写，第二次改逻辑必漂移。
正确做法：模块源码路径全部「**环境变量可覆盖 + Kaggle 原值作默认**」，一个 build 脚本生成两版，
并用校验脚本断言"**两版合并代码 cell 逐字相同**"。

### 3. 环境 cell 与自检 cell 的位置是有讲究的

- 设环境变量的 cell 必须在合并模块代码**之前**——模块在导入时读取路径。
- 自检 cell 必须在合并代码**之后**——它要校验 `cfg` 的**实际生效值**，而不是"你以为设进去的值"。

---

## 一、侦察：先把平台硬编码找全

```bash
grep -n "/kaggle\|os.environ\|Path(\|rglob\|data_root\|ckpt" <模块目录>/*.py
```

典型只有 5~10 处，分三类：

| 类别 | 例子 | 处理方式 |
|---|---|---|
| 显式路径字段 | `data_root` / `ckpt_path` / `exp_dir` | 改成环境变量驱动（见 §二） |
| 目录自动探测基准 | `for base in ["/kaggle/input", "/kaggle/working"]` | 抽成 `cfg.search_bases` 字段 |
| 报错文案里的平台名 | 「请挂载 Kaggle dataset xxx」 | 改成中性的"请确认已上传/挂载到 …" |

**别漏第三类**：文案不改，服务器上排障时会被"请挂载 Kaggle dataset"误导。

---

## 二、参数化模块：三个解析函数

在模块最顶部（任何 dataclass 之前）加：

```python
def _env_path(var: str, kaggle_default: str) -> str:
    """路径：环境变量优先，未设置时用 Kaggle 挂载路径。"""
    return os.environ.get(var) or kaggle_default


def _env_opt_path(var: str, kaggle_default: Optional[str]) -> Optional[str]:
    """可选路径：环境变量一旦存在即以其为准（空串 = 显式关闭）。"""
    if var in os.environ:
        return os.environ[var].strip() or None
    return kaggle_default


def _env_path_list(var: str, kaggle_default: tuple) -> tuple:
    """目录探测基准（逗号分隔），空串/未设置时用默认。"""
    items = tuple(p.strip() for p in os.environ.get(var, "").split(",") if p.strip())
    return items or kaggle_default
```

要点：

- **`_env_opt_path` 的空串语义必需**。`os.environ.get(x) or default` 表达不出"显式关闭"，
  而"服务器上不导入旧检查点"正是靠空串表达；否则 Kaggle 默认目录在服务器上不存在，
  只能靠"目录不存在就跳过"的隐式兜底，日志里会一直报 warn。
- **Kaggle 原值原样保留作默认**，改完 Kaggle 侧行为逐字不变——这是可以用测试断言锁死的（见 §五）。
- 探测基准要**同时把 `SERVER_ROOT` 和它的子目录**放进去，目录结构摆放有偏差时还能靠 rglob 找到。

---

## 三、build 脚本：一次生成两版

沿用 `kaggle-modularize` 的 merge 逻辑（模块 → 单 cell），加 `--target kaggle|cloud|all`：

- 共享：合并后的模块代码 cell、依赖安装 cell、运行模式开关 cell、入口 cell、markdown 主体。
- Kaggle 版独有：Kaggle 挂载章节。
- 云版独有：`环境与路径配置` cell + `环境与路径自检` cell + 服务器目录/上传清单章节。

**必须加编译门禁**：`ast.parse(merged_code)`——合并产物是合法 Python 才能落盘
（`%%bash` cell 不在其中，所以只编译模块代码）。

**云版环境 cell 的写法**：只暴露一个 `SERVER_ROOT`，其余路径按固定相对结构推导。
serverless 的场景下让用户改 6 个变量不如让他改 1 个。

**云版自检 cell 的内容**（这是云版最值钱的一格，别省）：

1. torch / CUDA / GPU 型号显存
2. `cfg` 实际生效的每个路径 + 存在性（`[OK]/[MISS]` 逐项打印）
3. 输出目录、续训导入配置
4. 索引加载 + 抽样校验（走一遍真实的索引加载路径，含一致性自检）
5. 结论行：全部 OK / 列出缺失项 + 修正指引

---

## 四、打包与部署

### 本地打包（`prepare_upload.py`）

- 输入：Kaggle 下载的 **zip**（索引、音频）+ 权重文件。仅接受 zip（见铁律 1）。
- 按 scp **逐条精确挑选**音频，不要整目录打包：只带走真正会被读到的文件。
  典型能省掉一半（如 Libri2Mix 的 `noise/mix_both/mix_single` 都不读）。
- 提供 `--mode smoke|full`：smoke 只带冒烟子集引用的文件（几十 MB），
  让"先冒烟再正式"这条路走得起。
- `--part-mb` 分卷（默认 900）。JupyterLab 网页上传大包容易失败，分卷 + 服务器端合并更稳。
- 产出 `MANIFEST.txt` 写明文件数与体积，供服务器端核对。

分卷用纯 Python 字节切分即可，服务器端 `cat parts | tar -xzf -` 能直接流式解开
（gzip 流按字节拼接是合法的）——**不要**用 `split` 命令生成 `.aa/.ab`，命名更容易传错。

### 服务器端（`server_setup.sh`）

合并分卷 → 解压 → 检查关键路径存在 → 打印音频/索引文件数 → 对照 `MANIFEST.txt` → 打印剩余磁盘。
**深度校验不要在这里重复实现**，交给 notebook 的自检 cell（它拿着真实 cfg，更权威）。

---

## 五、验证：四个自检脚本（没有这些等于没验证）

| 脚本 | 锁什么 |
|---|---|
| `verify_platform_paths.py` | 未设环境变量时路径 == 改造前原值；覆盖生效；空串语义；默认值字面量未变 |
| `verify_notebooks.py` | 两版合并代码 cell 逐字相同；cell 顺序契约；平台隔离（Kaggle 版不得出现环境变量设置）；合法 Python；无残留相对导入 |
| `verify_packing.py` | 保留名文件（如 `aux.scp`）成功进 tar；模式筛选数量 == scp 引用数；分卷 concat 后成员集合一致 |
| `smoke_test_*.py` | **合成一份服务器目录布局，真的跑一遍数据链路**：rebase 生效、音频根可探测、索引自检放行、DataLoader 出批、张量数值有限 |

第 4 个最关键。合成布局时有两个技巧：

- **scp 里写目标平台的假绝对路径**，音频只放在本地新布局下 → 这才真正测到"路径重定向"这条逻辑。
- 跑两个 case：**显式给音频根** / **不给、靠探测基准自动发现**，覆盖两条代码路径。

校验脚本自己要小心误命中：合并代码 cell 里含 `def build_dataloaders()`，
用「包含匹配」找入口 cell 会命中它——入口 cell 要用整格内容精确匹配；
markdown 说明格也含章节名，查找时要跳过第 0 格。

**另外两条纪律**（都是踩过的）：

- **每条 `PASS` 都必须有对应的实跑输出**。不要写完脚本就按"应该能过"去文档里写"全部通过"。
  本次就发生过：脚本其实一直在建测试数据时失败，而文档已写成"两个 case 全 PASS"。
- **四脚本统一输出 `ALL CHECKS PASSED` 字样**，便于一条 shell 循环汇总判定，避免人工逐个看。
- **子进程上报的"让步/降级标志"要进断言**（如 `shim_used`），否则降级会静默变成假通过。

---

## 六、坑位速查

| 现象 | 根因 | 处置 |
|---|---|---|
| `aux.scp` FileNotFoundError（本地） | Windows 保留设备名 | 不要解压，zip 直读打包 |
| 服务器上报「找不到音频文件」 | scp 靠路径标记（如 `wav8k/min`）重定向，标记层被改掉了 | 上传时保留该层级，不要拍平 |
| 训练到一半才报索引错 | 没做开跑前自检 | 加自检 cell，索引加载走一遍真实路径 |
| 服务器上仍读 Kaggle 路径 | 设环境变量的 cell 排在合并代码之后 | 顺序：环境配置 → 合并代码 → 自检 |
| Kaggle 版行为被改坏 | 默认值不是原值 / 环境变量被写进 Kaggle 版 | 用 `verify_platform_paths.py` + `verify_notebooks.py` 断言 |
| JupyterLab 上传大包失败 | 单包过大 | `--part-mb` 降到 500 或更小 |
| 租期到了 checkpoint 全丢 | 容器盘非持久 | 文档里写死"定期 tar 回传"，并建议数据盘挂载点 |

---

## 七、交付时要说清的三件事

1. **两版关系**：训练逻辑与超参逐字一致，差异只有路径来源；改逻辑要重建两版。
2. **上传清单**：每项的内容、来源、体积量级、必要性（必需/可选），以及"冒烟阶段只需传哪几项"。
3. **未验证部分**：没连过真实服务器就明说"未在真机跑通"，不要把合成验证说成实机验证。
