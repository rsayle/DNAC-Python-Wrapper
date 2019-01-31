#/usr/bin/env python

from dnac import DnacError, \
                 SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION
from dnacapi import DnacApi, \
                    DnacApiError
from crud import OK, \
                 REQUEST_NOT_OK, \
                 ERROR_MSGS

MODULE="taskresults.py"

class TaskResults(DnacApi):
    '''
    Class TaskResults gets and stores the results from a task run on
    Cisco DNA Center.  Cisco DNAC delivers the results from a file whose 
    contents are a string, which this class converts to a list.
    
    Like all entities in Cisco DNAC, files are referenced via a UUID.  Set
    the file UUID either during initialization or by using the class' id
    set method before attempting to retrieve the file's data with the
    getResults() method.

    Although this class may be instantiated independently, the Task
    class automatically creates and stores an instance of TaskResults to
    simplify handling tasks.

    TaskResults inherits from class DnacApi for its base attributes and
    for inclusion in a Dnac object's api store.

    Usage:
        d = Dnac()
        task = Task(d, "aTask")
        task.checkTask()
        # task.taskResults below is a TaskResults object
        results = task.taskResults.getResults()
    '''

    def __init__(self,
                 dnac,
                 name,
                 id = "",
                 verify=False,
                 timeout=5):
        '''
        Class method __init__ creates a new TaskResults instance.  When
        making a TaskResults object, pass it a Dnac object and give it
        a user-friendly name for retrieving it from Dnac's api store,
        Dnac.api{}.  Optionally, pass it the UUID of the file in Cisco DNAC
        that this object represents.

        Parameters:
            dnac: A reference to the containing Dnac object.
                type: Dnac object
                default: None
                required: Yes
            name: A user friendly name for find this object in a Dnac
                  instance.
                type: str
                default: None
                required: Yes
            id: The UUID of the file in Cisco DNAC this object represents.
                If included as part of calling __init__, the new object sets
                its name and url based on id's value:
                    name = "task_<id>"
                    url = "dnac.url/self.respath/<id>"
                type: str
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
            TaskResults object: a new TaskResults instance.

        Usage:
            d = Dnac()
            name = "task_"
            id = "<file UUID>"
            emptyResults = TaskResults(d, name)
            realResults = TaskResults(d, name, id)
        '''

        # check Cisco DNA Center's version and set the resourece path
        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            path  = "/api/v1/file"
        else:
            raise DnacError(
                "__init__: %s: %s" %
                (UNSUPPORTED_DNAC_VERSION, dnac.version)
                            )
        # setup the attributes
        self.__id = id # use the fileId in the task's progress
        self.__results = [] # raw data in case further processing needed
        super(TaskResults, self).__init__(dnac,
                                          name,
                                          resource=path,
                                          verify=verify,
                                          timeout=timeout)

## end __init__()

    @property
    def id(self):
        '''
        Get method id returns __id, the UUID of the file on Cisco DNA Center
        that contains the task's results.

        Parameters:
            None

        Return Values:
            str: The file's UUID with the task results.

        Usage:
            d = Dnac()
            task = Task(d, "aTask")
            task.checkTask()
            # task.taskResults below is a TaskResults object
            id = task.taskResults.id
        '''
        return self.__id

## end id getter

    @id.setter
    def id(self, id):
        '''
        Set method id changes the value of the object's __id based on
        the value passed.  In addition, it modifies the objects name
        and url to include the id value change.

        Parameters:
            id: str
            default: None
            required: Yes

        Return Values:
            None

        Usage:
            d = Dnac()
            task = Task(d, "aTask")
            id = task.checkTask()
            # task.taskResults below is a TaskResults object
            # checkTask() would have already set the id, but just for fun:
            task.taskResults.id = id
        '''
        self.__id = id
        self.name = "results_" + self.__id

## end id setter

    @property
    def results(self):
        '''
        Get method results returns __results, a list containing the
        task's results.

        Parameters:
            None

        Return Values:
            list: The task's results.

        Usage:
            d = Dnac()
            task = Task(d, "aTask")
            task.checkTask()
            # task.taskResults below is a TaskResults object
            for result in task.taskResults.results
                # each result will be a dict
                print str(result)
        '''
        return self.__results

## end results getter

    @results.setter
    def results(self, results):
        '''
        Set method results changes __results to the value passed.

        Parameters:
            results: list
            default: None
            required: Yes

        Return Values:
            None

        Usage:
            d = Dnac()
            task = Task(d, "aTask")
            task.checkTask()
            newTask = Task(d, "aNewTask")
            # Not a realistic example but here it is anyway
            # Remember: taskResults are TaskResults objects in Task()
            newTask.taskResults.results = task.taskResults.results
        '''
        self.__results = results

## end id setter

    def getResults(self):
        '''
        getResults makes an API call to Cisco DNA Center and retrieves the
        task results contained in the file identified by this object's
        __taskResultsId, i.e. the file's UUID.

        Parameters:
            None

        Return Values:
            list: The file's or task result's data.

        Usage:
            d = Dnac()
            task = Task(d, "aTask")
            task.checkTask()
            # task.taskResults below is a TaskResults object
            results = task.TaskResults.getResults()
        '''
        url = self.dnac.url + self.resource + ("/%s" % self.id)
        results, status = self.crud.get(url,
                                        headers=self.dnac.hdrs,
                                        verify=self.verify,
                                        timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, "getResults", REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(results)
                              )
        self.__results = results
        return self.__results

## end getResults()

## end class TaskResults()

if  __name__ == '__main__':

    from dnac import Dnac

    d = Dnac()

    r = TaskResults(d, "results", \
                    id="6e9e1261-f088-4e9c-b2a0-8f006c682694")

    print "TaskResults:"
    print
    print "  dnac    = " + str(r.dnac)
    print "  name    = " + r.name
    print "  id      = " + r.id
    print "  results = " + str(r.results)
    print "  verify  = " + str(r.verify)
    print "  timeout = " + str(r.timeout)
    print
    print "Setting the TaskResults id..."

    r.id = "dbb3426a-f855-4b65-b022-d4b742d11254"

    print
    print "  dnac    = " + str(r.dnac)
    print "  name    = " + r.name
    print "  id      = " + r.id
    print "  results = " + str(r.results)
    print "  verify  = " + str(r.verify)
    print "  timeout = " + str(r.timeout)
    print
    print "Getting the results from " + r.id + "..."
    print

    res = r.getResults()

    print
    print "  dnac    = " + str(r.dnac)
    print "  name    = " + r.name
    print "  id      = " + r.id
    print "  results = " + str(type(r.results))
    print "  results = " + str(r.results)
    print "  res     = " + str(type(res))
    print "  res     = " + str(res)
    print "  verify  = " + str(r.verify)
    print "  timeout = " + str(r.timeout)
    print
    print "TaskResults: unit test complete."
    print

