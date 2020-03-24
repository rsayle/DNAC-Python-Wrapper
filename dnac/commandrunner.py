
from dnac import DnacError, \
                 SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION
from dnac.dnacapi import DnacApi, \
                         DnacApiError
from dnac.crud import ACCEPTED, \
                      REQUEST_NOT_ACCEPTED, \
                      ERROR_MSGS
from dnac.task import Task
import json
import time

MODULE = 'commandrunner.py'

COMMANDRUNNER_RESOURCE_PATH = {
    '1.2.8': '/api/v1/network-device-poller/cli/read-request',
    '1.2.10': '/dna/intent/api/v1/network-device-poller/cli/read-request',
    '1.3.0.2': '/dna/intent/api/v1/network-device-poller/cli/read-request',
    '1.3.0.3': '/dna/intent/api/v1/network-device-poller/cli/read-request',
    '1.3.1.3': '/dna/intent/api/v1/network-device-poller/cli/read-request',
    '1.3.1.4': '/dna/intent/api/v1/network-device-poller/cli/read-request'
}


class CommandRunner(DnacApi):
    """
    The CommandRunner class provides the interface for running CLI commands on DNA Center.  Note that the command
    runner API only allows read-only commands, i.e. show commands.

    Command sets must be formatted as a dictionary with two lists.  The first item uses "commands" as its key and then
    has a list of the actual CLI commands to run.  The second value's key is "deviceUuids" and its values are the
    device IDs where the commands will be run. CommandRunner provides two functions to help produce the dictionary
    used as the API call's body: formatCmd and formatCmds.

    To execute the commands, CommandRunner provdes two different methods. run() issues the commands but does not wait
    for the task to complete. runSync() on the other hand, waits for the task to finish and then collects the results.

    Attributes:
        dnac: A pointer to the Dnac object containing the CommandRunner instance.
            type: Dnac object
            default: none
            scope: protected
        name: A user-friendly name for accessing the CommandRunner object in a Dnac.api{}.
            type: str
            default: none
            scope: protected
        task: A Task object associated with the commands being run.
            type: Task object
            default: none
            scope: protected
        cmds: The CLI commands to be run on the target devices.
            type: dict
            default: none
            scope: public
        resource: The URI for running commands within Cisco DNAC.
            type: str
            default: Cisco DNA Center version dependent
            scope: protected
        verify: A flag indicating whether or not to verify Cisco DNA Center's certificate.
            type: bool
            default: False
            scope: protected
        timeout: The number of seconds to wait for Cisco DNAC to respond before timing out.
            type: int
            default: 5
            scope: protected

    Usage:
        d = Dnac()
        cmds = {'commands': ['show version', 'show module'],
                'deviceUuids': ['<switch>', '<router>]}
        cmd = CommandRunner(d, "aName", cmds=cmds)
        progress = cmd.run()
        results = cmd.runSync()
    """

    def __init__(self,
                 dnac,
                 name,
                 cmds=None,
                 verify=False,
                 timeout=5):
        """
        The __init__ method creates a CommandRunner object.  As with all classes that inherit from DnacApi, a minimum
        of a Dnac container and a name must be given.  Optionally, a dictionary of the CLI commands to run and the
        UUIDs of devices to run them on may be specified.
        :param dnac: A reference to the containing Dnac object.
            type: Dnac object
            default: none
            required: yes
        :param name: A user friendly name for finding this object in a Dnac instance.
            type: str
            default: none
            required: yes
        :param cmds: A dict with the commands and target devices.
            type: dict
            default: none
            required: no
        :param verify: A flag used to check Cisco DNAC's certificate.
            type: boolean
            default: False
            required: no
        :param timeout: The number of seconds to wait for Cisco DNAC's response.
            type: int
            default: 5
            required: no
        """
        # check Cisco DNA Center's version and set the resourece path
        if cmds is None:
            cmds = {}
        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            path = COMMANDRUNNER_RESOURCE_PATH[dnac.version]
        else:
            raise DnacError(
                '__init__: %s: %s' %
                (UNSUPPORTED_DNAC_VERSION, dnac.version)
                           )
        # setup the attributes
        self.__cmds = cmds  # commands to run
        self.__task = None  # Task object created after running cmds
        super(CommandRunner, self).__init__(dnac,
                                            name,
                                            resource=path,
                                            verify=verify,
                                            timeout=timeout)

    # end __init__()

    @property
    def cmds(self):
        """
        Get method cmds returns the __cmds body to be sent to Cisco DNAC.
        :return: dict
        """
        return self.__cmds

    # end cmds getter

    @cmds.setter
    def cmds(self, cmds):
        """
        Method cmds sets its __cmds attribute to the dictionary of commands given.
        :param cmds: A dict of commands and device UUIDs to run the commands against.
             type: dict
             default: None
             required: Yes
        :return: none
        """
        self.__cmds = cmds

    # end cmds setter

    @property
    def task(self):
        """
        The task get function returns the Task object stored in __task.
        :return: Task object
        """
        return self.__task

# end cmds getter

    def format_cmd(self, cmd, uuid):
        """
        The formatCmd method takes a single CLI command and runs it against the UUID of a network device in Cisco DNA
        Center.  It converts the command and the UUID into a dict stored in the __cmds attribute and returns __cmds'
        value.
        :param cmd: A CLI command.
            type: str
            default: none
            required: yes
        :param uuid: A network device UUID.
            type: str
            default: none
            required: yes
        :return: dict
        """
        c = [cmd]
        u = [uuid]
        cmds = {'commands': c, 'deviceUuids': u}
        self.__cmds = json.dumps(cmds)
        return self.__cmds

    # end format_cmd()

    def format_cmds(self, cmd_list, uuid_list):
        """
        The format_cmds method accepts a list of CLI commands to run against a list of UUIDs for the target network
        devices in Cisco DNA Center. It converts the two lists into a dict stored in the __cmds attribute and returns
        __cmds' value.
        :param cmd_list: A list of CLI commands.
            type: list of str
            default: none
            required: yes
        :param uuid_list: A list of network device UUIDs.
            type: list of str
            default: none
            required: yes
        :return:
        """
        cmds = {'commands': cmd_list, 'deviceUuids': uuid_list}
        self.__cmds = json.dumps(cmds)
        return self.__cmds

    # end format_cmds()

    def run(self):
        """
        Method run instructs Cisco DNAC to execute the command set stored in the CommandRunner object.  It does not
        wait for the task to complete on Cisco DNA Center.  It does, however, create a new Task object, saves it in
        the __task attribute, checks the task, and then returns the task's status.  See the task.py module for
        valid task states.  When using this function, the programmer must handle task monitoring.
        :return: str
        """
        url = self.dnac.url + self.resource
        results, status = self.crud.post(url,
                                         headers=self.dnac.hdrs,
                                         body=self.__cmds,
                                         verify=self.verify,
                                         timeout=self.timeout)
        if status != ACCEPTED:
            raise DnacApiError(MODULE, 'run', REQUEST_NOT_ACCEPTED, url,
                               ACCEPTED, status, ERROR_MSGS[status],
                               str(results))
        task_id = results['response']['taskId']
        self.__task = Task(self.dnac, task_id)
        return self.__task.get_task_results()

    # end run()

    def run_sync(self, wait=3):
        """
        runSync issues the commands set in the CommandRunner and waits for their completion.  It performs this action
        by creating a Task object and then checks the task's state periodically according to the wait time (seconds)
        passed as an argument. If no wait time is given, it checks every three seconds.

        When the task finishes, the Task object will have also loaded the task's results, which can be immediately
        accessed via the CommandRunner instance (cmd.task.file.results) or from the function's return value
        (results = cmd.runSync()).

        :param wait: The time to wait before checking the results.
            type: int
            default: 3
            required: no
        :return: list
        """
        url = self.dnac.url + self.resource
        results, status = self.crud.post(url,
                                         headers=self.dnac.hdrs,
                                         body=self.__cmds,
                                         verify=self.verify,
                                         timeout=self.timeout)
        if status != ACCEPTED:
            DnacApiError(MODULE, 'run', REQUEST_NOT_ACCEPTED, url,
                         ACCEPTED, status, ERROR_MSGS[status], str(results))
        task_id = results['response']['taskId']
        self.__task = Task(self.dnac, task_id)
        self.__task.get_task_results()
        while self.__task.progress == TASK_CREATION:
            time.sleep(wait)
            self.__task.get_task_results()
        return self.__task.file.results

    # end runSync()

# end class CommandRunner()


