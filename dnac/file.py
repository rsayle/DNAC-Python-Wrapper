
from dnac import DnacError, \
                 SUPPORTED_DNAC_VERSIONS, \
                 UNSUPPORTED_DNAC_VERSION
from dnac.dnacapi import DnacApi, \
                         DnacApiError
from dnac.crud import OK, \
                      REQUEST_NOT_OK, \
                      ERROR_MSGS

MODULE = 'file.py'

FILE_RESOURCE_PATH = {
                      '1.2.8': '/api/v1/file',
                      '1.2.10': '/dna/intent/api/v1/file'
                     }


class File(DnacApi):
    """
    Class File gets and stores the results from a task run on
    Cisco DNA Center.  Cisco DNAC delivers the results from a file whose
    contents are a string, which this class converts to a list.

    Like all entities in Cisco DNAC, files are referenced via a UUID.  Set
    the file UUID either during initialization before attempting to
    retrieve the file's data with the get_results() method.

    Although this class may be instantiated independently, the Task
    class automatically creates and stores an instance of File to
    simplify handling tasks.

    File inherits from class DnacApi for its base attributes and
    for inclusion in a Dnac object's api store.

    Usage:
        d = Dnac()
        task = Task(d, 'aTask')
        task.checkTask()
        # task.file below is a File object
        results = task.file.get_results()
    """

    def __init__(self,
                 dnac,
                 id,
                 verify=False,
                 timeout=5):
        """
        Class method __init__ creates a new File instance.  When
        making a File object, pass it a Dnac object and the UUID
        of the file in Cisco DNAC that this object represents.

        Parameters:
            dnac: A reference to the containing Dnac object.
                type: Dnac object
                default: none
                required: yes
            id: The UUID of the file in Cisco DNAC this object represents.
                If included as part of calling __init__, the new object sets
                its name and url based on id's value:
                    name = 'task_<id>'
                    url = 'dnac.url/self.respath/<id>'
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
            File object: a new File instance.

        Usage:
            d = Dnac()
            id = '<file UUID>'
            results = File(d, id)
        """
        # check Cisco DNA Center's version and set the resource path
        if dnac.version in SUPPORTED_DNAC_VERSIONS:
            path = FILE_RESOURCE_PATH[dnac.version]
        else:
            raise DnacError(
                '__init__: %s: %s' %
                (UNSUPPORTED_DNAC_VERSION, dnac.version)
                            )
        # setup the attributes
        self.__id = id  # use the fileId in the task's progress
        self.__results = []  # raw data in case further processing needed
        super(File, self).__init__(dnac,
                                   ('file_%s' % self.__id),
                                   resource=path,
                                   verify=verify,
                                   timeout=timeout)

# end __init__()

    @property
    def id(self):
        """
        Get method id returns __id, the UUID of the file on Cisco DNA Center
        that contains the task's results.

        Parameters:
            none

        Return Values:
            str: The file's UUID with the task results.

        Usage:
            d = Dnac()
            task = Task(d, 'aTask')
            task.checkTask()
            # task.file below is a File object
            id = task.file.id
        """
        return self.__id

# end id getter

    @property
    def results(self):
        """
        Get method results returns __results, a list containing the
        task's results stored in the file.

        Parameters:
            none

        Return Values:
            list: The task's results given in the file.

        Usage:
            d = Dnac()
            task = Task(d, 'aTask')
            task.checkTask()
            # task.file below is a File object
            for result in task.file.results
                # each result will be a dict
                pprint.PrettyPrint(result)
        """
        return self.__results

# end results getter

    def get_results(self):
        """
        get_results makes an API call to Cisco DNA Center and retrieves the
        task results contained in the file identified by this object's
        __file_id, i.e. the file's UUID.

        Parameters:
            none

        Return Values:
            list: The file's or task result's data.

        Usage:
            d = Dnac()
            task = Task(d, 'aTask')
            task.checkTask()
            # task.file below is a File object
            results = task.file.get_results()
        """
        url = self.dnac.url + self.resource + ('/%s' % self.__id)
        results, status = self.crud.get(url,
                                        headers=self.dnac.hdrs,
                                        verify=self.verify,
                                        timeout=self.timeout)
        if status != OK:
            raise DnacApiError(
                MODULE, 'get_results', REQUEST_NOT_OK, url,
                OK, status, ERROR_MSGS[status], str(results)
                              )
        self.__results = results
        return self.__results

# end get_results()

# end class File()


if __name__ == '__main__':

    from dnac.dnac import Dnac

    d = Dnac()

    # remember to update the file ID before running test
    r = File(d, '6e9e1261-f088-4e9c-b2a0-8f006c682694')
    r.get_results()

    print('File:')
    print()
    print('  dnac    = ' + str(r.dnac))
    print('  name    = ' + r.name)
    print('  id      = ' + r.id)
    print('  verify  = ' + str(r.verify))
    print('  timeout = ' + str(r.timeout))
    print('  results = ' + str(r.results))
    print()
    print('File: unit test complete.')
    print()

