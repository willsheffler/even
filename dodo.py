from pathlib import Path

root = Path(__file__).parent.absolute()
build = root / '_build'

def task_cmake():
    return {
        'actions': [f'cmake -B {build} -S {root} -GNinja'],
        'file_dep': [root / 'CMakeLists.txt'],
        'targets': [build / 'build.ninja'],
    }

def task_build():
    return {
        'actions': [f'cd {build} && ninja'],
        'file_dep': [build / 'build.ninja'],
    }

def task_test():
    task_build()
    return {
        'actions': [f'cd {root} && PYTHONPATH=. pytest'],
        'file_dep': [build / 'Makefile'],
        'targets': [build / 'Testing/Temporary/LastTest.log'],  # Assuming this is where ctest logs
    }
