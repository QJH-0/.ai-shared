# AI 先读 / READ FIRST — 本目录是共享配置的硬链接入口

本目录（某个 AI 工具的配置根目录）通过链接指向唯一维护源：

    C:\Users\20448\.ai-shared

具体映射关系：
- AGENTS.md   → 硬链接（HardLink）    → C:\Users\20448\.ai-shared\AGENTS.md
- skills\     → 目录联接（Junction）   → C:\Users\20448\.ai-shared\skills\
- agents\     → 目录联接（Junction）   → C:\Users\20448\.ai-shared\agents\

## 重要：模型读的是这里的链接副本，不是 .ai-shared
你（AI 助手）直接读取的就是本目录下的 AGENTS.md / skills\ / agents\。
这些与 .ai-shared 下的是**同一份内容**：
- AGENTS.md 是硬链接（HardLink）：任意一个被修改，其余全部立即同步。
- skills\、agents\ 是目录联接（Junction）：读取与写入都透明穿透到 .ai-shared，无需复制。

## 更新规则（务必遵守）
1. ✅ 要改配置，直接编辑唯一源 C:\Users\20448\.ai-shared\ 下的对应文件/目录。
2. ✅ 保存后，本目录的 AGENTS.md / skills\ / agents\ 会自动同步更新。
3. ❌ 不要在本目录直接改写 AGENTS.md，也不要删除它后用新文件覆盖
   （删除 + 新建会破坏硬链接，使本目录与共享源脱钩，变成独立副本，改动不再同步）。
4. ❌ skills\ / agents\ 是目录联接，不要在本目录删除它们再重建
   （联接只应建一次；要改内容请直接操作 .ai-shared 下的源目录）。
5. 任何新增 / 调整都应在 C:\Users\20448\.ai-shared\ 中进行，由硬链接 / 联接自动分发到所有工具。
