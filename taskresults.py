#/usr/bin/env python

from dnacapi import DnacApi
import requests
import json

class TaskResults(DnacApi):
    '''
    Class TaskResults gets and stores the results from a task run on
    Cisco DNA Center.  DNAC delivers the results from a file whose contents
    are a string, which this class converts to a list.
    
    Like all entities in DNAC, files are referenced via a UUID.  Set the
    file UUID either during initialization or by using the class' id
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
                 dnac, \
                 name, \
                 id = "", \
                 requestFilter="", \
                 verify=False, \
                 timeout=5):
        '''
        Class method __init__ creates a new TaskResults instance.  When
        making a TaskResults object, pass it a Dnac object and give it
        a user-friendly name for retrieving it from Dnac's api store,
        Dnac.api{}.  Optionally, pass it the UUID of the file in DNAC
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
            id: The UUID of the file in DNAC this object represents.  If
                included as part of calling __init__, the new object sets
                its name and url based on id's value:
                    name = "task_<id>"
                    url = "dnac.url/self.respath/<id>"
                type: str
                default: None
                required: No
            requestFilter: An expression for filtering DNAC's response.
                type: str
                default: None
                required: No
            verify: A flag used to check DNAC's certificate.
                type: boolean
                default: False
                required: No
            timeout: The number of seconds to wait for DNAC's response.
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
        if dnac.version <= "1.2.8":
            self.__respath = "/api/v1/file"
        else:
            # rewrite this to throw an exception
            print "Unsupported version of DNAC: " + dnac.version

        self.__id = id # use the fileId in the task's progress
        self.__results = []
        self.__url = self.__respath + "/" + self.__id

        super(TaskResults, self).__init__(dnac, \
                                          name, \
                                          resourcePath=self.__respath, \
                                          requestFilter=requestFilter, \
                                          verify=verify, \
                                          timeout=timeout)

## end __init__()

    @property
    def id(self):
        '''
        Get method id returns __id, the UUID of the file on DNA Center
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
        self.__url = self.respath + "/" + self.__id

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

    @property
    def url(self):
        '''
        Get method url returns the object's __url value.

        Parameters:
            None

        Return Values:
            url: A url that can be used to retrieve the task results.

        Usage:
            d = Dnac()
            task = Task(d, "aTask")
            task.checkTask()
            # task.taskResults below is a TaskResults object
            url = task.taskResults.url
        '''
        return self.__url

## end url getter

    @url.setter
    def url(self, url):
        '''
        Set method url changes the object's __url attribute to the given
        value.

        Parameters:
            url: str
            default: None
            required: Yes

        Return Values:
            None

        Usage:
            d = Dnac()
            task = Task(d, "aTask")
            url = "/a/url/to/a/fileId"
            # Not a realistic example but here it is anyway
            # Remember: taskResults are TaskResults objects in Task()
            task.taskResults.url = url
        '''
        self.__url = url

## end id setter

    def getResults(self):
        '''
        getResults makes an API call to DNA Center and retrieves the task
        results contained in the file identified by this object's
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
        url = self.dnac.url + self.url + self.filter
        print url
        hdrs = self.dnac.hdrs
        resp = requests.request("GET", \
                                url, \
                                headers=hdrs, \
                                verify=self.verify, \
                                timeout=self.timeout)
        if resp.status_code != requests.codes.ok:
            print "Failed to get results from file " + \
                  self.id + \
                  " with status code: " + \
                  str(resp.status_code)
        else:
            self.__results = json.loads(resp.text)
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
    print "  url     = " + r.url
    print "  results = " + str(r.results)
    print "  respath = " + r.respath
    print "  filter  = " + r.filter
    print "  verify  = " + str(r.verify)
    print "  timeout = " + str(r.timeout)
    print
    print "Setting the TaskResults id..."

    r.id = "dbb3426a-f855-4b65-b022-d4b742d11254"

    print
    print "  dnac    = " + str(r.dnac)
    print "  name    = " + r.name
    print "  id      = " + r.id
    print "  url     = " + r.url
    print "  results = " + str(r.results)
    print "  respath = " + r.respath
    print "  filter  = " + r.filter
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
    print "  url     = " + r.url
    print "  results = " + str(type(r.results))
    print "  results = " + str(r.results)
    print "  res     = " + str(type(res))
    print "  res     = " + str(res)
    print "  respath = " + r.respath
    print "  filter  = " + r.filter
    print "  verify  = " + str(r.verify)
    print "  timeout = " + str(r.timeout)
    print


