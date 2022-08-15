from haversine import haversine, Unit
import configparser

class Config:
    def __init__(self, conf_file = None):
        config = configparser.ConfigParser()
        config.read(conf_file)
        if 'nuclear_warfare' not in config:
            print("invalid conf file!")
            raise Exception
        else:
            # population data for AS network
            if 'CUSTOMER_FILE' in config['nuclear_warfare']:
                self.CUSTOMER_FILE = config['nuclear_warfare']['CUSTOMER_FILE']
            else:
                print("undefined customer file")
                raise Exception

            # topology dataset
            if 'RELFILE' in config['nuclear_warfare']:
                self.RELFILE = config['nuclear_warfare']['RELFILE']
            else:
                print("undefined topology file")
                raise Exception

            # cached topology for quick init
            if 'LINKFILE' in config['nuclear_warfare']:
                self.LINKFILE = config['nuclear_warfare']['LINKFILE']
            else:
                print("undefined topology cache file")
                raise Exception

            # peeringdb facility db
            if 'DBFILE' in config['nuclear_warfare']:
                self.DBFILE = config['nuclear_warfare']['DBFILE']
            else:
                print("undefined database file")
                raise Exception

            # log file
            if 'LOGFILE' in config['nuclear_warfare']:
                self.LOGFILE = config['nuclear_warfare']['LOGFILE']
            else:
                print("undefined log file")
                raise Exception

            # number of samples for average measurements
            if 'NUMSAMPLES' in config['nuclear_warfare']:
                m = config['nuclear_warfare']['NUMSAMPLES']
                if int(m) > 0:
                    self.NUMSAMPLES = m
                else:
                    raise Exception
            else:
                print("undefined sample number")
                raise Exception

            # number of events between measurements
            if 'NUMEVENTS' in config['nuclear_warfare']:
                m = config['nuclear_warfare']['NUMEVENTS']
                if int(m) > 0:
                    self.NUMEVENTS = m
                else:
                    raise Exception
            else:
                print("undefined sample frequency")
                raise Exception
            #conservative or volatile nodes mode
            if 'MODE' in config['nuclear_warfare']:
                m = config['nuclear_warfare']['MODE']
                if m == 'volatile' or m == 'stable':
                    self.MODE = m
                else:
                    print("Only 'volatile' or 'stable' values allowed for MODE")
                    raise Exception
            else:
                print("undefined mode")
                raise Exception
            #full init or load previous topology
            if 'FULL_INIT' in config['nuclear_warfare']:
                m = config['nuclear_warfare']['FULL_INIT']
                if m == 'True' or m == 'False':
                    self.FULL_INIT = m
                else:
                    print("Only 'True' or 'False' values allowed for FULL_INIT")
                    raise Exception
            else:
                print("undefined mode")
                raise Exception


#aspl sampled over nsample nodes
#size of giant component
#number of disjoint components
#average node connectivity
#number of user that lost connection
#%of the internet users losing connectivity

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
