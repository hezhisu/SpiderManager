from cx_Freeze import setup, Executable

executables = [
    Executable('spider.py')
]

setup(name='spider',
      version='0.1',
      description='spider',
      executables=executables)