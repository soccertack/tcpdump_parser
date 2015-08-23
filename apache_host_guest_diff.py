#!/usr/bin/python

from __future__ import division
from enum import Enum
import collections
import sys
import statistics
from mycommon import *

dic_syn = []
dic_synack = []
dic_fin = []
dic_resp_1 = []
dic_req = []

def isValidLine(split_line):
        if split_line[1] == "IP":
                return True
        return False

def add_dic(check_flag, flag_item, seq_item, diff):

        if check_flag:
                if flag_item == "[S]":
                        dic_syn.append(diff)
                elif flag_item == "[S.]":
                        dic_synack.append(diff)
                elif flag_item == "[FP.]":
                        dic_fin.append(diff)
        else:
                if seq_item == "1:7241":
                        dic_resp_1.append(diff)
                elif seq_item == "1:94":
                        dic_req.append(diff)

def print_dic():
        print ("SYN delay")
        a = statistics.mean(dic_syn)
        print (a)

        print ("SYN_ACK delay")
        a = statistics.mean(dic_synack)
        print (a)

        print ("Request delay")
        a = statistics.mean(dic_req)
        print (a)

        print ("FIN delay")
        a = statistics.mean(dic_fin)
        print (a)

def main():
        if len(sys.argv) != 3:
                print ("Usage: python3.4 ./apache_host_guest_diff.py host_file guest_file")
                sys.exit()
        f_host = open(sys.argv[1])
        f_guest = open(sys.argv[2])

        cond_str = ""
        guest_cond_set = 1
        host_cond_set = 1

        flags = [ "[S]", "[S.]", "[FP.]" ]
        seq_num = [ "1:94" ] # request

        while True:
                guest_line = f_guest.readline()
                guest_line = guest_line.rstrip('\n')
                if len(guest_line) == 0:
                        break;
                guest_sp = guest_line.split(' ')
                guest_rest_of_line = guest_line.split('Flags') [1]

                if isValidLine(guest_sp) == False:
                        continue

                check_flag = False
                check_seq = False
                for flag_item in flags:
                        if hasFlag(flag_item, guest_sp):
                                check_flag = True
                                break
                seq_item = ""
                for seq_item in seq_num:
                        if hasSeq(seq_item, guest_sp):
                                check_seq = True
                                break

                if not check_flag and not check_seq:
                        continue

                while True:
                        host_line = f_host.readline()
                        host_line = host_line.rstrip('\n')
                        if len(host_line) == 0:
                                break
                        host_sp = host_line.split(' ')
                        if isValidLine(host_sp) == False:
                                continue
                        if check_flag and hasFlag (flag_item, host_sp):
                                break;  #Found it
                        elif check_seq and hasSeq(seq_item, host_sp):
                                break; #Found it

                host_rest_of_line = host_line.split('Flags') [1]

                if guest_rest_of_line == host_rest_of_line:
                        host_ts = getts(host_line.split(' ')) + 21600000000 #temp fix to adjust time zone
                        guest_ts = getts(guest_line.split(' '))
                        diff = abs(host_ts - guest_ts) 
                        add_dic(check_flag, flag_item, seq_item, diff)
                else:
                        print (guest_line)
                        print (host_line)
                        sys.exit()

                guest_cond_set = 1
                host_cond_set = 1

        
        print_dic()
if __name__ == "__main__":
                main()
