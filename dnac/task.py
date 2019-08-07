
from dnac import DnacError, \
                 SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION
from dnac.dnacapi import DnacApi, \
                         DnacApiError
from dnac.crud import OK, \
                      REQUEST_NOT_OK, \
                      ERROR_MSGS
from dnac.file import File
import json
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

    def __init__(self,
                 dnac,
                 id,
                 verify=False,
                 timeout=5):
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
            task.id
        """
        return self.__id

# end id getter

    @property 
    def progress(self):
        """
        Get method progress returns the value of __progress, which 
        indicates the current stat of the running task.

        Parameters:
            none

        Return Values:
            str: The task's current state:

        Usage:
            d = Dnac()
            task = Task(d, a_task_id)
            task.progress
        """
        return self.__progress

# end progress getter

    @property
    def start_time(self):
        return self.__start_time

# end start_time getter

    @property
    def end_time(self):
        return self.__end_time

# end end_time getter

    @property
    def task_results(self):
        return self.__task_results

# end results getter

    @property
    def is_error(self):
        return self.__is_error

# end is_error getter

    @property
    def failure_reason(self):
        return self.__failure_reason

# end failure_reason getter

    def __check_task__(self):
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
            self.__is_error = self.__task_results[FAILURE_REASON_KEY]
        return self.__task_results

# end check_task()

    def get_task_results(self, wait=3):
        if END_TIME_KEY not in self.task_results:
            time.sleep(wait)
            self.__check_task__()
            self.get_task_results(wait=wait)
        return self.__task_results

# end get_task_results()

# end class Task()


if __name__ == '__main__':
    pass

