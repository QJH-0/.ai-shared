#!/usr/bin/env python3
"""把 .ai-shared/mcp.json 同步到格式不兼容、无法硬链接的两个客户端。

背景：mcp.json 用 command/args 的 stdio 写法，能被 .cursor / .qoder / .workbuddy /
.workbuddy-ai / .catpawai / .agents 直接硬链接共用；但 Codex 用 TOML、Claude 把用户级
MCP 放在 ~/.claude.json 顶层，格式不同建不了链接，只能从唯一维护源派生。

TOML 侧只重生成源里出现过的 server 段，其余段（如 Codex 自管的 node_repl）原样保留。

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
CODEX_CONFIG = HOME / '.codex' / 'config.toml'
CLAUDE_JSON = HOME / '.claude.json'

HARDLINK_TARGETS = [
    HOME / '.cursor' / 'mcp.json',
    HOME / '.qoder' / 'mcp.json',
    HOME / '.workbuddy' / 'mcp.json',
    HOME / '.workbuddy-ai' / 'mcp.json',
    HOME / '.catpawai' / 'mcp.json',
    HOME / '.agents' / 'mcp.json',
]

# npx 首次拉包可能超过 Codex 默认的 30s，给足窗口
STARTUP_TIMEOUT_SEC = 120


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


def sync_codex(text, servers):
    """替换源里出现过的 [mcp_servers.<name>] 段；源里没有的段原样保留。"""
    nl = detect_newline(text)
    for name in servers:
        header = '[mcp_servers.%s]' % name
        start = text.find(nl + header + nl)
        block = render_toml_block(name, servers[name], nl)
        if start == -1:
            anchor = text.find('[mcp_servers]' + nl)
            if anchor == -1:
                sys.exit('%s：找不到 [mcp_servers] 段，无法插入' % CODEX_CONFIG)
            insert_at = anchor + len('[mcp_servers]' + nl)
            text = text[:insert_at] + nl + block + text[insert_at:]
            continue
        end = text.find(nl + '[', start + 1)
        end = len(text) if end == -1 else end + len(nl)
        text = text[:start + len(nl)] + block + nl + text[end:]
    return text


def sync_claude(text, servers):
    nl = detect_newline(text)
    data = json.loads(text)
    table = data.setdefault('mcpServers', {})
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

    servers = json.loads(read_text(SOURCE))['mcpServers']

    codex_new = sync_codex(read_text(CODEX_CONFIG), servers)
    claude_new = sync_claude(read_text(CLAUDE_JSON), servers)
    drift = []
    if codex_new != read_text(CODEX_CONFIG):
        drift.append(CODEX_CONFIG)
    if claude_new != read_text(CLAUDE_JSON):
        drift.append(CLAUDE_JSON)
    drift += check_hardlinks()

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
    print('hardlinks OK (%d)' % len(HARDLINK_TARGETS))
    return 0


if __name__ == '__main__':
    sys.exit(main())
