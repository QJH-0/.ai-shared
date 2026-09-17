---
name: kaggle-notebook-to-cloud-jupyter
description: >
  把原本跑在 Kaggle 的训练 notebook 迁移到租用的云 GPU 服务器（JupyterLab）上运行：
  模块源码「单源参数化」路径、加平台适配与开跑前自检 cell、原始 zip 平铺上传 + 服务器端解压、
  两级存储（文件存储 / 数据盘）分工、续训读写分离、依赖安装脚本。适用于「脚本要挪到 XX 云服务器跑」
  「数据集/权重/检查点要上传到服务器」「复制一份改成服务器适配版本」这类需求。
  Triggers: 云服务器, 服务器版, 智川云, AutoDL, JupyterLab 上传, 迁移到服务器, 云上训练,
  cloud server training, server-adapted notebook, upload dataset to server.
---

# Kaggle Notebook → 云服务器 JupyterLab 迁移

把 Kaggle notebook 搬到租用云服务器跑。目标不是"复制一份改改路径"，而是
**让两版共用同一份源码、只让平台差异集中在一处**，并让"路径写错/上传不全/依赖没装"在开跑前就暴露。

参考实现（照抄结构即可）：
`D:\Code\00cursor_code\ConvtasnetTwo\` 下的
`build_spex_nb.py` + `deploy/{server_setup.sh,server_install_deps.sh,SpExPlus云服务器部署操作文档.md,verify_*.py}`
以及对比参照的旧版 `NEW/ConvTasNet渐进位宽量化蒸馏训练_服务器版.ipynb`（手工改路径，不推荐）。
`deploy/prepare_upload.py`（本地打 tar 分卷）已降级为**遗留备选通道**，正常流程不用它。

---

## 零、五条铁律（先读，违反必踩坑）

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

**对策：根本不要在 Windows 上解压**。上传物一律是 Kaggle 下载的**原始 zip**，平铺丢进文件存储
（如 `/root/rivermind-fs`），由服务器端脚本在 Linux 上就地解压到数据盘。全程不落 Windows 文件系统，
这个坑自然绕开——**它是 Windows 的坑，不是服务器的坑**。

（遗留备选：确实需要在本地预打包时，用 `prepare_upload.py` 从 zip 直读成员、直接写 tar，
全程不落盘：）

```python
with zipfile.ZipFile(zip_path) as zf:
    with tarfile.open(out_tar, "w:gz") as tf:
        info = zf.getinfo(member)
        ti = tarfile.TarInfo(arcname); ti.size = info.file_size
        with zf.open(member) as fp:      # ZipExtFile 可直接喂给 addfile
            tf.addfile(ti, fp)
```

**只接受 zip 作为输入，不接受已解压目录**——否则半残索引（少了 `aux.scp`）会被当成完整索引打包出去，
错误被推迟到服务器上才炸。同理，也不要在 Windows 上先解压再上传。

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

### 4. 依赖安装脚本绝不重装 torch

云 GPU 镜像（如 `PyTorch/2.11.0-CUDA12.8-Devel-Py3.12-Ubuntu24`）自带 torch + CUDA 匹配构建。
脚本里一旦写 `pip install torch`，就会把它换成 PyPI 默认构建 → **CUDA 运行时错配**
（症状：`import torch` 报 undefined symbol，或 `is_available()` 变 False）。
只补训练代码真正 import 的包，装完打印 torch 版本 / CUDA 编译版本 / GPU 型号与计算能力
（如 4090 应是 `sm_89`）自证没被换掉。镜像名里的 `Devel` 表示带 gcc，`pesq` 这类 C 扩展可现编。

Ubuntu 24.04 的系统 python 带 PEP 668 标记，pip 会拒绝装包；按 `EXTERNALLY-MANAGED` 标记
**判断后再加** `--break-system-packages`（conda 环境并不需要它），别无脑加。

### 5. 两级存储：文件存储只做上传与回写，训练只在数据盘

租用平台的"文件存储"是网络盘，**小文件随机读比本地盘慢一个量级**。6 万个 wav 直接在它上面训练，
一个 epoch 就废掉。分工必须写死：

| 位置 | 性质 | 放什么 |
|---|---|---|
| 文件存储（如 `/root/rivermind-fs`） | 持久、容量大、慢 | 上传的 zip（**平铺**）+ 回写的产物目录 |
| 数据盘（如 `/root/rivermind-data`） | 本地快盘 | 解压后的数据 + 训练读写的一切（高频 checkpoint） |

**续训读写分离**：`<work>/resume/<exp>/` 是**只读**续训源（从上传的归档解出），
`<work>/<exp>/` 是**本次写入**目录。开训时把源里的 checkpoint 复制一份进写入目录（只补缺失），
此后所有写入都落在这一份上——续训源永不被改写，可以反复重跑、反复回退。
训练完 `--backup` 把写入目录**按目录名**回写到文件存储（同名先改名归档，不覆盖）。

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
- 探测基准要**把两个根（数据盘根 + `dataset/` 子目录）都放进去**，目录结构摆放有偏差时还能靠 rglob 找到。

---

## 三、build 脚本：一次生成两版

沿用 `kaggle-modularize` 的 merge 逻辑（模块 → 单 cell），加 `--target kaggle|cloud|all`：

- 共享：合并后的模块代码 cell、依赖安装 cell、运行模式开关 cell、入口 cell、markdown 主体。
- Kaggle 版独有：Kaggle 挂载章节。
- 云版独有：`环境与路径配置` cell + `环境与路径自检` cell + 服务器目录/上传清单章节。

**必须加编译门禁**：`ast.parse(merged_code)`——合并产物是合法 Python 才能落盘
（`%%bash` cell 不在其中，所以只编译模块代码）。

**云版环境 cell 的写法**：只暴露**两个根**（数据盘根 + 文件存储根），其余路径按固定相对结构推导
（`<work>/dataset/...`、`<work>/resume/<exp>/`、`<work>/<exp>/`）。
让用户改 6 个变量不如让他改 2 个——而多出来的那 1 个（文件存储根）不能省，
因为"上传与回写"和"训练读写"物理上就在两块盘上（铁律 5）。

**性能参数也走环境变量，且默认值必须与 Kaggle 逐字相同**。典型 4 个：
`SPEX_TRAIN_BATCH_SIZE` / `SPEX_GRAD_ACCUM` / `SPEX_VAL_BATCH_SIZE` / `SPEX_NUM_WORKERS`。
整数解析要另写一个 `_env_int`（`_env_path` 那套是字符串语义），并且**非法值/非正值要回退默认 + 打 warn**，
不要让它悄悄变成 `0` 或抛栈。

**等效 batch 是配方不变量，不是可调参数**。换卡只能改拆分、不能改乘积：

```
train_batch_size × gradient_accumulation_steps = 常量（本项目为 8）
```

Kaggle 上 `4 × 2`，4090 24G 上 `8 × 1` —— 乘积不变，所以 LR 与各阶段 epoch 预算都不用重标定，
两边结果可比。开训日志里要**回显乘积并对偏离打 warn**，否则有人把 batch 调大一圈，
等效 batch 变了却没人发现，最后只会得出"这个配方在 4090 上更差"的错误结论。

**云版自检 cell 的内容**（这是云版最值钱的一格，别省）：

1. torch / CUDA / GPU 型号显存
2. `cfg` 实际生效的每个路径 + 存在性（`[OK]/[MISS]` 逐项打印）
3. 输出目录、续训导入配置
4. 索引加载 + 抽样校验（走一遍真实的索引加载路径，含一致性自检）
5. 结论行：全部 OK / 列出缺失项 + 修正指引

---

## 四、打包与部署

### 主路径：原始 zip 平铺上传 + 服务器端解压

**上传物就是 Kaggle 下载的那个 zip，一个字节都不改**，平铺丢进文件存储根：

```
/root/rivermind-fs/
├── libri2mix-spexplus.zip        # 索引
├── libri2mix-8khz-min.zip        # 音频
├── best.zip                      # 权重（裸 best.pt）
├── exp_spex_dualteacher_v1.zip   # 续训归档（checkpoints/<阶段>/<阶段>_best|latest.pt）
├── server_setup.sh
├── server_install_deps.sh
└── SpExPlus...服务器版.ipynb
```

**不要建 `dataset/` `models/` `checkpoints/` 之类的子目录**——平铺 + 脚本按内容识别角色，
比"先商量好目录规范"可靠得多：用户上传时不会记规范，脚本却能从 zip 内部结构认出它是什么。

`server_setup.sh` 按**内容**识别 4 类角色（索引 / 音频 / 权重 / 续训归档），
候选位置依次试 `$FS → $FS/dataset → $FS/datasets → $SELF_DIR → $PWD → /root`。

**`$SELF_DIR` 这一项必须有**：脚本被 `bash server_setup.sh` 直接调用时 `$0` 是相对名，
zip 就摆在脚本旁边却找不到，用户会以为"上传失败了"。取 `dirname "$0"` 时要用 `cd ... && pwd`
包一层，并容忍失败（`|| SELF_DIR=""`）。

**上传前先自查一件事**：zip 里有没有 DOS 保留设备名（`aux.scp`）。有的话，
它在 Windows 上解压必失败，但上传的是 zip 本身所以没关系——**前提是上传流程里没有任何一步在 Windows 上解压**。

### 服务器端 `server_setup.sh` 的职责边界

解压 → 建目录树 → 检查关键路径存在 → 打印音频/索引文件数 → 打印剩余磁盘。

- **所有目录层级由脚本创建**，不要靠文档里写"请先 mkdir"。文档会过期，脚本不会。
- **深度校验不要在这里重复实现**，交给 notebook 的自检 cell（它拿着真实 `cfg`，更权威）。
- **续训要读/写分开**：从归档解到 `<work>/resume/<exp>/`（只读源），
  开训时复制进 `<work>/<exp>/`（写入目录），只补缺失。这样续训源可反复重跑、反复回退。
- `--backup` 把写入目录**按目录名**回写到文件存储；同名先改名 `..._<时间戳>/`，不覆盖。
  `--restore` 从回写目录或 zip 解回 `resume/`。

### 依赖安装：单独一个脚本，与文档同一份清单

`server_install_deps.sh` 独立成脚本（不写进 notebook 的 `%%bash` cell），理由：
部署文档要引它、notebook 也要调它，**清单只有一份才不会两处漂移**。

notebook 的安装 cell 里不要抄包名，直接调用：

```bash
%%bash
set -e
if [ ! -f server_install_deps.sh ]; then
  echo "[ERR] 找不到 server_install_deps.sh —— 请与 server_setup.sh 一起上传到同层目录" >&2
  exit 1
fi
bash server_install_deps.sh
```

脚本要提供 `--check`（只自检、缺必需包返回退出码 1），方便部署后单独复查；
支持 `SPEX_PIP_INDEX` 换源（国内机器默认源慢）。

**退出码是契约，而且要覆盖"镜像自带"的那一个**。踩过一次：`print_env` 里 torch 探测写成裸
heredoc（python 打印 `[MISS]` 后仍退出 0），`miss=1` 只由 pip 包触发 —— 结果
**torch 被换坏时 `--check` 报通过**，而防 torch 被换坏正是这个脚本存在的头号理由。
规则：**凡是"坏了训练必然失败"的东西，无论由谁提供，都必须计入失败**；
探测块要包成 `if ! "$PY" - <<EOF ... EOF; then miss=1; fi`，heredoc 内 `sys.exit(1)`。
同理，**安装后的复检也必须影响退出码**（`exit 1`），否则调用方会带着坏环境继续跑。

验证这类脚本不要靠读代码推演——**造解释器替身隔离变量**：一个正常替身、一个用
`PYTHONPATH` 指向 `torch.py: raise ImportError` 的替身，用 `PATH` 前缀切换，对比退出码。
更关键的是：**把改动前的版本程序化回退出来跑一遍**，确认旧行为真的会静默假绿——
否则你只是"觉得"修了个 bug。

**依赖清单必须由 `spex/` 的真实 import 推导，不要凭印象加**。典型：必需 `numpy soundfile tqdm`；
可选 `pesq pystoi`（代码里是 try/except，缺了只降级不崩）；apt 侧 `unzip libsndfile1`。
**顺手查一遍死依赖**：本项目 `matplotlib` 被装了很久但全仓库无人 import，已删。

### 遗留备选：本地预打包（`prepare_upload.py`）

正常流程用不到。仅在"必须先在本地筛掉不读的文件"时用：

- 按 scp **逐条精确挑选**音频，不要整目录打包：只带走真正会被读到的文件。
  典型能省掉一半（如 Libri2Mix 的 `noise/mix_both/mix_single` 都不读）。
- `--mode smoke|full`：smoke 只带冒烟子集引用的文件（几十 MB），让"先冒烟再正式"这条路走得起。
- `--part-mb` 分卷（默认 900），产出 `MANIFEST.txt` 供服务器端核对。
- 分卷用纯 Python 字节切分，服务器端 `cat parts | tar -xzf -` 直接流式解开
  （gzip 流按字节拼接是合法的）——**不要**用 `split` 生成 `.aa/.ab`，命名更容易传错。

但这条路要付代价：tar 是本地生成的产物，**行尾/文件名都要额外把关**（见 §五），
且与"上传原始 zip"是两条并行通道，容易只维护一条。**能用主路径就别用它**。

### 行尾是硬门禁

`set -euo pipefail` 遇到 CRLF 会报 `invalid option name`，而且**报错行号不指向行尾**，
排查时极容易被带偏。两条防线都要有：

- 仓库侧 `.gitattributes` 把 `*.sh` 锁成 LF。
- 校验脚本里遍历所有 shell 脚本断言无 `\r\n`，并跑一遍 `bash -n` 语法检查。


---

## 五、验证：四个自检脚本（没有这些等于没验证）

| 脚本 | 锁什么 |
|---|---|
| `verify_platform_paths.py` | 未设环境变量时路径 == 改造前原值；覆盖生效；空串语义；默认值字面量未变；**性能参数：Kaggle 默认 / 云端覆盖 / 非法值回退** |
| `verify_notebooks.py` | 两版合并代码 cell 逐字相同；cell 顺序契约；平台隔离（Kaggle 版不得出现环境变量设置）；合法 Python；无残留相对导入；**云版含依赖脚本调用、两版都不装死依赖** |
| `verify_packing.py` | 保留名文件（如 `aux.scp`）成功进 tar；模式筛选数量 == scp 引用数；分卷 concat 后成员集合一致；**zip 与脚本同层时 `$SELF_DIR` 能发现**；**两个 shell 脚本无 CRLF 且 `bash -n` 通过** |
| `smoke_test_*.py` | **合成一份服务器目录布局，真的跑一遍数据链路**：rebase 生效、音频根可探测、索引自检放行、DataLoader 出批、张量数值有限 |

第 4 个最关键。合成布局时有两个技巧：

- **scp 里写目标平台的假绝对路径**，音频只放在本地新布局下 → 这才真正测到"路径重定向"这条逻辑。
- 跑两个 case：**显式给音频根** / **不给、靠探测基准自动发现**，覆盖两条代码路径。

校验脚本自己要小心误命中：合并代码 cell 里含 `def build_dataloaders()`，
用「包含匹配」找入口 cell 会命中它——入口 cell 要用整格内容精确匹配；
markdown 说明格也含章节名，查找时要跳过第 0 格。

**跑校验脚本要指定解释器**：`verify_platform_paths.py` 与 `smoke_test_*.py` 会
`subprocess` 起一个真实导入 `spex` 的子进程，所以驱动解释器与 `--python` 目标**都必须带 numpy/torch**。
裸 `python` 很可能是不带三方包的托管解释器，会以 `ModuleNotFoundError: No module named 'numpy'` 报错——
**这是环境问题不是代码问题**，别去改代码。
另外 `--python` 要写 **Windows 风格路径**（`D:/...`）：`subprocess` 走 Win32 CreateProcess，
不认 MSYS 的 `/d/...`，会报 `FileNotFoundError: [WinError 2]`。

**另外几条纪律**（都是踩过的）：

- **每条 `PASS` 都必须有对应的实跑输出**。不要写完脚本就按"应该能过"去文档里写"全部通过"。
  本次就发生过：脚本其实一直在建测试数据时失败，而文档已写成"两个 case 全 PASS"。
- **四脚本统一输出 `ALL CHECKS PASSED` 字样**，便于一条 shell 循环汇总判定，避免人工逐个看。
- **子进程上报的"让步/降级标志"要进断言**（如 `shim_used`），否则降级会静默变成假通过。
- **断言不要依赖路径字符串风格**。Windows 上 `Path.as_posix()` 给 `D:/tmp/x`，
  而 Git Bash 里的 `pwd` 给 `/d/tmp/x`——同一个目录两种写法，断言必然假 FAIL。
  改成与风格无关的判据（如 `line.rstrip().endswith("scriptdir5")`）。
- **断言不要用宽松子串**。`"tar" not in cell` 这种会被 `start` / `target` 命中而假 FAIL；
  要检查"某条具体指令没出现"就写完整短语（`"bash deploy/server_setup.sh"`），
  否则合法的说明性提及（"即仓库里的 deploy/server_setup.sh"）也会被误杀。
- **行尾判断只信 Python 读 bytes**。`grep -c $'\r' *.sh` 报"每行都是 CR"时先别慌——
  转义可能没展开、退化成空模式匹配所有行，是**假阳性**。判据写
  `b"\r\n" not in path.read_bytes()`，一行搞定且不会骗你。
- **交付物是"配套的一组文件"时，必须显式提醒覆盖上传**。用户手上一定有历史版本；
  改过 notebook 却留着旧脚本，症状会伪装成"数据没传上去"（自检报 `[MISS]`），
  排查方向完全被带偏。提醒要写进**用户实际会看的那份载体**（notebook 内嵌 markdown
  与仓库侧部署文档都要写，只写一处就可能看不到），并用断言守住这两句话。
- **平台隔离断言要扫到代码 cell，不能只查说明 markdown**。踩过一次：断言只写在
  `cloud[0]`（markdown）上，结果代码 cell 里残留的 `bash deploy/server_setup.sh --backup`
  一路绿灯通过——用户照抄就是命令失败。正确做法是遍历**除第 0 格以外的所有 cell**
  找仓库侧路径（`deploy/`），把合法的说明性提及（只在 markdown 里）与可执行的错误指令区分开。
  **加完断言要做一次负向测试**：手动往代码 cell 里注入一处，确认它真的 FAIL，
  否则你不知道这条断言是不是"永远为真"。
- **同一个事实被多处硬编码时，必须有跨文件护栏**。本项目踩过：实验目录名在
  `server_setup.sh` 的 `EXP_NAME` 和 notebook 首格的 `EXP_DIR` / `RESUME_DIR` / `BACKUP_DIR`
  各写一份，谁都不管谁。漂移后 `--backup` 报「没有可回写的产物」——
  消息把人往"训练没产出 checkpoint"带，真实原因只是两边名字对不上。
  做法：护栏直接读两个文件、正则取值、断言同名。**平台路径、目录名、镜像名、版本号
  这类"两边都要写一遍"的常量，都值得这样锁一道。**
- **审计时先读清职责边界，别以"补漏"为由越界**。比如"解压脚本只验目录存在、不验索引里的
  `.scp` 文件"看着像漏了，但如果设计上明确写了"深度校验归 notebook 自检格（它拿着真实 cfg，
  更权威）"，那补上去就是重复实现 + 违反边界。**该放弃就明确写进交付说明，标注是"按边界放弃"
  而不是"漏掉"**——否则下一个人会当成 bug 再补一遍。

---

## 六、坑位速查

| 现象 | 根因 | 处置 |
|---|---|---|
| `aux.scp` FileNotFoundError（本地） | Windows 保留设备名 | 不要解压，上传原始 zip 交服务器解压 |
| 服务器上报「找不到音频文件」 | scp 靠路径标记（如 `wav8k/min`）重定向，标记层被改掉了 | 上传时保留该层级，不要拍平 |
| 几万成员的大包被判成「未识别」，同结构的**小包却正常** | 用 `printf ... \| grep -q` 判命中：`grep -q` 命中即退出，上游 `printf` 吃 SIGPIPE，`set -o pipefail` 于是把这条管道判成失败——「命中」变「未命中」。成员名列表越大越必然踩到（>64KB 管道缓冲区即触发），小包因列表装得下缓冲区而侥幸通过 | 存在性判断别走管道：一次流式扫描（`zip_members \| awk ... END{...}` 读满全流再判定）或纯 bash `case` 匹配。护栏里把「成员名列表 > 64KB」做成用例前提，否则这条回归是空门 |
| 训练到一半才报索引错 | 没做开跑前自检 | 加自检 cell，索引加载走一遍真实路径 |
| 服务器上仍读 Kaggle 路径 | 设环境变量的 cell 排在合并代码之后 | 顺序：环境配置 → 合并代码 → 自检 |
| 服务器上照抄 notebook 注释里的命令却报"找不到脚本" | 注释/提示里写了**仓库侧路径**（`deploy/xxx.sh`），但服务器上脚本与 notebook 同在 `/root`，没有 `deploy/` 层 | 代码 cell 里一律用裸脚本名；把"不得出现 `deploy/`"做成断言（扫代码 cell，不只扫 markdown） |
| 自检报路径 `[MISS]`，可数据明明传上去了 | 用户留着**旧版 `server_setup.sh`**，铺的是另一套目录层级 | 部署文档与 notebook 说明里显式写「三个文件配套、旧版必须覆盖上传」，并用断言守住这句话 |
| `grep -c $'\r' *.sh` 说每行都是 CRLF | shell 转义没展开，退化成空模式匹配所有行（假阳性） | 用 `b"\r\n" not in path.read_bytes()` 复核，别信 shell 的 `$'\r'` |
| Kaggle 版行为被改坏 | 默认值不是原值 / 环境变量被写进 Kaggle 版 | 用 `verify_platform_paths.py` + `verify_notebooks.py` 断言 |
| `set -euo pipefail` 报 `invalid option name` | 脚本是 CRLF 行尾（报错行号还指错地方） | `.gitattributes` 锁 LF + 校验脚本断言无 `\r\n` 并跑 `bash -n` |
| `import torch` 报 undefined symbol / `is_available()` 变 False | 依赖脚本重装了 torch，把镜像的 CUDA 匹配构建换成了 PyPI 默认构建 | **绝不 `pip install torch`**；装完打印 torch / CUDA 编译版本 / GPU 计算能力自证 |
| pip 报 `externally-managed-environment` | Ubuntu 24.04 系统 python 带 PEP 668 标记 | 先判 `EXTERNALLY-MANAGED` 标记再加 `--break-system-packages`，conda 环境不要加 |
| 环境检查脚本报"全部通过"，训练却 import 就崩 | 检查脚本的"必需项"漏了镜像自带的那个（如 torch），探测失败没计入退出码 → 静默假绿 | 凡是"坏了训练必然失败"的项都计入失败；探测块用 `if ! cmd; then miss=1; fi`，复检失败要 `exit 1` |
| `bash server_setup.sh` 说找不到 zip，可 zip 就在脚本旁边 | `$0` 是相对名，没取 `dirname "$0"` | 加 `$SELF_DIR` 进候选（`cd ... && pwd` 包一层，失败则留空） |
| loss 不降 / 有效步数远少于预期，但训练"没报错" | batch 过大，OOM 被**静默跳过**（只打印 `[OOM] step N ... skipped`，累计超阈值才 raise） | 开训后先确认 `oom_skip` **恒为 0**；调大 batch 必须看这个计数 |
| 换了卡之后结论和 Kaggle 对不上 | 等效 batch 被改了（`train_batch × accum` 变了） | 锁乘积不变量，开训日志回显乘积并对偏离打 warn |
| 训练慢到不可用 | 直接在网络盘（文件存储）上跑训练 | 数据盘放数据与 checkpoint，网络盘只做上传与回写 |
| 磁盘写满 | 系统盘只有 30 GB，数据全塞系统盘 | 解压与训练读写全指向数据盘根 |
| 租期到了 checkpoint 全丢 | 数据盘非持久 / 忘了回写 | 训练完 `--backup` 按目录名回写文件存储；文档写死这个动作 |

---

## 七、交付时要说清的六件事

1. **两版关系**：训练逻辑与超参逐字一致，差异只有路径来源；改逻辑要重建两版。
2. **上传清单**：每项的内容、来源、体积量级、必要性（必需/可选），以及"冒烟阶段只需传哪几项"。
   必须**逐个点名本次改过、用户手上那份已过期的文件**（notebook / 两个 `.sh`），
   否则用户会拿旧脚本配新 notebook，然后卡在一个"文档明明写了但就是不生效"的状态。
3. **依赖清单的来源**：哪些是训练代码真实 import 的、哪些是可选的（try/except 降级）、
   哪些由镜像提供（torch）。以及 `--check` 怎么单独复查。
4. **等效 batch 与调参口径**：改了什么、没改什么、为什么乘积不能动。
5. **未验证部分**：没连过真实服务器就明说"未在真机跑通"，不要把合成验证说成实机验证。
   具体到本项目：依赖脚本在**真实镜像**上的安装行为、以及目标 batch 在**真实 4090 24G** 上
   是否真的不 OOM，这两项本地都验不了，必须标为"待实机回归"并给出验证方法
   （跑起来后看 `oom_skip` 计数）。
6. **文档同步**：改完护栏或清单，**部署文档里描述它们的那几节会立刻过期**——
   命令清单的注释还写着旧断言、"踩坑记录"少了新踩的坑、"维护约定"没写新引入的耦合值。
   这类章节不会有人主动去读，所以交付时要**主动回填**（改了什么断言就补进命令清单注释；
   新踩的坑就进踩坑记录；新引入的"两处都要写"的常量就进维护约定）。
   顺带判断一下：这份文档**需不需要护栏**——纯人读、不参与构建的，通常不加（属扩范围），
   但要在交付说明里点出这个取舍，别让它静默地长期漂移。
