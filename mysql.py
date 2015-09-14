#!/usr/bin/python

from __future__ import division
from enum import Enum
import collections
import sys
import statistics
from mycommon import *

dic_sync = []
dic_sync_ack = []
dic_req_recv = []
dic_resp_1 = []
dic_resp_f = []
dic_fin = []
dic_diff = []

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

def main():
        f_host = open(sys.argv[1])

        # Init local variables
        cur_state = State.none
        ts_sync_start = 0
        ts_sync_ack = 0
        ts_sync_end = 0
        ts_req_recv = 0
        ts_resp_1 = 0
        packet_cnt = 0
        req_compl_cnt = 0

        while True:
                line = f_host.readline()

                if len(line) == 0:
                        break; 

                line = line.rstrip('\n')
                sp = line.split(' ')
                timestamp = getts(sp)

                if sp[1] != "IP":
                        continue

                if "mysql" in sp[2]:                # packet sent from server
                        ts_packet_sent = timestamp
                        diff = ts_packet_sent - ts_packet_recv
                        dic_diff.append(diff)
                        my_print (diff)
                        packet_cnt += 1
                
                elif "mysql" in sp[4]:                # packet received in server
                        ts_packet_recv = timestamp
                        if hasFlag("[.]", sp):
                                req_compl_cnt += 1
                        

        print ("Total # packets sent by server", end="\t")
        print (packet_cnt)

        print ("Total # completed requests", end="\t")
        print (req_compl_cnt)

        print ("Avg response time", end="\t")
        a = statistics.mean(dic_diff)
        print (round(a))

if __name__ == "__main__":
                main()
