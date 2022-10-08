#!/usr/bin/python
import os
import re
import _md5

"""
 In this case you need to produce n files from a template, liste of id and two dates.
dlms is a standard of communication in energy with iot object (smart meter)
You need to remplace the id of the template by the one in file  and change the start and the stop date.

filename_id : filename of the the list of  id 
dt_start : a date in format YYYY-MM-DDTHH:MM:SS
dt_stop : a date in format YYYY-MM-DDTHH:MM:SS
return the list of md5 for each xml string generated in list format 
"""

def compute_md5(file_name):
    hash_md5 = _md5.md5()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def templating_dlms(filename_id, dt_start, dt_stop):
     file = open(os.path.join("/data/media/", filename_id), "r")
     templateName = "/data/media/templating_tpl.xml"
     tplFile = open(templateName,"r")
     tpl = tplFile.read()

     tplFile.close();

     dstart = "2019-08-16T13:35:00" if (len(dt_start) < 4) else dt_start
     dend = "2019-08-16T13:35:00" if (len(dt_stop) < 5) else dt_stop

     md5s = []

     for line in file:
          newID = line.replace("\n", "")
          prefix = "Activation_2.76"

          s = re.sub("<devID>METER(.)+</devID>", "<devID>" + newID + "</devID>", tpl, 1)
          s = re.sub('taskId="' + prefix + '"', 'taskId="' + prefix + '_' + newID + '"', s, 1)
          s = re.sub('<start>([^<])+</start>', '<start>' + dstart + '</start>', s, 1)
          s = re.sub('<stop>([^<])+</stop>', '<stop>' + dend + '</stop>', s, 1)


          #md5_hash = hashlib.md5()
          #Aparamment, hashlib trois fois plus lent que md_5

          md5_hash = compute_md5(filename_id)

          #md5_hash = _md5.md5()
          #md5_hash.update(s.encode("UTF-8"))

          md5s.append(md5_hash.hexdigest())

     return md5s
