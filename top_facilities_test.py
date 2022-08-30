import sys
import multiprocessing
from os.path import exists
import operator
import graphAnalisys
import network_model as nw
from topology_analyzer import Event, Topology, get_topology, copy_topology
from scenario import get_scenario
from utility import Config
import networkx as nx

SCENARIO_COUNTERVALUE = "./Dataset/countervalue.csv"
SCENARIO_COUNTERFORCE = "./Dataset/counterforce.csv"
DEFAULT_CONFIG = "./default_conf.ini"
SEQUENTIAL = True
RESULT_FILE = "./results.txt"

if __name__ == '__main__':
    #loading configuration file
    if len(sys.argv) == 1:
        print("using default configuration")
        conf_file = DEFAULT_CONFIG
    else:
        conf_file = sys.argv[1]
    if not exists(conf_file):
        print("configuration file not found, shutting down")
        exit()
    else:
        try:
            conf = Config(conf_file)
        except Exception:
            print("error reading configuration file")
            exit()

    print("Number of cpu : ", multiprocessing.cpu_count())

    t_start = get_topology(conf.NUMSAMPLES, conf.NUMEVENTS, conf.CUSTOMER_FILE, conf.RELFILE, conf.LINKFILE, conf.DBFILE,
                 conf.LOGFILE, conf.MODE, conf.FULL_INIT, False)

    as_count_dict = {}
    for f in t_start.net.asnDict:
        as_count_dict[f] = len(t_start.net.asnDict[f])
    print("top 10 facilities by number of AS (facility, n* of AS)")
    sorted_as_dict = sorted(as_count_dict.items(), key=operator.itemgetter(1), reverse=True)
    top_fac = sorted_as_dict[:10]
    tt = []
    for t in top_fac:
        tt.append(t[0])

    print(tt)

    report = t_start.process_event(tt)

    report.print_report()