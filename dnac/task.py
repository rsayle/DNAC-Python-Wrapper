
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

MODULE = 'task.py'

#
# task behavior has changed in 1.2.10
# templates now use tasks to push CLI templates
# consider splitting task into subclasses - CommandRunnerTask and TemplateTask
#

TASK_RESOURCE_PATH = {
                      '1.2.8': '/api/v1/task',
                      '1.2.10': '/api/v1/task'
                     }

# task states
TASK_EMPTY = ''
TASK_CREATION = 'CLI Runner request creation'


class Task(DnacApi):
    """
    The Task class manages a task running on Cisco DNA Center.  Tasks run
    asynchronously on Cisco DNAC.  In other words, although a task is
    created, its results may not immediately be available.  Cisco DNA Center
    provides a task ID for checking a task's status, and this object stores
    it in its __id attribute.

    Task does not wait for a task running on Cisco DNAC to finish.  Instead,
    it returns the task's current state contained in the response's
    "progress" field.  Cisco DNAC provides two states: either the task is
    being created or it has finished.  During creation, Cisco DNAC sets
    progress to "CLI Runner request creation", and when it's done, progress
    is a string that can be converted to a dict that will look like:
    {fileId: <uuid>}.
    
    The task.py module defines two constants that can be used for
    monitoring a task with check_task().  Use TASK_EMPTY to see if a task
    has been created, and use TASK_CREATION to detect that Cisco DNA Center
    is preparing a task to run.  There is no constant for task completion.

    When a task has completed, Cisco DNA Center stores the results in a file
    and provides the file's ID as the results of making an API call to
    the task.  Subsequently, when using this class' check_task() method,
    if the task has completed, Task creates a File instance using
    the file ID returned.  Task then saves the File object as its
    __file attribute.  This makes it easy for programmers to
    quickly and easily retrieve the actual results to be parsed.

    Attributes:
        id: The task's UUID in Cisco DNA Center.
            type: str
            default: none
            scope: protected
        progress: The task's current running state.
            type: str
            default: none
            scope: protected
        file: A File object containing the task's results.
            type: File object
            default: none
            scope: protected
        file_id: The UUID of the file with the task's results.
            type: str
            default: none
            scope: protected

    Usage:
        d = Dnac()
        task = Task(d, a_task_id)
        task.check_task()
        results = task.file.get_results()
    """

    def __init__(self,
                 dnac,
                 id,
                 verify=False,
                 timeout=5):
        """
        __init__ makes a new Task object.  An empty task object may be
        created by only passing a Dnac object and the task's UUID.
        The Task instance sets its name as "task_<id>" and the URL for
        querying the task's progress.

        Parameters:
            dnac: A reference to the containing Dnac object.
                type: Dnac object
                default: none
                required: yes
            id: The UUID of the task running on Cisco DNAC. The new object
                sets its name and url based on id's value:
                     name = "task_<id>"
                     url = "dnac.url/self.resource/<id>"
                type: str
                default: none
                required: yes
            verify: A flag used to check Cisco DNAC's certificate.
                type: boolean
                default: False
                required: no
            timeout: The number of seconds to wait for Cisco DNAC's response.
                type: int
                default: 5
                required: no

        Return Values:
            Task object: a new Task object.

        Usage:
            d = Dnac()
            id = <task ID from Cisco DNAC>
            task = Task(d, a_task_id)
            task.check_task()
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
        self.__progress = TASK_EMPTY
        self.__file = None
        self.__file_id = ''
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
                TASK_EMPTY: no task has been created in Cisco DNAC
                TASK_CREATION: Cisco DNAC is preparing the task to run
                <progress>: a string formatted as "{fileId: <id>}".
                            Use json.loads to convert it to a dict.

        Usage:
            d = Dnac()
            task = Task(d, a_task_id)
            task.progress
        """
        return self.__progress

# end progress getter

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

    def check_task(self):
        """
        Class method check_task issues an API call to Cisco DNA Center and
        provides the task's results.

        If the task completed its work on Cisco DNAC, this function sets the
        __file_id value to the file's UUID on Cisco DNAC, and it
        creates a new File object using the UUID to that the actual
        results may easily be queried from this object.  The results get
        saved in __file.

        Parameters:
            none

        Return Values:
            str: The task's results identifier, a file UUID on Cisco DNAC.

        Usage:
            d = Dnac()
            task = Task(d, a_task_id)
            task.check_task()
        """
        url = self.dnac.url + self.resource + ('/%s' % self.id)
        results, status = self.crud.get(url,
                                        headers=self.dnac.hdrs,
                                        verify=self.verify,
                                        timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, 'check_task', REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(results)
                              )
        self.__progress = results['response']['progress']
        if self.__progress != TASK_CREATION:
            # task completed - get the fileId in the progress dict
            self.__progress = json.loads(self.__progress)
            self.__file_id = self.__progress['fileId']
            # create the task results
            self.__file = File(self.dnac, self.__file_id)
            # retrieve the results, which are automatically saved in
            # File' __results attribute
            self.__file.get_results()
        return self.__progress
                  
# end check_task()

# end class Task()


if __name__ == '__main__':

    from dnac.dnac import Dnac

    d = Dnac()

    t = Task(d, 'e749f5ce-ef1c-473f-bee3-aa370411975b')

    print('Task:')
    print()
    print('  dnac             = ' + str(type(t.dnac)))
    print('  name             = ' + t.name)
    print('  id               = ' + t.id)
    print('  verify           = ' + str(t.verify))
    print('  timeout          = ' + str(t.timeout))
    print('  file_id  = ' + t.file_id)
    print('  file     = ' + str(t.file))
    print()
    print('Checking task e749f5ce-ef1c-473f-bee3-aa370411975b...')
    print()
    
    progress = t.check_task()

    print('Task: unit test complete.')
    print()

