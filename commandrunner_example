#!/user/bin/env python

from dnac import Dnac
from commandrunner import CommandRunner

MODULE="commandrunner_example.py"

print "%s: preparing to run a command..." % MODULE

dnac = Dnac()

cmd = CommandRunner(dnac, "ShowRunInt")

print "%s: setting the CLI command..." % MODULE

command = "show run interface gig1/0/8"

print "%s: acquiring the target switch..." % MODULE

switch  = "a0116157-3a02-4b8d-ad89-45f45ecad5da"

print "%s: formatting the command for Cisco DNA Center..." % MODULE

dnac.api['ShowRunInt'].formatCmd(command, switch)

print "%s: running the command..." % MODULE

dnac.api['ShowRunInt'].runSync(wait=10)

print "%s: command results = %s" % \
    (MODULE, str(dnac.api['ShowRunInt'].task.taskResults.results))

print

