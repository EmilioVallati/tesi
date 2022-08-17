import sys
from os.path import exists
import graphAnalisys
import network_model as nw
from topology_analyzer import Event, Topology, ScenarioReport
from scenario import get_scenario
from utility import Config
import networkx as nx

SCENARIO_COUNTERVALUE = "./Dataset/countervalue.csv"
SCENARIO_COUNTERFORCE = "./Dataset/counterforce.csv"
DEFAULT_CONFIG = "./default_conf.ini"
SEQUENTIAL = True

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

    t = Topology(conf.NUMSAMPLES, conf.NUMEVENTS, conf.CUSTOMER_FILE, conf.RELFILE, conf.LINKFILE, conf.DBFILE,
                 conf.LOGFILE, conf.MODE, conf.FULL_INIT, True)

    sc = get_scenario(SCENARIO_COUNTERVALUE)
    #plotting degree distribution only for first and last event
    #total %damage must be collected and measured thorughout the process
    #substituting the single event damage with the total before to make the graph
    print("total events: " + str(len(sc)))

    report = t.run_scenario(sc, SEQUENTIAL)

    report.print_report()
    #elaborating statistics
    graphAnalisys.plot_stat_variation(report.stat_list, "prova")