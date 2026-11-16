"""Generate single-language English Practice index.html from lingogo/index.html."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINGOGO_ROOT = ROOT.parent / "lingogo"
SRC_HTML = LINGOGO_ROOT / "index.html"
DST_HTML = ROOT / "index.html"
EN_JSON = ROOT / "data" / "en.json"
VERSION_JSON = ROOT / "version.json"


def replace_exact(src: str, old: str, new: str, count: int = 1, label: str = "") -> str:
    """Replace an exact substring and verify the occurrence count matches."""
    found = src.count(old)
    if found != count:
        tag = label or repr(old[:60])
        raise ValueError(f"Expected {count} match(es) for {tag}, found {found}")
    return src.replace(old, new)


def replace_json_en_only(src: str, const_name: str, label: str = "") -> str:
    """Trim a top-level `const NAME = {en: ..., zh: ..., ja: ...};` object to `en` only."""
    m = re.search(rf"const {re.escape(const_name)} = (\{{.*?\}});", src)
    if not m:
        raise ValueError(f"Could not find const {const_name} ({label})")
    obj = json.loads(m.group(1))
    trimmed = json.dumps({"en": obj["en"]}, ensure_ascii=False, separators=(",", ":"))
    return src[:m.start()] + f"const {const_name} = {trimmed};" + src[m.end():]


def main() -> None:
    if not SRC_HTML.exists():
        raise FileNotFoundError(f"Source HTML not found: {SRC_HTML}")
    en_data = json.loads(EN_JSON.read_text(encoding="utf-8"))
    ver_data = json.loads(VERSION_JSON.read_text(encoding="utf-8"))
    build_id = ver_data["build"]
    app_ver = ver_data["version"]

    html = SRC_HTML.read_text(encoding="utf-8")

    # 1. Head, fonts, scripts, branding
    html = replace_exact(
        html,
        '<meta name="apple-mobile-web-app-title" content="Lingogo">\n<title>Lingogo</title>',
        '<meta name="apple-mobile-web-app-title" content="English Practice">\n<title>English Practice</title>',
        label="title tags",
    )
    html = replace_exact(
        html,
        "https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&family=Noto+Sans+JP:wght@400;500;700&family=Noto+Sans+SC:wght@400;500;700&display=swap",
        "https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&display=swap",
        label="google fonts",
    )
    html = replace_exact(
        html,
        '<script src="https://cdn.jsdelivr.net/npm/hanzi-writer@3.5.0/dist/hanzi-writer.min.js"></script>\n',
        "",
        label="hanzi-writer script",
    )
    html = replace_exact(
        html,
        '<script src="English/data/ielts_30day_listening.js"></script>',
        '<script src="data/ielts_30day_listening.js"></script>',
        label="ielts listening data script",
    )

    # 2. Header comment, build ID, single-language config & path helpers
    html = replace_exact(
        html,
        "   Lingogo — học Anh, Trung, Nhật trong một app.\n"
        "   Dữ liệu bài học nằm trong data/<ngôn ngữ>.json (tải khi cần), âm thanh thu sẵn\n"
        "   trong audio/, nét chữ trong data/strokes-<zh|ja>.json.",
        "   English Practice — Học & Luyện Tiếng Anh mỗi ngày (đồng bộ từ Lingogo).\n"
        "   Dữ liệu bài học nằm trong data/en.json và data/ielts_30day_listening.js,\n"
        "   âm thanh thu sẵn nằm trong audio/ (audio/w*.json, audio/mail/, audio/listen/, audio/ielts/).",
        label="banner comment",
    )
    html = re.sub(
        r"const APP_BUILD_ID = '[^']+';",
        f"const APP_BUILD_ID = '{build_id}';",
        html,
        count=1,
    )
    html = replace_exact(
        html,
        "const LANGS = {\n"
        "  en: { label: 'English', vi: 'Tiếng Anh', short: 'Anh', folder: 'English', tts: 'en-US', rec: 'en-US', lang: 'en', cjk: false },\n"
        "  zh: { label: '中文', vi: 'Tiếng Trung', short: 'Trung', folder: 'Chinese', tts: 'zh-CN', rec: 'zh-CN', lang: 'zh-Hans', cjk: true },\n"
        "  ja: { label: '日本語', vi: 'Tiếng Nhật', short: 'Nhật', folder: 'Japanese', tts: 'ja-JP', rec: 'ja-JP', lang: 'ja', cjk: true },\n"
        "};\n"
        "const langFolder = (code) => (LANGS[code] && LANGS[code].folder) || (code === 'en' ? 'English' : (code === 'zh' ? 'Chinese' : 'Japanese'));",
        "const LANGS = {\n"
        "  en: { label: 'English', vi: 'Tiếng Anh', short: 'Anh', folder: '', tts: 'en-US', rec: 'en-US', lang: 'en', cjk: false },\n"
        "};\n"
        "const langFolder = (code) => (LANGS[code] && LANGS[code].folder) || '';\n"
        "const langPath = (code, rel) => { const f = langFolder(code); return f ? f + '/' + rel : rel; };",
        label="LANGS and langPath",
    )

    # 3. Trim CATEGORIES and JSON metadata constants to English-only
    cats_start = html.index("const CATEGORIES = {")
    cats_end = html.index("\n// ===== DỮ LIỆU ĐỊNH DANH BÀI HỌC", cats_start)
    cats_block = html[cats_start:cats_end]
    zh_pos = cats_block.index(",\n  zh: [")
    en_cats_block = cats_block[:zh_pos] + "\n};\n"
    html = html[:cats_start] + en_cats_block + html[cats_end:]

    for const_name in ("TOPIC_META", "CAT_TOTAL_TOPICS", "CAT_TOTAL_LESSONS", "LANG_TOTAL_TOPICS", "LANG_TOTAL_LESSONS"):
        html = replace_json_en_only(html, const_name)

    # 4. Path lookups from English/<subpath> to root <subpath>
    html = replace_exact(
        html,
        "    const fld = langFolder(code);\n    const d = await getJSON(fld + '/data/' + code + '.json');",
        "    const d = await getJSON(langPath(code, 'data/' + code + '.json'));",
        label="loadLang",
    )
    html = replace_exact(
        html,
        "    const fld = langFolder(code);\n    try { STROKES[code] = await getJSON(fld + '/data/strokes-' + code + '.json'); } catch (e) { STROKES[code] = {}; }",
        "    try { STROKES[code] = await getJSON(langPath(code, 'data/strokes-' + code + '.json')); } catch (e) { STROKES[code] = {}; }",
        label="loadStrokes",
    )
    html = replace_exact(
        html,
        "  const fld = langFolder(code);\n"
        "  return code === 'en' ? { file: fld + '/audio/w' + a[0] + '.json', key: a[1] } : { file: fld + '/audio/' + code + '-' + a + '.json', key: text };",
        "  return code === 'en' ? { file: langPath(code, 'audio/w' + a[0] + '.json'), key: a[1] } : { file: langPath(code, 'audio/' + code + '-' + a + '.json'), key: text };",
        label="bundleOf",
    )
    html = replace_exact(
        html,
        "  if (track.audio.startsWith('audio/')) return langFolder(code) + '/' + track.audio;",
        "  if (track.audio.startsWith('audio/')) return langPath(code, track.audio);",
        label="resolveTrackAudioSrc",
    )
    html = replace_exact(
        html,
        "  const fld = langFolder(code);\n"
        "  let mailSrc = fill.audio || (code === 'en' && tid && !fill.src ? 'audio/mail/' + code + '-' + tid + '.mp3' : null);\n"
        "  if (mailSrc && mailSrc.startsWith('audio/')) {\n"
        "    mailSrc = fld + '/' + mailSrc;\n"
        "  }",
        "  let mailSrc = fill.audio || (code === 'en' && tid && !fill.src ? 'audio/mail/' + code + '-' + tid + '.mp3' : null);\n"
        "  if (mailSrc && mailSrc.startsWith('audio/')) {\n"
        "    mailSrc = langPath(code, mailSrc);\n"
        "  }",
        label="fillReveal mailSrc",
    )
    html = html.replace("'English/audio/ielts/", "'audio/ielts/")

    # 5. State normalization & Gist sync keys
    html = replace_exact(
        html,
        "try { const raw = localStorage.getItem(KEY); if (raw) S = Object.assign(fresh(), JSON.parse(raw)); } catch (e) { /* bị chặn lưu trữ */ }",
        "try { const raw = localStorage.getItem(KEY); if (raw) S = Object.assign(fresh(), JSON.parse(raw)); } catch (e) { /* bị chặn lưu trữ */ }\nS.lang = 'en';",
        label="force S.lang en on boot",
    )
    html = replace_exact(
        html,
        "const GH_KEY = 'lingogo-github-sync';\n"
        "const GH_SYNC = { timer: 0, seen: -1, running: false };\n"
        "function getGhConfig() {\n"
        "  try { const raw = localStorage.getItem(GH_KEY); return raw ? JSON.parse(raw) : { token: '', gistId: '', user: '' }; } catch (e) { return { token: '', gistId: '', user: '' }; }\n"
        "}",
        "const GH_KEY = 'english-practice-github-sync';\n"
        "const GH_SYNC = { timer: 0, seen: -1, running: false };\n"
        "function getGhConfig() {\n"
        "  try {\n"
        "    const raw = localStorage.getItem(GH_KEY);\n"
        "    if (raw) return JSON.parse(raw);\n"
        "    const old = localStorage.getItem('lingogo-github-sync');\n"
        "    if (old) return JSON.parse(old);\n"
        "    return { token: '', gistId: '', user: '' };\n"
        "  } catch (e) { return { token: '', gistId: '', user: '' }; }\n"
        "}",
        label="GH_KEY and getGhConfig fallback",
    )
    html = replace_exact(
        html,
        "description: 'Lingogo Learning Progress Backup (Tự động đồng bộ)',",
        "description: 'English Practice Learning Progress Backup (Tự động đồng bộ)',",
        label="gist description",
    )
    html = replace_exact(
        html,
        "S = mergeState(S, remote);",
        "S = mergeState(S, remote); S.lang = 'en';",
        count=2,
        label="pullGhSync and pushGhSync normalize lang",
    )
    html = replace_exact(
        html,
        "  if (!S.name) return welcomeView();",
        "  if (!LANGS[S.lang]) S.lang = 'en';\n  if (!S.name) return welcomeView();",
        label="route guard S.lang",
    )

    # 6. Schedule & Finish estimate for English-only mode
    html = replace_exact(
        html,
        "const WEEKLY_SCHEDULE = {\n"
        "  1: { // Thứ Hai\n"
        "    name: 'Thứ Hai', focus: 'en',\n"
        "    title: '🇬🇧 Thứ Hai: Trọng tâm Tiếng Anh (Nghe + Nói)',\n"
        "    desc: 'Học 1 bài mới Tiếng Anh (Hội thoại B2 & Phản xạ) · Tiếng Trung & Nhật ôn nhẹ gói 10 từ',\n"
        "    goals: { en: 2.0, zh: 0.5, ja: 0.5 }\n"
        "  },\n"
        "  2: { // Thứ Ba\n"
        "    name: 'Thứ Ba', focus: 'zh',\n"
        "    title: '🇨🇳 Thứ Ba: Trọng tâm Tiếng Trung (Đọc + Viết + Từ vựng)',\n"
        "    desc: 'Học 1 bài mới Tiếng Trung (Bộ thủ, Chiết tự & HSK) · Tiếng Anh & Nhật ôn nhẹ gói 10 từ',\n"
        "    goals: { zh: 2.0, en: 0.5, ja: 0.5 }\n"
        "  },\n"
        "  3: { // Thứ Tư\n"
        "    name: 'Thứ Tư', focus: 'ja',\n"
        "    title: '🇯🇵 Thứ Tư: Trọng tâm Tiếng Nhật (Giải trí + Nghe + Nhại giọng)',\n"
        "    desc: 'Học 1 bài mới Tiếng Nhật N5 & Luyện nghe/nhại giọng · Tiếng Anh & Trung ôn nhẹ gói 10 từ',\n"
        "    goals: { ja: 2.0, en: 0.5, zh: 0.5 }\n"
        "  },\n"
        "  4: { // Thứ Năm\n"
        "    name: 'Thứ Năm', focus: 'en',\n"
        "    title: '🇬🇧 Thứ Năm: Trọng tâm Tiếng Anh (Nghe + Nói)',\n"
        "    desc: 'Học 1 bài mới Tiếng Anh (Podcast & Giao tiếp thực tế) · Tiếng Trung & Nhật ôn nhẹ gói 10 từ',\n"
        "    goals: { en: 2.0, zh: 0.5, ja: 0.5 }\n"
        "  },\n"
        "  5: { // Thứ Sáu\n"
        "    name: 'Thứ Sáu', focus: 'zh',\n"
        "    title: '🇨🇳 Thứ Sáu: Trọng tâm Tiếng Trung (Đọc + Viết + Từ vựng)',\n"
        "    desc: 'Học 1 bài mới Tiếng Trung (Viết Hán tự & Ngữ pháp HSK) · Tiếng Anh & Nhật ôn nhẹ gói 10 từ',\n"
        "    goals: { zh: 2.0, en: 0.5, ja: 0.5 }\n"
        "  },\n"
        "  6: { // Thứ Bảy\n"
        "    name: 'Thứ Bảy', focus: 'ja',\n"
        "    title: '🇯🇵 Thứ Bảy: Trọng tâm Tiếng Nhật (Giải trí + Nghe + Nhại giọng)',\n"
        "    desc: 'Học 1 bài mới Tiếng Nhật N5 & Ôn Kanji · Tiếng Anh & Trung ôn nhẹ gói 10 từ',\n"
        "    goals: { ja: 2.0, en: 0.5, zh: 0.5 }\n"
        "  },\n"
        "  0: { // Chủ Nhật\n"
        "    name: 'Chủ Nhật', focus: 'all',\n"
        "    title: '🧘 Chủ Nhật: Tổng ôn nhẹ 3 ngôn ngữ hoặc Nghỉ ngơi',\n"
        "    desc: 'Không học bài mới · Ôn gói từ vựng dễ quên trong tuần của cả 3 tiếng',\n"
        "    goals: { en: 1.0, zh: 1.0, ja: 1.0 }\n"
        "  }\n"
        "};",
        "const WEEKLY_SCHEDULE = {\n"
        "  1: { name: 'Thứ Hai', focus: 'en', title: '🇬🇧 Thứ Hai: Từ vựng & Phản xạ Nghe', desc: 'Học 1 bài mới theo lộ trình CEFR + Ôn gói từ SRS', goals: { en: 1.0 } },\n"
        "  2: { name: 'Thứ Ba', focus: 'en', title: '🇬🇧 Thứ Ba: Nói & Giao tiếp Thương mại', desc: 'Học 1 bài mới + Luyện nói không giới hạn nâng % điểm', goals: { en: 1.0 } },\n"
        "  3: { name: 'Thứ Tư', focus: 'en', title: '🇬🇧 Thứ Tư: Đọc hiểu & Viết Email', desc: 'Học 1 bài mới + Hoàn thành mẫu email công việc', goals: { en: 1.0 } },\n"
        "  4: { name: 'Thứ Năm', focus: 'en', title: '🇬🇧 Thứ Năm: Hội thoại dài & Nghe chép', desc: 'Học 1 bài mới + Luyện nghe hội thoại B1–C2 thực tế', goals: { en: 1.0 } },\n"
        "  5: { name: 'Thứ Sáu', focus: 'en', title: '🇬🇧 Thứ Sáu: Kỹ năng & Luyện IELTS', desc: 'Học 1 bài mới + Thực hành đề IELTS 4 kỹ năng', goals: { en: 1.0 } },\n"
        "  6: { name: 'Thứ Bảy', focus: 'en', title: '🇬🇧 Thứ Bảy: Củng cố & Ôn tập SRS', desc: 'Học 1 bài mới + Giải quyết các từ dễ quên trong tuần', goals: { en: 1.0 } },\n"
        "  0: { name: 'Chủ Nhật', focus: 'all', title: '🧘 Chủ Nhật: Tổng ôn nhẹ hoặc Nghỉ ngơi', desc: 'Không học bài mới · Ôn nhẹ gói từ vựng dễ quên trong tuần', goals: { en: 1.0 } }\n"
        "};",
        label="WEEKLY_SCHEDULE",
    )
    html = replace_exact(
        html,
        "    // Lịch xoay vòng 2-2-2-1 cân bằng 3 thứ tiếng:\n"
        "    // Tiếng Anh: T2, T5 (2 bài/tuần)\n"
        "    // Tiếng Trung: T3, T6 (2 bài/tuần)\n"
        "    // Tiếng Nhật: T4, T7 (2 bài/tuần)\n"
        "    topicsPerDay = 2 / 7;",
        "    // Lịch đều đặn T2–T7 (6 bài/tuần · Chủ Nhật tổng ôn nhẹ):\n"
        "    topicsPerDay = 6 / 7;",
        label="calcFinishEstimate topicsPerDay",
    )
    html = replace_exact(
        html,
        "function getUnifiedDaySlots(dayIdx) {\n"
        "  const sch = WEEKLY_SCHEDULE[dayIdx] || WEEKLY_SCHEDULE[0];\n"
        "  const isSun = sch.focus === 'all';\n"
        "  const baseItems = [\n"
        "    {\n"
        "      code: 'en',\n"
        "      langTitle: '🇬🇧 Tiếng Anh (Giao tiếp & B2)',\n"
        "      focusTask: 'Học 1 bài mới (Giao tiếp / B2) + Luyện Nghe/Nói phản xạ & Ôn gói 15 từ.',\n"
        "      lightTask: 'Không học bài mới · Ôn nhanh gói 10 từ SRS để giữ phản xạ.'\n"
        "    },\n"
        "    {\n"
        "      code: 'zh',\n"
        "      langTitle: '🇨🇳 Tiếng Trung (Bộ thủ & HSK)',\n"
        "      focusTask: 'Học 1 bài mới (Bộ thủ, Chiết tự & HSK) + Tập viết chữ Hán & Ôn gói 15 từ.',\n"
        "      lightTask: 'Không học bài mới · Ôn nhanh gói 10 từ/chữ Hán đã học.'\n"
        "    },\n"
        "    {\n"
        "      code: 'ja',\n"
        "      langTitle: '🇯🇵 Tiếng Nhật (Giải trí & N5)',\n"
        "      focusTask: 'Học 1 bài mới N5 + Nghe hội thoại / Nhại giọng & Ôn gói 15 từ.',\n"
        "      lightTask: 'Không học bài mới · Ôn nhẹ gói 10 từ Kana/Kanji đã học.'\n"
        "    }\n"
        "  ];",
        "function getUnifiedDaySlots(dayIdx) {\n"
        "  const sch = WEEKLY_SCHEDULE[dayIdx] || WEEKLY_SCHEDULE[0];\n"
        "  const isSun = sch.focus === 'all';\n"
        "  const baseItems = [\n"
        "    {\n"
        "      code: 'en',\n"
        "      langTitle: '🇬🇧 Tiếng Anh (CEFR A1–C2 & IELTS)',\n"
        "      focusTask: sch.desc || 'Học 1 bài mới + Luyện Nghe/Nói phản xạ & Ôn gói từ SRS.',\n"
        "      lightTask: 'Ôn nhẹ gói từ vựng SRS & nghe lại hội thoại.'\n"
        "    }\n"
        "  ];",
        label="getUnifiedDaySlots",
    )

    # 7. Navigation & Pick / Roadmap / Progress single-language UX
    html = replace_exact(
        html,
        "function langSwitch() {\n"
        "  return h('button', { class: 'langchip', 'aria-label': 'Đang học ' + L().short + '. Đổi ngôn ngữ', onclick: () => { PICK_HUB_OPEN = false; go('pick'); } },\n"
        "    h('span', { lang: L().lang }, L().label), h('span', { class: 'caret', 'aria-hidden': 'true' }, '▾'));\n"
        "}",
        "function langSwitch() {\n"
        "  return h('button', { class: 'langchip', 'aria-label': 'Lộ trình & Thời gian biểu', title: 'Xem lộ trình học & tiến độ', onclick: () => { ROADMAP_LANG = 'en'; PICK_TAB = 'roadmap'; PICK_HUB_OPEN = true; go('pick'); } },\n"
        "    h('span', {}, '🗺️ Lộ trình'));\n"
        "}",
        label="langSwitch",
    )
    html = replace_exact(
        html,
        "let VIEW = 'pick'; // mở app là màn hình chọn ngôn ngữ",
        "let VIEW = 'home'; // mở thẳng vào trang học Tiếng Anh",
        label="default VIEW",
    )
    html = replace_exact(
        html,
        "        h('span', { class: 'small muted', style: { fontWeight: 600 } }, isSunday ? '🧘 Nghỉ bài mới · Ôn nhẹ 3 tiếng' : ('🎯 Trọng tâm: ' + LANGS[sch.focus].label))",
        "        h('span', { class: 'small muted', style: { fontWeight: 600 } }, isSunday ? '🧘 Nghỉ bài mới · Tổng ôn nhẹ' : ('🎯 Trọng tâm: ' + ((LANGS[sch.focus] && LANGS[sch.focus].label) || 'English')))",
        label="renderProgressTabContent header",
    )
    html = replace_exact(
        html,
        "  const shortDayNames = { 1: 'T2 (Anh)', 2: 'T3 (Trung)', 3: 'T4 (Nhật)', 4: 'T5 (Anh)', 5: 'T6 (Trung)', 6: 'T7 (Nhật)', 0: 'CN (Ôn)' };\n\n  return [\n    // 2. Bộ chọn Thứ trong tuần để xem hôm đó học gì",
        "  const shortDayNames = { 1: 'T2', 2: 'T3', 3: 'T4', 4: 'T5', 5: 'T6', 6: 'T7', 0: 'CN (Ôn)' };\n\n  return [\n    // 2. Bộ chọn Thứ trong tuần để xem hôm đó học gì",
        label="shortDayNames",
    )
    html = replace_exact(
        html,
        "        h('b', { style: { fontSize: '1rem', color: 'var(--ink)' } }, 'Nguyên tắc Lịch Học Xoay Vòng (1 Ngôn Ngữ Học Mới + 2 Ngôn Ngữ Ôn Nhẹ)')\n"
        "      ),\n"
        "      h('div', { class: 'stack', style: { gap: '5px', fontSize: '.82rem', lineHeight: 1.55, color: 'var(--muted)' } },\n"
        "        h('div', {}, h('b', { style: { color: 'var(--ink)' } }, '• Mỗi ngày chỉ học bài mới của 1 ngôn ngữ: '), 'Xoay vòng T2 & T5 Tiếng Anh · T3 & T6 Tiếng Trung · T4 & T7 Tiếng Nhật · Chủ Nhật nghỉ bài mới.'),\n"
        "        h('div', {}, h('b', { style: { color: 'var(--ink)' } }, '• 2 ngôn ngữ còn lại chỉ ôn duy trì: '), 'Không học bài mới, chỉ ôn nhanh gói 10 từ SRS để giữ phản xạ và chuỗi ngày học.'),",
        "        h('b', { style: { fontSize: '1rem', color: 'var(--ink)' } }, 'Nguyên tắc Học Tiếng Anh Đều Đặn Mỗi Ngày')\n"
        "      ),\n"
        "      h('div', { class: 'stack', style: { gap: '5px', fontSize: '.82rem', lineHeight: 1.55, color: 'var(--muted)' } },\n"
        "        h('div', {}, h('b', { style: { color: 'var(--ink)' } }, '• T2–T7 mỗi ngày học 1 bài mới: '), 'Kết hợp từ vựng, nghe hội thoại thực tế, nói phản xạ & viết email công việc.'),\n"
        "        h('div', {}, h('b', { style: { color: 'var(--ink)' } }, '• Chủ Nhật tổng ôn nhẹ: '), 'Không học bài mới, tập trung ôn nhanh gói từ SRS để giữ trí nhớ dài hạn.'),",
        label="schedule principles copy",
    )
    html = replace_exact(
        html,
        "          h('p', { class: 'small muted', style: { margin: '4px 0 0 0', fontSize: '.76rem', lineHeight: 1.5 } },\n"
        "            'Xây dựng phản xạ Tiếng Anh giao tiếp, nắm vững Bộ thủ & 10 bài đầu của Tiếng Trung (HSK 1–2) và Tiếng Nhật (N5).'\n"
        "          )\n"
        "        ),\n"
        "        h('div', { class: 'panel', style: { background: 'var(--surface)', border: '1px solid var(--line)', borderRadius: '10px', padding: '10px' } },\n"
        "          h('b', { style: { fontSize: '.84rem', color: 'var(--amber)' } }, '⚡ Giai đoạn 2 (Tháng 4–6): Tăng tốc Nghe & Nói'),\n"
        "          h('p', { class: 'small muted', style: { margin: '4px 0 0 0', fontSize: '.76rem', lineHeight: 1.5 } },\n"
        "            'Đẩy mạnh kỹ năng nghe hội thoại, Shadowing (nhại giọng) và ôn cuốn chiếu gói 10–15 từ dễ quên.'\n"
        "          )\n"
        "        ),\n"
        "        h('div', { class: 'panel', style: { background: 'var(--surface)', border: '1px solid var(--line)', borderRadius: '10px', padding: '10px' } },\n"
        "          h('b', { style: { fontSize: '.84rem', color: 'var(--ink)' } }, '🔄 Giai đoạn 3 (Tháng 6+): Duy trì bền vững'),\n"
        "          h('p', { class: 'small muted', style: { margin: '4px 0 0 0', fontSize: '.76rem', lineHeight: 1.5 } },\n"
        "            'Duy trì đều đặn lịch xoay vòng 2-2-2-1: T2 & T5 Anh · T3 & T6 Trung · T4 & T7 Nhật · CN tổng ôn nhẹ.'\n"
        "          )",
        "          h('p', { class: 'small muted', style: { margin: '4px 0 0 0', fontSize: '.76rem', lineHeight: 1.5 } },\n"
        "            'Xây dựng nền tảng từ vựng A1–A2, phát âm chuẩn và phản xạ giao tiếp hàng ngày.'\n"
        "          )\n"
        "        ),\n"
        "        h('div', { class: 'panel', style: { background: 'var(--surface)', border: '1px solid var(--line)', borderRadius: '10px', padding: '10px' } },\n"
        "          h('b', { style: { fontSize: '.84rem', color: 'var(--amber)' } }, '⚡ Giai đoạn 2 (Tháng 4–6): Giao tiếp & Thương mại B1–B2'),\n"
        "          h('p', { class: 'small muted', style: { margin: '4px 0 0 0', fontSize: '.76rem', lineHeight: 1.5 } },\n"
        "            'Luyện nghe hội thoại dài B1–C2, Shadowing (nhại giọng), viết email công việc & chốt deal đơn hàng.'\n"
        "          )\n"
        "        ),\n"
        "        h('div', { class: 'panel', style: { background: 'var(--surface)', border: '1px solid var(--line)', borderRadius: '10px', padding: '10px' } },\n"
        "          h('b', { style: { fontSize: '.84rem', color: 'var(--ink)' } }, '🏆 Giai đoạn 3 (Tháng 6+): Học thuật C1–C2 & IELTS'),\n"
        "          h('p', { class: 'small muted', style: { margin: '4px 0 0 0', fontSize: '.76rem', lineHeight: 1.5 } },\n"
        "            'Chinh phục chủ đề nâng cao C1–C2, luyện đề thi IELTS 4 kỹ năng và duy trì ôn tập SRS.'\n"
        "          )",
        label="schedule 3 stages copy",
    )
    html = replace_exact(
        html,
        "? 'Lộ trình cả 3 ngôn ngữ'",
        "? 'Lộ trình Tiếng Anh (A1–C2)'",
        label="roadmap header subtitle",
    )
    html = replace_exact(
        html,
        "  const paces = [\n"
        "    { id: 'schedule', name: '📅 Lịch chuẩn (2-2-2-1)', desc: currentLang === 'en' ? 'T2, T5 (2 bài/tuần)' : (currentLang === 'zh' ? 'T3, T6 (2 bài/tuần)' : (currentLang === 'ja' ? 'T4, T7 (2 bài/tuần)' : 'Mỗi tiếng 2 bài/tuần · CN ôn tổng hợp')) },\n"
        "    { id: 'daily1', name: '⚡ 1 bài/ngày', desc: '7 bài/tuần · Đều đặn mỗi ngày' },\n"
        "    { id: 'daily2', name: '🔥 2 bài/ngày', desc: '14 bài/tuần · Tăng tốc bứt phá' }\n"
        "  ];\n\n"
        "  const langFilterPills = [\n"
        "    { id: S.lang, label: (LANGS[S.lang] ? LANGS[S.lang].label : 'Ngôn ngữ đang học') + ' (Đang học)' },\n"
        "    ...Object.entries(LANGS).filter(([c]) => c !== S.lang).map(([c, v]) => ({ id: c, label: v.label })),\n"
        "    { id: 'all', label: '🌐 Cả 3 ngôn ngữ' }\n"
        "  ];",
        "  const paces = [\n"
        "    { id: 'schedule', name: '📅 Lịch đều đặn (T2–T7)', desc: '6 bài/tuần · CN tổng ôn' },\n"
        "    { id: 'daily1', name: '⚡ 1 bài/ngày', desc: '7 bài/tuần · Đều đặn mỗi ngày' },\n"
        "    { id: 'daily2', name: '🔥 2 bài/ngày', desc: '14 bài/tuần · Tăng tốc bứt phá' }\n"
        "  ];\n\n"
        "  const langFilterPills = [\n"
        "    { id: 'en', label: '🇬🇧 English (A1–C2)' }\n"
        "  ];",
        label="roadmap paces and filter pills",
    )
    html = replace_exact(
        html,
        "        STUDY_PACE === 'schedule'\n"
        "          ? (currentLang === 'en'\n"
        "              ? '💡 Lịch chuẩn Tiếng Anh (Thứ 2 & Thứ 5): Học 2 bài mới/tuần (Nghe + Nói & Giao tiếp B2), các ngày khác ôn gói 10 từ.'\n"
        "              : (currentLang === 'zh'\n"
        "                ? '💡 Lịch chuẩn Tiếng Trung (Thứ 3 & Thứ 6): Học 2 bài mới/tuần (Bộ thủ, Chiết tự & HSK), các ngày khác ôn gói 10 từ.'\n"
        "                : (currentLang === 'ja'\n"
        "                  ? '💡 Lịch chuẩn Tiếng Nhật (Thứ 4 & Thứ 7): Học 2 bài mới/tuần (Nghe hội thoại & N5), các ngày khác ôn gói 10 từ.'\n"
        "                  : '💡 Lịch xoay vòng 2-2-2-1: Anh (T2, T5) · Trung (T3, T6) · Nhật (T4, T7) · Chủ nhật tổng ôn nhẹ.')))",
        "        STUDY_PACE === 'schedule'\n"
        "          ? '💡 Lịch đều đặn (Thứ 2 – Thứ 7): Học 6 bài mới/tuần kết hợp ôn SRS · Chủ Nhật tổng ôn nhẹ.'",
        label="roadmap schedule description",
    )
    html = replace_exact(
        html,
        "  if (!PICK_HUB_OPEN) {\n",
        "  PICK_HUB_OPEN = true;\n  if (!PICK_HUB_OPEN) {\n",
        label="force PICK_HUB_OPEN true",
    )
    html = replace_exact(
        html,
        "      ['progress', '📊 Tiến độ ngôn ngữ'],\n",
        "      ['progress', '📊 Tiến độ Tiếng Anh'],\n",
        label="pick tab progress label",
    )
    html = replace_exact(
        html,
        "        onclick: () => { PICK_HUB_OPEN = false; pickView(); }\n      }, '← Quay lại chọn ngôn ngữ'),",
        "        onclick: () => { PICK_HUB_OPEN = false; go('home'); }\n      }, '← Về trang Học'),",
        label="pick hub back button",
    )
    html = replace_exact(
        html,
        "      h('p', { class: 'label' }, 'Lingogo'),\n"
        "      h('h1', {}, 'Học để nói được, mỗi ngày một chút'),\n"
        "      h('p', { class: 'muted' }, 'Ba thứ tiếng trong một app: bài học theo chủ đề, ôn tập đúng lúc, luyện nói và tập viết chữ Hán, kana.'),",
        "      h('p', { class: 'label' }, 'English Practice'),\n"
        "      h('h1', {}, 'Học để nói được, mỗi ngày một chút'),\n"
        "      h('p', { class: 'muted' }, 'Học Tiếng Anh giao tiếp & thương mại từ A1 đến C2: bài học theo chủ đề, nghe hội thoại thực tế, luyện nói, viết email và đề IELTS 4 kỹ năng.'),",
        label="welcome header",
    )
    html = replace_exact(
        html,
        "    goals.replaceChildren(...[[20, 'Tối thiểu', '20 XP ≈ 4 từ mới mỗi thứ tiếng'], [30, 'Vừa phải', '30 XP mỗi thứ tiếng'], [50, 'Nghiêm túc', '50 XP mỗi thứ tiếng']]\n"
        "      .map(([v, t, s]) => h('button', { 'aria-pressed': String(goal === v), onclick: () => { goal = v; draw(); } }, h('span', {}, h('b', {}, t), ' · ', h('span', { class: 'muted' }, s)))));\n"
        "    langs.replaceChildren(...Object.entries(LANGS).map(([k, v]) => h('button', { 'aria-pressed': String(lang === k), lang: v.lang, onclick: () => { lang = k; draw(); start.textContent = 'Bắt đầu học ' + LANGS[lang].short; } }, v.label)));",
        "    goals.replaceChildren(...[[20, 'Tối thiểu', '20 XP ≈ 4 từ mới mỗi ngày'], [30, 'Vừa phải', '30 XP mỗi ngày'], [50, 'Nghiêm túc', '50 XP mỗi ngày']]\n"
        "      .map(([v, t, s]) => h('button', { 'aria-pressed': String(goal === v), onclick: () => { goal = v; draw(); } }, h('span', {}, h('b', {}, t), ' · ', h('span', { class: 'muted' }, s)))));",
        label="welcome goals without lang picker",
    )
    html = replace_exact(
        html,
        "    h('div', { class: 'stack' }, h('span', { class: 'label' }, 'Bạn muốn học thứ tiếng nào trước?'), langs, h('p', { class: 'small muted' }, 'Có thể đổi sang thứ tiếng khác bất cứ lúc nào.')),\n"
        "    h('div', { class: 'stack' }, h('span', { class: 'label' }, 'Mục tiêu mỗi ngày, cho từng thứ tiếng'), goals),\n"
        "    (start = h('button', { class: 'primary block', onclick: () => { S.name = name.value.trim() || 'bạn'; S.goal = goal; S.lang = lang; save(); go('home'); } }, 'Bắt đầu học ' + LANGS[lang].short))));",
        "    h('div', { class: 'stack' }, h('span', { class: 'label' }, 'Mục tiêu mỗi ngày'), goals),\n"
        "    (start = h('button', { class: 'primary block', onclick: () => { S.name = name.value.trim() || 'bạn'; S.goal = goal; S.lang = 'en'; save(); go('home'); } }, 'Bắt đầu học Tiếng Anh'))));",
        label="welcome start button",
    )

    # 8. Review home/roadmap buttons, footer, knowledge copy, ACH, feedback repo, reload check
    html = replace_exact(
        html,
        "          h('button', { class: 'ghost', onclick: () => go('pick') }, 'Về Màn hình chính')",
        "          h('button', { class: 'ghost', onclick: () => { PICK_TAB = 'roadmap'; PICK_HUB_OPEN = true; go('pick'); } }, '🗺️ Xem lộ trình')",
        count=2,
        label="reviewView pick buttons",
    )
    html = replace_exact(
        html,
        f"'Lingogo v{app_ver} · Cập nhật 15/11/2026'",
        f"'English Practice v{app_ver} · Cập nhật 15/11/2026'",
        label="homeView footer",
    )
    html = replace_exact(
        html,
        "h('p', { class: 'label' }, 'Lingogo'),\n        h('h1', {}, 'Chào ' + S.name + ', hôm nay học gì?')",
        "h('p', { class: 'label' }, 'English Practice'),\n        h('h1', {}, 'Chào ' + S.name + ', hôm nay học gì?')",
        label="pickView label",
    )
    html = replace_exact(
        html,
        "tab Học của Lingogo",
        "tab Học của English Practice",
        label="knowledge tip 1",
    )
    html = replace_exact(
        html,
        "Tab Ôn tập của Lingogo",
        "Tab Ôn tập của English Practice",
        label="knowledge tip 2",
    )
    html = replace_exact(
        html,
        "  ['streak3', 'Ba ngày liền', 'Đạt mục tiêu một thứ tiếng 3 ngày liên tiếp', () => Object.keys(LANGS).some((c) => streak(c) >= 3)],\n"
        "  ['streak7', 'Một tuần bền bỉ', 'Đạt mục tiêu một thứ tiếng 7 ngày liên tiếp', () => Object.keys(LANGS).some((c) => streak(c) >= 7)],\n"
        "  ['goal3', 'Đủ cả ba', 'Một ngày đạt mục tiêu cả Anh, Trung, Nhật', () => Object.keys(LANGS).every((c) => metGoal(todayN(), c))],\n"
        "  ['words100', 'Trăm từ', '100 từ trong hàng ôn tập', () => Object.keys(S.srs).filter((k) => /:(w|v)/.test(k)).length >= 100],\n"
        "  ['polyglot', 'Ba thứ tiếng', 'Học ít nhất một bài mỗi thứ tiếng', () => ['en', 'zh', 'ja'].every((c) => Object.keys(S.lessons).some((k) => k.startsWith(c + ':')))],\n"
        "  ['speak20', 'Dám mở lời', 'Nói đạt từ 80% ở 20 câu', () => Object.values(S.spoken).filter((v) => v >= 80).length >= 20],\n"
        "  ['write50', 'Nắn nót', 'Tập viết 50 chữ khác nhau', () => Object.keys(S.written).length >= 50],",
        "  ['streak3', 'Ba ngày liền', 'Đạt mục tiêu Tiếng Anh 3 ngày liên tiếp', () => streak('en') >= 3],\n"
        "  ['streak7', 'Một tuần bền bỉ', 'Đạt mục tiêu Tiếng Anh 7 ngày liên tiếp', () => streak('en') >= 7],\n"
        "  ['words100', 'Trăm từ', '100 từ trong hàng ôn tập', () => Object.keys(S.srs).filter((k) => /:(w|v)/.test(k)).length >= 100],\n"
        "  ['listen10', 'Tai nghe nhạy bén', 'Hoàn thành 10 tiết học hoặc luyện nghe IELTS', () => Object.keys(S.lessons).filter((k) => k.startsWith('en:')).length >= 10 || Object.keys(S.ielts || {}).some((k) => k.endsWith(':listen') && S.ielts[k].done)],\n"
        "  ['speak20', 'Dám mở lời', 'Nói đạt từ 80% ở 20 câu', () => Object.values(S.spoken).filter((v) => v >= 80).length >= 20],\n"
        "  ['write5', 'Ngòi bút chuyên nghiệp', 'Luyện viết 5 bài email hoặc IELTS Writing', () => (Object.keys(S.fill || {}).filter((k) => k.startsWith('en:')).length + Object.keys(S.ielts || {}).filter((k) => k.endsWith(':write')).length) >= 5],",
        label="ACH single-language English",
    )
    html = replace_exact(
        html,
        "      `### 💬 [Báo lỗi Lingogo] ${tagObj.label}\\n` +",
        "      `### 💬 [Báo lỗi English Practice] ${tagObj.label}\\n` +",
        label="feedback title",
    )
    html = replace_exact(
        html,
        "https://github.com/nguyendang3103/lingogo/issues/new",
        "https://github.com/nguyendang3103/english-practice/issues/new",
        label="github issue url",
    )
    html = replace_exact(
        html,
        "https://api.github.com/repos/nguyendang3103/lingogo/issues",
        "https://api.github.com/repos/nguyendang3103/english-practice/issues",
        label="github issue api url",
    )
    html = replace_exact(
        html,
        "if (!confirmReset) { confirmReset = true; resetBtn.textContent = 'Bấm lần nữa để xóa toàn bộ tiến độ của cả ba thứ tiếng'; return; }",
        "if (!confirmReset) { confirmReset = true; resetBtn.textContent = 'Bấm lần nữa để xóa toàn bộ tiến độ học Tiếng Anh'; return; }",
        label="reset button warning",
    )
    html = replace_exact(
        html,
        "const reloadKey = 'lingogo_reload_' + data.build;",
        "const reloadKey = 'ep_reload_' + data.build;",
        label="checkAppUpdate reloadKey",
    )
    html = replace_exact(
        html,
        "href: 'https://github.com/settings/tokens/new?description=Lingogo%20Sync&scopes=gist',",
        "href: 'https://github.com/settings/tokens/new?description=English%20Practice%20Sync&scopes=gist',",
        label="token link description",
    )

    # Sanity checks against copied en.json
    topic_count = len(en_data["topics"])
    if topic_count != 71:
        raise ValueError(f"Expected 71 topics in en.json, got {topic_count}")
    if "English/" in html:
        leftovers = [line.strip() for line in html.splitlines() if "English/" in line]
        raise ValueError(f"Unconverted 'English/' path references remain: {leftovers[:5]}")

    DST_HTML.write_text(html, encoding="utf-8")
    print(f"Generated {DST_HTML} ({len(html):,} bytes, build {build_id}, v{app_ver}, {topic_count} topics)")


if __name__ == "__main__":
    main()
