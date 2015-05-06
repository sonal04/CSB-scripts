"""
Main file for running merging of signaling pathways
"""


from supp_functions import *


def build_pathway(pathway):
    print("######################")
    print("#BUILDING NEW PATHWAY#")
    print("######################")
    print("NAME:", pathway)
    modifiers = fetc_modifiers(pathway, verbose=True)
    or_species = or_links(pathway, verbose=True)
    spec_genes = fetch_spec_genes(pathway, verbose=True)
    my_model = cobra.io.read_sbml_model(pathway)
    build_gene_rela(my_model, modifiers, or_species, spec_genes)
    print('{} reactions model'.format(len(my_model.reactions)))
    print('{} metabolites model'.format(len(my_model.metabolites)))
    print('{} genes model'.format(len(my_model.genes)))
    print('######################')
    print()
    return my_model

comple_model = cobra.Model('Complete signaling')

for my_pathway in ["./pathways/AKT.xml", "./pathways/PDGF.xml", "./pathways/RAF.xml"]:
    model_addition = build_pathway(my_pathway)

    for reac in model_addition.reactions:
        if reac.id in comple_model.reactions:
            # sys.stderr.write('\nWarning duplicated pathway "{}"!\n'.format(reac.id))
            continue
        else:
            comple_model.add_reaction(reac)
    print('{} reactions in model'.format(len(comple_model.reactions)))
    print('{} metabolites in model'.format(len(comple_model.metabolites)))
    print('{} genes in model'.format(len(comple_model.genes)))
    print()


my_expressions = load_reactions("AKT_expressions.txt")

for reac in comple_model.reactions:
    if not eval_reac(reac, my_expressions, threshold=15, def_exp=False):
        reac.delete()

print("In model (after filtration there are) there are {} genes left:".format(len(comple_model.reactions)))
#save_model(comple_model, "merged_signaling.xml")
