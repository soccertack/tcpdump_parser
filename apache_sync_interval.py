#!/usr/bin/python

from __future__ import division
from enum import Enum
import collections
import sys
import statistics

SEC_TO_USEC = 1000*1000
MIN_TO_USEC = 60 * SEC_TO_USEC
HOUR_TO_USEC = 60 * MIN_TO_USEC

dic_sync = []
dic_req_recv = []
dic_resp_1 = []
dic_resp_f = []
dic_fin = []

class State(Enum):
        none = 0
        sync_start = 1
        sync_ack = 8
        sync_end = 2
        req_recv = 3
        resp_1 = 4
        resp_m = 5
        resp_f = 6
        fin = 7


def myreadline(cur_state):
        line = f_host.readline()

        return line

def getts(sp):
        timestamp = sp[0].split('.')
        usec = int(timestamp[1])
        low_resol = timestamp[0].split(':')
        sec = int(low_resol[2])
        minute = int(low_resol[1])
        hour = int(low_resol[0])

        total = usec
        total += SEC_TO_USEC*sec
        total += MIN_TO_USEC*minute
        total += HOUR_TO_USEC*hour
        return total



def main():
        global f_host
        f_host = open(sys.argv[1])

        cur_state = State.none

        sync_start = 0
        sync_end = 0
        req_recv = 0
        resp_1 = 0
        resp_f = 0
        f_cnt = 0
        global seq_num
        seq_num = 1

        tmp_cnt = 0
        s_cnt = 0
        tran_cnt = 0
        prev_ts = 0

        while True:
                line = myreadline(cur_state)

                if len(line) == 0:
                        break; 

                line = line.rstrip('\n')
                sp = line.split(' ')
                total = getts(sp)

                if sp[1] != "IP":
                        continue
                if "[S]" in sp[6]:
                        s_cnt += 1

                        if prev_ts != 0:
                                diff = total - prev_ts
                                dic_sync.append(diff)
                        prev_ts = total

        print ("Sync")
        a = statistics.mean(dic_sync)
        print (a)

if __name__ == "__main__":
                main()
