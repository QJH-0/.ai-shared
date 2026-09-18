---
name: feishu-job-import
description: |
  秋招投递管理：把别人分享的飞书岗位汇总表里的记录，按「记录链接」自动补全到用户自建的投递管理表；
  也支持反过来——从原表全量筛选出「我能投」的 N 家公司，按 record_id 批量新建到自建表；
  也支持来源换成腾讯文档智能表格（`@tdoc#<file_id>`）：读 tdoc 智能表 → 本地筛选 → 直接 batch-create 落表。
  触发场景：用户粘贴飞书多维表格记录链接（形如 https://xxx.feishu.cn/record/XXXX）并要求导入/补全/填充；
  提到「我的秋招投递管理」「投递进度」「补全整行」「导入投递记录」；要求扫描自建表中「原表链接」已填但岗位信息为空的行并补全；
  或要求「从汇总表里挑 N 个适合我的公司加到我表里」「按待遇/规模筛选国企」（汇总表可能是飞书表，也可能是腾讯文档智能表）。
  自动完成：解析链接/分页拉全量 → 读取来源记录 → 字段映射归一化 → 写入自建表。
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
metadata:
  agent_created: true
  trigger: 粘贴飞书记录链接导入/补全，或从原表筛选目标公司批量建行
---

# 秋招投递记录自动导入

## 核心坐标（固定，勿改）

| 项 | 值 |
|----|-----|
| 原表（他人分享，只读） | `2627届实习信息汇总` base_token `V24sbhVkCaJyhJs2zLWcQJNrnec` / table_id `tblMKWxJGIPhcDbw` |
| 自建表（用户所有） | `我的秋招投递管理` base_token `WYVgbZ489aAQjWshefTcotonnie` / table_id `tblzk49OlggwPUVl` |
| 自建表链接 | https://my.feishu.cn/base/WYVgbZ489aAQjWshefTcotonnie |
| 导入脚本 | `D:\Documents\飞书\ai_cli\import_records.py`（唯一维护源，skill 内不存副本） |

## 环境准备：lark-cli（Windows 必读）

所有命令都依赖 `lark-cli`。**本机 PATH 里默认没有**，先确认 `lark-cli --version` 能跑；跑不起来按下面补装：

1. 官方 CLI 是 npm 包 `@larksuite/cli`。**不要**用 `npm install @larksuite/cli` —— 它的 `scripts/install.js`
   会去下 14MB 二进制，本机实测 120s 超时失败。
2. 直接取二进制（v1.0.96，7 秒下完）：
   ```
   https://registry.npmmirror.com/-/binary/lark-cli/v1.0.96/lark-cli-1.0.96-windows-amd64.zip
   ```
   解压得到 `lark-cli.exe`。
3. 放一份到隔离目录 `C:\Users\20448\.workbuddy-ai\binaries\lark-cli\`，**再复制一份到
   `C:\Users\20448\bin\`**（该目录已在 PATH 中）。第二步不能省：脚本用 `subprocess(shell=True)`
   调 `lark-cli`，只认 PATH。
4. `lark-cli auth status` 报 `needs_refresh` 属正常，下次调用会自刷新；只有提示未授权时才走
   `lark-shared` 的 `config init` 重新授权。

## 用法

```bash
SCRIPT="D:/Documents/飞书/ai_cli/import_records.py"

# 模式 A：新建记录（用户直接给原表链接）
python "$SCRIPT" '<record_link1>' '<record_link2>'          # 预览
python "$SCRIPT" --write '<record_link1>' '<record_link2>'  # 写入

# 模式 B：就地补全（自建表已建行、只贴了链接、信息为空）—— 高频
python "$SCRIPT" --fill         # 预览 update_records
python "$SCRIPT" --fill-write   # 执行 +record-batch-update

# 模式 C：按原表 record_id 批量新建目标公司（先筛选，再落表）
python "$SCRIPT" --pick <record_id> [<record_id> ...]     # 预览
python "$SCRIPT" --pick-write <record_id> [...]           # 写入（状态置「未投递」）
python "$SCRIPT" --pick-write <record_id> [...] --force   # 跳过去重预检
```

模式 B 是最高频场景：用户在自建表新建若干行、只粘了「原表链接」，跑 `--fill-write` 即可整行补全。
判定规则：「原表链接」非空 且（公司名称 或 招聘岗位 为空）→ 待补全；已补全的行自动跳过，可重复执行、不会重复建行。

**与模式 A 的关键差异**：补全只写信息字段，**不覆盖「投递状态」（保留用户现有的未投递/已投递）**，也**不覆写「原表链接」**（避免 markdown 被裸 URL 覆盖）。

**模式 C 对应「从原表挑 N 个我能投的公司，加到我的表里」类需求**（原表 6900+ 条，无法靠翻页人工看）：

1. 先分页拉全量到本地 ndjson 分析，**不要**只拉第一页：
   ```bash
   for off in 0 2000 4000 6000; do
     lark-cli base +record-list --base-token V24sbhVkCaJyhJs2zLWcQJNrnec \
       --table-id tblMKWxJGIPhcDbw --format ndjson --offset $off --limit 2000 \
       --output "_src_page_$off.ndjson" --overwrite --as user
     [ "$(wc -l < "_src_page_$off.ndjson")" -lt 2000 ] && break
   done
   ```
2. 合并去重（按 `record_id`），用 Python 按口径筛选打分。默认口径：`招聘对象` 含 2027届（研三）+ `批次` ∈ {秋招, 秋招提前批, 提前批}（排除实习）+ `招聘岗位` 命中开发/AI 关键词 + `企业性质` 优先 央国企。**口径先跟用户确认**，尤其是届次、是否要实习、地域偏好。
3. 筛出的 record_id 走 `--pick-write` 落表；`--pick` 默认按公司名预检去重，仅确认要保留同公司多批次时才加 `--force`。
4. 落表后必须回读核对总数 = 原总数 + 新增数（见踩坑 8）。

> 注意：`/record/<record_id>` 拼出来的链接会被 url-resolve 判为非法。要拿到可点记录链接，必须用
> `lark-cli base +record-share-link-create --base-token <src> --table-id <src> --record-id X`
> 生成，再写成 `[url](url)` markdown 放进「原表链接」（脚本内 `share_links()` 已封装，最多 100 个/次）。

脚本用 `SCRIPT_DIR` 定位自身目录（payload 写入脚本同目录的 `_import_payload.json`），任意 cwd 下执行均可，无需先 cd。

## 模式 D：来源换成腾讯文档智能表格（2026-09-13 新增）

用户给的可能是**腾讯文档智能表格**（对话里以 `@tdoc#<file_id>` 引用，或 docs.qq.com/smartsheet/... 链接），
而不是飞书原表。**这种情况不能用 `import_records.py`**——脚本只认飞书原表的 field_id / record_id。
按下面流程走：

1. 用 tencent-docs 连接器的 `smartsheet.*` 工具读取。
   **不要**用 skill 自带的 `tencentdocs.py`：它依赖宿主注入 `TDOC_OAUTH_ACCESS_TOKEN`，
   AI 直接调用时通常报 `ERROR:no_token`；连接器形态的 MCP 工具才是有票的那条路。
   - `smartsheet.list_tables {"file_id": "<file_id>"}` → 拿 sheet_id
   - `smartsheet.list_fields` → 拿**字段标题**（智能表按标题定位，不是 field_id）
   - `smartsheet.list_records {"file_id","sheet_id","limit":100,"offset":N,"field_titles":[...]}`
   - ⚠️ 单次返回极易超过 30k tokens 被落盘成文件：**必须带 `field_titles` 只取需要的列**，
     落盘后用 Python 解析成紧凑行再读（骨架见 `_parse_tdoc.py`），不要硬读原文件。
2. 拉全量后本地筛选，口径同模式 C（2027届 + 27届秋招 + 开发/AI 关键词 + 企业性质优先央国企），
   再按「待遇 + 公司规模」排序；`更多企业介绍（请点开查看，含待遇等）` 列是判断待遇的主要依据，
   可只对入围公司二次拉取。
3. 写入自建表：**不能用 `--pick`**，直接 `lark-cli base +record-batch-create --json @payload.json`，
   payload 形如 `{"create_records":[{字段名: 值}]}`。字段写法必须对齐表内既有记录：
   - select 写数组：`"投递状态":["未投递"]`、`"企业性质":["央国企"]`、`"批次":["秋招"]`、`"招聘对象":["2027届"]`
   - `行业大类` 是多选，可给多个；央国企/事业单位另加一项 `"央国企/事业单位"`
   - `投递方式` / `原表链接` 写 `[url](url)` markdown；腾讯文档没有单条记录分享链接，
     `原表链接` 直接放该智能表文档 URL 兜底
   - `备注` 放「内推码：XXX；来源：腾讯文档《…》」（表里没有内推码专用字段，只能落在这）
   - `是否需要笔试` 只在来源确有说明时才填，别按常识猜（原表有该列，腾讯文档没有）
   - `投递日期` 有 default（record_created_time），不用写
4. **写入后必查重**：本次实测 `+record-batch-create` 再次触发客户端重试重复建行——
   返回 10 条，表里却多出 20 条（两批 record_id 前缀 `recvv6x8Vx…` / `recvv6xbpN…`，内容逐字段一致）。
   处置：逐字段比对确认内容一致 → 保留位置更靠前的那批 → `+record-delete --yes` 删多余批次 →
   回读确认「总数 = 原总数 + 新增数」。

可复用脚本骨架：`D:\Documents\飞书\ai_cli\_import_tdoc_top10.py`（构造 payload + 写入）、
`_parse_tdoc.py`（把落盘 JSON 解析成紧凑行）。

5. ⚠️ **重复写入的来源不只有 API 重试，写入脚本本身也可能被重复执行**
   （2026-09-14 实测：一条 Bash 写入命令被执行两次，两批 record_id 前缀 `recvv9Yk…` / `recvv9Yn…`）。
   所以**脚本必须自带「真跳过」的幂等预检**：先 `+record-list` 取现有公司名，命中的要从
   `create_records` 里**真正剔除**再提交。只 `print("[skip] …")` 而不剔除等于没做，照样写重。
   落表后无论如何都要回读核对。

## 模式 E：用户直接粘贴转发内推文案（无来源表，2026-09-14 新增）

职场群里的内推文案被用户直接贴进对话（如「XX公司-秋招内推…内推码：XXX 内推链接：XXX」）。
没有来源表 → 不走 list_records，直接构造 payload 写入。规则：

- 一段文案 = 一家公司；用户一次贴多段就是多家，按公司名分别建行（别漏、别合并）。
- 文案里没有的字段**不要凭常识编造**：`招聘岗位` 写「27届秋招各岗位（以官网为准）」，
  `工作地点` 写「<总部城市>（以官网为准）」，并在 `备注` 里把不确定项说清楚。
- 内推码一律进 `备注`，格式 `内推码：XXX`；`原表链接` 留空（没有来源表）。
- `投递方式` 取内推链接；一条文案有多个链接时，主链接进字段、次链接进 `备注`
  （如携程的社招链接、邀请人工号 TR054196）。
- 文案说「有机会免笔试」→ `是否需要笔试` 填 `含免笔试`；完全没提就留空，别猜。

可复用脚本骨架：`D:\Documents\飞书\ai_cli\_import_paste3.py`（转发文案版，含幂等预检）。

## 模式 F：来源换成 offerjack.cn（Jacky学长校招，2026-09-15 新增）

用户直接给一份「可选公司清单」（粘贴的表格/文字），要求「从 offerjack.cn 找投递链接，没有就网络搜索」时用这条。
**offerjack 有公开只读接口，不要去爬页面**：

```
GET https://www.offerjack.cn/api/offer/page
     ?pageNum=1&pageSize=20&enterpriseName=<公司名>
```

- 站点是 Vite SPA（`/assets/index-*.js` → 各页 chunk），数据全部走上面这个接口，页面本身抓不到内容。
- **未登录 `pageSize` 最多 20**，>20 返回 `{"code":401,"msg":"未登录用户每页最多查看20条数据"}`。
- 必带头（否则偶发 `data:null`）：`Origin: https://www.offerjack.cn`、`Referer: https://www.offerjack.cn/`、`User-Agent: Mozilla/5.0`；
  仍偶发空响应 → 做 3~5 次重试 + 1.2~1.5s 退避。
- 支持的过滤参数：`pageNum / pageSize / enterpriseName / position / workLocation / recruitmentBatch / enterpriseNature / industry / graduationYear / updateTime`。
- 返回记录字段（直接可用）：
  `enterpriseName / recruitmentBatch / enterpriseNature / industry / workLocation / position /
   graduationYear / deadline / announcementLink / deliveryAddress / id`
  → `deliveryAddress` 就是「投递方式」，`announcementLink` 是公告（放备注）。
- **`enterpriseName` 是子串匹配**：查「京东」会同时命中「京东方」，查「航空工业」会命中一堆子公司。
  必须按公司名二次过滤，并按公司名挑最匹配的一条（同名会有多条秋招/春招/提前批记录，
  只取 `recruitmentBatch ∈ {秋招, 秋招提前批, 秋招补录, 校招}` 且 `graduationYear` 含 2027/27届 的那条）。
- 该站没有的公司（如集团本级的南方电网、中核集团）→ 转 WebSearch 拿官方网申入口
  （南方电网 `zhaopin.csg.cn`、中核 `hr.cnnc.com.cn`、中国能建 `ceec.iguopin.com/job`）。
- ⚠️ 用 `head` 截断脚本输出会让脚本在收尾 `json.dump` 前因 BrokenPipe 死掉，落盘文件不生成。
  要留档就把 stdout 重定向到文件，再分页读。

落表方式与模式 E 相同：自建 `_import_*.py`，ROWS 里手写数据，**必带公司名幂等预检 + 写后回读核对**。
可复用脚本：`D:\Documents\飞书\ai_cli\_import_oj_2027fall.py`（28 行实例，含预检/核对）。

## 模式 G：用户点名「几家集团」，原表只有子公司 / 只有实习批次（2026-09-17 新增）

典型问法：「在原表找 A、B、C 这几家集团，加到我的表里，找不到就网络搜索招聘链接」。
原表是**子公司粒度的汇总表**（如「中国华电集团」有、但「华润集团」只有华润置地/万象/燃气泰州等子公司），
集团本级经常缺失，或只有已过期的实习批次。按下面走：

1. **先全量拉原表再按公司名筛选**（同模式 C 第 1 步，源表 7682 条需分页 4 次），
   对每个关键词把命中的**全部**记录列出来（含批次、招聘对象、截止时间），再判断是「集团本级」还是「子公司」。
2. **先跟用户确认口径**，两条必问：
   - 导入范围：只要集团本级 / 集团本级 + 子公司。
   - 原表只有过期实习批次时：跳过实习只建秋招 / 实习也一并导入。
   （2026-09-17 用户两次都选前者：只要集团本级、跳过过期实习。）
3. 原表有集团本级秋招记录的，走 `--pick`；没有的，网络搜索官方招聘入口后手写 JSON 建行。
4. **集团级「行业大类」写两个值**：`["<具体行业>", "央国企/事业单位"]`，对齐表里既有「北汽集团」写法；
   `企业性质` 写 `["央国企"]`，`批次` 写 `["秋招"]`，`投递状态` 写 `["未投递"]`。
5. **官网是 SPA 时抓不到公告细节**（南方电网 `zhaopin.csg.cn`、大唐 `zhaopin.china-cdt.com`、
   华润 `runjob.crc.com.cn` 都抓不到正文），只能拿到投递入口；这种**截止时间一律留空，不猜**，
   把「已启动 / 公告预计何时发布」写进 `备注`。能抓到官方公告的（国家能源集团
   `zhaopin.chnenergy.com.cn/annc/showgg?id=...`）才填截止与笔试信息。
6. `原表链接` 只有走 `--pick` 的才有；网络搜索来的留空，来源写在 `备注`。
7. **截止时间留空后要做一次交叉验证**，不能只是「抓不到就算了」：用模式 F 的 offerjack 接口按公司名查一遍。
   查不到 2027 届记录 = 集团公告确实还没发布，**留空是正确结论**，把这个结论写进 `备注`
   （例：「聚合站至 9/17 仍无 2027届记录，最新为 2026届秋招，去年截止 11/02」——顺便给出可参考的时间节奏）。
   查得到但与官网冲突时，以官网为准并把差异写进 `备注`
   （2026-09-17 实例：国家能源集团官网 10/07、聚合站 10/06，差 1 天）。

已确认的四家集团级官方入口（2026-09-17 实测，可复用）：

| 集团 | 官方投递入口 | 说明 |
| --- | --- | --- |
| 华润集团 | https://runjob.crc.com.cn/ | 各业务单元分别开放，无统一截止 |
| 中国南方电网 | https://zhaopin.csg.cn/ | 唯一报名渠道；提前批先启动，统一秋招公告约 10 月中旬 |
| 中国大唐集团 | https://zhaopin.china-cdt.com/ | 集团人力资源市场平台 |
| 国家能源投资集团 | https://zhaopin.chnenergy.com.cn/ | 统招公告网申 9/2–10/7，全国统考 10/25（博士免笔试），限投 1 个岗位 |

原表已确认有的集团本级（直接 `--pick` 即可）：中国华电集团、中国华能。
原表**只有子公司/过期实习**的：华润、南方电网、大唐、国家能源投资集团（原表只有国华能源投资）。

可复用脚本：`D:\Documents\飞书\ai_cli\_import_6energy.py`（6 条实例，含公司名幂等预检 + 写后核对）。

口径（2026-09-15 与用户确立）：
- 清单标「已截止」的不导入；表内已有公司不重复建行（但**顶尖人才专项/独立计划**如「快手 K-star」可单独建行）。
- `投递状态` 统一 `未投递`；`是否需要笔试` 清单没说明的一律**留空不猜**。
- 截止时间优先级：offerjack 有日期 → offerjack；只有清单有日期 → 清单；都无明确日期 → 留空。
  两边冲突时把差异写进 `备注`（如「清单标注 9.14 截止；offerjack 显示招满即止，以官网为准」）。

## 流程说明

脚本内部自动完成四步，无需手工干预：

1. `lark-cli base +url-resolve` 解析记录链接 → 得到 base_token / table_id / record_id
   （注意：`/record/XXX` 里的 token **不等于** record_id，必须经 url-resolve 转换）
2. `+record-get` 读取原表该条记录
3. 字段映射 + 归一化（见下）
4. `+record-batch-create` 写入自建表，投递状态默认 `已投递`

## 字段映射规则

原表字段 id（record-get 返回的 field_id_list 顺序）：

| 原表字段 | field_id |
|---------|----------|
| 公司名称 | `fldOksNbe6` |
| 行业大类 | `fld2uCdYzL` |
| 企业性质 | `fld5eOq8GQ` |
| 工作地点 | `fldAdv82yB` |
| 招聘对象 | `fldUhpDMKB` |
| 招聘岗位 | `fldItRD23k` |
| 截止时间 | `fldkDwWkN7` |
| 是否需要笔试 | `fldKOPLPMf` |
| 投递方式 | `fldm6Xe7U8` |
| 批次 | `fldylXLeov` |
| 工作地点②-文本格式（formula） | `fldZWx0fAi` |

归一化逻辑（脚本内已实现）：

- **行业大类**：原表 244 个杂项 → 自建表 15 类，关键词优先级匹配，未命中归「其他」
- **企业性质**：`民营企业/私企/民企`→`民企`；`外企/合资`→`外企`；`中外合资*`→`中外合资`；`公益组织/社会机构`→`事业单位`
- **批次**：`提前批`→`秋招提前批`；`夏招`→`春招补录`；`寒假实习`→`实习`
- **招聘对象**：只收录 2027/2026/2025/2024/2028 届，其余（如 2029 届）跳过
- **截止时间**：仅接受可解析日期（`2026/11/13` → `2026-11-13 00:00:00`）；「招满为止」等文本**直接丢弃**（见踩坑 5）
- **投递方式**：markdown 链接提取裸 URL
- **工作地点**：优先用 formula 文本字段，否则 join 数组
- **投递状态**：模式 A 固定 `已投递`；模式 B（补全）不写该字段；模式 C 固定 `未投递`（目标公司，尚未投递）

## 踩坑警示（务必遵守）

1. **select 字段必须写数组**：`{"投递状态":["已投递"]}` 正确，`{"投递状态":"已投递"}` 会被拒绝并生成空记录。单选也一样用数组。
2. **lark-cli 是 shell 脚本**：Python `subprocess` 在 Windows 下必须用 `shell=True`，否则报 `WinError 2`。
3. **`--json @file` 用相对路径**：`tempfile.gettempdir()` 的绝对路径在 Windows 下会因大小写/斜杠问题导致 lark-cli 报「找不到文件」。脚本已改为写到脚本同目录的 `_import_payload.json`。
4. **写入后必须验证**：执行 `+record-list` 确认记录数与字段正确；若发现重复记录，用 `+record-delete --yes` 清理。
5. **datetime 字段吞掉整批写入**（已修复，勿回退）：「截止时间」是 datetime 类型，写入「招满为止」这类文本会让整批 `batch_update` 报 `800010403 invalid_request`（要求 RFC3339 或 `2026-01-01 19:30:00`），**一条脏数据导致其余记录全部写不进去**。脚本 `norm_date` 现在对非日期文本返回 `None` 并丢弃。
6. **record-list 落盘必须带 `--overwrite`**：输出文件已存在时命令直接失败（即使刚 `rm`，其 manifest 仍在）。脚本内 `list_dst_records()` 已固定带 `--overwrite`。
7. **run_cli 必须回传 stderr**：lark-cli 失败信息常只写 stderr，只捕获 stdout 会让写入静默失败、看起来「执行成功但没变化」。脚本已修：stdout 为空时返回 stderr。
8. **`+record-batch-create` 会因客户端重试重复建行**（2026-09-13 两次实测：模式 C 一次、模式 D 一次）：一次调用只调一次 API，却返回两批、表里多出一模一样的新增行（两批 record_id 前缀不同，如 `recvv6uD…` / `recvv6uG…`、`recvv6x8Vx…` / `recvv6xbpN…`）。**内容完全一致 = 纯重复**，可安全删除其中一批（保留位置更靠前的那批）。对策：`--pick` 内置公司名预检去重 + `verify_create()` 核对；模式 D 无脚本兜底，**必须手工回读核对总数**。任何新增写入后都必须回读确认「总数 = 原总数 + 新增数」。

## 模式 B 排查顺序（写入后仍为空时）

1. 先看脚本输出有没有 API 错误（800010403 之类）→ 多半是 datetime/字段类型不合法
2. `--dry-run` 手动跑一次 `+record-batch-update --json @_import_payload.json --dry-run` 确认 payload 形状
3. 再 `+record-list --overwrite` 回读验证

## 相关资源

- 自建表仪表盘「投递进度统计」dashboard_id `blkvjkSbEPLrXvKx`
- 看板视图「看板-投递状态」view_id `vewnEy5tKH`（按投递状态分组）
