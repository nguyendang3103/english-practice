import re

with open(r'D:\Obsidian Vaults\lingogo\index.html', 'r', encoding='utf-8') as f:
    s = f.read()

# 1. Title & Meta
s = s.replace('<meta name="apple-mobile-web-app-title" content="Lingogo">', '<meta name="apple-mobile-web-app-title" content="English Practice">')
s = s.replace('<title>Lingogo</title>', '<title>English Practice — Tiếng Anh thương mại & Quản lý</title>')
s = s.replace('&family=Noto+Sans+JP:wght@400;500;700&family=Noto+Sans+SC:wght@400;500;700', '')
s = re.sub(r'<script src="https://cdn\.jsdelivr\.net/npm/hanzi-writer[^"]*"></script>', '', s)

# 2. Key & fresh
old_key = '''const KEY = 'noiduoc-v2'; // giữ khóa cũ để không mất tiến độ đã lưu trên máy
const fresh = () => ({ v: 2, name: '', goal: 20, lang: 'en', days: {}, dl: {}, pv: {}, srs: {}, lessons: {}, spoken: {}, written: {}, fill: {}, ach: {}, t: 0 });
let S = fresh();
try { const raw = localStorage.getItem(KEY); if (raw) S = Object.assign(fresh(), JSON.parse(raw)); } catch (e) { /* bị chặn lưu trữ */ }'''

new_key = '''const KEY = 'english-practice-v1';
const fresh = () => ({ v: 2, name: '', goal: 20, lang: 'en', days: {}, dl: {}, pv: {}, srs: {}, lessons: {}, spoken: {}, written: {}, fill: {}, ach: {}, t: 0 });
let S = fresh();
try {
  const raw = localStorage.getItem(KEY);
  if (raw) {
    S = Object.assign(fresh(), JSON.parse(raw));
  } else {
    const old = localStorage.getItem('noiduoc-v2');
    if (old) {
      S = Object.assign(fresh(), JSON.parse(old));
      S.lang = 'en';
      try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e2) {}
    }
  }
} catch (e) { /* bị chặn lưu trữ */ }'''

s = s.replace(old_key, new_key)

# 3. LANGS
old_langs = '''const LANGS = {
  en: { label: 'English', short: 'Anh', tts: 'en-US', rec: 'en-US', lang: 'en', cjk: false },
  zh: { label: '中文', short: 'Trung', tts: 'zh-CN', rec: 'zh-CN', lang: 'zh-Hans', cjk: true },
  ja: { label: '日本語', short: 'Nhật', tts: 'ja-JP', rec: 'ja-JP', lang: 'ja', cjk: true },
};'''

new_langs = '''const LANGS = {
  en: { label: 'English', short: 'Anh', tts: 'en-US', rec: 'en-US', lang: 'en', cjk: false },
};'''

s = s.replace(old_langs, new_langs)

# 4. GH Sync Key
old_gh = '''const GH_KEY = 'lingogo-github-sync';
const GH_SYNC = { timer: 0, seen: -1, running: false };
function getGhConfig() {
  try { const raw = localStorage.getItem(GH_KEY); return raw ? JSON.parse(raw) : { token: '', gistId: '', user: '' }; } catch (e) { return { token: '', gistId: '', user: '' }; }
}'''

new_gh = '''const GH_KEY = 'english-practice-github-sync';
const GH_SYNC = { timer: 0, seen: -1, running: false };
function getGhConfig() {
  try {
    const raw = localStorage.getItem(GH_KEY);
    if (raw) return JSON.parse(raw);
    const old = localStorage.getItem('lingogo-github-sync');
    if (old) return JSON.parse(old);
    return { token: '', gistId: '', user: '' };
  } catch (e) { return { token: '', gistId: '', user: '' }; }
}'''

s = s.replace(old_gh, new_gh)

# 5. ICON mail
old_icon = '''const ICON = {
  github:'''

new_icon = '''const ICON = {
  mail: 'M3 8l7.89 5.26a2 2 0 0 0 2.22 0L21 8M5 19h14a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2z',
  github:'''

s = s.replace(old_icon, new_icon)

# 6. TABS
old_tabs = "const TABS = [['home', 'Học', ICON.home], ['review', 'Ôn tập', ICON.cards], ['speak', 'Luyện nói', ICON.speak], ['write', 'Viết', ICON.pen], ['progress', 'Tiến độ', ICON.chart]];"
new_tabs = "const TABS = [['home', 'Học', ICON.home], ['review', 'Ôn tập', ICON.cards], ['speak', 'Luyện nói', ICON.speak], ['email', 'Viết email', ICON.mail], ['progress', 'Tiến độ', ICON.chart]];"
s = s.replace(old_tabs, new_tabs)

# 7. Route
old_route = """  if (view === 'speak') return speakView();
  if (view === 'write') return writeView();
  if (view === 'progress') return progressView();"""

new_route = """  if (view === 'speak') return speakView();
  if (view === 'email' || view === 'write') return emailView();
  if (view === 'progress') return progressView();"""

s = s.replace(old_route, new_route)

# 8. emailView definition
old_write = """// ===== Viết =====
function writeView() {
  const code = S.lang, d = DATA[code];
  const pick = topicPicker(code, WRITE_TOPIC, writeView);
  const t = d.topics.find((x) => x.id === WRITE_TOPIC[code]) || d.topics[0];
  const head = h('div', { class: 'stack' }, h('div', { class: 'row between' }, h('h1', {}, 'Viết'), langSwitch()), pick);
  if (code === 'en') {
    if (!t.fill) { mount(h('div', { class: 'stack-lg' }, head, h('p', { class: 'note' }, 'Chủ đề này chưa có bài điền email. Chọn chủ đề khác.'))); return; }
    return mount(h('div', { class: 'stack-lg' }, head, fillBlock(t)));
  }"""

new_write = """// ===== Viết email =====
function emailView() {
  VIEW = 'email'; setTabs(true);
  const code = 'en', d = DATA[code];
  if (!d) return;
  const pick = topicPicker(code, WRITE_TOPIC, emailView);
  const t = d.topics.find((x) => x.id === WRITE_TOPIC[code]) || d.topics[0];
  const head = h('div', { class: 'stack' },
    h('div', { class: 'row between' },
      h('h1', {}, 'Viết email'),
      h('span', { class: 'small muted' }, 'Điền từ email')
    ),
    pick
  );
  if (!t.fill) { mount(h('div', { class: 'stack-lg' }, head, h('p', { class: 'note' }, 'Chủ đề này chưa có bài điền email. Chọn chủ đề khác.'))); return; }
  return mount(h('div', { class: 'stack-lg' }, head, fillBlock(t)));
}
function writeView() { return emailView(); }
function _unusedWrite() {
  const code = S.lang, d = DATA[code];"""

s = s.replace(old_write, new_write)

# 9. Home view header
old_home_head = """  mount(h('div', { class: 'stack-lg' },
    h('div', { class: 'row between' }, h('h1', {}, 'Chào ' + S.name + '!'), langSwitch()),"""

new_home_head = """  mount(h('div', { class: 'stack-lg' },
    h('div', { class: 'row between' },
      h('div', {},
        h('h1', {}, 'Chào ' + S.name + '!'),
        h('span', { class: 'small muted' }, '32 chủ đề thương mại · Quản lý')
      ),
      h('button', { class: 'sync-btn', 'aria-label': 'Đồng bộ', title: 'Đồng bộ', onclick: showSyncModal }, icon(ICON.sync))
    ),"""

s = s.replace(old_home_head, new_home_head)

# 10. Home topic button "Viết" -> "Viết email"
old_write_btn = "(LANGS[t.lang].cjk || t.fill) && h('button', { class: 'mini', onclick: () => { WRITE_TOPIC[t.lang] = t.id; go('write'); } }, 'Viết')"
new_write_btn = "t.fill && h('button', { class: 'mini', onclick: () => { WRITE_TOPIC['en'] = t.id; go('email'); } }, 'Viết email')"
s = s.replace(old_write_btn, new_write_btn)

# 11. Welcome view
old_welcome = """    mount(h('div', { class: 'stack-lg', style: { paddingTop: '24px' } },
    h('div', { class: 'stack' },
      h('p', { class: 'label' }, 'Lingogo'),
      h('h1', {}, 'Học để nói được, mỗi ngày một chút'),
      h('p', { class: 'muted' }, 'Ba thứ tiếng trong một app: bài học theo chủ đề, ôn tập đúng lúc, luyện nói và tập viết chữ Hán, kana.'),
      had && h('p', { class: 'note' }, 'Đã có tiến độ cũ của bạn. Bạn sẽ học tiếp từ chỗ đã dừng.')),
    h('div', { class: 'stack' }, h('label', { for: 'name', class: 'label' }, 'Tên của bạn'), name),
    h('div', { class: 'stack' }, h('span', { class: 'label' }, 'Bạn muốn học thứ tiếng nào trước?'), langs, h('p', { class: 'small muted' }, 'Có thể đổi sang thứ tiếng khác bất cứ lúc nào.')),
    h('div', { class: 'stack' }, h('span', { class: 'label' }, 'Mục tiêu mỗi ngày, cho từng thứ tiếng'), goals),
    (start = h('button', { class: 'primary block', onclick: () => { S.name = name.value.trim() || 'bạn'; S.goal = goal; S.lang = lang; save(); go('home'); } }, 'Bắt đầu học ' + LANGS[lang].short))));"""

new_welcome = """    mount(h('div', { class: 'stack-lg', style: { paddingTop: '24px' } },
    h('div', { class: 'stack' },
      h('p', { class: 'label' }, 'English Practice'),
      h('h1', {}, 'Tiếng Anh thương mại & Quản lý'),
      h('p', { class: 'muted' }, '32 chủ đề chuyên sâu: xuất nhập khẩu, supply chain, đàm phán, họp đối tác, viết email và tình huống quản lý.'),
      had && h('p', { class: 'note' }, 'Đã có tiến độ của bạn. Bạn sẽ học tiếp từ chỗ đã dừng.')),
    h('div', { class: 'stack' }, h('label', { for: 'name', class: 'label' }, 'Tên của bạn'), name),
    h('div', { class: 'stack' }, h('span', { class: 'label' }, 'Mục tiêu mỗi ngày'), goals),
    (start = h('button', { class: 'primary block', onclick: () => { S.name = name.value.trim() || 'bạn'; S.goal = goal; S.lang = 'en'; save(); go('home'); } }, 'Bắt đầu học ngay'))));"""

s = s.replace(old_welcome, new_welcome)

# 12. Speak view header
old_speak_head = "h('div', { class: 'stack' }, h('div', { class: 'row between' }, h('h1', {}, 'Luyện nói'), langSwitch()), pick)"
new_speak_head = "h('div', { class: 'stack' }, h('div', { class: 'row between' }, h('h1', {}, 'Luyện nói'), h('span', { class: 'small muted' }, 'Phản xạ & Coach')), pick)"
s = s.replace(old_speak_head, new_speak_head)

# 13. Progress view header
old_prog_head = "h('div', { class: 'row between' }, h('h1', {}, 'Tiến độ'), langSwitch())"
new_prog_head = "h('div', { class: 'row between' }, h('h1', {}, 'Tiến độ'), h('button', { class: 'sync-btn', 'aria-label': 'Đồng bộ', title: 'Đồng bộ', onclick: showSyncModal }, icon(ICON.sync)))"
s = s.replace(old_prog_head, new_prog_head)

with open(r'D:\Obsidian Vaults\english-practice\index.html', 'w', encoding='utf-8') as f:
    f.write(s)

print('Success! Wrote D:\\Obsidian Vaults\\english-practice\\index.html')
