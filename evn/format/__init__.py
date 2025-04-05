import os
import sys
import evn

with evn.cd_project_root() as project_exists:
    if project_exists and os.path.exists('_build'):
            assert os.path.exists('pyproject.toml')
            os.system('doit build')
            sys.path.append('_build')
            from _detect_formatted_blocks import *
            from _token_column_format import *
            sys.path.pop(0)  # Remove the build path so it doesn't interfere with import
    else:
        from evn.format._detect_formatted_blocks import *
        from evn.format._token_column_format import *

from evn.format.formatter import *
