#!/usr/bin/env python3
"""从 agents/*.md 重生成派生副本 agents/*.toml，保证两者永不漂移。

背景：agents/<name>.md 是唯一维护源（人读），agents/<name>.toml 是给 Codex 用的
派生副本（name + description + developer_instructions）。历史上靠手工转换，出现过
analyst / researcher 的悬空引用（toml 里留着已改名的 skill）。本脚本消除该手工步骤。

两种既有格式按原文件的引号形式自动识别，不做统一：
  \"\"\" 形式 —— 正文每行末尾追加字面量 \\r（反斜杠 + r 两个字符，TOML 解析时还原为 CR），
            正文里的反斜杠转义为 \\\\；正文中的 \" 不转义（三引号串内单个 \" 合法）。
  ''' 形式 —— 正文为真实换行，无 \\r 标记、无反斜杠转义。

head 的 name / description 是单行基本字符串，反斜杠与双引号都要转义。

用法：
  python sync-agent-toml.py --check     # 只校验，有漂移则退出码 1
  python sync-agent-toml.py             # 写回
"""

import argparse
import re
import sys
from pathlib import Path

BLOCK_RE = re.compile(r'developer_instructions\s*=\s*("""|\'\'\')(.*?)\1', re.S)


def read_text(path):
    with open(path, 'r', encoding='utf-8', newline='') as fh:
        return fh.read()


def write_text(path, text):
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(text)


def escape_basic(text):
    return text.replace('\\', '\\\\').replace('"', '\\"')


def parse_md(path):
    text = read_text(path).replace('\r\n', '\n')
    try:
        _, front, body = text.split('---', 2)
    except ValueError:
        sys.exit('%s：缺少 YAML frontmatter' % path)
    fields = {}
    for line in front.split('\n'):
        if line.strip():
            key, _, value = line.partition(':')
            fields[key.strip()] = value.strip()
    for key in ('name', 'description'):
        if key not in fields:
            sys.exit('%s：frontmatter 缺少 %s' % (path, key))
    return fields, body.strip('\n').split('\n')


def parse_toml(path):
    """返回 (正文引号形式, 收尾引号之后的尾部文本)。头部由 frontmatter 重建，不保留。"""
    raw = read_text(path)
    m = BLOCK_RE.search(raw)
    if not m:
        sys.exit('%s：找不到 developer_instructions 块' % path)
    return m.group(1), raw[m.end(0):]


def render(fields, lines, quote):
    # 起始引号后不换行，内容紧跟其后；末行仍带行尾标记，收尾引号紧随其后
    if quote == '"""':
        body = '\n'.join(line.replace('\\', '\\\\') + '\\r' for line in lines) + '\n'
    else:
        body = '\n'.join(lines) + '\n'
    return 'name = "%s"\ndescription = "%s"\ndeveloper_instructions = %s%s%s' % (
        escape_basic(fields['name']), escape_basic(fields['description']), quote, body, quote)


def main():
    parser = argparse.ArgumentParser(description='从 agents/*.md 重生成 agents/*.toml')
    parser.add_argument('--agents-dir', type=Path,
                        default=Path(__file__).resolve().parents[3] / 'agents',
                        help='agents 目录（默认取仓库根的 agents/）')
    parser.add_argument('--check', action='store_true', help='只校验，不写回；有漂移则退出码 1')
    args = parser.parse_args()

    md_files = sorted(args.agents_dir.glob('*.md'))
    if not md_files:
        sys.exit('%s 下没有 *.md' % args.agents_dir)

    drifted = []
    for md in md_files:
        toml = md.with_suffix('.toml')
        if not toml.exists():
            print('%-14s 缺少对应 .toml' % md.name)
            drifted.append(md.name)
            continue
        quote, tail = parse_toml(toml)
        fields, lines = parse_md(md)
        expected = render(fields, lines, quote) + tail
        if read_text(toml) == expected:
            print('%-14s OK' % md.name)
            continue
        drifted.append(md.name)
        print('%-14s 漂移' % md.name)
        if not args.check:
            write_text(toml, expected)
            print('%-14s 已重写 %s' % ('', toml.name))

    if drifted:
        print('\n%s %d 个文件' % ('待同步' if args.check else '已重写', len(drifted)))
        return 1 if args.check else 0
    print('\n全部一致')
    return 0


if __name__ == '__main__':
    sys.exit(main())
