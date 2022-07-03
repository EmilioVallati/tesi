import re
HTML_FILE = "Dataset/customers-per-as-measurements.html"


def parse_html(file):
    wrFile = "Dataset/population-data.txt"
    lines = []
    serviceDict = {}
    with open(file) as f:
        for cnt, l in enumerate(f):
            result = re.findall('\[(.*)\]', l)
            for i in result:
                if '0' <= i[0] <= '9':
                    lines.append(i)
        f.close()
    for s in lines:
        vals = s.split(',')
        #index key
        serviceDict[vals[0]] = []
        #ASN
        asn = vals[1][3:-1]
        serviceDict[vals[0]].append(int(asn))
        #CC
        cc = vals[-5][-7:-5]
        serviceDict[vals[0]].append(str(cc))
        #Users
        serviceDict[vals[0]].append(int(vals[-4]))
        #country %
        serviceDict[vals[0]].append(float(vals[-3]))
        #internet %
        serviceDict[vals[0]].append(float(vals[-2]))

        #print(serviceDict[vals[0]])
    return serviceDict

if __name__ == '__main__':
    print(parse_html(HTML_FILE))
