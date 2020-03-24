
from dnac.task import Task

MODULE = 'device_archive_task.py'


class DeviceArchiveTask(Task):
    """
    The DeviceArchiveTask is a subclass of Task.  As of this version of the wrapper package, DeviceArchiveTask does
    not modify Task's behavior.  This class exists for stronger class typing and in the event that archiving tasks
    behavior changes and needs additional processing beyond what Task offers.

    When a DeviceArchive instance performs CRUD operations for a device, e.g. create a new version, it creates a
    new DeviceArchiveTask to handle monitoring the transaction and reporting its results.

    Attributes:
        dnac: A pointer to the Dnac object containing the ConfigArchive instance.
            type: Dnac object
            default: none
            scope: protected
        name: A user-friendly name for accessing the ConfigArchive object in a Dnac.api{}.
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
        device_archive_task = DeviceArchiveTask(d, <task_uuid>)
    """

    def __init__(self,
                 dnac,
                 id,
                 verify=False,
                 timeout=5):
        """
        The __init__ method creates a new device archive task instance.  Use the task ID returned by Cisco DNA Center
        as the id for the new object.
        :param dnac: A reference to the containing Dnac object.
            type: Dnac object
            default: none
            required: yes
        :param id: The UUID for monitoring the task in Cisco DNAC.
            type: str
            default: none
            required: yes
        :param verify: A flag used to check Cisco DNAC's certificate.
            type: boolean
            default: False
            required: no
        :param timeout: The number of seconds to wait for Cisco DNAC's response.
            type: int
            default: 5
            required: no
        """
        super(DeviceArchiveTask, self).__init__(dnac,
                                                id=id,
                                                verify=verify,
                                                timeout=timeout)

    # end __init__()

# end class Task()

