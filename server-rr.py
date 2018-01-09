#!/usr/bin/python

import pexpect
import sys
import os
import datetime
import time
import socket

LOCAL_SOCKET = 8889

child = []

def wait_for(sk, string):
	while True:
		buf = sk.recv(64)
		if buf == string:
			break;

def prepare():

	for i in range (0, 3):
		child.append(pexpect.spawn('bash'))
		child[i].logfile = sys.stdout
		child[i].timeout=None

	# L0 shell
	child[0].sendline('')
	child[0].expect('kvm-node.*')

	# Make sure that we are in UTC
	child[0].sendline('export TZ=Etc/UTC')
	child[0].expect('kvm-node.*')

	# L1 shell
	child[1].sendline('')
	child[1].expect('kvm-node.*')
	child[1].sendline('ssh root@10.10.1.100')
	child[1].expect('L1.*$')

	# L2 shell
	child[2].sendline('')
	child[2].expect('kvm-node.*')
	child[2].sendline('ssh root@10.10.1.101')
	child[2].expect('L2.*$')

def tcpdump_start():
	for i in range (0, 3):
		child[i].sendline('sudo tcpdump -i eth1 -n -w tcp_rr_dump')

def tcpdump_stop():
	# Stop tcpdump
	for i in range (0, 3):
		child[i].sendcontrol('c')

	# Wait for the shell
	child[0].expect('kvm-node.*')
	child[1].expect('L1.*$')
	child[2].expect('L2.*$')

	time.sleep(3)

def tcpdump_get_result():

	# Convert dump to txt
	for i in range (0, 3):
		child[i].sendline('tcpdump -r tcp_rr_dump > result.txt')

	# Wait until all result.txt are ready
	child[1].expect('L1.*$')
	child[2].expect('L2.*$')
	child[0].expect('kvm-node.*')

	# Copy data from VM and nested VM, then extract result
	child[0].sendline('scp root@10.10.1.101:/root/result.txt l2_result.txt')
	child[0].expect('kvm-node.*')
	child[0].sendline('scp root@10.10.1.100:/root/result.txt guest_result.txt')
	child[0].expect('kvm-node.*')
	child[0].sendline('python3 ./r2r.py result.txt guest_result.txt l2_result.txt')
	child[0].expect('kvm-node.*')

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', LOCAL_SOCKET))
server.listen(1) # become a server socket.

serversocket, address = server.accept()

wait_for(serversocket, 'netperf-rr-start')
prepare()
serversocket.send('netperf-rr-ready')

while 1:

	buf = serversocket.recv(64)
	if buf == 'tcpdump-start':
		tcpdump_start()
		serversocket.send('tcpdump-ready')
	elif buf == 'tcpdump-stop':
		tcpdump_stop()
		tcpdump_get_result()
		serversocket.send('tcpdump-done')
	elif buf == 'netperf-rr-done':
		break

