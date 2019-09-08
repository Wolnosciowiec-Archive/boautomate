# standard bootstrap code
import sys
import os

sys.path = [os.environ.get('BOAUTOMATE_PATH', '/opt/boautomate')] + sys.path
# end of standard bootstrap code


import subprocess

print('Hello from %s' % subprocess.check_output('uname -a', shell=True).decode('utf-8'))
