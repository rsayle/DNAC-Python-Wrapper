from datetime import datetime
import time

# globals

MODULE = 'timestamp.py'

NO_TIME = -1
GET_CURRENT_TIME = 0

class TimeStamp(object):
    """
    The TimeStamp class takes the system's time in UTC and converts it to epoch time given in milliseconds.
    Remember that the TimeStamp's value is set when it is created and is not updated whenever it is referenced.
    Future enhancements to this class may change this behavior if needed.

    Attributes:
        timestamp: Current system epoch time in milliseconds
            type: int
            default: current epoch time
            scope: protected

    Usage:
        time = TimeStamp()
        print(time)
    """

    def __init__(self, time=GET_CURRENT_TIME):
        """
        The TimeStamp's __init__ method sets its value to the current number of milliseconds in epoch time.
        :param time: Epoch time with which to initialize the new object.
            type: int
            required: no
            default: retrieves the current time
        """
        if time == GET_CURRENT_TIME:
            self.get_current_time()
        else:
            self.__timestamp = int(time)

    # end __init__

    def __str__(self):
        """
        TimeStamp class' __str__ function converts its timestamp attribute, an int, into a string.
        :return: The epoch time in milliseconds when the TimeStamp object was created.
        """

    # end __str__

    @property
    def timestamp(self):
        """
        The timestamp getter method returns the object's epoch time in milliseconds.
        :return: The epoch time in milliseconds when the TimeStamp object was created.
        """
        return self.__timestamp

    # end timestamp getter

    @timestamp.setter
    def timestamp(self, time):
        """
        TimeStamp's timestamp setter method resets its time.  The method automatically converts whatever time is
        passed to an int.  Use an epoch time in milliseconds.
        :param time: Epoch time in milliseconds.
            type: int or str
            default: none
            required: yes
        :return: none
        """
        self.__timestamp = int(time)

    # end timestamp setter

    def utc_timestamp(self):
        """
        The utc_timestamp method returns the object's current timestamp value as a formatted string in UTC time.
        :return: The timestamp in UTC time formatted as %Y-%m-%d %H:%M:%S
        """
        t = self.__timestamp / 1000
        t = time.gmtime(t)
        return time.strftime('%Y-%m-%d %H:%M:%S', t)

    # end utc_timestamp()

    def local_timestamp(self):
        """
        The local_timestamp method returns the object's current timestamp value as a formatted string in the Cisco
        DNA Center instance's local timezone.
        :return: The timestamp in local time formatted as %Y-%m-%d %H:%M:%S
        """
        t = self.__timestamp / 1000
        t = time.localtime(t)
        return time.strftime('%Y-%m-%d %H:%M:%S', t)

    # end local_timestamp()

    def sleep(self, seconds):
        """
        Instructs the TimeStamp object to wait the number of seconds given.
        :param seconds: The number of seconds to halt program activity.
            type: int
            required: yes
            default: none
        :return: none
        """
        time.sleep(seconds)

    # end sleep()

    def get_current_time(self):
        """
        Resets the TimeStamp to the current time.
        :return: The current time as an epoch integer.
        """
        self.__timestamp = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() * 1000)
        return self.__timestamp

    # end get_current_time()

# end class TimeStamp()

