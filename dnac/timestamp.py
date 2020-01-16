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

        Parameters:
            None

        Return Values:
            TimeStamp object: a new TimeStamp instance

        Usage:
            t = TimeStamp()
        """
        if time == GET_CURRENT_TIME:
            self.__timestamp = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() * 1000)
        else:
            self.__timestamp = int(time)

    # end __init__

    def __str__(self):
        """
        TimeStamp class' __str__ function converts its timestamp attribute, an int, into a string.

        Parameters:
            None

        Return Values:
            str: the epoch time in milliseconds when the TimeStamp object was created.

        Usage:
            t = TimeStamp()
            print(t)
        """
        return str(self.__timestamp)

    # end __str__

    @property
    def timestamp(self):
        """
        The timestamp getter method returns the object's epoch time in milliseconds.

        Parameters:
            None

        Return Values:
            int: The epoch time in milliseconds when the TimeStamp object was created.

        Usage:
            t = TimeStamp()
            print(str(t.timestamp))
        """
        return self.__timestamp

    # end timestamp getter

    @timestamp.setter
    def timestamp(self, time):
        """
        TimeStamp's timestamp setter method resets its time.  The method automatically converts whatever time is
        passed to an int.  Use an epoch time in milliseconds.

        Parameters:
            time: Epoch time in milliseconds
                type: int or str
                default: none
                required: yes

        Return Values:
            None

        Usage:
            t = TimeStamp()
            t.timestamp = newtime
        """
        self.__timestamp = int(time)

    # end timestamp setter

    def utc_timestamp(self):
        """
        The utc_timestamp method returns the object's current timestamp value as a formatted string in UTC time.

        Parameters:
            None

        Return Values:
            str: the timestamp in UTC time formatted as %Y-%m-%d %H:%M:%S

        Usage:
            t = TimeStamp()
            print(t.utc_timestamp())
        """
        t = self.__timestamp / 1000
        t = time.gmtime(t)
        return time.strftime('%Y-%m-%d %H:%M:%S', t)

    # end utc_timestamp()

    def local_timestamp(self):
        """
        The local_timestamp method returns the object's current timestamp value as a formatted string in the Cisco
        DNA Center instance's local timezone.

        Parameters:
            None

        Return Values:
            str: the timestamp in local time formatted as %Y-%m-%d %H:%M:%S

        Usage:
            t = TimeStamp()
            print(t.local_timestamp())
        """
        t = self.__timestamp / 1000
        t = time.localtime(t)
        return time.strftime('%Y-%m-%d %H:%M:%S', t)

    # end local_timestamp()

# end class TimeStamp()

# begin unit test


if __name__ == '__main__':

    ts = TimeStamp()

    print('TimeStamp:')
    print()
    print("Getting the current time...")
    print('  timestamp      = %i' % ts.timestamp)
    print('  str(timestamp) = %s' % ts)
    print('  as UTC time    = %s' % ts.utc_timestamp())
    print('  as local time  = %s' % ts.local_timestamp())
    print()

    ts = TimeStamp(time=1564780178759)

    print()
    print('Getting a specific time...')
    print('  timestamp      = %i' % ts.timestamp)
    print('  str(timestamp) = %s' % ts)
    print('  as UTC time    = %s' % ts.utc_timestamp())
    print('  as local time  = %s' % ts.local_timestamp())

    print('TimeStamp: unit test complete')
    print()
