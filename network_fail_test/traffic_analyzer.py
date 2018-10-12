from scapy.all import *
import json
import sys
import operator

TOP_COUNT = 5

def getSummaryMap(p):
    summaryStr = str(p)
    summaryStr = summaryStr.replace('<', '').replace('>', '').replace('Sniffed: ', '')
    paramList = summaryStr.split(' ')
    summaryMap = {}

    for i in paramList:
        tmp = i.split(':')
        summaryMap[tmp[0]] = tmp[1]

    return summaryMap

def cleanPayload(p):
    p = str(p)
    return p.split('Raw')[0].split("Padding")[0].replace('|','\n').strip('<')\
            .strip('bound method Ether.show of ').replace('>','').replace('[<','[')\
            .replace('\n<','<').replace('<','\n')



if __name__ == "__main__":
    # sys.argv[0] is python file name.
    input_timeout = sys.argv[1] # sniffing time
    
    try:
        TOP_COUNT = int(sys.argv[2])
    except Exception as e:
        pass

    packet = sniff(timeout=int(input_timeout))

    l2CountingMap = {}
    l3CountingMap = {}
    srcIpCountingMap = {}
    dstIpCountingMap = {}
    srcPortCountingMap = {}
    dstPortCountingMap = {}
    ArpCount = 0

    for i in range(len(packet)):
        try:
            #l2 = packet[i][0]
            #l3 = packet[i][1]
            if packet[i].haslayer("ARP"):
                ArpCount = ArpCount + 1

            srcIp = packet[i][IP].src
            dstIp = packet[i][IP].dst
            srcPort = packet[i][IP].sport
            dstPort = packet[i][IP].dport

            #l2Count = l2CountingMap.get(l2, 0)
            #l3Count = l3CountingMap.get(l3, 0)
            srcIpCount = srcIpCountingMap.get(srcIp, 0)
            dstIpCount = dstIpCountingMap.get(dstIp, 0)
            srcPortCount = srcPortCountingMap.get(srcPort, 0)
            dstPortCount = dstPortCountingMap.get(dstPort, 0)

            #l2CountingMap[l2] = l2Count + 1
            #l3CountingMap[l3] = l3Count + 1
            srcIpCountingMap[srcIp] = srcIpCount + 1
            dstIpCountingMap[dstIp] = dstIpCount + 1
            srcPortCountingMap[srcPort] = srcPortCount + 1
            dstPortCountingMap[dstPort] = dstPortCount + 1
        except Exception as e:
            continue

    #l2CountingList = sorted(l2CountingMap.items(), key=operator.itemgetter(1), reverse=True)
    #l3CountingList = sorted(l3CountingMap.items(), key=operator.itemgetter(1), reverse=True)    
    srcIpCountingList = sorted(srcIpCountingMap.items(), key=operator.itemgetter(1), reverse=True)
    dstIpCountingList = sorted(dstIpCountingMap.items(), key=operator.itemgetter(1), reverse=True)    
    srcPortCountingList = sorted(srcPortCountingMap.items(), key=operator.itemgetter(1), reverse=True)    
    dstPortCountingList = sorted(dstPortCountingMap.items(), key=operator.itemgetter(1), reverse=True)

    srcIpCountingList = srcIpCountingList[0:min(TOP_COUNT, len(srcIpCountingList))]
    dstIpCountingList = dstIpCountingList[0:min(TOP_COUNT, len(dstIpCountingList))]
    srcPortCountingList = srcPortCountingList[0:min(TOP_COUNT, len(srcPortCountingList))]
    dstPortCountingList = dstPortCountingList[0:min(TOP_COUNT, len(dstPortCountingList))]

    summaryMap = getSummaryMap(packet)
    summaryMap["duration"] = input_timeout
    summaryMap["total_packet_count"] = len(packet)
    summaryMap["TopNumber"] = TOP_COUNT
    summaryMap["ARP"] = ArpCount
    summaryMap["Other"] = int(summaryMap["Other"]) - ArpCount

    returnMap = {}
    returnMap["SUMMARY"] = summaryMap
    returnMap["SOURCE_IP_COUNT"] = srcIpCountingList
    returnMap["DESTINATION_IP_COUNT"] = dstIpCountingList
    returnMap["SOURCE_PORT_COUNT"] = srcPortCountingList
    returnMap["DESTINATION_PORT_COUNT"] = dstPortCountingList

    print(json.dumps(returnMap))