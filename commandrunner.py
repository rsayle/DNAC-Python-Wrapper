#!/usr/bin/env python

from dnac import DnacError, \
                 SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION
from dnacapi import DnacApi, \
                    DnacApiError
from crud import ACCEPTED, \
                 REQUEST_NOT_ACCEPTED, \
                 ERROR_MSGS
from task import Task, TASK_CREATION
import json
import time

MODULE="commandrunner.py"

class CommandRunner(DnacApi):
    '''
    The CommandRunner class provides the interface for running CLI commands
    on DNA Center.  Note that the command runner API only allows read-only
    commands, i.e. show commands.

    Command sets must be formatted as a dictionary with two lists.  The
    first item uses "commands" as its key and then has a list of the
    actual CLI commands to run.  The second value's key is "deviceUuids"
    and its values are the device IDs where the commands will be run.
    CommandRunner provides two functions to help produce the dictionary
    used as the API call's body: formatCmd and formatCmds.

    To execute the commands, CommandRunner provdes two different methods.
    run() issues the commands but does not wait for the task to complete.
    runSync() on the other hand, waits for the task to finish and then
    collects the results.

    Usage:
        d = Dnac()
        cmds = {'commands': ['show version', 'show module'],
                'deviceUuids': ['<switch>', '<router>]}
        cmd = CommandRunner(d, "aName", cmds=cmds)
        progress = cmd.run()
        results = cmd.runSync()
    '''

    def __init__(self,
                 dnac,
                 name,
                 cmds="",
                 verify=False,
                 timeout=5):
        '''
        The __init__ method creates a CommandRunner object.  As with all
        classes that inherit from DnacApi, a mimimum of a Dnac container
        and a name must be given.  Optionally, a dictionary of the CLI
        commands to run and the UUIDs of devices to run them on may
        be specified.

                Parameters:
            dnac: A reference to the containing Dnac object.
                type: Dnac object
                default: None
                required: Yes
            name: A user friendly name for finding this object in a Dnac
                  instance.  If name is not included, __init__ sets
                  __name to "task__<id>", where <id> is the value of
                  the object's __id attribute..
                type: str
                default: None
                required: Yes
            cmds: A dict with the commands and target devices.
                type: dict
                default: None
                required: No
            verify: A flag used to check Cisco DNAC's certificate.
                type: boolean
                default: False
                required: No
            timeout: The number of seconds to wait for Cisco DNAC's
                     response.
                type: int
                default: 5
                required: No

        Return Values:
            CommandRunner object: The newly constructed CommandRunner

        Usage:
	    d = Dnac()
	    cmds = {'commands': ['show version', 'show module'],
                    'deviceUuids': ['<switch>', '<router>]}
	    cmd = CommandRunner(d, "aName", cmds=cmds)
        '''
        # check Cisco DNA Center's version and set the resourece path
        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            path = "/api/v1/network-device-poller/cli/read-request"
        else:
            raise DnacError(
                "__init__: %s: %s" %
                (UNSUPPORTED_DNAC_VERSION, dnac.version)
                           )
        # setup the attributes
        self.__cmds = cmds # commands to run
        self.__task = None # Task object created after running cmds
        super(CommandRunner, self).__init__(dnac,
                                            name,
                                            resource=path,
                                            verify=verify,
                                            timeout=timeout)

## end __init__()

    @property
    def cmds(self):
        '''
        Get method cmds returns the __cmds body to be sent to Cisco DNAC.

        Paramters:
            None

        Return Values:
            dict: A list of CLI commands and the devices on which to 
                  execute them.

        Usage:
	    d = Dnac()
	    cmds = {'commands': ['show version', 'show module'],
                    'deviceUuids': ['<switch>', '<router>]}
	    cmd = CommandRunner(d, "aName", cmds=cmds)
            print str(cmd.cmds)
        '''
        return self.__cmds

## end cmds getter

    @cmds.setter
    def cmds(self, cmds):
	'''
	Method cmds sets its __cmds attribute to the dictionary of
        commands given.
	
	Paramters:
	    cmds: A dict of commands and device UUIDs to run the
                  commands against.
                type: dict
                default: None
                required: Yes
	
	Return Values:
	    None
	
	Usage:
	    d = Dnac()
	    cmd = CommandRunner(d, "aName")
	    cmds = ['show version', 'show module', 'show proc cpu']
	    cmd.cmds = cmds
	'''
        self.__cmds = cmds

## end cmds setter

    @property
    def task(self):
        '''
        The task get function returns the Task object stored in __task.

        Parameters:
            None
        
        Return Values:
            Task object: The task associated with the CommandRunner
            instance.

        Usage:
            d = Dnac()
            cmd = CommandRunner(d, "aName")
            cliCmd = "show module"
            switch = "<switch's UUID>"
            cmd.formatCmd(cliCmd, switch)
            cmd.run()
            task = cmd.task
        '''
        return self.__task

## end cmds getter

    @task.setter
    def task(self, task):
        '''
        The task set method sets the __task attribute to the Task object
        given.
   
        Paramters:
            task: A task object for monitoring the command's results
                type: Task object
                default: None
                required: Yes
   
        Return Values:
           None
   
        Usage:
           d = Dnac()
           cmd = CommandRunner(d, "aName")
           # Not the preferred way of doing this.  run and runSync will
           # automatically set up __task.
           task = Task(d, "taskName")
           cmd.task = task
        '''
        self.__task = task

## end task setter

    def formatCmd(self, cmd, uuid):
        '''
        The formatCmd method takes a single CLI command and runs it against
        the UUID of a network device in Cisco DNA Center.  It converts the
        command and the UUID into a dict stored in the __cmds attribute
        and returns __cmds' value.

        Parameters:
            cmd: A CLI command.
                type: str
                default: None
                required: Yes
            uuid: A network device UUID.
                type: str
                default: None
                required: Yes

        Return Values:
            dict: The command instructions used as the body for making
                  an API call to Cisco DNAC's command runner.

        Usage:
            d = Dnac()
            cmd = 'show version'
            uuid = '<switch_uuid>'
            cmd = CommandRunner(d, "aName")
            cmd.formatCmd(cmd, uuid)
        '''
        c = [cmd]
        u = [uuid]
        cmds = {'commands': c, \
                'deviceUuids': u}
        self.__cmds = json.dumps(cmds)
        return self.__cmds

## end formatCmd()

    def formatCmds(self, cmdList, uuidList):
        '''
        The formatCmds method accepts a list of CLI commands to run against
        a list of UUIDs for the target network devices in Cisco DNA Center.
        It converts the two lists into a dict stored in the __cmds attribute
        and returns __cmds' value.

        Parameters:
            cmdList: A list of CLI commands.
                type: list of str
                default: None
                required: Yes
            uuidList: A list of network device UUIDs.
                type: list of str
                default: None
                required: Yes

        Return Values:
            dict: The command instructions used as the body for making
                  an API call to Cisco DNAC's command runner.

        Usage:
            d = Dnac()
            cmds = ['show version', 'show ip interface brief']
            uuids = ['<switch_uuid>', '<router_uuid>']
            cmds = CommandRunner(d, "aName")
            cmds.formatCmds(cmds, uuids)
        '''
        cmds = {'commands': cmdList, \
                'deviceUuids': uuidList}
        self.__cmds = json.dumps(cmds)
        return self.__cmds

## end formatCmds()

    def run(self):
        '''
        Method run instructs Cisco DNAC to execute the command set stored in
        the CommandRunner object.  It does not wait for the task to
        complete on Cisco DNA Center.  It does, however, create a new Task
        object, saves it in the __task attribute, checks the task, and
        then returns the task's status.  See the task.py module for
        valid task states.  When using this function, the programmer
        must handle task monitoring.

        Parameters:
            None

        Return Vaules:
            str: The current state of the command's progress.

        Usage:
            d = Dnac()
            cmd = CommandRunner(d, "aName")
            cmdState = cmd.run()
        '''
        url = self.dnac.url + self.resource
        results, status = self.crud.post(url,
                                         headers=self.dnac.hdrs,
                                         body=self.cmds,
                                         verify=self.verify,
                                         timeout=self.timeout)
        if status != ACCEPTED:
            raise DnacApiError(MODULE, "run", REQUEST_NOT_ACCEPTED, url,
                               ACCEPTED, status, ERROR_MSGS[status],
                               str(results))
        tId = results['response']['taskId']
        tName = "task_" + tId
        self.__task = Task(self.dnac, tName, tId)
        return self.__task.checkTask()

## end run()

    def runSync(self, wait=3):
        '''
        runSync issues the commands set in the CommandRunner and waits
        for their completion.  It performs this action by creating a
        Task object and then checks the task's state periodically
        according to the wait time (seconds) passed as an argument.
        If no wait time is given, it checks every three seconds.

        When the task finishes, the Task object will have also loaded
        the task's results, which can be immediately accessed via the
        CommandRunner instance (cmd.task.taskResults.results) or from
        the function's return value (results = cmd.runSync()).

        Parameters:
            wait: The time to wait before checking the results.
                type: int
                default: 3
                required: No

        Return Vaules:
            list: The command set's output

        Usage:
            d = Dnac()
            cmd = CommandRunner(d, "aCmdName")
            results = cmd.runSync(wait=10)
        '''
        url = self.dnac.url + self.resource
        results, status = self.crud.post(url,
                                         headers=self.dnac.hdrs,
                                         body=self.cmds,
                                         verify=self.verify,
                                         timeout=self.timeout)
        if status != ACCEPTED:
            DnacApiError(MODULE, "run", REQUEST_NOT_ACCEPTED, url,
                         ACCEPTED, status, ERROR_MSGS[status], str(results))
        tid = results['response']['taskId']
        tname = "task_" + tid
        self.task = Task(self.dnac, tname, taskId=tid)
        self.task.checkTask()
        while self.task.progress == TASK_CREATION:
            time.sleep(wait)
            self.task.checkTask()
        return self.task.taskResults.results

## end runSync()

## end class CommandRunner()

## begin unit test

if  __name__ == '__main__':

    from dnac import Dnac
    from taskresults import TaskResults
    import time
    import sys

    d = Dnac()

    c = CommandRunner(d, "command-runner")

    print "CommandRunner:"
    print
    print "  dnac      = " + str(type(c.dnac))
    print "  name      = " + c.name
    print "  cmds      = " + c.cmds
    print "  task      = " + str(c.task)
    print "  resource  = " + c.resource
    print "  verify    = " + str(c.verify)
    print "  timeout   = " + str(c.timeout)
    print
    print "Setting a single command on a single device..."
    print

    cmd = c.formatCmd("show vlan", "84e4b133-2668-4705-8163-5694c84e78fb")

    print "  format  = " + cmd
    print "  cmds    = " + c.cmds
    print
    print "Running the command asynchronously..."
    print

    resp = c.run()
    while c.task.progress == TASK_CREATION:
        time.sleep(1)
        print "task     = " + str(c.task)
        print "progress = " + c.task.progress
        c.task.checkTask()
    print "progress = " + str(c.task.progress)
    tid = c.task.progress['fileId']
    name = "task_" + tid
    c.task.taskResults = TaskResults(c.dnac, name, tid)
    results = c.task.taskResults.getResults()

    print "  response                 = " + str(resp)
    print "  task                     = " + str(c.task)
    print "  task.id                  = " + c.task.id
    print "  task.progress            = " + str(c.task.progress)
    print "  task.taskResults         = " + str(c.task.taskResults)
    print "  task.taskResults.results = " + str(c.task.taskResults.results)
    print
    print "Setting multiple commands for multiple devices..."
    print

    cmds = ['show vlan', 'show ver']
    uuids = ['84e4b133-2668-4705-8163-5694c84e78fb', \
             'ca27cdcc-241c-456f-92d8-63e1361fbfd7']
    multicmds = c.formatCmds(cmds, uuids)

    print "  format = " + multicmds
    print "  cmds   = " + c.cmds
    print
    print "Running the commands syncronously..."
    print

    resp = c.runSync(wait=5)
    c.task.checkTask()

    print "  response     = " + str(resp)
    print "  task         = " + str(c.task)
    print "  task.id      = " + c.task.id
    print "  task.taskResults = " + str(c.task.taskResults)
    print "  task.taskResults.results = " + str(c.task.taskResults.results)
    print
    print "CommandRunner: unit test complete."
    print
