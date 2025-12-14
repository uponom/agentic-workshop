"""
Демонстрация различий в поддержке сигналов между операционными системами
"""

import signal
import platform

def check_signal_support():
    """Проверяет поддержку различных сигналов в текущей ОС"""
    
    print(f"🖥️  Операционная система: {platform.system()} {platform.release()}")
    print(f"🐍 Python версия: {platform.python_version()}")
    print()
    
    # Список сигналов для проверки
    signals_to_check = [
        ('SIGALRM', 'Alarm signal (таймер)'),
        ('SIGINT', 'Interrupt signal (Ctrl+C)'),
        ('SIGTERM', 'Termination signal'),
        ('SIGUSR1', 'User-defined signal 1'),
        ('SIGUSR2', 'User-defined signal 2'),
        ('SIGHUP', 'Hangup signal'),
        ('SIGKILL', 'Kill signal (немедленное завершение)'),
        ('SIGSTOP', 'Stop signal (приостановка)'),
        ('SIGCHLD', 'Child process signal'),
        ('SIGPIPE', 'Broken pipe signal'),
    ]
    
    print("📋 Проверка поддержки сигналов:")
    print("-" * 50)
    
    supported = []
    not_supported = []
    
    for sig_name, description in signals_to_check:
        try:
            sig_value = getattr(signal, sig_name)
            supported.append((sig_name, description, sig_value))
            print(f"✅ {sig_name:<10} = {sig_value:<3} | {description}")
        except AttributeError:
            not_supported.append((sig_name, description))
            print(f"❌ {sig_name:<10} = N/A | {description} (НЕ ПОДДЕРЖИВАЕТСЯ)")
    
    print()
    print(f"📊 Статистика:")
    print(f"   Поддерживается: {len(supported)}")
    print(f"   Не поддерживается: {len(not_supported)}")
    
    return supported, not_supported

def demonstrate_sigalrm_usage():
    """Демонстрирует использование SIGALRM (только для Unix)"""
    
    print("\n🔔 Демонстрация SIGALRM:")
    print("-" * 30)
    
    if platform.system() == 'Windows':
        print("❌ SIGALRM не поддерживается в Windows")
        print("💡 В Windows используются другие механизмы:")
        print("   - threading.Timer")
        print("   - asyncio.wait_for()")
        print("   - signal.alarm() недоступен")
        return
    
    try:
        import time
        
        def timeout_handler(signum, frame):
            print("⏰ Таймаут! Операция прервана по SIGALRM")
            raise TimeoutError("Операция превысила лимит времени")
        
        # Устанавливаем обработчик сигнала
        signal.signal(signal.SIGALRM, timeout_handler)
        
        print("✅ SIGALRM поддерживается")
        print("🔧 Пример использования:")
        print("   signal.alarm(5)  # Установить таймаут 5 секунд")
        print("   # выполнить долгую операцию")
        print("   signal.alarm(0)  # Отменить таймаут")
        
    except AttributeError:
        print("❌ SIGALRM недоступен в этой системе")

def show_windows_alternatives():
    """Показывает альтернативы для Windows"""
    
    print("\n🪟 Альтернативы для Windows:")
    print("-" * 35)
    
    print("1️⃣ threading.Timer:")
    print("""
import threading

def timeout_function():
    print("Таймаут!")
    # Логика обработки таймаута

timer = threading.Timer(5.0, timeout_function)
timer.start()
# выполнить операцию
timer.cancel()  # Отменить если завершилось раньше
""")
    
    print("2️⃣ asyncio.wait_for():")
    print("""
import asyncio

async def long_operation():
    await asyncio.sleep(10)  # Долгая операция

try:
    await asyncio.wait_for(long_operation(), timeout=5.0)
except asyncio.TimeoutError:
    print("Операция превысила таймаут")
""")
    
    print("3️⃣ subprocess с timeout:")
    print("""
import subprocess

try:
    result = subprocess.run(['command'], timeout=5)
except subprocess.TimeoutExpired:
    print("Процесс превысил таймаут")
""")

def analyze_mcp_server_issue():
    """Анализирует проблему с MCP сервером AWS"""
    
    print("\n🔍 Анализ проблемы MCP сервера AWS:")
    print("-" * 45)
    
    print("🐛 Проблема:")
    print("   AWS Diagram MCP Server использует signal.SIGALRM для таймаутов")
    print("   при генерации диаграмм, но этот сигнал недоступен в Windows")
    
    print("\n📋 Детали ошибки:")
    print('   AttributeError: module "signal" has no attribute "SIGALRM"')
    
    print("\n🔧 Где это происходит:")
    print("   1. MCP сервер пытается установить таймаут для Graphviz")
    print("   2. Использует signal.alarm() для ограничения времени выполнения")
    print("   3. В Windows signal.alarm() и SIGALRM недоступны")
    print("   4. Код падает с AttributeError")
    
    print("\n💡 Почему это важно:")
    print("   - Graphviz может зависнуть при сложных диаграммах")
    print("   - Таймауты предотвращают бесконечное ожидание")
    print("   - Unix-системы имеют встроенную поддержку сигналов")
    print("   - Windows требует другие подходы к таймаутам")
    
    print("\n🛠️ Решения:")
    print("   ✅ Локальная генерация диаграмм (наше решение)")
    print("   ✅ Использование WSL (Windows Subsystem for Linux)")
    print("   ✅ Docker контейнер с Linux")
    print("   ✅ Патч MCP сервера для Windows совместимости")

def main():
    print("🚀 Анализ совместимости сигналов операционной системы")
    print("=" * 60)
    
    check_signal_support()
    demonstrate_sigalrm_usage()
    show_windows_alternatives()
    analyze_mcp_server_issue()
    
    print("\n" + "=" * 60)
    print("✨ Анализ завершен!")

if __name__ == "__main__":
    main()