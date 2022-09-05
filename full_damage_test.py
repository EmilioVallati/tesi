import sys
import multiprocessing
from os.path import exists
import operator
import graphAnalisys
import network_model as nw
import numpy as np
from topology_analyzer import Event, Topology, get_topology, copy_topology, EventReport, get_aggregated_result
from scenario import get_scenario
from utility import Config
import networkx as nx
import matplotlib.pyplot as plt
from scipy import stats

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

    cnt = 0
    report_list = []

    for e in t_start.net.asnDict:
        cnt += 1
        tgt = []
        tgt.append(e)
        temp = copy_topology(t_start)
        report = EventReport()
        report = temp.process_event(tgt)
        report_list.append(report)

    get_aggregated_result(report_list)

    damages = []
    l_AS = []
    l_links = []

    #lost links, lost as, user damage
    for r in report_list:
        tot_dmg = 0
        for d in r.damage_list:
            tot_dmg += d.users_damage
        damages.append(tot_dmg)
        l_AS.append(len(r.lost_AS))
        l_links.append(len(r.lost_links))

    #as plot
    print(l_AS)
    l_AS.sort()
    print(l_AS)

    count_a, bins_count_a = np.histogram(l_AS, bins=20)

    # finding the PDF of the histogram using count values
    pdf_a = count_a / sum(count_a)

    # using numpy np.cumsum to calculate the CDF
    # We can also find using the PDF values by looping and adding
    cdf_a = np.cumsum(pdf_a)

    # plotting PDF and CDF
    plt.plot(bins_count_a[1:], pdf_a, color="red", label="PDF")
    plt.plot(bins_count_a[1:], cdf_a, label="CDF")
    plt.legend()

    plt.tight_layout()
    plt.savefig("facility_AS_distr.png")
    plt.close()


    #link plot
    print(l_links)
    l_links.sort()
    print(l_links)

    count_l, bins_count_l = np.histogram(l_links, bins=20)

    # finding the PDF of the histogram using count values
    pdf_l = count_l / sum(count_l)

    # using numpy np.cumsum to calculate the CDF
    # We can also find using the PDF values by looping and adding
    cdf_l = np.cumsum(pdf_l)

    # plotting PDF and CDF
    plt.plot(bins_count_l[1:], pdf_l, color="red", label="PDF")
    plt.plot(bins_count_l[1:], cdf_l, label="CDF")
    plt.legend()

    plt.tight_layout()
    plt.savefig("facility_links_distr.png")
    plt.close()

    #damage plot
    damages.sort()

    # getting data of the histogram
    count, bins_count = np.histogram(damages, bins=20)

    # finding the PDF of the histogram using count values
    pdf = count / sum(count)

    # using numpy np.cumsum to calculate the CDF
    # We can also find using the PDF values by looping and adding
    cdf = np.cumsum(pdf)

    # plotting PDF and CDF
    plt.plot(bins_count[1:], pdf, color="red", label="PDF")
    plt.plot(bins_count[1:], cdf, label="CDF")
    plt.legend()

    plt.tight_layout()
    plt.savefig("facility_damage_distr.png")
    plt.close()

