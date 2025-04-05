import os
import sys
import evn

with evn.cd_project_root() as project_exists:
    if project_exists and os.path.exists('_build'):
        assert os.path.exists('pyproject.toml')
        os.system('doit build')
        try:
            sys.path.append('_build')
            from _detect_formatted_blocks import *  # type: ignore
            from _token_column_format import *  # type: ignore
            using_local_build = True
        except ImportError:
            using_local_build = False
        finally:
            sys.path.pop(0)  # Remove the build path so it doesn't interfere with import
    if not using_local_build:
        from evn.format._detect_formatted_blocks import *  # type: ignore
        from evn.format._token_column_format import *  # type: ignore

from evn.format.formatter import *
