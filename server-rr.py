#!/usr/bin/python

import pexpect
import sys
import os
import datetime
import time
import socket

LOCAL_SOCKET = 8889

child = []

target_virt_level = 2
if len(sys.argv) > 1:
	target_virt_level = int(sys.argv[1])

# This will be used for iterations for each virt level
max_level = target_virt_level + 1

def wait_for(sk, string):
	while True:
		buf = sk.recv(64)
		if buf == string:
			break;

def prepare():

	for i in range (0, max_level):
		child.append(pexpect.spawn('bash'))
		child[i].logfile = sys.stdout
		child[i].timeout=None

	# L0 shell
	child[0].sendline('')
	child[0].expect('kvm-node.*')

	# Make sure that we are in UTC
	child[0].sendline('export TZ=Etc/UTC')
	child[0].expect('kvm-node.*')

	if target_virt_level < 1:
		return

	# L1 shell
	child[1].sendline('')
	child[1].expect('kvm-node.*')
	child[1].sendline('ssh root@10.10.1.100')
	child[1].expect('L1.*$')

	if target_virt_level < 2:
		return

	# L2 shell
	child[2].sendline('')
	child[2].expect('kvm-node.*')
	child[2].sendline('ssh root@10.10.1.101')
	child[2].expect('L2.*$')

def tcpdump_start():
	for i in range (0, max_level):
		child[i].sendline('sudo tcpdump -i eth1 -n -w tcp_rr_dump')

def tcpdump_stop():
	# Stop tcpdump
	for i in range (0, max_level):
		child[i].sendcontrol('c')

	# Wait for the shell
	child[0].expect('kvm-node.*')

	if target_virt_level > 0:
		child[1].expect('L1.*$')

	if target_virt_level > 1:
		child[2].expect('L2.*$')

	time.sleep(3)

def tcpdump_get_result():

	cmd = 'python3 ./r2r.py result.txt'
	# Convert dump to txt
	for i in range (0, max_level):
		child[i].sendline('tcpdump -r tcp_rr_dump > result.txt')

	# Wait until all result.txt are ready
	child[0].expect('kvm-node.*')

	if target_virt_level > 0:
		child[1].expect('L1.*$')
		child[0].sendline('scp root@10.10.1.100:/root/result.txt guest_result.txt')
		child[0].expect('kvm-node.*')
		cmd += ' guest_result.txt'

	if target_virt_level > 1:
		child[2].expect('L2.*$')
		child[0].sendline('scp root@10.10.1.101:/root/result.txt l2_result.txt')
		child[0].expect('kvm-node.*')
		cmd += ' l2_result.txt'

	child[0].sendline(cmd)
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
		serversocket.send('tcpdump-done')
	elif buf == 'netperf-rr-done':
		tcpdump_get_result()
		break

