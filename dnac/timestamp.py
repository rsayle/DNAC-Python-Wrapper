from datetime import datetime

# globals

MODULE = 'timestamp.py'

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

    def __init__(self):
        """
        The TimeStamp's __init__ method sets its value to the current number of milliseconds in epoch time.

        Parameters:
            None

        Return Values:
            TimeStamp object: a new TimeStamp instance

        Usage:
            t = TimeStamp()
        """
        self.__timestamp = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() * 1000)

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

# end class TimeStamp()

# begin unit test

if __name__ == '__main__':

    ts = TimeStamp()

    print('TimeStamp:')
    print()
    print(' timestamp      = %i' % ts.timestamp)
    print(' str(timestamp) = %s' % ts)
    print()
    print('TimeStamp: unit test complete')
    print()
