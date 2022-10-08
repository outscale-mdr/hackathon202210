# x_max_v4.py : suppression de la première fonction
# computing a list of max from a key/value input
# input :
#     * a filename to a file with the list of couple of letter(key) and an integer (value) as (a,3) separate by ';' # output
#     * n number of max to return
# ouput :
#     the list key of the keys of the n max value as python list [a,f,3]
# the resolution must be done in less time than the naive implemented here on big files tests
# ____________
# command : max
# args :
#   - pathfile
#   - n
# n must be changed to 1 of negative or null
# the naive algorithm implemeted
# run is the function called by the test runner


def get_x_max(path, n):
    nbmax = max(1, int(n))

    flist = open(path, "r")
    s = flist.read()
    keys = []
    while len(keys) < nbmax:
        pairs = s.replace("(", "").replace(")", "").split(";")
        m = -1
        key = "NONE"
        for pair in pairs:
            kv = pair.split(",")
            i = int(kv[1])
            if m < i:
                m = i
                key = kv[0]

        maxi = key + "," + str(m)
        keys.append(maxi.split(",")[0])
        s = s.replace("(" + str(maxi) + ");", "").replace(";(" + str(maxi) + ")", "")

    return str(keys)
