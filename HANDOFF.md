# تسليم للجلسة المحلية

> ملف مؤقت. امسحه لما تخلص الدمج.

## ١. الوضع: فيه نسختين للبرنامج

| | المحلي (جهازك) | الفرع `claude/jolly-turing-90uykg` |
|---|---|---|
| آخر commit | `0fb98bd` (الأولاني) | `1791bed` |
| البنية | ملف واحد `claude_rtl.py` | مقسوم ٥ موديولز |
| الحالة | تعديلات **مش متسجّلة** `+398/−102` | مرفوع ومتستّت جزئياً |

النسختين اشتغلوا على نفس الملف بالتوازي. **ماتعملش `git pull` أو `checkout`
قبل ما تحفظ شغلك المحلي** — هيتمسح.

## ٢. أول حاجة: احفظ المحلي

```bash
git checkout -b local-wip
git add -A
git commit -m "WIP: local changes before merge"
git fetch origin claude/jolly-turing-90uykg
```

كده مافيش حاجة ممكن تضيع، ونقدر نقارن براحتنا.

## ٣. المقارنة

```bash
git diff local-wip origin/claude/jolly-turing-90uykg -- claude_rtl.py
git show origin/claude/jolly-turing-90uykg:README.md
```

من اللي ظهر في الجلسة المحلية، التعديلات المحلية بتغطي الحاجات دي — وكلها
موجودة في الفرع بشكل أو بآخر:

| التعديل المحلي | مقابله في الفرع |
|---|---|
| `config.json` + `history.json` على الديسك | `settings.py` — `%APPDATA%\ClaudeRTL\settings.json` + `history.json`، كتابة ذرّية، ودمج مع القيم الافتراضية |
| `_persist_geometry` | `remember_geometry()` + وضع ظهور «آخر مكان» |
| `set_font` / تكبير وتصغير الخط | لوحة إعدادات: ٦ خطوط + حجم + تباعد أسطر + عرض سطر بالـ`ch` |
| `add_entry` / `nav` / navigation بين النصوص | درج سجل ببحث، `Alt+←/→`، آخر ٤٠ نص |
| `on_blur` | `auto_hide_on_blur` مع مهلة ٩٠٠ms بعد الظهور، ومعطّل وقت التثبيت |
| `force_foreground(hwnd)` | نفس الفكرة بـ`AttachThreadInput` في `winapi.py` |
| `hotkey_listener` + تثبيت النافذة قدام | `Ctrl+Shift+A` و`Ctrl+Shift+D` عبر `RegisterHotKey` في ثريد مستقل |
| `pin toggle` + counter | زر تثبيت (`Ctrl+P`) + عدّاد كلمات/حروف في شريط الحالة |
| `tray menu: on_show_last / on_clear` | قايمة tray: إظهار آخر نص / تشغيل المراقبة / الإعدادات / خروج |

**التوصية:** خُد الفرع كأساس، وعدّي على الـdiff تدوّر على أي سلوك محلي مش
مغطّى (خصوصاً تفاصيل صغيرة في الـtray أو الـnav). التغطية مش مضمونة ١٠٠٪،
فالمقارنة مش خطوة شكلية.

لو اخترت الفرع كأساس:

```bash
git checkout claude/jolly-turing-90uykg
# local-wip فاضل موجود للرجوع ليه في أي وقت
```

## ٤. المهم: كود ويندوز ماتجربش ولا مرة

الفرع اتكتب في كونتينر Linux. المتستّت فعلاً هو `mdrender` و`settings`
(`python tests\test_mdrender.py` — ١٨/١٨). أي حاجة بتلمس ويندوز اتكتبت من
غير تشغيل.

جرّب بالترتيب ده — مرتّب من الأكثر احتمالاً للفشل:

1. **الاختصارات العامة** — `Ctrl+Shift+A` و`Ctrl+Shift+D`.
   `RegisterHotKey` مربوط بالثريد اللي سجّلها، والـloop في `winapi.hotkey_loop`.
2. **الإخفاء التلقائي** — `blur` في `ui.py`. المهلة ٩٠٠ms بعد الظهور؛ لو
   النافذة بتقفل على طول أول ما تظهر، المهلة قليلة أو `SetForegroundWindow` فشل.
3. **مراقبة الحافظة** — انسخ عربي من Claude Desktop. لو مافيش رد فعل، شوف
   `winapi.foreground_process_name()` راجعة إيه؛ الفلتر على `claude.exe`.
4. **مواضع الظهور التلاتة** على شاشات متعددة، وعلى DPI scaling مش ١٠٠٪.
   دي أكتر حتة فيها شك: إحداثيات `GetCursorPos` فيزيائية، وpywebview بيتعامل
   بوحداته — ممكن يحصل انزياح.
5. **السحب والتحجيم** — المقبض في الركن السفلي جهة الشمال، و`resize_by`
   بيحرّك `x` كمان عشان الحافة دي هي اللي بتتحرك.
6. **الـtray** — الأيقونة والقايمة و«مراقبة الحافظة» كـchecked.
7. **البناء** — `build.bat` (اختبارات ← cx_Freeze ← Inno Setup).

## ٥. الملفات الجديدة عندك

`.gitignore` اتحدّث ليشمل `*.bak*` و`*.egg-info/`.

ملفات الهوية (`Claude-arabc-branding.ai`، `Icon-claude-arabic.svg`،
`Icon-claude-arabic@5x.png`، `Claude-arabc-Cover-02.png`) مصادر تصميم —
الأفضل تتسجّل، ويفضل في مجلد `assets/`. الاسكرين شوتس (`Screenshot*`،
`image-*.jpg`) مالهاش لزوم في الريبو.
