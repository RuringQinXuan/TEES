import sys, os
from collections import defaultdict
extraPath = os.path.dirname(os.path.abspath(__file__))+"/../.."
sys.path.append(extraPath)
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import cElementTree as ET
import Utils.ElementTreeUtils as ETUtils
import re

RETYPE = type(re.compile('dummy'))
    
def mapAttributes(parent, elementName, attributes, counts):
    for element in parent.getchildren():
        if element.tag == elementName:
            for name in attributes.keys():
                values = attributes[name]
                currentValue = element.get(name)
                if currentValue in values:
                    newValue = values[currentValue]
                    if newValue == None:
                        del element.attrib[name]
                        counts["del:" + elementName + ":" + name + ":" + str(currentValue)] += 1
                    else:
                        element.set(name, newValue)
                        counts["map:" + elementName + ":" + name + ":" + str(currentValue) + "->" + str(newValue)] += 1
        mapAttributes(element, elementName, attributes, counts)

def processCorpus(input, output, rules):
    if rules == None:
        raise Exception("No mapping rules defined")
    elif isinstance(rules, basestring):
        rules = eval(rules)
    print >> sys.stderr, "Mapping attributes, rules =", rules
    print >> sys.stderr, "Loading corpus file", input
    corpusTree = ETUtils.ETFromObj(input)
    corpusRoot = corpusTree.getroot()
    
    counts = defaultdict(int)
    for key in sorted(rules.keys()):
        mapAttributes(corpusRoot, key, rules[key], counts)
    
    print >> sys.stderr, "Mapped", dict(counts)
    
    if output != None:
        print >> sys.stderr, "Writing output to", output
        ETUtils.write(corpusRoot, output)
    return corpusTree

if __name__=="__main__":
    import sys
    print >> sys.stderr, "##### Map attributes #####"
    
    from optparse import OptionParser
    optparser = OptionParser(usage="%prog [options]\nPath generator.")
    optparser.add_option("-i", "--input", default=None, dest="input", help="Corpus in interaction xml format", metavar="FILE")
    optparser.add_option("-o", "--output", default=None, dest="output", help="Output file in interaction xml format.")
    optparser.add_option("-r", "--rules", default=None, dest="rules", help="dictionary of python dictionaries with attribute:value pairs.")    
    (options, args) = optparser.parse_args()
    
    if options.input == None:
        print >> sys.stderr, "Error, input file not defined."
        optparser.print_help()
        sys.exit(1)
    if options.output == None:
        print >> sys.stderr, "Error, output file not defined."
        optparser.print_help()
        sys.exit(1)

    # Rules e.g. "{'element':{'attrname':{'oldvalue':'newvalue'}}}"
    rules = eval(options.rules)
    print >> sys.stderr, "Rules:", rules
    processCorpus(options.input, options.output, rules)
