from datetime import datetime
from datetime import timedelta
import time

from common.Singleton import Singleton


class TestTime(metaclass=Singleton):
    __fstart = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
    start_time = time.monotonic()
    
    
    def get_fstart() -> str:
        return TestTime.__fstart
    
    def get_now() -> float:
        return time.monotonic()
    
    def get_fnow() -> str:
        return datetime.now().strftime('%m/%d/%Y %H:%M:%S')
    
    def get_timediff(start_time: float) -> str:
        __end_time = time.monotonic()
        timediff = str(timedelta(seconds=__end_time - start_time))
        
        timediff = timediff.split(":")

        hours = int(timediff[0])
        minutes = int(timediff[1])
        seconds_ms = float(timediff[2])

        if (hours == 0 and minutes == 0):
            return f'{seconds_ms} seconds'
        elif (hours == 0):
            if minutes == 1:
                return f'{minutes} minute and {seconds_ms} seconds'
            else:
                return f'{minutes} minutes and {seconds_ms} seconds'
        elif (hours == 1):
            if minutes == 1:
                return f'{hours} hour, {minutes} minute, and {seconds_ms} seconds'
            else:
                return f'{hours} hour, {minutes} minutes, and {seconds_ms} seconds'
        else:
            return f'{hours} hours, {minutes} minutes, and {seconds_ms} seconds'

    
    



### main ###
if (__name__ == "__main__"):
    TestTime()

    start = TestTime.get_time()
    print(str(start))

    counter = 5

    while counter > 0:
        print(f'Count = {counter}')
        time.sleep(1)
        counter -= 1
        
    print(TestTime.get_timediff(start))


        