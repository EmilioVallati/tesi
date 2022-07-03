from __future__ import division

from os.path import exists
import itertools
import sqlite3
from sqlite3 import Error
import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx
from itertools import groupby

from utility import get_distance, read_rebuilt_links, read_full_links

from graphAnalisys import test_degree, plot_topology, test_degree_distribution

from population_dataset_extractor import parse_html

#default config
# population data for AS network
CUSTOMER_FILE = "Dataset/customers-per-as-measurements.html"

# topology dataset
RELFILE = 'Dataset/20220601.as-rel.v6-stable.txt'
# cached topology for quick init
LINKFILE = 'links.txt'
# peeringdb facility db
DBFILE = './Dataset/peeringdb.sqlite3'
# log file
LOGFILE = 'log'


# collects failed lins and AS after a facility is removed
class Result:
    def __init__(self):
        self.dead_links = []
        self.dead_AS = []

class networkModel:
    def __init__(self, cf=CUSTOMER_FILE, rf=RELFILE, lf=LINKFILE, dbf=DBFILE, logf=LOGFILE):
        #file names init
        self.cf = cf
        self.rf = rf
        self.lf = lf
        self.dbf = dbf
        self.logf = logf

        # key: fac_id (int) {lat (float), long (float), name (str)}
        self.facilityDict = {}

        # key: fac_id (int) {asn_list}
        self.asnDict = {}

        # topology links list (asn1, asn2) (int, int)
        self.linksList = []

        # as customer service dataset
        # key: entry_id (AS, country code, #users, % of population serviced, % of internet served) (int, str, int, float, float)
        self.serviceDict = {}

        #separated group of links that can be reproduced in facilities
        self.detectableLink = {}

    # returns facilities within 'size' from center
    def check_impact(self, lat, lon, size):
        targets = []
        for entry in self.facilityDict:
            if get_distance(lat, lon, self.facilityDict[entry][0], self.facilityDict[entry][1]) < size:
                targets.append(entry)
        return targets

    # returns list of links deleted from topology
    def remove_facility(self, fac_id):
        count = 0
        ret = Result()
        if fac_id in self.asnDict:
            del self.asnDict[fac_id]
        for link in self.detectableLinks:
            # print("looking for " + str(fac_id) + " into " + str(detectableLinks[link]))
            if fac_id in self.detectableLinks[link]:
                count += 1
                # print(str(fac_id) + " fac_id found for link " + str(link))
                self.detectableLinks[link].remove(fac_id)
                # no more facility for a link means it's dead
                if len(self.detectableLinks[link]) == 0:
                    ret.dead_links.append(link)
        for l in ret.dead_links:
            # removing dead links from detectable list and topology
            del self.detectableLinks[l]
            # searching if single AS are still available in facilities
            ll = list(l)
            f1 = 0
            f2 = 0
            l1 = 0
            l2 = 0
            for e in self.asnDict:
                if l[0] in self.asnDict[e]:
                    f1 += 1
                if l[1] in self.asnDict[e]:
                    f2 += 1

            # removing from topology
            if l in self.linksList:
                self.linksList.remove(l)

            # looking for links in topology containing the AS
            for entry in self.linksList:
                ee = list(entry)
                if ll[0] in ee:
                    l1 += 1
                if ll[1] in ee:
                    l2 += 1

            # print("AS " + str(l[0]) + " found in " + str(f1) + " facilities")
            # print("AS " + str(l[0]) + " found in " + str(l1) + " links")
            # print("AS " + str(l[1]) + " found in " + str(f2) + " facilities")
            # print("AS " + str(l[1]) + " found in " + str(l2) + " links")

            if f1 == 0 and l1 == 0:
                ret.dead_AS.append(l[0])
                print("AS " + str(l[0]) + " no longer connected!")
            if f2 == 0 and l2 == 0:
                ret.dead_AS.append(l[1])
                print("AS " + str(l[1]) + " no longer connected!")

        # if count != 0:
        # print("facility " + str(fac_id) + " removed from " + str(count) + " links\n")
        # if len(deleted_links) == 0:
        # print("no links lost\n")
        # if len(deleted_links) != 0:
        # print(str(len(deleted_links)) + " links lost")
        return ret

    def update_topology(self, targets):
        starting_links = len(self.linksList)
        dead_links = []
        dead_AS = []
        # removing facility
        for t in targets:
            print("removing facility " + str(t) + "\n")
            ret = self.remove_facility(t)
            # collect dead links for statistics
            for l in ret.dead_links:
                dead_links.append(l)
            for a in ret.dead_AS:
                dead_AS.append(a)
        remaining = len(self.linksList)
        print("dead_links")
        print(len(dead_links))
        print("dead_AS")
        print(len(dead_AS))

        # measure the impact of the event on the service
        self.get_service_damage(dead_AS)
        # rebuilding the topology (for each link remaining we search for a faculty that houses both AS)
        print("starting links: " + str(starting_links) + "\n")
        print("lost links: " + str(len(dead_links)) + "\n")
        print("remaining links: " + str(remaining) + "\n")

    def print_dictionaries(self, filename):
        wrFilename1 = filename + 'facility.txt'
        wrFilename2 = filename + 'facnet.txt'
        wrFilename3 = filename + 'detectable-links.txt'
        wrFilename4 = filename + 'service.txt'
        wrFilename5 = filename + 'total-links.txt'
        with open(wrFilename1, 'w', encoding="utf-8") as wrF:
            for e1 in self.facilityDict:
                wrF.write(str(e1) + ' ' + str(self.facilityDict[e1]) + "\n")
            wrF.close()
        with open(wrFilename2, 'w', encoding="utf-8") as wrF:
            for e2 in self.asnDict:
                wrF.write(str(e2) + ' ' + str(self.asnDict[e2]) + "\n")
            wrF.close()
        with open(wrFilename3, 'w', encoding="utf-8") as wrF:
            for e3 in self.detectableLinks:
                wrF.write(str(e3) + ' ' + str(self.detectableLinks[e3]) + "\n")
            wrF.close()
        with open(wrFilename4, 'w', encoding="utf-8") as wrF:
            for e4 in self.serviceDict:
                wrF.write(str(e4) + ' ' + str(self.serviceDict[e4]) + '\n')
            wrF.close()
        with open(wrFilename5, 'w', encoding="utf-8") as wrF:
            for e5 in self.linksList:
                wrF.write(str(e5))
            wrF.close()

    # populates the asnDict and facilityDict dictionaries
    def populate_facilities(self):
        """ create a database connection to a SQLite database """
        conn = None
        try:
            conn = sqlite3.connect(self.dbf)
            cur = conn.cursor()
            cur.execute(
                "SELECT id, latitude, longitude, name FROM peeringdb_facility where latitude is not NULL and "
                "longitude is not NULL;")
            facilities = cur.fetchall()

            for fac in facilities:
                self.facilityDict[fac[0]] = [float(fac[1]), float(fac[2]), fac[3]]

            cur.execute("SELECT local_asn, fac_id from peeringdb_network_facility;")
            asn = cur.fetchall()

            for entry in asn:
                if entry[1] in self.asnDict.keys():
                    self.asnDict[entry[1]].append(entry[0])
                else:
                    self.asnDict[entry[1]] = [entry[0]]

        except Error as e:
            print("error")
            print(e)
        finally:
            if conn:
                conn.close()

    def build_topology_full(self):

    def build_topology_quick(self):
        for l in read_full_links(self.rf):
            self.linksList.append(l)
        #print(len(self.linksList))
        return read_rebuilt_links(self.lf)

    def initialize(self, full_init):
        #dictionaries initialization
        #facilityDict and asnDict
        self.populate_facilities()

        #serviceDict
        self.serviceDict = parse_html(self.cf)

        #list of links and detectableLinks
        if full_init:
            #build topology from full dataset
            self.build_topology_full()
        elif exists(self.lf):
            #use preprocessed data from file
            self.build_topology_quick()
        else:
            print("ERROR, TOPOLOGY FILE NOT FOUND")

