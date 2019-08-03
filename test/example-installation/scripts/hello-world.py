

import subprocess

print('Hello from %s' % subprocess.check_output('uname -a', shell=True).decode('utf-8'))
