
from dnac import DnacError, \
                 SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION
from dnac.dnacapi import DnacApi, \
                         DnacApiError
from dnac.crud import OK, \
                      REQUEST_NOT_OK, \
                      ERROR_MSGS
import time

# globals

MODULE = 'task.py'

TASK_RESOURCE_PATH = {
                      '1.2.8': '/api/v1/task',
                      '1.2.10': '/api/v1/task',
                      '1.3.0.2': '/api/v1/task',
                      '1.3.0.3': '/api/v1/task',
                      '1.3.1.3': '/api/v1/task',
                      '1.3.1.4': '/dna/intent/api/v1/task'
}

PROGRESS_KEY = 'progress'
END_TIME_KEY = 'endTime'
START_TIME_KEY = 'startTime'
IS_ERROR_KEY = 'isError'
FAILURE_REASON_KEY = 'failureReason'

# error conditions

NO_PROGRESS = ''
NO_START_TIME = -1
NO_END_TIME = -1
NO_IS_ERROR = ''
NO_FAILURE_REASON = ''

class Task(DnacApi):
    """
    The Task class manages and monitors Cisco DNA Center jobs.  Many actions Cisco DNAC performs happen asychronously
    and are scheduled using a Task, for example, running show commands (CommandRunner) or applying templates (Template).
    A task's state and the format of its results varies by job type.  Consequently, it may be necessary to subtype
    Task and extend its behavior.  The base class monitors itself by looking for an endTime parameter in its results.
    Until endTime appears, the Task remains in some form of a running state that is usually reflected in the progress
    field.  Upon job completion, Task populates the results.  If the Task's isError field indicates a problem
    (isError == True), then check the progress and failureReason for fault indicators.  If not, then the Task results
    should be loaded into the __task attribute.  This last action depends upon the task subtype; for example, a
    CommandRunner task points to a file with the command's output, but a Template job simply ends in success or failure.

    Usage:
        d = Dnac()
        t = Task(d, <task_uuid>)
        results = t.getTaskResults()
    """
    def __init__(self,
                 dnac,
                 id,
                 verify=False,
                 timeout=5):
        # check Cisco DNA Center's version and set the resource path
        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            path = TASK_RESOURCE_PATH[dnac.version]
        else:
            raise DnacError('__init__: %s: %s' % (UNSUPPORTED_DNAC_VERSION, dnac.version))
        # setup the attributes
        self.__task = {}
        self.__id = id
        super(Task, self).__init__(dnac,
                                   ('task_%s' % self.__id),
                                   resource=path,
                                   verify=verify,
                                   timeout=timeout)

    # end __init__()

    @property
    def id(self):
        """
        Provides the task's UUID.
        :return: str
        """
        return self.__id

    # end id getter

    @property 
    def progress(self):
        """
        Gives the task's current run state.
        :return: str
        """
        if PROGRESS_KEY in self.__task.keys():
            return self.__task[PROGRESS_KEY]
        else:
            return NO_PROGRESS

    # end progress getter

    @property
    def start_time(self):
        """
        Indicates when the task started using epoch time.
        :return: int
        """
        if START_TIME_KEY in self.__task.keys():
            return self.__task[START_TIME_KEY]
        else:
            return NO_START_TIME

    # end start_time getter

    @property
    def end_time(self):
        """
        Indicates when the task ended using epoch time.
        :return: int
        """
        if END_TIME_KEY in self.__task.keys():
            return self.__task[END_TIME_KEY]
        else:
            return NO_END_TIME

    # end end_time getter

    @property
    def is_error(self):
        """
        Returns the task's error state.  True, if error; otherwise, false, if succeeded.
        :return: bool
        """
        if IS_ERROR_KEY in self.__task.keys():
            return self.__task[IS_ERROR_KEY]
        else:
            return NO_IS_ERROR

    # end is_error getter

    @property
    def failure_reason(self):
        """
        If the task ended with an error, this method provides the reason it failed.
        :return: str
        """
        if FAILURE_REASON_KEY in self.__task.keys():
            return self.__task[FAILURE_REASON_KEY]
        else:
            return NO_FAILURE_REASON

    # end failure_reason getter

    def __check_task__(self):
        """
        Hidden method used to retrieve the task results from Cisco DNAC.
        :return: dict
        """
        url = '%s%s/%s' % (self.dnac.url, self.resource, self.id)
        results, status = self.crud.get(url,
                                        headers=self.dnac.hdrs,
                                        verify=self.verify,
                                        timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, '__check_task__', REQUEST_NOT_OK, url, OK, status, ERROR_MSGS[status], str(results)
            )
        self.__task = results['response']
        return self.__task

    # end check_task()

    def get_task_results(self, wait=3):
        """
        Checks for the task's endTime.  If endTime does not exist, then the method waits for the number of seconds
        given and checks again.  If endTime exists, then the results get loaded into the object's __task attribute.
        :param wait: Number of seconds to sleep before checking again.
            type: int
            required: no
            default: 3
        :return: dict
        """
        while END_TIME_KEY not in self.__task.keys():
            time.sleep(wait)
            self.__check_task__()
        return self.__task

    # end get_task_results()

# end class Task()
