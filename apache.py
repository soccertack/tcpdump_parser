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
dic_sync_ack = []
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

debug = False
def my_print(string):
        if debug == True:
                print (string)

def main():
        f_host = open(sys.argv[1])

        # Init local variables
        cur_state = State.none
        ts_sync_start = 0
        ts_sync_ack = 0
        ts_sync_end = 0
        ts_req_recv = 0
        ts_resp_1 = 0
        tran_cnt = 0

        while True:
                line = f_host.readline()

                if len(line) == 0:
                        break; 

                line = line.rstrip('\n')
                sp = line.split(' ')
                timestamp = getts(sp)

                if sp[1] != "IP":
                        continue

                if cur_state == State.none:             # Wait for SYN packet
                        if hasFlag("[S]", sp):
                                ts_sync_start = timestamp
                                next_state = State.sync_start
                                tran_cnt += 1
                elif cur_state == State.sync_start:     # Wait for SYN_ACK packet
                        if hasFlag("[S.]", sp):
                                next_state = State.sync_ack
                                ts_sync_ack = timestamp
                                diff = ts_sync_ack - ts_sync_start
                                my_print(diff)
                                dic_sync_ack.append(diff)
                elif cur_state == State.sync_ack:       # Wait for ACK packet
                        if hasFlag("[.]", sp):
                                ts_sync_end = timestamp
                                next_state = State.sync_end
                                diff = ts_sync_end - ts_sync_ack
                                my_print(diff)
                                dic_sync.append(diff)
                elif cur_state == State.sync_end:       # Wait for request packet 
                        if hasFlag("[P.]", sp):
                                ts_req_recv = timestamp
                                next_state = State.req_recv
                                diff = ts_req_recv - ts_sync_end
                                my_print(diff)
                                dic_req_recv.append(diff)
                elif cur_state == State.req_recv:       # Wait for the first response
                        if "seq" in sp[7]:
                                ts_resp_1 = timestamp
                                next_state = State.resp_1
                                diff = ts_resp_1 - ts_req_recv
                                my_print (diff)
                                dic_resp_1.append(diff)
                elif cur_state == State.resp_1:         # Wait for intermediate [P] packet
                        if hasFlag("[P.]", sp):
                                next_state = State.resp_m
                elif cur_state == State.resp_m:         # Wait for the last response and the first FIN

                        if hasFlag("P", sp):
                                last_resp = timestamp
                        if hasFlag("F", sp):
                                next_state = State.fin
                                diff = last_resp - ts_resp_1
                                dic_resp_f.append(diff)
                                my_print (diff)

                elif cur_state == State.fin:
                        if hasFlag("[S]", sp):          # Last FIN_ACK is coming after [S]. Count [S] as an end of transaction
                                ts_sync_start = timestamp
                                diff = ts_sync_start - last_resp
                                my_print (diff)
                                dic_fin.append (diff)
                                next_state = State.sync_start
                                tran_cnt += 1

                cur_state = next_state

        print ("Total Transaction", end="\t")
        print (tran_cnt)

        print ("Sync to Sync Ack", end="\t")
        a = statistics.mean(dic_sync_ack)
        print (round(a))
        time_per_trasaction = a

        print ("Sync Ack to Ack ", end="\t")
        a = statistics.mean(dic_sync)
        print (round(a))
        time_per_trasaction += a

        print ("Receive request ", end="\t")
        a = statistics.mean(dic_req_recv)
        print (round(a))
        time_per_trasaction += a

        print ("Send First resp ", end="\t")
        a = statistics.mean(dic_resp_1)
        print (round(a))
        time_per_trasaction += a

        print ("Send last resp  ", end="\t")
        a = statistics.mean(dic_resp_f)
        print (round(a))
        time_per_trasaction += a

        print ("End of trans    ", end="\t")
        a = statistics.mean(dic_fin)
        print (round(a))
        time_per_trasaction += a

        print ("Time per transac", end="\t")
        print (round(time_per_trasaction))



if __name__ == "__main__":
                main()
