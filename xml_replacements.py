import argparse
import sys
import os
import re

parser = argparse.ArgumentParser(description='Convert "species id" and "reactions" in a SMBL file')
parser.add_argument('-x', '--xml', required=True, help='input XML file')
parser.add_argument('-o', '--out', required=False, help='Output file. Default is STDOUT')
parser.add_argument('-s', '--swl', action='store_true', default=False,
                    help='Outputs a "switch list" to STDERR of names that have been changed')
parser.add_argument('--nospec', action='store_true', default=False,
                    help='Skip conversion of species ID')
parser.add_argument('--noreac', action='store_true', default=False,
                    help='Skip conversion of reaction IDs')
parser.add_argument('--noabb', action='store_true', default=False,
                    help='Skip abbreviations of cellular  compartments')
args = parser.parse_args()


def spec_transform_func(in_str):
    """
    Extract species or reacion names and ID from row
    :param in_str: string from RE match
    :return: list of pair
    """
    sp_id = re.findall(r'species id=".+?"', in_str)
    sp_name = re.findall(r'name=".+?"', in_str)
    if len(sp_id) != 1 or len(sp_name) != 1:
        raise ValueError('Proble Detected! Can properly parse string: "{}"'.format(in_str))
    return sp_id[0][12:-1], sp_name[0][6:-1]


def reac_transform_func(in_str):
    """
    Extract species or reacion names and ID from row
    :param in_str: string from RE match
    :return: list of pair
    """
    sp_id = re.findall(r'reaction id=".+?"', in_str)
    sp_name = re.findall(r'name=".+?"', in_str)
    if len(sp_id) != 1 or len(sp_name) != 1:
        raise ValueError('Proble Detected! Can properly parse string: "{}"'.format(in_str))
    return sp_id[0][13:-1], sp_name[0][6:-1]


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


# Check if files do or do not exist
if not os.path.isfile(args.xml):
    raise ValueError('XML file {} does not exist'.format(args.xml))

if args.out and os.path.isfile(args.out):
    raise ValueError('Output file {} already exists'.format(args.out))

if args.out:
    sys.stdout = open(args.out, 'w')

# Reading data
with open(args.xml, 'r') as xml_hand:
    in_xml = xml_hand.read()

    # RE term you are searching for
    if not args.noreac:
        re_term = r'<reaction id=".+?" name=".+?" metaid='
        re_matchs = re.findall(re_term, in_xml)
        # Convert to dictionary
        replacements = dict(map(reac_transform_func, re_matchs))
        in_xml = replace_all(in_xml, replacements)
        if args.swl:
            sys.stderr.write("REACTION REPLACEMENTS\n")
            sys.stderr.write("\n".join(["\t".join(my_pair) for my_pair in replacements.items()]) + "\n")
    if not args.nospec:
        re_term = r'<species id=".+?" name=".+?" metaid='
        re_matchs = re.findall(re_term, in_xml)
        # Convert to dictionary
        replacements = dict(map(spec_transform_func, re_matchs))
        in_xml = replace_all(in_xml, replacements)
        if args.swl:
            sys.stderr.write("SPECIES REPLACEMENTS\n")
            sys.stderr.write("\n".join(["\t".join(my_pair) for my_pair in replacements.items()]) + "\n")

# Abbreviations part
replacements = {" [plasma membrane]": "[p]",
                " [cytosol]": "[c]",
                " [nucleoplasm]": "[n]"}

if not args.noabb:
    in_xml = replace_all(in_xml, replacements)

print in_xml