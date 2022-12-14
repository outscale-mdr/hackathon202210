"""

This file is used to parse the mpeg-ts file in order to get the
delta between PCR and PTS and in order to get stream element statistics

MPEG-TS stream is the usual format used for IPTV (TV over IP), the format
is basic, here some elements:
    - MPEG-TS is composed of 188 Bytes packets;
    - Each packet describes an stream elements (Video, Audio, Subtitles,
    Program information, ...);
    - All packets are not used for streaming a video...
    - Each video or audio packet own a PTS (timestamp) in order to know
    when the element stream is played;
    - Usually video and audio packets are played following a given clock
    called PCR;
    - During streaming (real time), the delta between the packet arrival
    and the PCR is very important, this is something usually monitored
    in the stream pipeline.

"""

import sys
import struct

from optparse import OptionParser

class SystemClock:
    def __init__(self):
        self.PCR = 0x0

class PESPacketInfo:
    def __init__(self):
        self.PTS = 0
        self.streamID = 0
        self.AUType = ""

def readFile(fileHandle, startPos, width):
    fileHandle.seek(startPos,0)
    if width == 4:
        string = fileHandle.read(4)
        if len(string) != 4:
            raise IOError
        return struct.unpack('>L',string[:4])[0]
    elif width == 2:
        string = fileHandle.read(2)
        if len(string) != 2:
            raise IOError
        return struct.unpack('>H',string[:2])[0]
    elif width == 1:
        string = fileHandle.read(1)
        if len(string) != 1:
            raise IOError
        return struct.unpack('>B',string[:1])[0]

def parseAdaptation_Field(fileHandle, n, PCR):
    flags = 0
    adaptation_field_length = readFile(fileHandle,n,1)
    if adaptation_field_length > 0:

        string = fileHandle.read(1)
        if len(string) != 1:
            raise IOError
        flags = struct.unpack('>B', string[:1])[0]

        PCR_flag = (flags>>4)&0x1
        if PCR_flag:
            string = fileHandle.read(6)
            if len(string) != 6:  # check like in the function
                raise IOError
            time1, time2, time3, time4, time5, time6 = struct.unpack('>6B', string)

            PCR_val  = time1 * 0x2000000
            PCR_val += time2 * 0x20000
            PCR_val += time3 * 0x200
            PCR_val += time4 * 2
            PCR_val |= (time5 & 0x80) >> 7

            PCR_val *= 300
            PCR_val |= (time5 & 0x01) << 8
            PCR_val |= time6

            PCR.PCR = PCR_val
    return [adaptation_field_length + 1, flags]

def getPTS(fileHandle, n):
    time1 = readFile(fileHandle,n,1)

    string = fileHandle.read(4)
    if len(string) != 4:  # check like in the function
        raise IOError
    time2, time3, time4, time5 = struct.unpack('>4B', string)

    PTS   = (time1 & 0x0E) >> 1
    PTS <<= 8
    PTS  |= time2
    PTS <<= 7
    PTS  |= (time3 & 0xFE) >> 1
    PTS <<= 8
    PTS  |= time4
    PTS <<= 7
    PTS  |= (time5 & 0xFE) >> 1

    return PTS

def parseIndividualPESPayload(fileHandle, n):
    local = readFile(fileHandle,n,4)
    k = 0
    while (local&0xFFFFFF00) != 0x00000100:
        k += 1;
        if k > 100:
            return "Unknown AU type"
        local = readFile(fileHandle,n+k,4)

    if (((local&0xFFFFFF00) == 0x00000100)&(local&0x1F == 0x9)):
        primary_pic_type = readFile(fileHandle,n+k+4,1)
        primary_pic_type = (primary_pic_type&0xE0)>>5
        if primary_pic_type == 0x0:
            return "IDR_picture"
        else:
            return "non_IDR_picture"

def parsePESHeader(fileHandle, n, PESPktInfo):
    stream_ID = readFile(fileHandle, n+3, 1)
    PES_packetLength = readFile(fileHandle, n+4, 2)
    PESPktInfo.streamID = stream_ID

    k = 6

    if ((stream_ID != 0xBC)& \
        (stream_ID != 0xBE)& \
        (stream_ID != 0xF0)& \
        (stream_ID != 0xF1)& \
        (stream_ID != 0xFF)& \
        (stream_ID != 0xF9)& \
        (stream_ID != 0xF8)):

        PES_packet_flags = readFile(fileHandle, n+5, 4)
        PTS_DTS_flag = ((PES_packet_flags>>14)&0x3)
        PES_header_data_length = PES_packet_flags&0xFF

        k += PES_header_data_length + 3

        if (PTS_DTS_flag == 0x2):
            PTS = getPTS(fileHandle, n+9)
            PESPktInfo.PTS = PTS

        elif (PTS_DTS_flag == 0x3):
            PTS = getPTS(fileHandle, n+9)
            PESPktInfo.PTS = PTS

            DTS = getPTS(fileHandle, n+14)
        else:
            k = k
            return

        auType = parseIndividualPESPayload(fileHandle, n+k)
        PESPktInfo.AUType = auType

def parsePATSection(fileHandle, k):

    local = readFile(fileHandle,k,4)
    table_id = (local>>24)
    if table_id != 0x0:
        return


    section_length = (local>>8)&0xFFF


    transport_stream_id = (local&0xFF) << 8;
    local = readFile(fileHandle, k+4, 4)
    transport_stream_id += (local>>24)&0xFF
    transport_stream_id = (local >> 16)
    version_number = (local>>17)&0x1F
    current_next_indicator = (local>>16)&0x1
    section_number = (local>>8)&0xFF
    last_section_number = local&0xFF;


    length = section_length - 4 - 5
    j = k + 8

    while length > 0:
        local = readFile(fileHandle, j, 4)
        program_number = (local >> 16)
        program_map_PID = local & 0x1FFF

        length = length - 4;
        j += 4



def parsePMTSection(fileHandle, k):

    local = readFile(fileHandle,k,4)

    table_id = (local>>24)
    if table_id != 0x2:
        return



    section_length = (local>>8)&0xFFF


    program_number = (local&0xFF) << 8;

    local = readFile(fileHandle, k+4, 4)

    program_number += (local>>24)&0xFF


    version_number = (local>>17)&0x1F
    current_next_indicator = (local>>16)&0x1
    section_number = (local>>8)&0xFF
    last_section_number = local&0xFF;


    local = readFile(fileHandle, k+8, 4)

    PCR_PID = (local>>16)&0x1FFF

    program_info_length = (local&0xFFF)


    n = program_info_length
    m = k + 12
    while n>0:
        descriptor_tag = readFile(fileHandle, m, 1)
        descriptor_length = readFile(fileHandle, m+1, 1)

        n -= descriptor_length + 2
        m += descriptor_length + 2

    j = k + 12 + program_info_length
    length = section_length - 4 - 9 - program_info_length

    while length > 0:
        local1 = readFile(fileHandle, j, 1)
        local2 = readFile(fileHandle, j+1, 4)

        stream_type = local1;
        elementary_PID = (local2>>16)&0x1FFF
        ES_info_length = local2&0xFFF


        n = ES_info_length
        m = j+5
        while n>0:
            descriptor_tag = readFile(fileHandle, m, 1)
            descriptor_length = readFile(fileHandle, m+1, 1)

            n -= descriptor_length + 2
            m += descriptor_length + 2

        j += 5 + ES_info_length
        length -= 5 + ES_info_length



def parseSITSection(fileHandle, k):
    local = readFile(fileHandle,k,4)

    table_id = (local>>24)
    if table_id != 0x7F:
        return



    section_length = (local>>8)&0xFFF

    local = readFile(fileHandle, k+4, 4)

    section_number = (local>>8)&0xFF
    last_section_number = local&0xFF;

    local = readFile(fileHandle, k+8, 2)
    transmission_info_loop_length = local&0xFFF

    n = transmission_info_loop_length
    m = k + 10
    while n>0:
        descriptor_tag = readFile(fileHandle, m, 1)
        descriptor_length = readFile(fileHandle, m+1, 1)

        n -= descriptor_length + 2
        m += descriptor_length + 2

    j = k + 10 + transmission_info_loop_length
    length = section_length - 4 - 7 - transmission_info_loop_length

    while length > 0:
        local1 = readFile(fileHandle, j, 4)
        service_id = (local1>>16)&0xFFFF;
        service_loop_length = local1&0xFFF


        n = service_loop_length
        m = j+4
        while n>0:
            descriptor_tag = readFile(fileHandle, m, 1)
            descriptor_length = readFile(fileHandle, m+1, 1)

            n -= descriptor_length + 2
            m += descriptor_length + 2

        j += 4 + service_loop_length
        length -= 4 + service_loop_length


def getDeltaPcrPts(pid, pcr, pts):
    listDelta = []
    pcrIdx = 0

    for packet in pts:
        if packet['pid'] != pid:
            continue
        while (pcr[pcrIdx]['packet'] < packet['packet']) & (pcrIdx < len(pcr) - 1):
            pcrIdx += 1
        if pcr[pcrIdx]['packet'] < packet['packet']:
            break
        listDelta.append (packet['pts'] / 90 - pcr[pcrIdx]['pcr'] / 27000)
    return listDelta


def getTrackStat (pid, count, pts):
    firstPacket = 0
    lastPacket = len(pts)-1

    while pts[firstPacket]['pid'] != pid:
        firstPacket += 1

    while pts[lastPacket]['pid'] != pid:
        lastPacket -= 1

    duration = pts[lastPacket]['pts'] / 90 - pts[firstPacket]['pts'] / 90
    size = count * 188

    return { 'duration': int(duration / 1000), 'size': int(size), 'bandwidth': int((8 * 1000 * size) / duration) }

def getPidStats (pidList, pcr, pts):
    stats = []

    for pid in pidList:
        deltaPid = getDeltaPcrPts(pid['pid'], pcr, pts)
        deltaStats = {'min': int(min(deltaPid)), 'max': int(max(deltaPid)), 'average': int(sum(deltaPid) / len(deltaPid))}
        stat = getTrackStat (pid['pid'], pid['count'], pts)

        stats.append ({'pid': pid['pid'], 'deltaPcrPts': deltaStats, 'duration': stat['duration'], 'size': stat['size'], 'bandwidth': stat['bandwidth'] })

    return stats

def parsePcrPts(fileHandle):

    PCR = SystemClock()
    PESPktInfo = PESPacketInfo()

    n = 0
    packet_size = 188

    packetCount = 0

    PESPidList = []
    PTSList = []
    PCRList = []

    try:
        while True:

            PacketHeader = readFile(fileHandle,n,4)

            syncByte = (PacketHeader>>24)


            payload_unit_start_indicator = (PacketHeader>>22)&0x1

            PID = ((PacketHeader>>8)&0x1FFF)

            adaptation_fieldc_trl = ((PacketHeader>>4)&0x3)
            Adaptation_Field_Length = 0

            if (adaptation_fieldc_trl == 0x2)|(adaptation_fieldc_trl == 0x3):
                [Adaptation_Field_Length, flags] = parseAdaptation_Field(fileHandle,n+4,PCR)

                if (flags >> 4)&0x1:
                    discontinuity = False
                    if (flags >> 7)&0x1:
                        discontinuity = True


                    PCRList.append ({'packet':packetCount,'pid':PID, 'pcr':PCR.PCR, 'discontinuity':discontinuity})

            if (adaptation_fieldc_trl == 0x1)|(adaptation_fieldc_trl == 0x3):

                PESstartCode = readFile(fileHandle,n+Adaptation_Field_Length+4,4)

                if (PESstartCode & 0xFFFFFF00) == 0x00000100:

                    if payload_unit_start_indicator == 1:
                        parsePESHeader(fileHandle, n+Adaptation_Field_Length+4, PESPktInfo)

                        PTSList.append ({'packet':packetCount,'pid':PID, 'pts':PESPktInfo.PTS})

                    pidFound = False
                    for index in PESPidList:
                        if index['pid'] == PID:
                            pidFound = True
                            break

                    if not pidFound:
                        PESPidList.append ({'pid':PID, 'count':0})

                elif (((PESstartCode&0xFFFFFF00) != 0x00000100)& \
                    (payload_unit_start_indicator == 1)):

                    pointer_field = (PESstartCode >> 24)
                    table_id = readFile(fileHandle,n+Adaptation_Field_Length+4+1+pointer_field,1)



                    k = n+Adaptation_Field_Length+4+1+pointer_field





            n += packet_size
            for index in PESPidList:
                if index['pid'] == PID:
                    index['count'] += 1
                    break

            packetCount += 1

    except IOError:

        return [PESPidList, PCRList, PTSList]
    else:
        fileHandle.close()
    return [PESPidList, PCRList, PTSList]

def parse_transport_stream(filename):

    fileHandle = open(filename,'rb')

    [pesPidList, pcr, pts] = parsePcrPts(fileHandle)
    stats = getPidStats(pesPidList, pcr, pts)

    return stats


# print(parse_transport_stream("../../media/test_arte.ts"))
