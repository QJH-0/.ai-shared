---
name: framework-migration-verification
description: 把自建实现迁回框架官方 API、或升级框架版本前，先核实官方 API 在「当前版本 + 当前调用通道」下的真实行为，而不是依赖文档描述或历史结论。适用于：想「改回官方写法」、评估依赖升级、怀疑某条旧结论已过时、需要在两套实现间做取舍。核心教训：旧结论会因版本或通道变化而失效，照旧结论实施会做出错误取舍（本次实测中两条旧结论都已失效，且官方路径在当前版本反而更弱）。
agent_created: true
---

# 框架迁移前的真实行为核实

## 适用场景

- 想把自建实现换成框架官方 API（「官方推荐写法应该更好」）
- 升级框架版本以获取某个新能力
- 手里有一条历史结论（「X 方案不可用，只能自己写」），但环境已经变过

**不要直接开工，也不要相信旧结论。** 先花 15 分钟核实：官方 API 在**当前版本**下到底做什么。

## 为什么必须核实：本次实测

某项目有一条结论：「框架的 `response_format` 走强制 `tool_choice`，我们的 provider 只接受 `none`/`auto`，所以必须自建 bind + 手工解析」。核实后发现：

| 旧结论 | 核实结果 |
| --- | --- |
| 官方路径不可用 | **已失效** —— 它成立于原生 SDK 通道；项目早已切到 OpenAI 兼容通道，官方路径可用 |
| 官方写法等价可换 | **部分成立** —— 但当前版本的官方策略**不带 strict**，换过去约束反而变弱 |
| 自动策略选择会挑最好的 | **错误** —— 自动选择是**硬编码型号名白名单**，项目用的模型不在内，会静默退化成工具调用策略 |

三条里只有一条完全成立。若照旧结论实施，会写出「约束变弱却不自知」的实现。

## 核实五步法

### 1. 确认版本与 API 签名

```bash
# 装了哪些、什么版本
python -c "import importlib.metadata as md; print(md.version('<pkg>'))"

# 参数到底有没有（不要靠文档，文档可能描述的是更新的版本）
python -c "
import inspect
from <pkg> import <Class>
print(inspect.signature(<Class>.<method>))"
```

判据：**文档里写的参数在当前签名里不存在，说明文档对应的是更新版本** —— 本次就是这样发现 `strict` 参数要更高版本才有的。

### 2. 读源码确认内部实现

`description` 与实现经常不一致。直接看它怎么构造请求：

```bash
# 在 site-packages 里定位关键分支
grep -rn "isinstance(effective_response_format, ProviderStrategy)" -A 12 <pkg>/<module>.py
```

本次靠这一步发现：所谓「provider 原生策略」的绑定实现其实是 `model.bind_tools(final_tools, strict=True, **kwargs)` —— 与直觉相反，但仍会带上 `response_format`，所以机制成立。

**同时找策略选择的判据**：

```bash
grep -rn "_supports_<feature>" -A 20 <pkg>/<module>.py
```

本次发现判据是硬编码白名单（`grok` / `gpt-5` / `gpt-4.1` / `o3-*` 等），**项目用的模型不在内** → 裸传 schema 会静默退化。这一条直接改变了实施方案（必须显式传策略对象）。

### 3. 拦截请求体，确认实际发出的参数

比真实调用更快、更省，且能看到「框架实际发了什么」：

```python
# SDK 层拦截：让它抛异常并捕获 kwargs（零成本）
import openai
_orig = openai.resources.chat.completions.Completions.create
def fake(self, **kwargs):
    captured.update(kwargs)
    raise RuntimeError("STOP")
openai.resources.chat.completions.Completions.create = fake
```

坑：**并非所有路径都走同一个 endpoint** —— 本次 HTTP 层与 SDK 层各拦截失败过一次（某条路径走了别的接口）。若拦截不到，退回到**纯函数直接打印**：

```python
print(ProviderStrategy(schema, strict=True).to_model_kwargs())
```

判据：确认 `strict` / `tool_choice` / `tools` / `response_format` 这些关键字段的真实取值，而不是推测。

### 4. 依赖升级前先 dry-run 看连带影响

```bash
pip install "<pkg>==<target-version>" --dry-run 2>&1 | grep "^Would install"
```

本次实测：升到最新版会连带升级 3 个核心依赖（其中一个是大版本跳跃），而**升到满足需求的最低版本只动一个包**。

判据：**选满足需求的最低版本**，把升级面压到最小；大版本跳跃留作独立议题。

### 5. 真实调用验证 + 保留下游契约

- 改完至少真实调用一次，确认新路径产出正确（不只是测试通过）
- **让下游消费契约不变**：本次把结构化结果 `model_dump()` 成原有的 dict 形态，下游一行未改，改动面从「全链路」缩到「构造 + 调用」两处

## 反模式

- ❌ 相信旧结论直接实施 —— 结论可能成立于「另一个调用通道」或「另一个版本」
- ❌ 只看文档描述就下判断 —— 描述对应的是最新版，装的是旧版
- ❌ 以为「官方 = 更好」—— 本次官方路径在当前版本**反而更弱**（丢 strict），只是代码更少
- ❌ 为了用官方 API 而升级到大版本 —— 先看连带影响面，再决定升到哪一版
- ❌ 迁移时顺手重构下游 —— 保持下游契约不变，才能把风险限制在迁移本身

## 与其他 skill 的分工

| skill | 关注点 |
| --- | --- |
| `plan-premise-verification` | 计划条目在**本代码库**有没有对象可做（死配置、断链、无触发场景） |
| 本 skill | 官方 API / 框架在**当前版本与通道**下真实做什么（签名、源码、请求体、升级影响面） |

两者常配合使用：先核实「有没有对象」，再核实「官方实现是不是真如预期」。

## 断言有效性自检

迁移后若补了断言（如「请求体必须带 strict」），**必须注入一次人为退化**确认它真会失败 —— 做法见 `plan-premise-verification` 的「断言有效性自检」一节。
