#!/usr/bin/python

from __future__ import division
from enum import Enum
import collections
import sys
import statistics

SEC_TO_USEC = 1000*1000
MIN_TO_USEC = 60 * SEC_TO_USEC
HOUR_TO_USEC = 60 * MIN_TO_USEC

'''
check netperf_rr packet (length, sec, x:y)
1. host recv
  get host recv time
  change to host send or guest recv

2. guest recv
  get guest recv time
  get diff from 1.
  change to guest send

In between, there can be L2 recv and L2 send

3. guest send
  get guest send time
  get diff from 2.
  change to host recv

4. host send
  get host send time
  put it in the list
  get diff from 3.
  change to host recv
  '''

hr_hr_raw = []
hr_hs_raw = []
hr_gr_raw = []
gr_l2r_raw = []
l2r_l2s_raw = []
l2s_gs_raw = []
gr_gs_raw = []
gs_hs_raw = []

class State(Enum):
	host_recv = 1
	guest_recv = 2
	guest_send = 3
	host_send = 4
	l2_recv = 5
	l2_send = 6


def myreadline(cur_state):
	if cur_state == State.guest_recv or cur_state == State.guest_send:
		line = f_guest.readline()
	elif cur_state == State.l2_recv or cur_state == State.l2_send:
		line = f_l2.readline()
	else:
		line = f_host.readline()

	return line

def isCorrectLine(line):

	line = line.rstrip('\n')
	sp = line.split(' ')

	if (sp[-2]+' '+sp[-1]) != "length 1":
	       return False 
	
	if sp[7] != "seq":
	       return False 

	seq_str = str(seq_num) + ":" + str(seq_num+1) + ","
	if sp[8] != seq_str: 
	       return False 

	return True 

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
	global has_guest
	has_guest = False

	global has_l2
	has_l2 = False

	global f_host
	f_host = open(sys.argv[1])

	if len(sys.argv) > 2:
		global f_guest
		f_guest = open(sys.argv[2])
		has_guest = True

	if len(sys.argv) > 3:
		global f_l2
		f_l2 = open(sys.argv[3])
		has_l2 = True

	cur_state = State.host_recv

	host_recv = 0
	guest_recv = 0
	guest_send = 0
	host_send = 0
	global seq_num
	seq_num = 1

	while True:
		line = myreadline(cur_state)

		if len(line) == 0:
			break; 

		if isCorrectLine(line) == False:
			continue

		line = line.rstrip('\n')
		sp = line.split(' ')
		total = getts(sp)

		if cur_state == State.host_recv:
			if host_recv != 0:
				r2r = total - host_recv
				hr_hr_raw.append(r2r)
			host_recv = total
			if has_guest:
				next_state = State.guest_recv
			else:
				next_state = State.host_send

		elif cur_state == State.guest_recv:
			guest_recv = total
			timediff = guest_recv - host_recv
			hr_gr_raw.append(timediff)
			if has_l2:
				next_state = State.l2_recv
			else:
				next_state = State.guest_send

		elif cur_state == State.l2_recv:
			l2_recv = total
			timediff = l2_recv - guest_recv
			gr_l2r_raw.append(timediff)
			next_state = State.l2_send

		elif cur_state == State.l2_send:
			l2_send = total
			timediff = l2_send - l2_recv
			l2r_l2s_raw.append(timediff)
			next_state = State.guest_send

		elif cur_state == State.guest_send:
			guest_send = total
			if has_l2:
				timediff = guest_send - l2_send
				l2s_gs_raw.append(timediff)
			timediff = guest_send - guest_recv
			gr_gs_raw.append(timediff)
			next_state = State.host_send

		elif cur_state == State.host_send:
			host_send = total
			timediff = host_send - host_recv
			hr_hs_raw.append(timediff)
			if has_guest:
				gs_hs = host_send - guest_send
				gs_hs_raw.append(gs_hs)
			next_state = State.host_recv
			seq_num += 1
		cur_state = next_state


	print ("host recv to host recv") 
	a = statistics.mean(hr_hr_raw)
	print (a)

	print ("host recv to host send") 
	a = statistics.mean(hr_hs_raw)
	print (a)

	if has_guest:
		print ("host recv to guest recv") 
		a = statistics.mean(hr_gr_raw)
		print (a)
		print ("guest recv to guest send") 
		a = statistics.mean(gr_gs_raw)
		print (a)
		print ("guest send to host send") 
		a = statistics.mean(gs_hs_raw)
		print (a)

	if has_l2:
		print ("guest recv to l2 recv") 
		a = statistics.mean(gr_l2r_raw)
		print (a)
		print ("l2 recv to l2 send") 
		a = statistics.mean(l2r_l2s_raw)
		print (a)
		print ("l2 send to guest send") 
		a = statistics.mean(l2s_gs_raw)
		print (a)

if __name__ == "__main__":
		main()
