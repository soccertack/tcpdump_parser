
SEC_TO_USEC = 1000*1000
MIN_TO_USEC = 60 * SEC_TO_USEC
HOUR_TO_USEC = 60 * MIN_TO_USEC

def getts(sp):
        timestamp = sp[0].split('.')
        usec = int(timestamp[1])
        low_resol = timestamp[0].split(':')
        sec = int(low_resol[2])
        minute = int(low_resol[1])
        hour = int(low_resol[0])

        timestamp = usec
        timestamp += SEC_TO_USEC*sec
        timestamp += MIN_TO_USEC*minute
        timestamp += HOUR_TO_USEC*hour
        return timestamp

def hasFlag(flag, sp):
        if flag in sp[6]:
                return True
        return False

def hasSeq(seq, sp):
        if seq in sp[8]:
                return True
        return False

debug = True
debug = False
def my_print(string):
        if debug == True:
                print (string)

