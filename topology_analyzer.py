import sys
from os.path import exists
from network_model import Result, DamageReport
import graphAnalisys
import network_model as nw
from utility import Config
import networkx as nx

class SingleScenarioReport:
    def __init__(self):
        self.mode = ""
        self.starting_links = 0
        self.starting_AS = 0
        self.starting_facilities = 0
        self.damage_list = []
        self.lost_facilities = []
        self.lost_AS = []
        self.lost_links = []
        self.graph_nodes_start = 0
        self.graph_nodes_end = 0
        self.starting_giant_component = 0
        self.ending_giant_component = 0
        self.starting_disjoint = 0
        self.ending_disjoint = 0
        self.sample_nodes = []
        self.num_samples = 0
        self.starting_aspl = 0
        self.ending_aspl = 0
        self.starting_isolates = 0
        self.ending_isolates = 0
        self.global_user_loss = 0
        self.global_internet_loss = 0

    def print_report(self):
        print("link mode:")
        print(self.mode)
        print("links contained in the topology")
        print(self.starting_links)
        print("facilities found within database")
        print(self.starting_facilities)
        print("total number of AS in topology (number of nodes in the graph)")
        print(self.graph_nodes_start)
        print("lost facilities:")
        print(len(self.lost_facilities))
        print("lost links:")
        print(len(self.lost_links))
        print("lost AS:")
        print(len(self.lost_AS))
        print("global user lost")
        print(self.global_user_loss)
        print("global internet loss")
        print(self.global_internet_loss)
        print("ending graph nodes")
        print(self.graph_nodes_end)
        print("lost_nodes")
        print(self.graph_nodes_start - self.graph_nodes_end)
        print("starting size of giant component")
        print(self.starting_giant_component)
        print("ending size of giant component")
        print(self.ending_giant_component)
        print("starting number of disjoint components")
        print(self.starting_disjoint)
        print("ending number of disjoint components")
        print(self.ending_disjoint)
        print("number of samples")
        print(self.num_samples)
        print("sample nodes")
        print(self.sample_nodes)
        print("starting sampled aspl")
        print(self.starting_aspl)
        print("ending sampled aspl")
        print(self.ending_aspl)

    def get_global_damage(self):
        total_pop = 0
        total_internet = 0
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


class DynamicStatsReport:
    def __init__(self):
        self.sampling_freq = 0
        self.num_events = 0
        self.max_targets = 0
        self.avg_targets = 0
        self.num_miss = 0
        self.target_distribution = []
        #users
        self.max_damage = 0
        self.avg_damage = 0
        self.damage_distribution = []
        self.damage_list = []
        self.stat_list = []


    def print_report(self):
        print("starting_links")
        print(self.starting_links)
        print("starting_AS")
        print(self.starting_AS)
        print("starting_facilities")
        print(self.starting_facilities)
        print("number of events")
        print(self.num_events)
        print("highest number of targets hit")
        print(self.max_targets)
        print("number of misses")
        print(self.num_miss)
        print("average facilities hit")
        print(self.avg_targets)
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
        print("isolated AS")
        print(self.isolated_AS)
        print("global user lost")
        print(self.global_user_loss)
        print("global internet loss")
        print(self.global_internet_loss)
        print("starting graph nodes")
        print(self.graph_nodes_start)
        print("lost_nodes")
        print(self.lost_nodes)
        print("giant component variation over time plotted in")
        print("number of disjoint components variation over time plotted in")
        print("number of samples")
        print(self.num_samples)
        print("sample nodes")
        print(self.sample_nodes)
        print("sampling frequency")
        print(self.sampling_freq)
        print("starting sampled aspl")
        print(self.starting_aspl)
        print("ending sampled aspl")
        print(self.ending_aspl)
        print("aspl variation over time plotted in")



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
        try:
            self.net.initialize()
        except Exception:
            sys.exit()

        self.samples = self.net.get_samples(self.n_samples)

    # updates topology removing a list of target facilities, generates a single global report
    def process_targets(self, targets, report):
        if self.verbose:
            print("processing next event")
            print("target facilities")
            print(targets)
            print("starting links: " + str(len(self.net.linksList)) + "\n")
        #compiles report
        res = self.net.update_topology(targets, self.verbose)
        for l in res.dead_links:
            report.lost_links.append(res.dead_links)
        for a in res.dead_AS:
            report.lost_AS.append(res.dead_AS)
        if self.verbose:
            remaining = len(self.net.linksList)
            print("lost links: " + str(len(res.dead_links)) + "\n")
            print("remaining links: " + str(remaining) + "\n")
            print("lost AS")
            print(len(res.dead_AS))
        # returns a DamageReport list
        return self.net.get_service_damage(res.dead_AS)



    # produces measurements after elaborating a list of consecutive events defined by geographical coordinates,
    # either consecutively or simultaneously
    def run_scenario(self, event_list, sequential=False):
        #generating report at the start
        report = SingleScenarioReport()
        report.starting_AS = self.net.get_detected_as_num()
        report.starting_facilities = len(self.net.asnDict)
        report.starting_links = len(self.net.linksList)
        report.sample_nodes = self.samples
        report.num_samples = self.n_samples
        report.mode = self.net.mode

        report_d = DynamicStatsReport()



        #number of nodes, giant component size, number of disjoint component, isolated nodes, aspl of sample
        start_stat = graphAnalisys.get_stats(self.net.topology_graph, self.samples)
        report.graph_nodes_start = start_stat.nodes_number
        report.starting_giant_component = start_stat.size_of_giant_component
        report.starting_disjoint = start_stat.disjoint_components
        report.starting_isolates = start_stat.isolated_nodes
        report.starting_aspl = start_stat.aspl
        report.num_events = len(event_list)

        if sequential:
            report_d.num_events = len(event_list)
            report_d.sampling_freq = self.rep_frequency


        cnt = 0
        targets = []
        target_nums = []
        ev_damages = []
        for e in event_list:
            cnt += 1
            ev_tgt = self.net.get_targets(e.latitude, e.longitude, e.radius)
            if cnt%(int(len(event_list)/100)) == 0:
                percent = int((cnt/len(event_list)*100))
                print("progress: " + str(percent) + "%")

            if not sequential:
                if self.verbose:
                    # building complete list of possible targets from the events before processing
                    print("processing targets for event: lat: " + str(e.latitude) + ", lon: " + str(e.longitude)
                          + ", radius: " + str(e.radius))
                for t in ev_tgt:
                    if t not in targets:
                        targets.append(t)
            else:
                target_nums.append(len(ev_tgt))
                if self.verbose:
                    print("processing event: lat: " + str(e.latitude) + ", lon: " + str(e.longitude) + ", radius: " + str(
                        e.radius))
                tot_dmg = 0
                if len(ev_tgt) > 0:
                    dmg = self.process_targets(ev_tgt)
                    for d in dmg:
                        report.damage_list.append(d)
                        tot_dmg += d.users_damage
                ev_damages.append(tot_dmg)
                if cnt%int(self.rep_frequency) == 0:
                    #s = ("ev_" + str(cnt) + "_snapshot")
                    report_d.stat_list.append(graphAnalisys.get_stats(self.net.topology_graph, self.samples))

        if not sequential:
            print("processing full event")
            if len(targets) > 0:
                report.lost_facilities = targets
                damage = self.process_targets(targets, report)
                for d in damage:
                    report.damage_list.append(d)
        else:
            cnt = 0
            tot = 0
            for n in targets:
                tot += n
                if n == 0:
                    cnt += 1
            report_d.num_miss = cnt
            report_d.avg_targets = tot/len(targets)
            report_d.max_targets = max(target_nums)
            tot_d = 0
            for d in ev_damages:
                tot_d += d
            report_d.max_damage = max(ev_damages)
            report_d.avg_damage = tot_d/len(ev_damages)


        #generate final global damage report
        report.get_global_damage()

        #ending stats
        ending_stat = graphAnalisys.get_stats(self.net.topology_graph, self.samples)
        report.graph_nodes_end = ending_stat.nodes_number
        report.ending_giant_component = ending_stat.size_of_giant_component
        report.ending_aspl = ending_stat.aspl
        report.ending_disjoint = ending_stat.disjoint_components
        report.ending_isolates = ending_stat.isolated_nodes

        if sequential:
            graphAnalisys.plot_distributions(self.net.topology_graph, report_d.stat_list)
            graphAnalisys.plot_stat_variation(report_d.stat_list)
        return report

