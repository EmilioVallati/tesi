import graphAnalisys
import network_model as nw
from scenario import Event, get_radius, get_scenario
from utility import Stats

SCENARIO_COUNTERVALUE = "./Dataset/countervalue.csv"
SCENARIO_COUNTERFORCE = "./Dataset/counterforce.csv"


if __name__ == '__main__':
    net = nw.NetworkModel()
    net.initialize(False)
    sc = get_scenario(SCENARIO_COUNTERVALUE)
    targets = []
    print("building full list of targets")
    for i in sc:
        tgt = net.get_targets(i.latitude, i.longitude, i.radius)
        for t in tgt:
            if t not in targets:
                targets.append(t)
    print("processing full event")
    ret = net.process_impact(targets, True)
    net.print_dictionaries("poffo")
    #elaborating statistics

    #graphAnalisys.plot_stat_variation(statList, "prova")