
from dnac.task import Task

MODULE = 'device_archive_task.py'


class DeviceArchiveTask(Task):

    def __init__(self,
                 dnac,
                 id,
                 verify=False,
                 timeout=5):
        super(DeviceArchiveTask, self).__init__(dnac,
                                                id=id,
                                                verify=verify,
                                                timeout=timeout)

# end __init__()

# end class Task()


if __name__ == '__main__':
    pass
