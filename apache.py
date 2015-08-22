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
        sync_ack = 0
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

        while True:
                line = myreadline(cur_state)

                if len(line) == 0:
                        if cur_state == State.fin:
                                tran_cnt += 1
                        break; 

                line = line.rstrip('\n')
                sp = line.split(' ')
                total = getts(sp)

                if sp[1] != "IP":
                        continue
                if "[S]" in sp[6]:
                        s_cnt += 1

                if cur_state == State.none:     # Wait for [S] packet
                        if "[S]" in sp[6]:
                                sync_start = total
                                next_state = State.sync_start
                if cur_state == State.sync_start: # Wait for SYN_ACK packet
                        if "[S.]" in sp[6]:
                                next_state = State.sync_ack
                                sync_ack = total
                                diff = sync_ack - sync_start
                                #print (diff)
                                dic_sync_ack.append(diff)
                elif cur_state == State.sync_ack: # Wait for ACK packet
                        if "[.]" in sp[6]:
                                sync_end = total
                                next_state = State.sync_end
                                diff = sync_end - sync_ack
                                #print (diff)
                                dic_sync.append(diff)
                elif cur_state == State.sync_end:
                        if "[P.]" in sp[6]:
                                req_recv = total
                                next_state = State.req_recv
                                diff = req_recv - sync_end
                                #print (diff)
                                dic_req_recv.append(diff)
                elif cur_state == State.req_recv:
                        if "seq" in sp[7]:
                                resp_1 = total
                                next_state = State.resp_1
                                diff = resp_1 - req_recv
                                #print (diff)
                                dic_resp_1.append(diff)
                elif cur_state == State.resp_1:
                        if "[P.]" in sp[6]:
                                resp_m = total
                                next_state = State.resp_m
                elif cur_state == State.resp_m: # last response packet
                        if ("[P.]" in sp[6]):
                                last_resp = total
                        elif ("FP." in sp[6]):
                                last_resp = total
                                next_state = State.resp_f
                                diff = last_resp - resp_1
                                dic_resp_f.append(diff)
                                f_cnt += 1
                        elif "F." in sp[6]:
                                next_state=State.resp_f
                                diff = last_resp - resp_1
                                dic_resp_f.append(diff)
                                f_cnt += 1

                elif cur_state == State.resp_f: # Wait for FIN from client. The second FIN
                        if "F." in sp[6]:
                                f_cnt+= 1
                        if f_cnt == 2:
                                next_state = State.fin
                                f_cnt = 0

                        if "[S]" in sp[6]: # Last FIN is coming after [S]. Count [S] as an end of transaction
                                sync_start = total
                                diff = sync_start - last_resp
                                #print ("---------")
                                dic_fin.append (diff)
                                next_state = State.sync_start
                                tran_cnt += 1
                                f_cnt = 0
                                if s_cnt != tran_cnt+1: #s_cnt is already increased by one at the top of the while loop
                                        print (s_cnt)
                                        print (tran_cnt)
                                        print(line)
                                        break;

                elif cur_state == State.fin:
                        '''
                        if "[.]" in sp[6]:
                                fin = total
                                diff = fin - last_resp 
                                #print (diff)
                                #print ("---------")
                                dic_fin.append (diff)
                                next_state = State.none
                                tran_cnt += 1
                                if s_cnt != tran_cnt:
                                        print (s_cnt)
                                        print (tran_cnt)
                                        print(line)
                                        break;
                        '''
                        if "[S]" in sp[6]: # Last FIN_ACK is coming after [S]. Count [S] as an end of transaction
                                sync_start = total
                                diff = sync_start - last_resp
                                #print ("---------")
                                dic_fin.append (diff)
                                next_state = State.sync_start
                                tran_cnt += 1
                                if s_cnt != tran_cnt+1: #s_cnt is already increased by one at the top of the while loop
                                        print (s_cnt)
                                        print (tran_cnt)
                                        print(line)
                                        break;

                cur_state = next_state

        print ("Total Transaction")
        print (tran_cnt)

        print ("Sync to Sync Ack")
        a = statistics.mean(dic_sync_ack)
        print (a)

        print ("Sync ack to Sync Fin")
        a = statistics.mean(dic_sync)
        print (a)

        print ("Recv request")
        a = statistics.mean(dic_req_recv)
        print (a)

        print ("Send 1st resp")
        a = statistics.mean(dic_resp_1)
        print (a)

        print ("Send last resp")
        a = statistics.mean(dic_resp_f)
        print (a)

        print ("End of transaction. acks and FINs")
        a = statistics.mean(dic_fin)
        print (a)


if __name__ == "__main__":
                main()
