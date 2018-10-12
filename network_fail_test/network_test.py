import sys
import socket
import fcntl
import struct
import array
import subprocess
import re
from time import sleep

def get_interface_list():
    host_interfaces = []
    bridge = []
    container_interface = []
    output = subprocess.Popen(['cat','/proc/net/if_inet6'], stdout=subprocess.PIPE).communicate()[0]
    lines = output.strip().splitlines()
    for line in lines:
        line = line.strip().split()
        if 'v-' in line[5]:
            bridge.append(line[5])
        if 'veth' in line[5]:
            container_interface.append(line[5]) 
        else:
            host_interfaces.append(line[5])
    return (host_interfaces, bridge, container_interface)


def get_from_ip_addr(ifname):
    output = subprocess.Popen(['ip','addr','show', ifname], stdout=subprocess.PIPE).communicate()[0]
    state = re.search(r'state (\S+)', output)
    ip = re.search(r'inet (\S+)', output)
    mac = re.search(r'link/ether (\S+)', output)

    if state:
        result = state.group(1)
    else:
        result = "DOWN"

    result += "\t"
    if ip:
        result += ip.group(1)
    else:
        result += "nothing   "

    result += "\t\t"
    if mac:
        result += mac.group(1)
    else:
        result += "nothing   "
    return result

def get_from_netstat():
    output_before = subprocess.Popen(['netstat','-i'], stdout=subprocess.PIPE).communicate()[0]
    sleep(3)
    output_after = subprocess.Popen(['netstat','-i'], stdout=subprocess.PIPE).communicate()[0]

    lines_before = output_before.strip().splitlines()
    lines_after = output_after.strip().splitlines()
    lines_before.pop(0)
    lines_after.pop(0)

    rx_flag = int(lines_before[0].strip().split().index("RX-OK"))
    tx_flag = int(lines_before[0].strip().split().index("TX-OK"))

    result_dic = {}
    for i in range(1, len(lines_before)):
        line_be = lines_before[i].strip().split()
        line_af = lines_after[i].strip().split()

        result_line = ( str(int(line_af[rx_flag]) - int(line_be[rx_flag])) )
        result_line += '\t'
        result_line += ( str(int(line_af[tx_flag]) - int(line_be[tx_flag])) )

        result_dic[line_af[0]] = result_line 
    return result_dic

def get_from_arp():
    output = subprocess.Popen(['ip','neibh','show', ifname], stdout=subprocess.PIPE).communicate()[0]
    state = re.search(r'state (\S+)', output)
      

if __name__ == '__main__':
    #interfaces = list_interfaces()
    (host_if, bridge, con_if) = get_interface_list()
    netstat_result = get_from_netstat()

    print "Host interfaces : %s. \n" % (host_if)
    print "bridge : %s. \n" % (bridge)
    print "Container interfaces : %s. \n" % (con_if)
    print "IF [interface_name] --> ip \t mac \t RX \t TX(3 seconds)"
    print " "
    print "----------- host interface -----------------------------"
    for ifname in host_if :
        print "IF [%s] --> %s\t%s" %(ifname, get_from_ip_addr(ifname), netstat_result[ifname])

    print " "
    print "----------- bridge -----------------------------"
    for ifname in bridge :
        print "IF [%s] --> %s" %(ifname, get_from_ip_addr(ifname))

    print " "
    print "----------- container interface -----------------------------"
    for ifname in con_if :
        print "IF [%s] --> %s" %(ifname, get_from_ip_addr(ifname))

    print " "
    print "-----------------------------"
    
