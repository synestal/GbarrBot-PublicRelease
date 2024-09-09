from cx_Freeze import setup, Executable

executables = [Executable('main.py',
base='Win32GUI',
icon='5793724.ico', target_name="GbarrBotApp.exe")]


includes = ['pandas', 'requests', 'datetime', 'openpyxl']

zip_include_packages = ['libs/vk_api-11.9.9.zip']

include_files = ['blocks.xlsx',
'config.py']

options = {
'build_exe': {
'include_msvcr': True,
'includes': includes,
'zip_include_packages': zip_include_packages,
'build_exe': 'build_windows',
'include_files': include_files,
}
}

setup(name='GbarrBotApp',
version='3.0',
description='GbarrBotApp',
executables=executables,
options=options)
