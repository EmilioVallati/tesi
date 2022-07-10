import graphAnalisys
import network_model as nw
from scenario import Event, get_radius, get_scenario
from utility import Stats
import math

SCENARIO_COUNTERVALUE = "./Dataset/countervalue.csv"
SCENARIO_COUNTERFORCE = "./Dataset/counterforce.csv"


if __name__ == '__main__':
    net = nw.NetworkModel()
    net.initialize(False)
    sc = get_scenario(SCENARIO_COUNTERVALUE)
    cnt = 0
    statList = []
    #plotting degree distribution only for first and last event
    #total %damage must be collected and measured thorughout the process
    #substituting the single event damage with the total before to make the graph
    total_internet_damage = 0
    nn = int(len(sc)/100)
    print(nn)
    for i in sc:
        print("processing event: lat: " + str(i.latitude) + ", lon: " + str(i.longitude) + ", radius: " + str(i.radius))
        if cnt == 0:
            ret = net.process_impact(i.latitude, i.longitude, i.radius, True, True, "start")
            total_internet_damage += ret.internet_damage
            ret.internet_damage = total_internet_damage
            statList.append(ret)
            cnt += 1
        elif cnt == len(sc)-1:
            ret = net.process_impact(i.latitude, i.longitude, i.radius, True, True, "end")
            total_internet_damage += ret.internet_damage
            ret.internet_damage = total_internet_damage
            statList.append(ret)
            cnt += 1
        else:
            ret = net.process_impact(i.latitude, i.longitude, i.radius, False, True)
            total_internet_damage += ret.internet_damage
            ret.internet_damage = total_internet_damage
            #sampling for stats
            if cnt%100 == 0:
                statList.append(ret)
            if cnt%(int(len(sc)/100)) == 0:
                percent = int((cnt/len(sc)*100))
                print("progress: " + str(percent) + "%")
            cnt += 1

    #elaborating statistics
    graphAnalisys.plot_stat_variation(statList, "prova")