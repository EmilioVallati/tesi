from __future__ import division

from os.path import exists
import sqlite3
from sqlite3 import Error

import graphAnalisys
from utility import get_distance, read_rebuilt_links, read_full_links, Config

from population_dataset_extractor import parse_html

# collects failed lins and AS after a facility is removed
class Result:
    def __init__(self):
        self.dead_links = []
        self.dead_AS = []
        self.users_damage = 0
        self.internet_damage = 0

class NetworkModel:
    def __init__(self, conf_file):
        #file names init
        self.cf = conf_file.CUSTOMER_FILE
        self.rf = conf_file.RELFILE
        self.lf = conf_file.LINKFILE
        self.dbf = conf_file.DBFILE
        self.logf = conf_file.LOGFILE
        self.ns = conf_file.NUMSAMPLES

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
        self.detectableLinks = {}


    # returns facilities within 'size' from center
    def get_targets(self, lat, lon, size):
        targets = []
        for entry in self.facilityDict:
            if get_distance(lat, lon, self.facilityDict[entry][0], self.facilityDict[entry][1]) < size:
                targets.append(entry)
        return targets

    # returns list of links deleted from topology
    def remove_facility(self, fac_id, logging=False):
        count = 0
        ret = Result()
        if fac_id in self.asnDict:
            del self.asnDict[fac_id]
        for link in self.detectableLinks:
            if logging:
                print("looking for " + str(fac_id) + " into " + str(self.detectableLinks[link]))
            if fac_id in self.detectableLinks[link]:
                count += 1
                if logging:
                    print(str(fac_id) + " fac_id found for link " + str(link))
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

            if logging:
                print("AS " + str(l[0]) + " found in " + str(f1) + " facilities")
                print("AS " + str(l[0]) + " found in " + str(l1) + " links")
                print("AS " + str(l[1]) + " found in " + str(f2) + " facilities")
                print("AS " + str(l[1]) + " found in " + str(l2) + " links")

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

    #removes target facilities and returns list of dead links and AS
    def update_topology(self, targets, logging=False):
        # removing facility
        ret1 = Result()
        long = False
        cnt = 0
        if len(targets) >= 100:
            long = True
        for t in targets:
            if long:
                cnt += 1
                if cnt % (int(len(targets) / 100)) == 0:
                    percent = int((cnt / len(targets) * 100))
                    print("progress: " + str(percent) + "%")

            if logging:
                print("removing facility " + str(t) + "\n")
            ret = self.remove_facility(t)
            # collect dead links for statistics
            for l in ret.dead_links:
                ret1.dead_links.append(l)
            for a in ret.dead_AS:
                ret1.dead_AS.append(a)
        #measuring damage
        ret1 = self.get_service_damage(ret1)
        if logging:
            print("total damage: " + str(ret1.users_damage) + " users lost service, for " + str(
                ret1.internet_damage) + "% of the total internet")

        return ret1


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
        print("getting facilities geographical coordinates from peeringdb...")
        try:
            conn = sqlite3.connect(self.dbf)
            cur = conn.cursor()
            cur.execute(
                "SELECT id, latitude, longitude, name FROM peeringdb_facility where latitude is not NULL and "
                "longitude is not NULL;")
            facilities = cur.fetchall()

            for fac in facilities:
                self.facilityDict[fac[0]] = [float(fac[1]), float(fac[2]), fac[3]]
            print("facilities found:")
            print(len(self.facilityDict))

            print("building list of facilities per AS using peeringdb database...")
            cur.execute("SELECT DISTINCT local_asn from peeringdb_network_facility;")
            c = cur.fetchall()
            print("number of AS found within peeringdb facilities:")
            print(len(c))
            cur.execute("SELECT local_asn, fac_id from peeringdb_network_facility;")
            asn = cur.fetchall()
            for entry in asn:
                if entry[1] in self.asnDict.keys():
                    self.asnDict[entry[1]].append(entry[0])
                else:
                    self.asnDict[entry[1]] = [entry[0]]
            print("number of facilities found within peeringdb with at least one AS:")
            print(len(self.asnDict))

        except Error as e:
            print("error")
            print(e)
        finally:
            if conn:
                conn.close()

    def build_topology_full(self):
        wrFilename3 = self.lf
        # preparing detectable topology
        # intermediate dataset detectableLinks contains only links that can be recreated in facilities present in asnDict
        for link in self.linksList:
            l = list(link)
            key = (int(l[0]), int(l[1]))
            #links are bidirectional, so inverted src, dest count as same key
            inv_key = (int(l[1]), int(l[0]))

            #searching for facilities containing both src, dest AS
            for fac in self.asnDict:
                if l[0] in self.asnDict[fac] and l[1] in self.asnDict[fac]:
                    if key not in self.detectableLinks.keys() and inv_key not in self.detectableLinks.keys():
                        self.detectableLinks[key] = []
                        self.detectableLinks[key].append(fac)
                    elif key in self.detectableLinks.keys():
                        if fac not in self.detectableLinks[key]:
                            self.detectableLinks[key].append(fac)
                    else:
                        if fac not in self.detectableLinks[inv_key]:
                            self.detectableLinks[inv_key].append(fac)
        # saving detectableLinks for faster access in later runs
        print("number of links that can be reproduced inside peeringdb facilities")
        print(len(self.detectableLinks))
        print("saving detectable topology in " + str(wrFilename3))
        with open(wrFilename3, 'w', encoding="utf-8") as wrF:
            for entry in self.detectableLinks:
                string = str(entry)
                for i in self.detectableLinks[entry]:
                    string += "|"
                    string += str(i)
                string += "\n"
                wrF.write(string)
            wrF.close()

    def build_topology_quick(self):
        self.detectableLinks = read_rebuilt_links(self.lf)
        print("number of links read:")
        print(len(self.detectableLinks))

    def initialize(self, full_init):
        print("initializing topology...")
        #dictionaries initialization
        #facilityDict and asnDict
        self.populate_facilities()

        #serviceDict
        print("collecting customer service data...")
        self.serviceDict = parse_html(self.cf)

        #list of links and detectableLinks
        print("reading link list from " + str(self.rf))
        for l in read_full_links(self.rf):
            self.linksList.append(l)
        print("number of links in full topology:")
        print(len(self.linksList))

        #detectableLinks
        if full_init:
            #build topology from full dataset
            print("generating detectable topology from scratch...")
            self.build_topology_full()

        elif exists(self.lf):
            #use preprocessed data from file
            print("reading detectable links from file")
            self.build_topology_quick()
        else:
            print("ERROR, TOPOLOGY FILE NOT FOUND")

    # prints an evaluation of how much population, internet structure would be affected by a loss of a number of AS
    def get_service_damage(self, result, logging=True):

        # measure the impact of the event on the service
        # rebuilding the topology (for each link remaining we search for a faculty that houses both AS)
        # AS are not unique and can appear multiple times if they appear in different countries
        entries = []
        for e in self.serviceDict.keys():
            if self.serviceDict[e][0] in result.dead_AS:
                entries.append(self.serviceDict[e])
        # for each country code show damage
        countries = {}
        # collecting entries for each cc
        for entry in entries:
            if entry[1] not in countries.keys():
                countries[entry[1]] = []
            countries[entry[1]].append(entry)
        total_pop = 0
        total_internet = 0
        for c in countries:
            local_percent = 0
            local_pop = 0
            local_internet = 0
            for c1 in countries[c]:
                local_pop += c1[2]
                local_percent += c1[3]
                local_internet += c1[4]
            total_pop += local_pop
            total_internet += local_internet

            if logging:
                print(
                    "country code: " + str(c) +
                    " service lost for " + str(local_pop) + " users, " + str(local_percent) +
                    "% of national coverage, totaling " + str(local_internet) + "% of global internet infrastructure")

        result.users_damage = total_pop
        result.internet_damage = total_internet
        return result

    def get_stats(self):
        stats = graphAnalisys.get_stats(self.linksList, self.ns)
        return stats

    #returns object containing dead links and dead AS
    def process_impact(self, targets, logging=False):
        starting_links = len(self.linksList)
        if(logging):
            print("starting links: " + str(starting_links) + "\n")

        result = self.update_topology(targets, logging)

        #damage% is always needed for cumulative measurement
        if(logging):
            remaining = len(self.linksList)
            print("lost links: " + str(len(result.dead_links)) + "\n")
            print("remaining links: " + str(remaining) + "\n")

        return result

