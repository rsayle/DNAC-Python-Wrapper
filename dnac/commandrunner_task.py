from dnac.task import Task
from dnac.file import File
import json

MODULE = 'commandrunner_task.py'

# globals

NO_FILE = None
NO_FILE_ID = ''


class CommandRunnerTask(Task):
    """
    CommandRunnerTask extends the Task class by providing the means to monitor the task and return the results that
    Cisco DNAC stores in a file.  A CommandRunner instance automatically manages the use of a CommandRunnerTask.
    It is unnecessary for users to create objects from this class.

    ROADMAP: This class may eventually be generalized to any task that produces a file for the task's results.

    Usage:
            d = Dnac()
            task = CommandRunnerTask(d, a_task_id)
            pprint.PrettyPrinter(task.get_task_results())
    """
    def __init__(self,
                 dnac,
                 id,
                 verify=False,
                 timeout=5):
        """
        Instantiates a new CommandRunnerTask object.
        :param dnac: A reference to the master Dnac object.
            type: Dnac object
            required: yes
            default: None
        :param id: The object's UUID from Cisco DNA Center.
            type: str
            required: yes
            default: None
        :param verify: A flag that determines whether or not Cisco DNAC's certificate should be authenticated.
            type: bool
            required: no
            default: None
        :param timeout: The number of seconds to wait for a response from Cisco DNAC.
            type: int
            required: no
            default: 5
        """
        super(CommandRunnerTask, self).__init__(dnac,
                                                'commandrunner_task_%s' % id,
                                                verify=verify,
                                                timeout=timeout)
        self.__file = NO_FILE
        self.__file_id = NO_FILE_ID

    # end __init__()

    @property
    def file(self):
        """
        Get method file returns the File object associated with the task referenced by this object.  If the task has not
        finished, None is returned.
        :return: File object
        """
        return self.__file

    # end file getter

    @property
    def file_id(self):
        """
        The file_id get method retrieves the object current value for __file_id, which can be used to generate a new
        File object.
        :return: str
        """
        return self.__file_id

    # end file_id getter

    def get_task_results(self, wait=3):
        """
        Retrieves the command runner task's results from the file where Cisco DNAC stores the CLI output."
        :param wait: Number of seconds to wait for Cisco DNAC to finish the command.
            type: int
            required: no
            default: 3
        :return: dict
        """
        # run the CLI command
        super(CommandRunnerTask, self).get_task_results(wait)
        # task completed - get the fileId in the progress dict
        self.__progress = json.loads(self.__progress)
        self.__file_id = self.__progress['fileId']
        # create the task results
        self.__file = File(self.dnac, self.__file_id)
        # retrieve the results, which are automatically saved in
        # File's __results attribute
        self.__file.get_results()
        return self.__task_results
                  
    # end get_task_results()

# end class CommandrunnerTask()

