#!/usr/bin/env python3
"""Tạo bản index.html có nhúng sẵn dữ liệu tiếng Anh (dùng cho artifact hoặc mở trực tiếp không cần server)."""
import json, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FILES = ['data/en.json']
MARK = '<script>'

def block(rel):
    data = json.loads((ROOT / rel).read_text(encoding='utf-8'))
    text = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    text = text.replace('<', '\\u003c')
    return '<script type="application/json" data-file="%s">%s</script>\n' % (rel, text)

def main():
    out_name = sys.argv[1] if len(sys.argv) > 1 else 'index-inline.html'
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    inline = ''.join(block(f) for f in FILES)
    out = html.replace(MARK, inline + MARK, 1)
    pathlib.Path(ROOT / out_name).write_text(out, encoding='utf-8')
    print(f"Created {out_name} successfully!")

if __name__ == '__main__':
    main()
