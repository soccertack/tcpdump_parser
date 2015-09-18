#!/usr/bin/python3.4

from __future__ import division
from enum import Enum
import collections
import sys
import statistics
from mycommon import *

dic_diff = []
dic_large_diff = []

ts_recv_query = {}
diff_per_port  = {}
packet_cnt_per_port = {}

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
        large_cnt = 0
        large_interval = 0
        client_port = 0

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
                        client_sp = sp[4].split('.')
                        client_port = client_sp[len(client_sp)-1]
                        client_port = client_port[:-1]        # Remove trailing :

                        ts_packet_sent = timestamp
                        diff = ts_packet_sent - ts_recv_query[client_port]

                        if client_port in diff_per_port:
                                diff_per_port[client_port].append(diff)
                        else:
                                diff_per_port[client_port] = [diff]

                        if client_port in packet_cnt_per_port:
                                packet_cnt_per_port[client_port] += 1
                        else:
                                packet_cnt_per_port[client_port] = 1

                        dic_diff.append(diff)
                        my_print (diff)
                        large_interval += 1
                        if diff > 1000:
                                my_print (large_interval)
                                large_interval = 0
                                my_print (line)
                                large_cnt += 1
                                dic_large_diff.append(diff)
                        packet_cnt += 1
                
                elif "mysql" in sp[4]:                # packet sent from the client
                        client_sp = sp[2].split('.')
                        client_port = client_sp[len(client_sp)-1]
                        
                        ts_recv_query[client_port] = timestamp
                        if hasFlag("[.]", sp):
                                req_compl_cnt += 1
                        

        for key in diff_per_port:
                thefile = open('test_%s.txt'%key, 'w')
                print ("<Port %s>" % key)
                print ("num of packet: ", end="\t")
                print (packet_cnt_per_port[key])
                print ("Avg resp time: ", end="\t")
                a = statistics.mean(diff_per_port[key])
                print (round(a))
                print ()
                for item in diff_per_port[key]:
                        thefile.write("%s\n" % item)

        print ("Total # large diff ", end="\t")
        print (large_cnt)

if __name__ == "__main__":
                main()
