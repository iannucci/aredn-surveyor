# Invoke via python -m tests

import pathlib
import sys
import os

projectDir = pathlib.Path(__file__).parent.parent.resolve()
moduleDir = '%s/src' % projectDir
configFilePath = '%s/config/config.ini' % moduleDir
sys.path.append(os.fspath(projectDir))

from src.debugger.debug_log import debugLog

from tests.query import queryBoundsAndZoom

debugLog(str(queryBoundsAndZoom({ 'height': 1000, 'width': 800 }, channel=175)))