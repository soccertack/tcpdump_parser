#!/usr/bin/python

import collections

SEC_TO_USEC = 1000*1000
MIN_TO_USEC = 60 * SEC_TO_USEC
HOUR_TO_USEC = 60 * MIN_TO_USEC

f = open("tcp_rr_dump.txt")
prev_recv = 0
r2r_dic = {}
r2s_dic = {}
while True:
        line = f.readline()
        if len(line) == 0:
                break
        line = line.rstrip('\n')
        sp = line.split(' ')

        if (sp[-2]+' '+sp[-1]) != "length 1":
                continue

        timestamp = sp[0].split('.')
        usec = int(timestamp[1])
        low_resol = timestamp[0].split(':')
        sec = int(low_resol[2])
        minute = int(low_resol[1])
        hour = int(low_resol[0])

        total = usec
        total += SEC_TO_USEC*sec
        total += MIN_TO_USEC*60*minute
        total += HOUR_TO_USEC*60*60*hour

        if sp[2][0] == 'c':
                if prev_recv != 0:
                        r2r = total - prev_recv
                        if r2r in r2r_dic:
                                r2r_dic[r2r] +=1
                        else:
                                r2r_dic[r2r] = 1

                prev_recv = total

        elif sp[2][0] == 'b':
                if prev_recv != 0:
                        r2s = total - prev_recv
                        if r2s in r2s_dic:
                                r2s_dic[r2s] +=1
                        else:
                                r2s_dic[r2s] = 1

sorted_r2r_dic = collections.OrderedDict(sorted(r2r_dic.items()))
sorted_r2s_dic = collections.OrderedDict(sorted(r2s_dic.items()))
print "r2r"
for num, times in sorted_r2r_dic.items():
        print "%s\t%d" % (num, times)

print "r2s"
for num, times in sorted_r2s_dic.items():
        print "%s\t%d" % (num, times)
