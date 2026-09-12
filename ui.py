"""واجهة Claude RTL — HTML + CSS + JS في قالب واحد عشان يتجمّد مع الـexe."""

HTML = r'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="color-scheme" content="dark light">
<title>Claude RTL</title>
<style>
/* ══════════════════ التوكنز ══════════════════ */
:root {
    --accent:      #D97757;
    --accent-2:    #E0916F;
    --accent-soft: rgba(217, 119, 87, .15);
    --bg:          #1B1B19;
    --panel:       #232321;
    --elev:        #2B2B28;
    --line:        #35342F;
    --line-soft:   #2C2B27;
    --ink:         #EDEBE6;
    --ink-2:       #C9C6BF;
    --muted:       #918E87;
    --code-bg:     #131312;
    --shadow:      0 18px 48px rgba(0,0,0,.55);
    --radius:      12px;
}
:root[data-theme="light"] {
    --accent:      #C15F3C;
    --accent-2:    #A94E2E;
    --accent-soft: rgba(193, 95, 60, .12);
    --bg:          #FAF9F5;
    --panel:       #FFFFFF;
    --elev:        #F2F0EA;
    --line:        #E2DFD6;
    --line-soft:   #EDEAE2;
    --ink:         #262520;
    --ink-2:       #4A4842;
    --muted:       #74716A;
    --code-bg:     #F4F2EC;
    --shadow:      0 18px 48px rgba(50,45,35,.18);
}

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body {
    height: 100%;
    overflow: hidden;
    background: var(--bg);
    color: var(--ink);
    font-family: "Segoe UI", system-ui, sans-serif;
    font-size: 14px;
    -webkit-font-smoothing: antialiased;
}
body { display: flex; flex-direction: column; }

button { font: inherit; color: inherit; background: none; border: none; cursor: pointer; }
button:focus-visible, input:focus-visible, select:focus-visible {
    outline: 2px solid var(--accent); outline-offset: 2px;
}

::selection { background: var(--accent-soft); color: inherit; }

.scroll::-webkit-scrollbar { width: 9px; height: 9px; }
.scroll::-webkit-scrollbar-track { background: transparent; }
.scroll::-webkit-scrollbar-thumb {
    background: var(--line); border-radius: 9px;
    border: 3px solid var(--bg); background-clip: padding-box;
}
.scroll::-webkit-scrollbar-thumb:hover { background: var(--muted); background-clip: padding-box; }

/* ══════════════════ شريط العنوان ══════════════════ */
.titlebar {
    display: flex; align-items: center; gap: 2px;
    height: 42px; flex: 0 0 42px; padding: 0 8px 0 10px;
    background: var(--panel);
    border-bottom: 1px solid var(--line-soft);
    cursor: move; user-select: none;
}
.brand {
    display: flex; align-items: center; gap: 7px;
    padding-inline-start: 4px; margin-inline-end: 6px;
    font-size: 12.5px; font-weight: 650; letter-spacing: .2px; color: var(--ink-2);
}
.brand .mark {
    width: 16px; height: 16px; border-radius: 5px; flex: none;
    background: linear-gradient(140deg, var(--accent), var(--accent-2));
    box-shadow: 0 0 0 3px var(--accent-soft);
}
.spacer { flex: 1; }

.iconbtn {
    width: 30px; height: 30px; border-radius: 8px; flex: none;
    display: grid; place-items: center; color: var(--muted);
    transition: background .14s, color .14s, transform .14s;
}
.iconbtn:hover { background: var(--elev); color: var(--ink); }
.iconbtn:active { transform: scale(.92); }
.iconbtn.on { color: var(--accent); background: var(--accent-soft); }
.iconbtn.danger:hover { background: rgba(214, 84, 62, .18); color: #E8735A; }

/* شريط تقدّم القراءة */
.progress { height: 2px; flex: none; background: var(--line-soft); }
.progress > i {
    display: block; height: 100%; width: 0;
    background: linear-gradient(90deg, var(--accent-2), var(--accent));
    transition: width .1s linear;
}

/* ══════════════════ لوحة الإعدادات ══════════════════ */
.panel {
    flex: none; overflow: hidden; max-height: 0;
    background: var(--panel); border-bottom: 1px solid transparent;
    transition: max-height .22s ease, border-color .22s;
}
.panel.open { max-height: 340px; border-bottom-color: var(--line-soft); overflow-y: auto; }
.panel-inner { padding: 12px 14px 14px; display: grid; gap: 11px; }

.row { display: flex; align-items: center; gap: 10px; min-height: 26px; }
.row > label:first-child {
    flex: 0 0 88px; font-size: 12px; color: var(--muted); user-select: none;
}
.row .val { font-size: 11px; color: var(--muted); min-width: 34px; text-align: left; font-variant-numeric: tabular-nums; }

.seg { display: flex; gap: 3px; background: var(--elev); padding: 3px; border-radius: 9px; }
.seg button {
    padding: 4px 11px; font-size: 11.5px; border-radius: 6px;
    color: var(--muted); transition: .14s;
}
.seg button:hover { color: var(--ink); }
.seg button.on { background: var(--panel); color: var(--ink); box-shadow: 0 1px 3px rgba(0,0,0,.18); }

select {
    flex: 1; padding: 5px 9px; font-size: 12px; border-radius: 8px;
    background: var(--elev); border: 1px solid var(--line); color: var(--ink);
    cursor: pointer;
}

input[type="range"] {
    flex: 1; -webkit-appearance: none; height: 4px; border-radius: 4px;
    background: var(--line); cursor: pointer;
}
input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none; width: 14px; height: 14px; border-radius: 50%;
    background: var(--accent); border: 2px solid var(--panel);
    box-shadow: 0 1px 4px rgba(0,0,0,.3);
}

.switch { display: flex; align-items: center; gap: 8px; cursor: pointer; user-select: none; }
.switch input { display: none; }
.switch .track {
    width: 32px; height: 18px; border-radius: 999px; background: var(--line);
    position: relative; transition: background .18s; flex: none;
}
.switch .track::after {
    content: ''; position: absolute; inset-inline-start: 2px; top: 2px;
    width: 14px; height: 14px; border-radius: 50%; background: var(--panel);
    transition: transform .18s;
}
.switch input:checked + .track { background: var(--accent); }
.switch input:checked + .track::after { transform: translateX(-14px); }
html[dir="rtl"] .switch input:checked + .track::after { transform: translateX(-14px); }
.switch span.lbl { font-size: 12px; color: var(--ink-2); }

.panel .divider { height: 1px; background: var(--line-soft); margin: 1px 0; }
.panel .hint { font-size: 10.5px; color: var(--muted); line-height: 1.7; }
.panel .hint kbd {
    background: var(--elev); border: 1px solid var(--line); border-bottom-width: 2px;
    border-radius: 5px; padding: 0 4px; font-family: inherit; font-size: 10px;
    direction: ltr; display: inline-block;
}

/* ══════════════════ درج السجل ══════════════════ */
.drawer {
    position: absolute; inset: 42px 0 0 0; z-index: 20;
    background: var(--bg); display: flex; flex-direction: column;
    transform: translateY(-8px); opacity: 0; pointer-events: none;
    transition: opacity .16s, transform .16s;
}
.drawer.open { opacity: 1; transform: none; pointer-events: auto; }
.drawer-head {
    display: flex; align-items: center; gap: 8px;
    padding: 10px 12px; border-bottom: 1px solid var(--line-soft);
}
.drawer-head input {
    flex: 1; padding: 7px 11px; font-size: 13px; border-radius: 9px;
    background: var(--elev); border: 1px solid var(--line); color: var(--ink);
}
.drawer-head input::placeholder { color: var(--muted); }
.hlist { flex: 1; overflow-y: auto; padding: 8px; display: flex; flex-direction: column; gap: 5px; }
.hitem {
    text-align: start; width: 100%; padding: 9px 11px; border-radius: 10px;
    background: var(--panel); border: 1px solid transparent;
    transition: border-color .14s, background .14s;
}
.hitem:hover { border-color: var(--line); background: var(--elev); }
.hitem .t { font-size: 13px; line-height: 1.6; color: var(--ink-2); }
.hitem .m { font-size: 10.5px; color: var(--muted); margin-top: 4px; }

/* ══════════════════ المحتوى ══════════════════ */
.content {
    flex: 1; overflow-y: auto; padding: 18px 20px 22px;
    font-size: 18px; line-height: 2;
    direction: rtl; text-align: start;
    user-select: text; cursor: auto;
}
.measure { max-width: 72ch; margin-inline: auto; }
.content.tashkeel-off { font-feature-settings: normal; }

.fade { animation: fade .22s cubic-bezier(.2,.7,.3,1); }
@keyframes fade { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }

/* حالة فاضية */
.empty {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 12px; height: 100%; text-align: center; color: var(--muted);
    user-select: none; cursor: default; font-size: 14px; line-height: 1.8;
}
.empty svg { opacity: .35; }
.empty .sub { font-size: 12px; opacity: .75; }

/* ماركداون */
.content p { margin: 0 0 .7em; }
.content h1, .content h2, .content h3, .content h4 {
    line-height: 1.5; margin: 1em 0 .4em; font-weight: 650;
}
.content h1 { font-size: 1.32em; color: var(--accent); }
.content h2 { font-size: 1.18em; color: var(--accent); }
.content h3 { font-size: 1.06em; }
.content h4 { font-size: 1em; color: var(--ink-2); }
.content > *:first-child { margin-top: 0; }
.content ul, .content ol { margin: 0 0 .7em; padding-inline-start: 1.5em; }
.content li { margin: .2em 0; }
.content li > ul, .content li > ol { margin: .2em 0 .2em; }
.content li::marker { color: var(--accent); }
.content .task { display: flex; align-items: flex-start; gap: 7px; }
.content .task input { margin-top: .55em; accent-color: var(--accent); }
.content blockquote {
    border-inline-start: 3px solid var(--accent);
    background: var(--accent-soft);
    padding: .5em .9em; border-radius: 0 8px 8px 0;
    margin: 0 0 .7em; color: var(--ink-2);
}
html[dir="rtl"] .content blockquote { border-radius: 8px 0 0 8px; }
.content blockquote > *:last-child { margin-bottom: 0; }
.content strong { font-weight: 700; color: var(--ink); }
.content em { font-style: italic; }
.content del { opacity: .6; }
.content a { color: var(--accent); text-decoration: none; border-bottom: 1px solid var(--accent-soft); }
.content a:hover { border-bottom-color: var(--accent); }
.content hr { border: none; border-top: 1px solid var(--line); margin: 1.2em 0; }

.content code.inl {
    background: var(--code-bg); border: 1px solid var(--line);
    border-radius: 6px; padding: .1em .4em;
    font-family: "Cascadia Code", Consolas, monospace;
    font-size: .84em; unicode-bidi: isolate;
}

.codeblock {
    margin: 0 0 .8em; border: 1px solid var(--line); border-radius: var(--radius);
    overflow: hidden; background: var(--code-bg);
}
.codebar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 5px 8px 5px 10px; background: var(--elev);
    border-bottom: 1px solid var(--line);
}
.codebar .lang {
    font-size: 10.5px; color: var(--muted); text-transform: lowercase;
    font-family: "Cascadia Code", Consolas, monospace; letter-spacing: .3px;
}
.codebar .ccopy {
    width: 24px; height: 22px; border-radius: 6px; color: var(--muted);
    display: grid; place-items: center; transition: .14s;
}
.codebar .ccopy:hover { background: var(--line); color: var(--ink); }
.codeblock pre { padding: 11px 13px; overflow-x: auto; }
.codeblock pre::-webkit-scrollbar { height: 7px; }
.codeblock pre::-webkit-scrollbar-thumb { background: var(--line); border-radius: 7px; }
.codeblock code {
    font-family: "Cascadia Code", Consolas, monospace;
    font-size: 13px; line-height: 1.65; white-space: pre; color: var(--ink-2);
}

.tablewrap { overflow-x: auto; margin: 0 0 .8em; border-radius: var(--radius); border: 1px solid var(--line); }
.content table { border-collapse: collapse; width: 100%; font-size: .92em; }
.content th, .content td { padding: .5em .75em; border-bottom: 1px solid var(--line-soft); }
.content th { background: var(--elev); font-weight: 650; text-align: start; }
.content tbody tr:last-child td { border-bottom: none; }
.content tbody tr:hover { background: var(--accent-soft); }

/* ══════════════════ شريط الحالة ══════════════════ */
.statusbar {
    flex: none; height: 26px; display: flex; align-items: center; gap: 9px;
    padding: 0 12px; font-size: 10.5px; color: var(--muted);
    background: var(--panel); border-top: 1px solid var(--line-soft);
    user-select: none;
}
.statusbar .sep { opacity: .4; }
.statusbar .live { display: flex; align-items: center; gap: 5px; }
.statusbar .led {
    width: 6px; height: 6px; border-radius: 50%; background: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-soft);
}
.statusbar .led.off { background: var(--muted); box-shadow: none; }

/* ══════════════════ التوست ══════════════════ */
.toast {
    position: fixed; bottom: 40px; inset-inline: 0; margin-inline: auto; width: max-content;
    max-width: 80%; padding: 7px 15px; border-radius: 999px;
    background: var(--elev); border: 1px solid var(--line); box-shadow: var(--shadow);
    font-size: 12px; color: var(--ink); z-index: 50;
    opacity: 0; transform: translateY(6px); pointer-events: none;
    transition: opacity .18s, transform .18s;
}
.toast.show { opacity: 1; transform: none; }

/* مقبض التحجيم */
.grip {
    position: fixed; bottom: 0; inset-inline-start: 0;
    width: 18px; height: 18px; cursor: nesw-resize; z-index: 60; opacity: .35;
}
html[dir="rtl"] .grip { cursor: nesw-resize; }
.grip::after {
    content: ''; position: absolute; inset: 5px;
    border-bottom: 2px solid var(--muted); border-inline-start: 2px solid var(--muted);
    border-radius: 0 0 0 3px;
}
.grip:hover { opacity: .8; }
</style>
</head>
<body>

<div class="titlebar" id="dragBar">
    <span class="brand"><span class="mark"></span>Claude RTL</span>
    <span class="spacer"></span>

    <button class="iconbtn" id="btnPin" title="تثبيت — يمنع الإخفاء التلقائي (Ctrl+P)">
        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 17v5"/><path d="M9 10.8V4h6v6.8l2 3.2H7l2-3.2Z"/></svg>
    </button>
    <button class="iconbtn" id="btnHistory" title="السجل (Ctrl+H)">
        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l3 2"/></svg>
    </button>
    <button class="iconbtn" id="btnSettings" title="الإعدادات (Ctrl+,)">
        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.6 1.6 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-2.7 1.1V21a2 2 0 1 1-4 0v-.1A1.6 1.6 0 0 0 7.9 19.4a1.6 1.6 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.6 1.6 0 0 0-1.1-2.7H2a2 2 0 1 1 0-4h.1A1.6 1.6 0 0 0 3.7 7.9a1.6 1.6 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.6 1.6 0 0 0 2.7-1.1V2a2 2 0 1 1 4 0v.1a1.6 1.6 0 0 0 2.7 1.1 1.6 1.6 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.6 1.6 0 0 0 1.1 2.7H22a2 2 0 1 1 0 4h-.1a1.6 1.6 0 0 0-1.5 1.6Z"/></svg>
    </button>
    <button class="iconbtn" id="btnCopy" title="نسخ النص كامل (Ctrl+C)">
        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg>
    </button>
    <button class="iconbtn danger" id="btnClose" title="إغلاق (Esc)">
        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
    </button>
</div>

<div class="progress"><i id="prog"></i></div>

<div class="panel" id="panel">
  <div class="panel-inner">
    <div class="row">
        <label>الثيم</label>
        <div class="seg" id="segTheme">
            <button data-v="light">فاتح</button>
            <button data-v="dark">غامق</button>
            <button data-v="system">النظام</button>
        </div>
    </div>
    <div class="row">
        <label for="selFont">الخط</label>
        <select id="selFont">
            <option value="plex">IBM Plex Sans Arabic</option>
            <option value="dubai">Dubai</option>
            <option value="segoe">Segoe UI</option>
            <option value="tahoma">Tahoma</option>
            <option value="naskh">Noto Naskh · نسخ</option>
            <option value="amiri">Amiri · تقليدي</option>
        </select>
    </div>
    <div class="row">
        <label for="rngSize">حجم الخط</label>
        <input type="range" id="rngSize" min="13" max="34" step="1">
        <span class="val" id="vSize"></span>
    </div>
    <div class="row">
        <label for="rngLine">تباعد الأسطر</label>
        <input type="range" id="rngLine" min="14" max="28" step="1">
        <span class="val" id="vLine"></span>
    </div>
    <div class="row">
        <label for="rngMeasure">عرض السطر</label>
        <input type="range" id="rngMeasure" min="36" max="120" step="2">
        <span class="val" id="vMeasure"></span>
    </div>
    <div class="divider"></div>
    <div class="row">
        <label>الظهور</label>
        <select id="selPos">
            <option value="cursor">عند مؤشر الماوس</option>
            <option value="remember">آخر مكان استخدمته</option>
            <option value="right">ملتصق بيمين الشاشة</option>
        </select>
    </div>
    <div class="row" style="flex-wrap:wrap; gap:14px">
        <label class="switch"><input type="checkbox" id="swTashkeel"><span class="track"></span><span class="lbl">إخفاء التشكيل</span></label>
        <label class="switch"><input type="checkbox" id="swBlur"><span class="track"></span><span class="lbl">إخفاء عند فقد التركيز</span></label>
    </div>
    <div class="row" style="flex-wrap:wrap; gap:14px">
        <label class="switch"><input type="checkbox" id="swAllApps"><span class="track"></span><span class="lbl">مراقبة كل البرامج</span></label>
        <label class="switch"><input type="checkbox" id="swPersist"><span class="track"></span><span class="lbl">حفظ السجل على القرص</span></label>
    </div>
    <div class="divider"></div>
    <div class="hint">
        <kbd>Ctrl+Shift+A</kbd> إظهار آخر نص &nbsp;·&nbsp;
        <kbd>Ctrl+Shift+D</kbd> إيقاف/تشغيل المراقبة &nbsp;·&nbsp;
        <kbd>Ctrl</kbd>+<kbd>+/-</kbd> حجم الخط &nbsp;·&nbsp;
        <kbd>Alt</kbd>+<kbd>←/→</kbd> تنقّل في السجل
    </div>
  </div>
</div>

<div class="drawer" id="drawer">
    <div class="drawer-head">
        <input type="search" id="hSearch" placeholder="ابحث في السجل…" autocomplete="off">
        <button class="iconbtn danger" id="btnClearHistory" title="مسح السجل">
            <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M8 6V4h8v2M6 6l1 14h10l1-14"/></svg>
        </button>
        <button class="iconbtn" id="btnCloseHistory" title="رجوع (Esc)">
            <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
        </button>
    </div>
    <div class="hlist scroll" id="hlist"></div>
</div>

<div class="content scroll" id="content">
    <div class="measure" id="measure">
        <div class="empty">
            <svg viewBox="0 0 24 24" width="42" height="42" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><rect x="8" y="3" width="12" height="16" rx="2"/><path d="M16 21H6a2 2 0 0 1-2-2V7"/><path d="M12 8h4M12 12h4"/></svg>
            <div>انسخ أي نص عربي</div>
            <div class="sub">هيظهر هنا مظبوط من اليمين لليسار</div>
        </div>
    </div>
</div>

<div class="statusbar">
    <span class="live"><i class="led" id="led"></i><span id="liveTxt">المراقبة شغالة</span></span>
    <span class="sep">·</span>
    <span id="stats">جاهز</span>
    <span class="spacer"></span>
    <span id="hintTxt">Esc للإغلاق</span>
</div>

<div class="toast" id="toast"></div>
<div class="grip" id="grip"></div>

<script>
"use strict";

const FONTS = {
    plex:   '"IBM Plex Sans Arabic","Segoe UI",system-ui,sans-serif',
    dubai:  '"Dubai","Segoe UI",system-ui,sans-serif',
    segoe:  '"Segoe UI",system-ui,sans-serif',
    tahoma: 'Tahoma,"Segoe UI",sans-serif',
    naskh:  '"Noto Naskh Arabic","Traditional Arabic","Segoe UI",serif',
    amiri:  '"Amiri","Sakkal Majalla","Traditional Arabic",serif'
};
const TASHKEEL = /[ؐ-ًؚ-ٰٟۖ-ۭ]/g;

const $ = (id) => document.getElementById(id);
const el = {
    content: $('content'), measure: $('measure'), panel: $('panel'), drawer: $('drawer'),
    prog: $('prog'), toast: $('toast'), stats: $('stats'), led: $('led'), liveTxt: $('liveTxt'),
    hlist: $('hlist'), hSearch: $('hSearch')
};

let cfg = {};
let rawText = '';
let baseHTML = '';
let history = [];
let historyPos = -1;
let shownAt = 0;
let ready = false;

/* ─────────── أدوات ─────────── */
function toast(msg) {
    el.toast.textContent = msg;
    el.toast.classList.add('show');
    clearTimeout(toast._t);
    toast._t = setTimeout(() => el.toast.classList.remove('show'), 1500);
}

function api(name, ...args) {
    if (window.pywebview && window.pywebview.api && window.pywebview.api[name]) {
        return window.pywebview.api[name](...args);
    }
    return Promise.resolve(null);
}

let saveTimer = null;
function persist() {
    if (!ready) return;
    clearTimeout(saveTimer);
    saveTimer = setTimeout(() => api('save_settings', cfg), 350);
}

/* ─────────── تطبيق الإعدادات على الواجهة ─────────── */
function applyTheme() {
    let theme = cfg.theme;
    if (theme === 'system') {
        theme = matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    }
    document.documentElement.setAttribute('data-theme', theme);
    [...$('segTheme').children].forEach(b => b.classList.toggle('on', b.dataset.v === cfg.theme));
}

function applyTypography() {
    el.content.style.fontFamily = FONTS[cfg.font_family] || FONTS.plex;
    el.content.style.fontSize = cfg.font_size + 'px';
    el.content.style.lineHeight = cfg.line_height;
    el.measure.style.maxWidth = cfg.measure + 'ch';
    $('vSize').textContent = cfg.font_size;
    $('vLine').textContent = Number(cfg.line_height).toFixed(1);
    $('vMeasure').textContent = cfg.measure;
    $('rngSize').value = cfg.font_size;
    $('rngLine').value = Math.round(cfg.line_height * 10);
    $('rngMeasure').value = cfg.measure;
}

function applyAll() {
    applyTheme();
    applyTypography();
    $('selFont').value = cfg.font_family;
    $('selPos').value = cfg.position_mode;
    $('swTashkeel').checked = !!cfg.hide_tashkeel;
    $('swBlur').checked = !!cfg.auto_hide_on_blur;
    $('swAllApps').checked = !!cfg.monitor_all_apps;
    $('swPersist').checked = !!cfg.persist_history;
    $('btnPin').classList.toggle('on', !!cfg.pinned);
    setMonitoring(cfg.monitor_enabled);
}

/* ─────────── يستدعيها بايثون ─────────── */
function init(settings) {
    cfg = settings;
    applyAll();
    ready = true;
}

function openSettings() {
    if (!el.panel.classList.contains('open')) togglePanel();
}

function setMonitoring(on) {
    cfg.monitor_enabled = !!on;
    el.led.classList.toggle('off', !on);
    el.liveTxt.textContent = on ? 'المراقبة شغالة' : 'المراقبة متوقفة';
}

function setHistory(list) {
    history = list || [];
    renderHistory();
}

function updateContent(htmlStr, plain, isNew) {
    rawText = plain || '';
    baseHTML = htmlStr;
    if (isNew) historyPos = -1;
    renderBody();
    el.content.scrollTop = 0;
    el.prog.style.width = '0%';
    shownAt = Date.now();
    closeDrawer();
    const words = rawText.trim() ? rawText.trim().split(/\s+/).length : 0;
    el.stats.textContent = words + ' كلمة · ' + rawText.length + ' حرف';
}

function renderBody() {
    let html = baseHTML;
    el.measure.innerHTML = html;
    if (cfg.hide_tashkeel) stripTashkeelDOM(el.measure);
    el.measure.classList.remove('fade');
    void el.measure.offsetWidth;
    el.measure.classList.add('fade');
}

function stripTashkeelDOM(root) {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    for (const n of nodes) {
        if (n.parentElement && n.parentElement.closest('pre, code')) continue;
        const v = n.nodeValue.replace(TASHKEEL, '');
        if (v !== n.nodeValue) n.nodeValue = v;
    }
}

/* ─────────── السجل ─────────── */
function renderHistory() {
    const q = el.hSearch.value.trim().toLowerCase();
    const items = history.filter(h => !q || h.preview.toLowerCase().includes(q));
    if (!items.length) {
        el.hlist.innerHTML = '<div class="empty" style="height:auto;padding:32px 0">'
            + (q ? 'مفيش نتائج' : 'السجل فاضي') + '</div>';
        return;
    }
    el.hlist.innerHTML = items.map(h =>
        '<button class="hitem" data-id="' + h.id + '">'
        + '<div class="t">' + escapeHTML(h.preview) + '</div>'
        + '<div class="m">' + h.when + ' · ' + h.words + ' كلمة</div></button>'
    ).join('');
}

function escapeHTML(s) {
    return s.replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
}

function openEntry(id) {
    api('load_entry', id).then(r => {
        if (r) {
            updateContent(r.html, r.plain, false);
            historyPos = history.findIndex(h => h.id === id);
        }
    });
}

function stepHistory(delta) {
    if (!history.length) return;
    let pos = historyPos < 0 ? 0 : historyPos + delta;
    pos = Math.max(0, Math.min(history.length - 1, pos));
    openEntry(history[pos].id);
}

function openDrawer() {
    el.drawer.classList.add('open');
    $('btnHistory').classList.add('on');
    el.hSearch.value = '';
    renderHistory();
    setTimeout(() => el.hSearch.focus(), 60);
}
function closeDrawer() {
    el.drawer.classList.remove('open');
    $('btnHistory').classList.remove('on');
}
function toggleDrawer() { el.drawer.classList.contains('open') ? closeDrawer() : openDrawer(); }

function togglePanel() {
    const open = el.panel.classList.toggle('open');
    $('btnSettings').classList.toggle('on', open);
}

/* ─────────── نسخ ─────────── */
function copyAll() {
    if (!rawText) return;
    const out = cfg.hide_tashkeel ? rawText.replace(TASHKEEL, '') : rawText;
    navigator.clipboard.writeText(out).then(() => toast('اتنسخ ✓')).catch(() => toast('النسخ فشل'));
}

/* ─────────── الأحداث ─────────── */
$('btnClose').onclick = () => api('hide_popup');
$('btnCopy').onclick = copyAll;
$('btnSettings').onclick = togglePanel;
$('btnHistory').onclick = toggleDrawer;
$('btnCloseHistory').onclick = closeDrawer;
$('btnPin').onclick = () => {
    cfg.pinned = !cfg.pinned;
    $('btnPin').classList.toggle('on', cfg.pinned);
    api('set_pinned', cfg.pinned);
    persist();
    toast(cfg.pinned ? 'مثبّت' : 'التثبيت اتشال');
};
$('btnClearHistory').onclick = () => {
    api('clear_history').then(() => { history = []; renderHistory(); toast('السجل اتمسح'); });
};

el.hSearch.oninput = renderHistory;
el.hlist.onclick = (e) => {
    const item = e.target.closest('.hitem');
    if (item) openEntry(item.dataset.id);
};

$('segTheme').onclick = (e) => {
    const b = e.target.closest('button');
    if (!b) return;
    cfg.theme = b.dataset.v; applyTheme(); persist();
};
$('selFont').onchange = (e) => { cfg.font_family = e.target.value; applyTypography(); persist(); };
$('rngSize').oninput = (e) => { cfg.font_size = +e.target.value; applyTypography(); persist(); };
$('rngLine').oninput = (e) => { cfg.line_height = +e.target.value / 10; applyTypography(); persist(); };
$('rngMeasure').oninput = (e) => { cfg.measure = +e.target.value; applyTypography(); persist(); };
$('selPos').onchange = (e) => { cfg.position_mode = e.target.value; persist(); };
$('swTashkeel').onchange = (e) => { cfg.hide_tashkeel = e.target.checked; renderBody(); persist(); };
$('swBlur').onchange = (e) => { cfg.auto_hide_on_blur = e.target.checked; persist(); };
$('swAllApps').onchange = (e) => { cfg.monitor_all_apps = e.target.checked; persist(); };
$('swPersist').onchange = (e) => { cfg.persist_history = e.target.checked; persist(); };

matchMedia('(prefers-color-scheme: light)').addEventListener('change', () => {
    if (cfg.theme === 'system') applyTheme();
});

el.content.addEventListener('scroll', () => {
    const max = el.content.scrollHeight - el.content.clientHeight;
    el.prog.style.width = (max > 4 ? (el.content.scrollTop / max) * 100 : 0) + '%';
});

// نسخ بلوك كود + فتح اللينكات في المتصفح
el.content.addEventListener('click', (e) => {
    const copyBtn = e.target.closest('.ccopy');
    if (copyBtn) {
        const code = copyBtn.closest('.codeblock').querySelector('code');
        navigator.clipboard.writeText(code.textContent).then(() => toast('الكود اتنسخ ✓'));
        return;
    }
    const link = e.target.closest('a[data-ext]');
    if (link) {
        e.preventDefault();
        api('open_url', link.getAttribute('href'));
    }
});

// اختصارات الكيبورد
window.addEventListener('keydown', (e) => {
    const ctrl = e.ctrlKey || e.metaKey;
    if (e.key === 'Escape') {
        e.preventDefault();
        if (el.drawer.classList.contains('open')) return closeDrawer();
        if (el.panel.classList.contains('open')) return togglePanel();
        return api('hide_popup');
    }
    if (ctrl && (e.key === '=' || e.key === '+')) {
        e.preventDefault();
        cfg.font_size = Math.min(34, cfg.font_size + 1); applyTypography(); persist();
    } else if (ctrl && e.key === '-') {
        e.preventDefault();
        cfg.font_size = Math.max(13, cfg.font_size - 1); applyTypography(); persist();
    } else if (ctrl && e.key.toLowerCase() === 'h') {
        e.preventDefault(); toggleDrawer();
    } else if (ctrl && e.key === ',') {
        e.preventDefault(); togglePanel();
    } else if (ctrl && e.key.toLowerCase() === 'p') {
        e.preventDefault(); $('btnPin').click();
    } else if (ctrl && e.key.toLowerCase() === 'c') {
        if (!String(getSelection())) { e.preventDefault(); copyAll(); }
    } else if (e.altKey && (e.key === 'ArrowRight' || e.key === 'ArrowLeft')) {
        e.preventDefault();
        stepHistory(e.key === 'ArrowLeft' ? 1 : -1);
    }
});

// إخفاء تلقائي عند فقد التركيز
window.addEventListener('blur', () => {
    setTimeout(() => {
        if (!cfg.auto_hide_on_blur || cfg.pinned) return;
        if (document.hasFocus()) return;
        if (Date.now() - shownAt < 900) return;           // مهلة بعد الظهور
        if (el.panel.classList.contains('open')) return;
        if (el.drawer.classList.contains('open')) return;
        if (String(getSelection())) return;                // المستخدم بيحدّد نص
        api('hide_popup');
    }, 180);
});

// السحب من شريط العنوان
(function () {
    const bar = $('dragBar');
    let on = false, sx = 0, sy = 0;
    bar.addEventListener('mousedown', (e) => {
        if (e.target.closest('.iconbtn')) return;
        on = true; sx = e.screenX; sy = e.screenY;
    });
    document.addEventListener('mousemove', (e) => {
        if (!on) return;
        const dx = e.screenX - sx, dy = e.screenY - sy;
        sx = e.screenX; sy = e.screenY;
        if (dx || dy) api('move_by', dx, dy);
    });
    document.addEventListener('mouseup', () => { if (on) { on = false; api('geometry_changed'); } });
})();

// التحجيم من المقبض (الركن السفلي جهة اليسار في RTL)
(function () {
    const grip = $('grip');
    let on = false, sx = 0, sy = 0;
    grip.addEventListener('mousedown', (e) => { on = true; sx = e.screenX; sy = e.screenY; e.preventDefault(); });
    document.addEventListener('mousemove', (e) => {
        if (!on) return;
        const dx = e.screenX - sx, dy = e.screenY - sy;
        sx = e.screenX; sy = e.screenY;
        if (dx || dy) api('resize_by', -dx, dy);
    });
    document.addEventListener('mouseup', () => { if (on) { on = false; api('geometry_changed'); } });
})();
</script>
</body>
</html>'''
