import os
import sys
import evn

if build := evn.projroot / '_build':
    os.system(f'cd {build} && ninja')
    sys.path.insert(0, str(build))  # Add the build path to sys.path for imports
    from _detect_formatted_blocks import *
    from _token_column_format     import *
    sys.path.pop(0)  # Remove the build path so it doesn't interfere with import
else:
    from evn.format._detect_formatted_blocks import *
    from evn.format._token_column_format     import *

from evn.format.formatter                import *
