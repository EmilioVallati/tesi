import sys
from os.path import exists
from network_model import Result, DamageReport
import graphAnalisys
import network_model as nw
from utility import Config
import networkx as nx

class ScenarioReport:
    def __init__(self):
        self.damage_list = []
        self.stat_list = []
        self.lost_facilities = []
        self.lost_AS = []
        self.lost_links = []
        self.global_user_loss = 0
        self.global_internet_loss = 0

    def print_report(self):
        print("damage_list")
        print(self.damage_list)
        print("stat_list")
        print(self.stat_list)
        print("lost facilities:")
        print(self.lost_facilities)
        print("lost links:")
        print(self.lost_links)
        print("lost AS:")
        print(self.lost_AS)
        print("global user lost")
        print(self.global_user_loss)
        print("global internet loss")
        print(self.global_internet_loss)

    def get_global_damage(self):
        total_pop = 0
        total_internet = 0
        print(self.damage_list)
        for r in self.damage_list:
            total_pop += r.users_damage
            total_internet += r.total_percent
            print(
                "country code: " + str(r.cc) +
                " service lost for " + str(r.users_damage) + " users, " + str(r.local_percent) +
                "% of national coverage, totaling " + str(r.total_percent) + "% of global internet infrastructure")

        print("total damage: " + str(total_pop) + " users lost service, for " +
              str(total_internet) + "% of the total internet")

        # generating global report
        self.global_user_loss = total_pop
        self.global_internet_loss = total_internet



class Event:
    def __init__(self, lat, lon, dist):
        self.latitude = lat
        self.longitude = lon
        self.radius = dist

class Topology:
    def __init__(self, n_samples, rep_frequency, c_file, r_file, l_file, db_file, log_file, mode, full_init, v):
        self.verbose = v
        self.n_samples = n_samples
        self.rep_frequency = rep_frequency
        # creating topology
        self.net = nw.NetworkModel(c_file, r_file, l_file, db_file, log_file, mode, full_init)
        self.net.initialize()

        self.samples = self.net.get_samples(self.n_samples)

    # updates topology removing a list of target facilities, generates a single global report
    def process_targets(self, targets):
        if self.verbose:
            print("processing next event")
            print("target facilities")
            print(targets)
            print("starting links: " + str(len(self.net.linksList)) + "\n")
        #returns a Result
        res = self.net.update_topology(targets, self.verbose)
        if self.verbose:
            remaining = len(self.net.linksList)
            print("lost links: " + str(len(res.dead_links)) + "\n")
            print("remaining links: " + str(remaining) + "\n")
            print("lost AS list")
            print(res.dead_AS)
        # returns a DamageReport list
        return self.net.get_service_damage(res.dead_AS)

    # produces measurements after elaborating a list of consecutive events defined by geographical coordinates,
    # either consecutively or simultaneously
    def run_scenario(self, event_list, sequential=False):
        #generating report at the start
        report = ScenarioReport()
        report.stat_list.append(graphAnalisys.get_stats(self.net.topology_graph, self.samples, "start_snapshot.txt"))
        cnt = 0
        targets = []
        for e in event_list:
            cnt += 1
            ev_tgt = self.net.get_targets(e.latitude, e.longitude, e.radius)
            if cnt%(int(len(event_list)/100)) == 0:
                percent = int((cnt/len(event_list)*100))
                print("progress: " + str(percent) + "%")

            if not sequential:
                # building complete list of possible targets from the events before processing
                print("processing targets for event: lat: " + str(e.latitude) + ", lon: " + str(e.longitude)
                      + ", radius: " + str(e.radius))
                for t in ev_tgt:
                    if t not in targets:
                        targets.append(t)
            else:
                print("processing event: lat: " + str(e.latitude) + ", lon: " + str(e.longitude) + ", radius: " + str(
                    e.radius))
                if len(ev_tgt) > 0:
                    dmg = self.process_targets(ev_tgt)
                    for d in dmg:
                        report.damage_list.append(d)
                if cnt%int(self.rep_frequency) == 0:
                    s = ("ev_" + str(cnt) + "_snapshot")
                    report.stat_list.append(graphAnalisys.get_stats(self.net.topology_graph, self.samples, s))

        if not sequential:
            print("processing full event")
            if len(targets) > 0:
                report.damage_list = self.process_targets(targets)
        #generate final global damage report
        report.get_global_damage()

        report.stat_list.append(graphAnalisys.get_stats(self.net.topology_graph, self.samples, "end_snapshot"))
        return report

