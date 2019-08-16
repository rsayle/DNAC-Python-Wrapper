
from dnac import DnacError, \
                 SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION
from dnac.dnacapi import DnacApi, \
                         DnacApiError
from dnac.crud import OK, \
                      REQUEST_NOT_OK, \
                      ERROR_MSGS
import time

MODULE = 'task.py'

TASK_RESOURCE_PATH = {
                      '1.2.8': '/api/v1/task',
                      '1.2.10': '/api/v1/task',
                      '1.3.0.2': '/api/v1/task',
                      '1.3.0.3': '/api/v1/task'
}

NO_PROGRESS = ''
NO_TIME = -1
NO_TASK_RESULTS = {}
NO_FAILURE_REASON = ''
PROGRESS_KEY = 'progress'
END_TIME_KEY = 'endTime'
START_TIME_KEY = 'startTime'
IS_ERROR_KEY = 'isError'
FAILURE_REASON_KEY = 'failureReason'

class Task(DnacApi):
    """
    The Task class manages and monitors Cisco DNA Center jobs.  Many actions Cisco DNAC performs happen asychronously
    and are scheduled using a Task, for example, running show commands (CommandRunner) or applying templates (Template).
    A task's state and the format of its results varies by job type.  Consequently, it may be necessary to subtype
    Task and extend its behavior.  The base class monitors itself by looking for an endTime parameter in its results.
    Until endTime appears, the Task remains in some form of a running state that is usually reflected in the progress
    field.  Upon job completion, Task populates the progress, isError and failureReason as well as the endTime.  If
    the Task's isError field indicates a problem (isError == True), then check the progress and failureReason for
    fault indicators.  If not, then the Task results should be loaded into the taskResults attribute.  This last action
    depends upon the task subtype; for example, a CommandRunner task points to a file with the command's output, but
    a Template job simply ends in success or failure.

    Attributes:
        dnac: A pointer to the Dnac object containing the ConfigArchive instance.
            type: Dnac object
            default: none
            scope: protected
        id: The task's UUID.  It also doubles as the task's name for accessing it in a Dnac.api{}, where the name's
            format is task_<id>.
            type: str
            default: none
            scope: protected
        progress: A textual description of the Task's current state.  The progress value is dependent upon the Task
                  subtype and should not be used to monitor a Task.  Instead, monitor the Task endTime.
            type: str
            default: ''
            scope: protected
        startTime: The epoch time in milliseconds that the Task began.
            type: int
            default: none
            scope: protected
        endTime: The epoch time in milliseconds that the Task completed
            type: int
            default: none
            scope: protected
        isError: Flags whether or not the Task finished with an error.  True if the job experienced an error; False
                 otherwise.
            type: bool
            default: False
            scope: protected
        taskResults: Provides the output of the job's task and is implementation dependent opon the type of Task
                     that was instantiated.
            type: implementation dependent
            default: none
            scope: protected
        failureReason: Gives a reason why a task failed to execute properly.
            type: str
            default: none
            scope: protected
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
        t = Task(d, <task_uuid>)
        results = t.getTaskResults()
    """
    def __init__(self,
                 dnac,
                 id,
                 verify=False,
                 timeout=5):
        """
        The Task class' __init__ method creates a blank Task object.  When creating one, use the task ID provided by
        the Cisco DNAC cluster as the object's ID, which also serves as the basis of its name in the Dnac.api{}.  The
        class uses 'task_<UUID>" as its name.

        Parameters:
            dnac: A reference to the containing Dnac object.
                type: Dnac object
                default: none
                required: yes
            id: The task's UUID as assigned by Dnac.
                type: str
                default: none
                required: yes
            verify: A flag used to check Cisco DNAC's certificate.
                type: boolean
                default: False
                required: no
            timeout: The number of seconds to wait for Cisco DNAC's
                     response.
                type: int
                default: 5
                required: no

        Return Values:
            Task object: The task instance

        Usage:
           d = Dnac()
            t = Task(d, <task_uuid>)
        """
        # check Cisco DNA Center's version and set the resource path
        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            path = TASK_RESOURCE_PATH[dnac.version]
        else:
            raise DnacError(
                '__init__: %s: %s' %
                (UNSUPPORTED_DNAC_VERSION, dnac.version)
                           )
        # setup the attributes
        self.__id = id
        self.__progress = NO_PROGRESS
        self.__start_time = NO_TIME
        self.__end_time = NO_TIME
        self.__is_error = False
        self.__task_results = NO_TASK_RESULTS
        self.__failure_reason = NO_FAILURE_REASON
        super(Task, self).__init__(dnac,
                                   ('task_%s' % self.__id),
                                   resource=path,
                                   verify=verify,
                                   timeout=timeout)

# end __init__()

    @property
    def id(self):
        """
        Get method id returns the value of __id, the task's UUID in Cisco DNAC.

        Parameters:
            none

        Return Values:
            str: The task's UUID.

        Usage:
            d = Dnac()
            task = Task(d, a_task_id)
            print(task.id)
        """
        return self.__id

# end id getter

    @property 
    def progress(self):
        """
        Get method progress returns the value of __progress, which indicates the current state of the running task.
        This attribute is implementation dependent on the task subtype.

        Parameters:
            none

        Return Values:
            str: The task's current state

        Usage:
            d = Dnac()
            task = Task(d, a_task_id)
            task.progress
        """
        return self.__progress

# end progress getter

    @property
    def start_time(self):
        """
        Get method start_time returns the epoch time in milliseconds that the task began.

        Parameters:
            none

        Return Values:
            int: The task's start time in milliseconds of epoch time.

        Usage:
            d = Dnac()
            task = Task(d, a_task_id)
            print(task.start_time)
        """
        return self.__start_time

# end start_time getter

    @property
    def end_time(self):
        """
        Get method end_time returns the epoch time in milliseconds that the task completed.

        Parameters:
            none

        Return Values:
            int: The task's end time in milliseconds of epoch time.

        Usage:
            d = Dnac()
            task = Task(d, a_task_id)
            print(task.end_time)
        """
        return self.__end_time

# end end_time getter

    @property
    def task_results(self):
        """
        The task_results method returns the task's output, which is implementation dependent upon the subtask class.

        Parameters:
            none

        Return Values:
            varies: The task's results.

        Usage:
            d = Dnac()
            task = Task(d, a_task_id)
            print(task.task_results)
        """
        return self.__task_results

# end results getter

    @property
    def is_error(self):
        """
        is_error indicates whether or not the task failed (True) or succeeded (False).

        Parameters:
            none

        Return Values:
            bool: The task's completion error state.

        Usage:
            d = Dnac()
            task = Task(d, a_task_id)
            if task.is_error == False:
                print(task.task_results)
        """
        return self.__is_error

# end is_error getter

    @property
    def failure_reason(self):
        """
        A task's failure_reason provides an error code indicating why a task failed.  The error code is a string that
        depends upon the task subclasses implementation.

        Parameters:
            none

        Return Values:
            str: A description why the task failed.

        Usage:
            d = Dnac()
            task = Task(d, a_task_id)
            if task.is_error == True:
                print(task.failure_reason)
        """
        return self.__failure_reason

# end failure_reason getter

    def __check_task__(self):
        """
        __check_task__ is a hidden method used to make an API call to a Cisco DNAC cluster and monitor its progress.
        The get_task_results method uses this method to process the results provided by the API call.  Users should
        use get_task_results instead of calling this method directly.

        Parameters:
            none

        Return Values:
            dict: the task's raw results as given by Dnac

        Usage:
            Do not call this method directly.  Use get_task_results and override it as necessary.
        """
        url = self.dnac.url + self.resource + ('/%s' % self.id)
        results, status = self.crud.get(url,
                                        headers=self.dnac.hdrs,
                                        verify=self.verify,
                                        timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, '__check_task__', REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(results)
                              )
        self.__task_results = results['response']
        if PROGRESS_KEY in self.__task_results:
            self.__progress = self.__task_results[PROGRESS_KEY]
        if START_TIME_KEY in self.__task_results:
            self.__start_time = self.__task_results[START_TIME_KEY]
        if END_TIME_KEY in self.__task_results:
            self.__end_time = self.__task_results[END_TIME_KEY]
        if IS_ERROR_KEY in self.__task_results:
            self.__is_error = self.__task_results[IS_ERROR_KEY]
        if FAILURE_REASON_KEY in self.__task_results:
            self.__failure_reason = self.__task_results[FAILURE_REASON_KEY]
        return self.__task_results

# end check_task()

    def get_task_results(self, wait=3):
        """
        This class' get_task_results method periodically monitors a task's progress by calling the hidden method,
        __check_task__.  The method loops for the wait time in seconds passed to this function until it detects an
        end time for the task.  Upon completion, it returns the task's results.

        Parameters:
            wait: the time to wait in seconds before checking a task's progress.
                type: int
                default: 3
                required: no

        Return values:
            dict: the task results

        Usage:
            d = Dnac()
            task = Task(d, a_task_id)
            task.get_task_results(wait=5)
            print(task.task_results)
        """
        while END_TIME_KEY not in self.__task_results:
            time.sleep(wait)
            self.__check_task__()
        return self.__task_results

# end get_task_results()

# end class Task()


if __name__ == '__main__':
    pass

