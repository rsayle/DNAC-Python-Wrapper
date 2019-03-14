
from dnac import Dnac
from dnac.commandrunner import CommandRunner

MODULE = 'commandrunner_example.py'

print('%s: preparing to run a command...' % MODULE)

dnac = Dnac()

cmd = CommandRunner(dnac, 'ShowRunInt')

print('%s: setting the CLI command...' % MODULE)

command = 'show run interface gig1/0/8'

print('%s: acquiring the target switch...' % MODULE)

switch = '84e4b133-2668-4705-8163-5694c84e78fb'

print('%s: formatting the command for Cisco DNA Center...' % MODULE)

dnac.api['ShowRunInt'].format_cmd(command, switch)

print('%s: running the command...' % MODULE)

dnac.api['ShowRunInt'].run_sync(wait=10)

print('%s: command results = %s' %
      (MODULE, str(dnac.api['ShowRunInt'].task.file.results)))

print()
