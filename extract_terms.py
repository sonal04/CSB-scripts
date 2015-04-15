import argparse
import re
import os


parser = argparse.ArgumentParser(description='Extract DB terms from a SMBL file')
parser.add_argument('-x', '--xml', required=True, help='input XML file')
args = parser.parse_args()


def replace_all(text, in_dic):
    """
    Make replacemets in a
    :param text: String in which to perform replacements
    :param in_dic: Dictionary of replacements to be made
    :return: String with replacements
    """
    for i, j in in_dic.iteritems():
        text = text.replace(i, j)
    return text


def extractions(re_idterm, sstring, estring):
    """
    Prints out lists of associated terms
    :param re_idterm: extracting parameter
    :param sstring: start string
    :param estring: end string
    :return: None
    """
    start_signal = False
    entry = ''
    with open(args.xml, 'r') as xml_hand:
        for c_line in xml_hand.readlines():
            # find correct position for parsing
            if sstring in c_line:
                start_signal = True
            if not start_signal:
                continue
            # actual parsing
            re_match = re.findall(re_idterm, c_line)
            if re_match:
                if entry:
                    print entry
                sp_name = re.findall(r'name=".+?"', c_line)
                if len(sp_name) != 1:
                    raise ValueError('Proble Detected! Can not extract name from "{}"'.format(c_line))
                entry = replace_all(sp_name[0][6:-1], replacements)
            elif re.findall(re_dbterm, c_line):
                try:
                    entry += "\t" + re.findall(r'urn:miriam:[a-zA-Z0-9:\._:\-%]+"/>', c_line)[0][11:-3]
                except:
                    raise ValueError('You missed something in line "{}"'.format(c_line))

            # ending of parsing part
            if estring in c_line:
                print entry
                return
        raise ValueError('Your set did not properly end!')


re_dbterm = r'<rdf:li rdf:resource="urn:miriam:'

replacements = {" [plasma membrane]": "[p]",
                " [cytosol]": "[c]",
                " [nucleoplasm]": "[n]"}

# execution part
if not os.path.isfile(args.xml):
    raise ValueError('XML file {} does not exist'.format(args.xml))

extractions(r'<species id=".+?" name=".+?" metaid=', "<listOfSpecies>", "</listOfSpecies>")

# print "\n\nList of reactions with their terms"
# extractions(r'<reaction id=".+?" name=".+?" metaid=', "<listOfReactions>", "</listOfReactions>")
