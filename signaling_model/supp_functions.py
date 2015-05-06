"""
Support functions for model merging
"""
import re
import xml.etree.ElementTree as et
import cobra
import sys


def fetch_spec_genes(my_xml, verbose=False):
    """
    Returns dictionary species: associated genes(uniprot)
    """
    # Setting up values
    n_met = 0
    n_gen = 0
    curr_spec = ""
    spec_dict = {}
    re_prots = r'<rdf:li rdf:resource="urn:miriam:uniprot:[A-Z0-9]+"'
    re_ids = r'<species id=".+?" name=".+?" metaid='
    start = '<listOfSpecies>'
    end = '</listOfSpecies>'
    start_signal = False

    # Beggining of iteration
    with open(my_xml, 'r') as handle:
        for line in handle:
            if start in line:
                start_signal = True
            if not start_signal:
                continue
            match = re.search(re_ids, line)
            pro_match = re.search(re_prots, line)
            if match:
                n_met += 1
                curr_spec = match.group(0)
                curr_spec = curr_spec.split('id="')[1].split('"')[0]
            elif pro_match:
                n_gen += 1
                pro_match = pro_match.group(0)
                pro_match = pro_match.split(':')[-1][:-1]
                spec_dict[curr_spec] = spec_dict.get(curr_spec, set()) | set([pro_match])
            if end in line:
                break

    if verbose:
        print('For {} species {} genes have been found.'.format(n_met, n_gen))
    return spec_dict


def or_links(my_xml, verbose=False):
    """
    Returns list of species names that are OR linked
    """
    keyword = 'entities, any of which can perform'
    matches = []
    n_ors = 0

    tree = et.parse(my_xml)
    root = tree.getroot()
    assert root[0][3].tag.endswith('listOfSpecies')
    species = root[0][3]
    for spec in species:
        if keyword in spec[0][0].text:
            n_ors += 1
            matches.append(spec.attrib['id'])
    if verbose:
        print("There are total of {} species that have OR linked genes.".format(n_ors))
    return matches


def fetc_modifiers(my_xml, verbose=False):
    """
    Returns set of modifiers for each reaction.
    """
    tree = et.parse(my_xml)
    root = tree.getroot()
    modifiersx = {}
    assert root[0][4].tag.endswith('listOfReactions')
    for reaction in root[0][4]:
        name = reaction.attrib['id']
        vals = []

        for mof in reaction.iter('{http://www.sbml.org/sbml/level2/version4}modifierSpeciesReference'):
            vals.append(mof.attrib['species'])
        if vals:
            modifiersx[name] = tuple(vals)
    if verbose:
        print("Total of {} modifiers have been found.".format(sum([len(x) for x in modifiersx.values()])))
    return modifiersx


def build_gene_rela(model, modif, or_linked, spec_genes):
    """
    Given a cobra model and genes (rules) make rules and apply to the model!
    """
    for react in model.reactions:
        reac_id = str(react)
        spec_list = [x for x in modif.get(reac_id, []) if x in spec_genes] + list([met.id for met in react.metabolites
                                                                                   if met.id in spec_genes])
        if len(spec_list) == 0:
            sys.stderr.write('\nWarning reaction "{}" has no species with genes!\n'.format(react.name))
            continue
        all_genes = set([gene for spec in spec_list for gene in spec_genes[spec]])
        or_genes = set([tuple(spec_genes[spec]) for spec in spec_list if spec in or_linked])
        or_genes = [set(g_set) for g_set in or_genes]
        for g_set in or_genes:
            all_genes = all_genes - g_set
        or_genes = ["( " + " OR ".join(subset) + " )" for subset in or_genes]
        react.gene_reaction_rule = " AND ".join(list(all_genes) + or_genes)


def eval_reac(reac, expressions, threshold=5, def_exp=False):
    """
    Evaluates if given cobra reaction is possible given protein expressions
    threshold: minimal treshold to consider it as expressed
    def_exp: True if genes not present in expression should be considered as expressed
    """
    rule = reac.gene_reaction_rule
    boolenized = {gene: int(expressions[gene]) > threshold for gene in expressions}
    genes = set(re.findall(r'[A-Z0-9]+', rule)) - set(['AND', 'OR'])
    for gene in genes:
        re_gene = r"\b{}\b".format(gene)
        rule = re.sub(re_gene, str(boolenized.get(gene, def_exp)), rule)
        rule = rule.replace('AND', 'and')
        rule = rule.replace('OR', 'or')
    return eval(rule)


def load_reactions(f_path):
    exp_dict = {}
    with open(f_path, 'r') as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            line = line.split()
            exp_dict[line[0]] = float(line[1])
    return exp_dict


def save_model(model, sa_file):
    """
    saves given model to a SBML file
    """
    cobra.io.write_sbml_model(model, sa_file, use_fbc_package=False)