"""
محرك تحويل الماركداون إلى HTML، مضبوط لنص مختلط عربي/إنجليزي.

الوحدة دي مستقلة تماماً عن ويندوز، فتقدر تتستّ على أي نظام.
"""

import html as html_mod
import re

# نطاقات يونيكود العربية (أساسي + ملحق + موسّع + أشكال العرض)
ARABIC_RE = re.compile(
    r'[؀-ۿݐ-ݿࢠ-ࣿﭐ-﷿ﹰ-﻿]'
)

# علامات التشكيل — تستخدم لخيار "إخفاء التشكيل"
TASHKEEL_RE = re.compile(r'[ؐ-ًؚ-ٰٟۖ-ۭ]')

_UL_RE = re.compile(r'^(\s*)[-*+]\s+(.*)$')
_OL_RE = re.compile(r'^(\s*)\d+[.)]\s+(.*)$')
_HEADING_RE = re.compile(r'^(#{1,6})\s+(.*)$')
_HR_RE = re.compile(r'^\s*([-*_])(\s*\1){2,}\s*$')
_QUOTE_RE = re.compile(r'^\s*>\s?')
_CODE_MARK_RE = re.compile(r'^\x00CB(\d+)\x00$')
_TASK_RE = re.compile(r'^\[([ xX])\]\s+(.*)$')


def has_arabic(text):
    return bool(ARABIC_RE.search(text))


def strip_tashkeel(text):
    return TASHKEEL_RE.sub('', text)


def _esc(text):
    return html_mod.escape(text, quote=True)


def _dir_of(text):
    """اتجاه الفقرة: rtl لو فيها عربي، وإلا auto عشان المتصفح يقرر."""
    return 'rtl' if has_arabic(text) else 'auto'


# ─────────────────────────── المستوى السطري (inline) ───────────────────────────

def _inline(text):
    """يحوّل تنسيقات السطر الواحد. المدخل نص خام غير مهروب."""
    text = _esc(text)

    codes = []
    anchors = []

    def _save_code(m):
        codes.append(m.group(1))
        return f'\x00IC{len(codes) - 1}\x00'

    def _save_link(m):
        anchors.append((m.group(1), m.group(2)))
        return f'\x00LK{len(anchors) - 1}\x00'

    def _save_auto(m):
        url = m.group(0)
        trail = ''
        # ماننفعش نبلع علامات الترقيم في آخر اللينك
        while url and url[-1] in '.,;:!?)':
            trail = url[-1] + trail
            url = url[:-1]
        if not url:
            return m.group(0)
        anchors.append((url, url))
        return f'\x00LK{len(anchors) - 1}\x00' + trail

    # الكود السطري أولاً عشان مايتأثرش بباقي التنسيقات
    text = re.sub(r'`([^`\n]+)`', _save_code, text)
    text = re.sub(r'\[([^\]\n]*)\]\(([^)\s]+)\)', _save_link, text)
    text = re.sub(r'(?<![\w@])https?://[^\s<>"\'؀-ۿ]+', _save_auto, text)

    text = re.sub(r'\*\*(?=\S)(.+?)(?<=\S)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'~~(?=\S)(.+?)(?<=\S)~~', r'<del>\1</del>', text)
    text = re.sub(r'(?<![*\w])\*(?=\S)([^*\n]+?)(?<=\S)\*(?!\*)', r'<em>\1</em>', text)

    for i, (label, url) in enumerate(anchors):
        safe_url = url if re.match(r'^(https?:|mailto:)', url, re.I) else '#'
        text = text.replace(
            f'\x00LK{i}\x00',
            f'<a href="{safe_url}" data-ext="1">{label}</a>',
        )
    for i, code in enumerate(codes):
        text = text.replace(
            f'\x00IC{i}\x00',
            f'<code class="inl" dir="ltr">{code}</code>',
        )
    return text


# ─────────────────────────── بلوكات الكود ───────────────────────────

def _extract_fences(src):
    """يسحب بلوكات ``` ويسيب مكانها علامة، عشان مايتفسّروش كماركداون."""
    blocks = []

    def _sub(m):
        blocks.append((m.group(1) or '', m.group(2).rstrip('\n')))
        return f'\n\x00CB{len(blocks) - 1}\x00\n'

    src = re.sub(
        r'(?m)^[ \t]*```[ \t]*([\w+#-]*)[ \t]*\n([\s\S]*?)^[ \t]*```[ \t]*$',
        _sub, src,
    )
    return blocks, src


def _render_code(lang, code, index):
    lang_label = f'<span class="lang">{_esc(lang)}</span>' if lang else '<span class="lang"></span>'
    return (
        f'<div class="codeblock" dir="ltr" data-i="{index}">'
        f'<div class="codebar">{lang_label}'
        f'<button class="ccopy" type="button" title="نسخ الكود">'
        f'<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" '
        f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'<rect x="9" y="9" width="11" height="11" rx="2"/>'
        f'<path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg></button></div>'
        f'<pre><code>{_esc(code)}</code></pre></div>'
    )


# ─────────────────────────── الجداول ───────────────────────────

def _split_row(line):
    line = line.strip()
    if line.startswith('|'):
        line = line[1:]
    if line.endswith('|') and not line.endswith('\\|'):
        line = line[:-1]
    return [c.strip() for c in re.split(r'(?<!\\)\|', line)]


def _is_table_sep(line):
    if '|' not in line:
        return False
    cells = _split_row(line)
    return bool(cells) and all(re.fullmatch(r':?-{1,}:?', c) for c in cells if c != '')


def _render_table(header, sep, rows):
    aligns = []
    for cell in _split_row(sep):
        left, right = cell.startswith(':'), cell.endswith(':')
        aligns.append('center' if left and right else 'left' if left else 'right' if right else '')

    def cells(line, tag):
        out = []
        for i, cell in enumerate(_split_row(line)):
            align = aligns[i] if i < len(aligns) else ''
            style = f' style="text-align:{align}"' if align else ''
            out.append(f'<{tag}{style}>{_inline(cell)}</{tag}>')
        return ''.join(out)

    body = ''.join(f'<tr>{cells(r, "td")}</tr>' for r in rows)
    d = _dir_of(header + ' '.join(rows))
    return (
        f'<div class="tablewrap"><table dir="{d}">'
        f'<thead><tr>{cells(header, "th")}</tr></thead>'
        f'<tbody>{body}</tbody></table></div>'
    )


# ─────────────────────────── القوائم ───────────────────────────

def _collect_list(lines, i):
    """يجمع سطور قائمة متتالية، ويرجّع (عناصر، المؤشر الجديد)."""
    items = []
    while i < len(lines):
        line = lines[i]
        mu, mo = _UL_RE.match(line), _OL_RE.match(line)
        m = mu or mo
        if m:
            items.append([len(m.group(1)), 'ul' if mu else 'ol', m.group(2)])
            i += 1
            continue
        # سطر تكملة مُزاح تحت آخر عنصر
        if items and line.strip() and len(line) - len(line.lstrip()) >= 2:
            items[-1][2] += ' ' + line.strip()
            i += 1
            continue
        break
    return items, i


def _render_items(items, pos, indent):
    typ = items[pos][1]
    joined = ' '.join(it[2] for it in items[pos:])
    parts = [f'<{typ} dir="{_dir_of(joined)}">']
    while pos < len(items):
        ind, t, text = items[pos]
        if ind < indent or (ind == indent and t != typ):
            break
        if ind > indent:
            break
        task = _TASK_RE.match(text)
        if task:
            checked = ' checked' if task.group(1).lower() == 'x' else ''
            inner = (
                f'<label class="task"><input type="checkbox" disabled{checked}>'
                f'<span>{_inline(task.group(2))}</span></label>'
            )
        else:
            inner = _inline(text)
        parts.append(f'<li>{inner}')
        pos += 1
        while pos < len(items) and items[pos][0] > indent:
            sub, pos = _render_items(items, pos, items[pos][0])
            parts.append(sub)
        parts.append('</li>')
    parts.append(f'</{typ}>')
    return ''.join(parts), pos


def _render_list(items):
    out, pos = [], 0
    while pos < len(items):
        html, new_pos = _render_items(items, pos, items[pos][0])
        if new_pos == pos:       # حماية من لوب لا نهائي
            break
        out.append(html)
        pos = new_pos
    return ''.join(out)


# ─────────────────────────── المحرك الرئيسي ───────────────────────────

def render(src):
    """يحوّل نص ماركداون إلى HTML جاهز للعرض داخل .content"""
    src = src.replace('\r\n', '\n').replace('\r', '\n').replace('\t', '    ')
    code_blocks, src = _extract_fences(src)
    lines = src.split('\n')
    out, i = [], 0

    while i < len(lines):
        line = lines[i]

        cm = _CODE_MARK_RE.match(line)
        if cm:
            idx = int(cm.group(1))
            lang, code = code_blocks[idx]
            out.append(_render_code(lang, code, idx))
            i += 1
            continue

        if not line.strip():
            i += 1
            continue

        hm = _HEADING_RE.match(line)
        if hm:
            level, text = len(hm.group(1)), hm.group(2)
            out.append(f'<h{level} dir="{_dir_of(text)}">{_inline(text)}</h{level}>')
            i += 1
            continue

        if _HR_RE.match(line):
            out.append('<hr>')
            i += 1
            continue

        if '|' in line and i + 1 < len(lines) and _is_table_sep(lines[i + 1]):
            header, sep = line, lines[i + 1]
            i += 2
            rows = []
            while i < len(lines) and '|' in lines[i] and lines[i].strip():
                rows.append(lines[i])
                i += 1
            out.append(_render_table(header, sep, rows))
            continue

        if _QUOTE_RE.match(line):
            buf = []
            while i < len(lines) and _QUOTE_RE.match(lines[i]):
                buf.append(_QUOTE_RE.sub('', lines[i]))
                i += 1
            inner = render('\n'.join(buf))
            out.append(f'<blockquote dir="{_dir_of(" ".join(buf))}">{inner}</blockquote>')
            continue

        if _UL_RE.match(line) or _OL_RE.match(line):
            items, i = _collect_list(lines, i)
            out.append(_render_list(items))
            continue

        # فقرة عادية
        buf = [line]
        i += 1
        while i < len(lines):
            nxt = lines[i]
            if (not nxt.strip()
                    or _CODE_MARK_RE.match(nxt)
                    or _HEADING_RE.match(nxt)
                    or _HR_RE.match(nxt)
                    or _QUOTE_RE.match(nxt)
                    or _UL_RE.match(nxt)
                    or _OL_RE.match(nxt)
                    or ('|' in nxt and i + 1 < len(lines) and _is_table_sep(lines[i + 1]))):
                break
            buf.append(nxt)
            i += 1
        # السطر الجديد جوه الفقرة سطر ليّن زي الماركداون القياسي — بيتجمّع
        # بمسافة. الكسر الصريح بمسافتين في آخر السطر أو بشرطة مايلة.
        parts = []
        for pos, raw in enumerate(buf):
            hard = raw.endswith('  ') or raw.rstrip().endswith('\\')
            chunk = raw.strip().rstrip('\\').strip()
            parts.append(_inline(chunk))
            if pos < len(buf) - 1:
                parts.append('<br>' if hard else ' ')
        text = ' '.join(buf)
        out.append(f'<p dir="{_dir_of(text)}">{"".join(parts)}</p>')

    return ''.join(out)
