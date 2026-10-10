#!/usr/bin/env python3
"""把 .ai-shared/mcp.json 同步到格式不兼容、无法硬链接的两个客户端。

背景：mcp.json 用 command/args 的 stdio 写法，能被 .cursor / .qoder / .workbuddy /
.workbuddy-ai / .agents 直接硬链接共用；但 Codex 用 TOML、Claude 把用户级
MCP 放在 ~/.claude.json 顶层，格式不同建不了链接，只能从唯一维护源派生。

同步是**双向**的：源里新增或修改的 server 写入派生端，源里**消失**的 server 也从派生端删除。
删除范围只覆盖本脚本自己写过的 server——名单记在 STATE 里，所以 Codex 自管的
`[mcp_servers.node_repl]` 这类段不会被误删。

用法：
  python sync-mcp-config.py --check   # 只校验，有漂移则退出码 1
  python sync-mcp-config.py           # 写回
"""

import argparse
import json
import sys
from pathlib import Path

HOME = Path(r'C:\Users\20448')
SOURCE = HOME / '.ai-shared' / 'mcp.json'
STATE = HOME / '.ai-shared' / '.mcp-synced.json'
CODEX_CONFIG = HOME / '.codex' / 'config.toml'
CLAUDE_JSON = HOME / '.claude.json'

HARDLINK_TARGETS = [
    HOME / '.cursor' / 'mcp.json',
    HOME / '.qoder' / 'mcp.json',
    HOME / '.workbuddy' / 'mcp.json',
    HOME / '.workbuddy-ai' / 'mcp.json',
    HOME / '.agents' / 'mcp.json',
]

# npx 首次拉包可能超过 Codex 默认的 30s，给足窗口
STARTUP_TIMEOUT_SEC = 120

MCP_TABLE = '[mcp_servers]'


def read_text(path):
    with open(path, 'r', encoding='utf-8', newline='') as fh:
        return fh.read()


def write_text(path, text):
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(text)


def detect_newline(text):
    return '\r\n' if '\r\n' in text else '\n'


def toml_value(value):
    # 字符串优先用字面量单引号：Windows 路径的反斜杠在基本字符串里会被当转义符
    if isinstance(value, str):
        return "'%s'" % value if "'" not in value else json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return '[%s]' % ', '.join(toml_value(item) for item in value)
    if isinstance(value, dict):
        return '{%s}' % ', '.join('%s = %s' % (k, toml_value(v)) for k, v in value.items())
    return json.dumps(value, ensure_ascii=False)


def render_toml_block(name, spec, nl):
    lines = ['[mcp_servers.%s]' % name]
    for key, value in spec.items():
        lines.append('%s = %s' % (key, toml_value(value)))
    if 'startup_timeout_sec' not in spec:
        lines.append('startup_timeout_sec = %d' % STARTUP_TIMEOUT_SEC)
    return nl.join(lines) + nl


def load_source():
    """读源 mcp.json。容忍空文件、空对象与缺失 mcpServers。"""
    raw = read_text(SOURCE).strip()
    if not raw:
        return {}
    return json.loads(raw).get('mcpServers') or {}


def load_state():
    """返回上次由本脚本写入派生端的 server 名集合。"""
    if not STATE.exists():
        return set()
    raw = read_text(STATE).strip()
    if not raw:
        return set()
    return set(json.loads(raw).get('servers') or [])


def save_state(names):
    write_text(STATE, json.dumps({'servers': sorted(names)}, ensure_ascii=False, indent=2) + '\n')


def _is_section(line):
    stripped = line.strip()
    return stripped.startswith('[') and stripped.endswith(']')


def drop_sections(lines, names):
    """删除 [mcp_servers.<name>] 及其子段（如 .env）。

    段前的空行保留下来充当分隔，段后的空行随段一起吃掉——这样「插入再删除」
    能逐字节回到原状。
    """
    if not names:
        return lines
    heads = {'mcp_servers.%s' % name for name in names}
    kept, skipping = [], False
    for line in lines:
        if _is_section(line):
            head = line.strip()[1:-1]
            skipping = any(head == h or head.startswith(h + '.') for h in heads)
        if not skipping:
            kept.append(line)
    return kept


def section_range(lines, header):
    """返回 (start, end) 行索引；end 指向下一段或文件末尾。找不到返回 None。"""
    start = next((i for i, line in enumerate(lines) if line.strip() == header), None)
    if start is None:
        return None
    end = start + 1
    while end < len(lines) and not _is_section(lines[end]):
        end += 1
    return start, end


def sync_codex(text, servers, stale):
    nl = detect_newline(text)
    lines = drop_sections(text.split(nl), stale - set(servers))
    for name, spec in servers.items():
        block = render_toml_block(name, spec, nl).rstrip(nl).split(nl)
        rng = section_range(lines, '[mcp_servers.%s]' % name)
        if rng:
            lines[rng[0]:rng[1]] = block
            continue
        anchor = next((i for i, line in enumerate(lines) if line.strip() == MCP_TABLE), None)
        if anchor is None:
            sys.exit('%s：找不到 %s 段，无法插入' % (CODEX_CONFIG, MCP_TABLE))
        lines[anchor + 1:anchor + 1] = [''] + block
    return nl.join(lines)


def sync_claude(text, servers, stale):
    nl = detect_newline(text)
    data = json.loads(text)
    table = data.setdefault('mcpServers', {})
    for name in stale:
        table.pop(name, None)
    table.update(servers)
    return json.dumps(data, ensure_ascii=False, indent=2).replace('\n', nl) + nl


def check_hardlinks():
    problems = []
    source_bytes = SOURCE.read_bytes()
    for target in HARDLINK_TARGETS:
        if not target.exists():
            problems.append('%s：不存在' % target)
        elif target.read_bytes() != source_bytes:
            problems.append('%s：内容与源不一致（链接已脱钩）' % target)
    expected = 1 + len(HARDLINK_TARGETS)
    actual = SOURCE.stat().st_nlink
    if actual != expected:
        problems.append('%s：硬链接数 %d，应为 %d' % (SOURCE, actual, expected))
    return problems


def main():
    parser = argparse.ArgumentParser(description='从 .ai-shared/mcp.json 派生 Codex / Claude 的 MCP 配置')
    parser.add_argument('--check', action='store_true', help='只校验，有漂移则退出码 1')
    args = parser.parse_args()

    servers = load_source()
    state = load_state()
    stale = state - set(servers)

    codex_new = sync_codex(read_text(CODEX_CONFIG), servers, stale)
    claude_new = sync_claude(read_text(CLAUDE_JSON), servers, stale)

    drift = []
    if codex_new != read_text(CODEX_CONFIG):
        drift.append(CODEX_CONFIG)
    if claude_new != read_text(CLAUDE_JSON):
        drift.append(CLAUDE_JSON)
    if state != set(servers):
        drift.append(STATE)
    drift += check_hardlinks()

    if stale:
        print('PRUNE %s' % ', '.join(sorted(stale)))

    if args.check:
        for item in drift:
            print('DRIFT %s' % item)
        print('OK' if not drift else 'FAILED: %d 处漂移' % len(drift))
        return 1 if drift else 0

    if CODEX_CONFIG in drift:
        write_text(CODEX_CONFIG, codex_new)
        print('WROTE %s' % CODEX_CONFIG)
    if CLAUDE_JSON in drift:
        write_text(CLAUDE_JSON, claude_new)
        print('WROTE %s' % CLAUDE_JSON)
    if STATE in drift:
        save_state(servers)
        print('WROTE %s' % STATE)
    print('hardlinks OK (%d)' % len(HARDLINK_TARGETS))
    return 0


if __name__ == '__main__':
    sys.exit(main())
