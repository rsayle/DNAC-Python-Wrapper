from dnac.task import Task
from dnac.file import File
import json

MODULE = 'commandrunner_task.py'

NO_FILE = None
NO_FILE_ID = ''


class CommandRunnerTask(Task):

    def __init__(self,
                 dnac,
                 id,
                 verify=False,
                 timeout=5):
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
        Get method file returns the File object associated
        with the task referenced by this object.  If the task has not
        finished, None is returned.

        Rather than using this method, users are encouraged to directly
        access the File object and call its getResults method,
        which returns a list with the task's output.

        Parameters:
            none

        Return Values:
            str: The task's resource path.

        Usage:
            d = Dnac()
            task = Task(d, a_task_id)
            task.check_task()
            results = task.results
        """
        return self.__file

# end file getter

    @property
    def file_id(self):
        """
        The file_id get method retrieves the object current value
        for __file_id, which can be used to generate a new
        File object.

        Parameters:
            none

        Return Values:
            str: The UUID to the task's results, a file on Cisco DNAC.

        Usage:
            d = Dnac()
            task = Task(d, a_task_id)
            task.check_task()
            results = File(d, task.file_id)
        """
        return self.__file_id

# end file_id getter

    def get_task_results(self, wait=3):
        super(CommandRunnerTask, self).get_task_results(wait)
        # task completed - get the fileId in the progress dict
        self.__progress = json.loads(self.__progress)
        self.__file_id = self.__progress['fileId']
        # create the task results
        self.__file = File(self.dnac, self.__file_id)
        # retrieve the results, which are automatically saved in
        # File's __results attribute
        self.__file.get_results()
        return self.task_results
                  
# end get_task_results()

# end class CommandrunnerTask()


if __name__ == '__main__':
    pass

