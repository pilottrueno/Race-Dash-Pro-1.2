#!/bin/bash
echo "========================================="
echo "🔍 ДИАГНОСТИКА RACE DASH PRO"
echo "========================================="
echo ""

echo "📁 1. ПРОВЕРКА ФАЙЛОВ ПРОЕКТА:"
ls -la /home/pi/Race-Dash-Pro-1.1/ | grep -E "main.py|screens|widgets|utils|rgb"
echo ""

echo "📂 2. ПРОВЕРКА ПАПОК:"
for dir in screens widgets utils rgb controllers logs; do
    if [ -d "/home/pi/Race-Dash-Pro-1.1/$dir" ]; then
        echo "   ✅ Папка $dir существует"
    else
        echo "   ❌ Папка $dir ОТСУТСТВУЕТ"
    fi
done
echo ""

echo "📄 3. ПРОВЕРКА ОСНОВНЫХ ФАЙЛОВ:"
for file in main.py screens/demo_screen.py screens/logs_screen.py widgets/tachometer.py utils/swipe_container.py; do
    if [ -f "/home/pi/Race-Dash-Pro-1.1/$file" ]; then
        echo "   ✅ $file существует"
    else
        echo "   ❌ $file ОТСУТСТВУЕТ"
    fi
done
echo ""

echo "🔑 4. ПРОВЕРКА ПРАВ НА ФАЙЛЫ:"
if [ -f "/home/pi/Race-Dash-Pro-1.1/main.py" ]; then
    ls -la /home/pi/Race-Dash-Pro-1.1/main.py
fi
echo ""

echo "🔄 5. ПРОВЕРКА АВТОЗАПУСКА:"
if [ -f "/home/pi/.config/autostart/race-dash.desktop" ]; then
    echo "   ✅ Файл автозапуска существует:"
    cat /home/pi/.config/autostart/race-dash.desktop
else
    echo "   ❌ Файл автозапуска ОТСУТСТВУЕТ"
fi
echo ""

echo "🖥️ 6. ПРОВЕРКА ЯРЛЫКОВ НА РАБОЧЕМ СТОЛЕ:"
ls -la /home/pi/Desktop/ | grep -E "RACE|race|RDP|rdp|run" || echo "   ❌ Ярлыки не найдены"
echo ""

echo "🐍 7. ПРОВЕРКА PYTHON:"
python3 --version
echo ""

echo "📦 8. ПРОВЕРКА БИБЛИОТЕК:"
python3 -c "import PyQt5; print('   ✅ PyQt5 установлен')" 2>/dev/null || echo "   ❌ PyQt5 НЕ УСТАНОВЛЕН"
python3 -c "import board; print('   ✅ board установлен')" 2>/dev/null || echo "   ❌ board НЕ УСТАНОВЛЕН"
python3 -c "import neopixel; print('   ✅ neopixel установлен')" 2>/dev/null || echo "   ❌ neopixel НЕ УСТАНОВЛЕН"
echo ""

echo "💡 9. ПРОВЕРКА RGB:"
if [ -f "/home/pi/Race-Dash-Pro-1.1/rgb/rgb_controller.py" ]; then
    echo "   ✅ RGB модуль существует"
else
    echo "   ❌ RGB модуль ОТСУТСТВУЕТ"
fi
echo ""

echo "🛰️ 10. ПРОВЕРКА CAN:"
if [ -d "/home/pi/Race-Dash-Pro-1.1/can" ]; then
    echo "   ✅ Папка CAN существует"
    ls -la /home/pi/Race-Dash-Pro-1.1/can/ 2>/dev/null || echo "   📁 Папка пуста"
else
    echo "   ❌ Папка CAN ОТСУТСТВУЕТ"
fi
echo ""

echo "========================================="
echo "✅ ДИАГНОСТИКА ЗАВЕРШЕНА"
echo "========================================="
