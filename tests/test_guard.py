import unittest,json,tempfile
from unittest.mock import patch
from guard import validate
class Tests(unittest.TestCase):
 def test_identity(self):
  with tempfile.TemporaryDirectory() as d:
   c={'mountpoint':d,'uuid':'synthetic-disk'};reply=json.dumps({'filesystems':[{'target':d,'uuid':'other','options':'rw'}]})
   with patch('guard.os.path.ismount',return_value=True),patch('guard.subprocess.check_output',return_value=reply):
    with self.assertRaises(ValueError):validate(c)
 def test_missing_mount(self):
  with patch('guard.os.path.ismount',return_value=False):
   with self.assertRaises(ValueError):validate({'mountpoint':'/srv/example','uuid':'synthetic'})
