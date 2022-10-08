import json
from collections import OrderedDict
import datetime

"""
In this case, it's a classic frame decoding problem

inputs : 
frame : a frame in hexa with type string

output:  
json decoded with no blank type string
or the error message

"""


DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
FOS_LIST = ["CC29","23FE"]



def decode_hex_to_dec(hexa_string):
    n = int(hexa_string[:2], 16)
    if n<128:
        return n
    else:
        return n-256


def decode_date(hexa_string):
    # minutes
    minute = int(hexa_string[0:2], 16)%64
    # hour
    hour = int(hexa_string[2:4], 16)%32
    # day
    day = int(hexa_string[4:6], 16)%32
    # month
    month = int(hexa_string[6:8], 16)%16
    # year
    year_thousand = 1900 + 100 * ((int(hexa_string[2:4], 16)%128)//32)
    year_cut = int(str("{0:08b}".format(int(hexa_string[6:8], 16)))[0:4] + str("{0:08b}".format(int(hexa_string[4:6], 16)))[0:3],2)
    year = year_thousand + year_cut

    date = datetime.datetime(year, month, day, hour, minute)
    return date



def frame_to_json(frame):
    date = decode_date(frame[106:114])

    return OrderedDict([
        ("FOS", frame[2:6]),
        ("FFC", frame[6:10]),
        ("MetrologicalSerialNumber", frame[10:26]),
        ("CustomerSerialNumber", frame[26:58]),
        ("Backflow",
            OrderedDict([
                ("value", decode_hex_to_dec(frame[58:66])),
                ("unit", "m3")
            ])
         ),
        ("SignalStrenght",
             OrderedDict([
                 ("value", decode_hex_to_dec(frame[66:70])),
                 ("unit", "dbm")
            ])
         ),
        ("SignalQuality",
         OrderedDict([
             ("value", decode_hex_to_dec(frame[70:72])),
             ("unit", "dbm")
         ])
         ),
        ("Alarms", frame[72:80]),
        ("Battery Remaining",
             OrderedDict([
                 ("value", decode_hex_to_dec(frame[80:84])),
                 ("unit", "days")
             ])
         ),
        ("Operating Time",
         OrderedDict([
             ("value", decode_hex_to_dec(frame[84:88])),
             ("unit", "days")
         ])
         ),
        ("Customer Location", frame[88:104]),
        ("Operator Specific Data", frame[104:106]),
        ("Date_Time",
         OrderedDict([
             ("value", date.strftime(DATE_FORMAT)),
             ("storage", 1)
         ])
         ),
        ("BaseIndex",
         OrderedDict([
             ("value", decode_hex_to_dec(frame[114:122])),
             ("unit", "m3"),
             ("storage", 1)
         ])
         ),
        ("CompactProfile",[
         OrderedDict([
             ("value", decode_hex_to_dec(frame[128:132])),
             ("unit", "m3"),
             ("storage", 1),
             ("date", (date + datetime.timedelta(minutes=-15)).strftime(DATE_FORMAT))

         ]),
            OrderedDict([
                ("value", decode_hex_to_dec(frame[132:136])),
                ("unit", "m3"),
                ("storage", 1),
                ("date", (date + datetime.timedelta(minutes=-30)).strftime(DATE_FORMAT))

            ]),
            OrderedDict([
                ("value", decode_hex_to_dec(frame[136:140])),
                ("unit", "m3"),
                ("storage", 1),
                ("date", (date + datetime.timedelta(minutes=-45)).strftime(DATE_FORMAT))

            ]),
            OrderedDict([
                ("value", decode_hex_to_dec(frame[136:144])),
                ("unit", "m3"),
                ("storage", 1),
                ("date", (date + datetime.timedelta(minutes=-60)).strftime(DATE_FORMAT))

            ])
         ]
         ),

    ])


def decode_frame(frame):
    s = ""
    if len(frame) != 144:
        s = "Invalid frame"
    elif frame[0:2] != "79":
        s = "Frame doesn't start with 79"
    elif frame[2:6] not in FOS_LIST:
        s = "Invalid FOS"
    else:
        frame_dict = frame_to_json(frame)
        s = json.dumps(frame_dict, indent=4)
    return s
