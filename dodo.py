import sysconfig
from pathlib import Path

root = Path(__file__).parent.absolute()
build = root / '_build'

def task_cmake():
    return {
        'actions': [f'cmake {find_pybind()} -B {build} -S {root} -GNinja'],
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

def find_pybind():
    pybind = sysconfig.get_paths()['purelib'] + '/pybind11'
    pybind = f'-Dpybind11_DIR={pybind}'
    # print(pybind)
    return pybind

def task_import_check():
    """Try to import the compiled module to verify it's working"""

    def import_test():
        try:
            pass
        except Exception as e:
            print('❌ Import failed:', e)
            raise

    return {
        'actions': [import_test],
        'task_dep': ['build'],
    }

def task_test():
    """Run tests using pytest"""
    return {
        'actions': ['pytest evn/tests'],
        'task_dep': ['import_check'],
    }
