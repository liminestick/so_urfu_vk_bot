import sys
from cx_Freeze import setup, Executable

# Определяем исполняемые файлы
executables = [
    Executable('main.py')
]

# Настройки для cx_Freeze
build_exe_options = {
    'packages': ['vk_api', 'json', 'time'],
    'include_files': ['HelloMessage.txt', 'question.json', 'token.txt', 'users.json', 'finished.txt']
}

# Создаем исполняемый файл
setup(
    name='VKbotUrfu',
    version='1.0',
    description='A special bot of the Ural Federal University for conducting quizzes in a group',
    options={'build_exe': build_exe_options},
    executables=executables
)