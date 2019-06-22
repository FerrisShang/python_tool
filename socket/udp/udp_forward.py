from socket import *

port_dict = {
    '192.168.100.189':  ('192.168.5.249', 65535),
    '192.168.5.249':  ('192.168.100.189', 65535),
}
addr_list = []
local_port = 23333
bufsize = 1024

udpServer = socket(AF_INET, SOCK_DGRAM)
udpServer.bind(('', local_port))

while True:
    data, addr = udpServer.recvfrom(bufsize)
    if addr[0] in port_dict:
        port_dict[port_dict[addr[0]][0]] = addr
    udpServer.sendto(data, port_dict[addr[0]])
