import math
from haversine import haversine, Unit

#aspl sampled over nsample nodes
#size of giant component
#number of disjoint components
#average node connectivity
#number of user that lost connection
#%of the internet users losing connectivity

class Stats:
    def __init__(self):
        self.aspl = 0
        self.size_of_giant_component = 0
        self.disjoint_components = 0
        self.nsample = 0
        self.user_damage = 0
        self.internet_damage = 0

def get_distance(lat1, lon1, lat2, lon2):
    src = (lat1, lon1)
    dest = (lat2, lon2)
    ret = haversine(src, dest)
    #print(ret)
    return ret

def read_rebuilt_links(file):
    links = {}
    # preparing topology
    with open(file) as f:
        for cnt, line in enumerate(f):
            line = line[:-1]
            vals = line.split('|')
            link = str(vals[0])
            link = link[1:-1]
            del vals[0]
            # print(vals)
            k = link.split(", ")
            key = (int(k[0]), int(k[1]))
            links[key] = []
            for v in vals:
                links[key].append(int(v))
        f.close()
    return links

#returns list of links
def read_full_links(file):
    links_list = []
    with open(file) as f:
        for cnt, line in enumerate(f):
            if line[0] != '#':
                vals = line.split('|')
                link = (int(vals[0]), int(vals[1]))
                links_list.append(link)
    f.close()
    return links_list
