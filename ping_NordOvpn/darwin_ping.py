from __future__ import print_function
import os
import select
import socket
import struct
import sys
import time
# On Windows, the best timer is time.clock()
# On most other platforms the best timer is time.time()
default_timer = time.clock if sys.platform == "win32" else time.time
# From /usr/include/linux/icmp.h; your milage may vary.
ICMP_ECHO_REQUEST = 8  # Seems to be the same on Solaris.
def checksum(source_string):
    sum = 0
    countTo = (len(source_string)/2)*2
    count = 0
    while count<countTo:
        v1 = source_string[count + 1]
        if not isinstance(v1, int):
            v1 = ord(v1)
        v2 = source_string[count]
        if not isinstance(v2, int):
            v2 = ord(v2)
        thisVal = v1 * 256 + v2
        sum = sum + thisVal
        sum = sum & 0xffffffff # Necessary?
        count = count + 2
    if countTo<len(source_string):
        sum = sum + ord(source_string[len(source_string) - 1])
        sum = sum & 0xffffffff # Necessary?
    sum = (sum >> 16)  +  (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    # Swap bytes. Bugger me if I know why.
    answer = answer >> 8 | (answer << 8 & 0xff00)

    return answer


def receive_one_ping(my_socket, ID, timeout):
    timeLeft = timeout
    while True:
        startedSelect = default_timer()
        whatReady = select.select([my_socket], [], [], timeLeft)
        howLongInSelect = (default_timer() - startedSelect)
        if whatReady[0] == []:
            return
        timeReceived = default_timer()
        recPacket, addr = my_socket.recvfrom(1024)
        icmpHeader = recPacket[20:28]
        type, code, checksum, packetID, sequence = struct.unpack(
            b"bbHHh", icmpHeader
        )
        if type != 8 and packetID == ID:
            bytesInDouble = struct.calcsize(b"d")
            timeSent = struct.unpack(b"d", recPacket[28:28 + bytesInDouble])[0]
            return timeReceived - timeSent
        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return


def send_one_ping(my_socket, dest, ID):
    dest = socket.gethostbyname(dest)
    my_checksum = 0
    header = struct.pack(b"bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1)
    bytes_double = struct.calcsize("d")
    data = (192 - bytes_double) * b"Q"
    data = struct.pack("d", default_timer()) + data
    my_checksum = checksum(header + data)
    header = struct.pack(
        b"bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1
    )
    packet = header + data
    my_socket.sendto(packet, (dest, 1))


def do_one(dest_addr, timeout):
    icmp = socket.getprotobyname("icmp")
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, icmp)
    my_ID = os.getpid() & 0xFFFF
    send_one_ping(my_socket, dest_addr, my_ID)
    delay = receive_one_ping(my_socket, my_ID, timeout)
    my_socket.close()
    return delay


def verbose_ping(destination, timeout=2, count=4, interval=1.0):
    lost_cnt = 0
    delays = []
    for _ in range(count):
        try:
            delay = do_one(destination, timeout)
        except socket.gaierror as e:
            print("failed. (socket error: '%s')" % e[1])
            raise e
        if delay is None:
            lost_cnt += 1
            if lost_cnt == 3:
                return 8799
        else:
            time.sleep(min(0, interval-delay))
            delays.append(delay * 1000)
    return sum(delays)/len(delays) + lost_cnt / 100*1200


def darwin_ping(destination, timeout=2, count=16, interval=1):
    return verbose_ping(destination, timeout, count, interval)

if __name__ == '__main__':
    s = verbose_ping('8.8.8.8')
    print(s)
