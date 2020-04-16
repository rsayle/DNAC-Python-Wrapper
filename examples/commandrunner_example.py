
from dnac import Dnac
from dnac.commandrunner import CommandRunner
import pprint


MODULE = 'commandrunner_example.py'

print('%s: preparing to run a command...' % MODULE)

dnac = Dnac()

cmd = CommandRunner(dnac, 'ShowRunInt')

print('%s: setting the CLI command...' % MODULE)

command = 'show run interface gig1/0/8'

print('%s: acquiring the target switch...' % MODULE)

switch = 'bf5eda5f-05d7-48a8-84e3-481aaa0c4da5'

print('%s: formatting the command for Cisco DNA Center...' % MODULE)

dnac.api['ShowRunInt'].format_cmd(command, switch)

print('%s: running the command...' % MODULE)

dnac.api['ShowRunInt'].run(wait=10)

print('%s: command results = ' % MODULE)
pprint.pprint(dnac.api['ShowRunInt'].task.file.results, indent=4)

print()
