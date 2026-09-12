@echo off
chcp 65001 >nul
echo.
echo  ── Claude RTL — بناء ──
echo.

python -m pip install -r requirements.txt || goto :err

echo.
echo  [1/3] تشغيل الاختبارات...
python tests\test_mdrender.py || goto :err

echo.
echo  [2/3] بناء الـexe...
rmdir /s /q build 2>nul
python setup_cx.py build || goto :err

echo.
echo  [3/3] بناء المُثبِّت...
where iscc >nul 2>nul
if errorlevel 1 (
    echo  Inno Setup مش متسطّب — اتخطّينا المُثبِّت.
    echo  الـexe جاهز في مجلد build\
    goto :done
)
iscc installer.iss || goto :err
echo  المُثبِّت جاهز في output\ClaudeRTL-Setup.exe

:done
echo.
echo  تمام ✓
exit /b 0

:err
echo.
echo  فشل البناء.
exit /b 1
