import os, sys
import requests
import json
import django
import argparse

'''
This is a command line script to import data from BIOSNAP dataset (http://snap.stanford.edu/biodata/) into the 
side-effects app. Documentation is intrinsic to the argparse arguments. 
'''

def get_or_create_drug_by_cid(cid):
    # The following import directive must be left here
    from side_effects.models import Drug, Effect, Interaction

    property_list = ["Title", "MolecularFormula"]  # To change this effectively we need to change the model
    request_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/" + \
                  cid + "/property/" + ','.join(property_list) + "/JSON"

    print("Getting CID", cid, "... ", end="")
    response = requests.get(request_url)
    if (response.status_code == 200):

        title = None
        molecular_formula = None
        jdata = json.loads(response.text)
        try:
            title = jdata["PropertyTable"]["Properties"][0]["Title"]
        except:
            pass
        try:
            molecular_formula = jdata["PropertyTable"]["Properties"][0]["MolecularFormula"]
        except:
            pass

    else:
        print("[ERROR] Unable to request CID" + cid + ".")
        return

    description = None
    descriptionURL = None
    request_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/" + cid + "/description/JSON"
    response = requests.get(request_url)
    if (response.status_code == 200):
        jdata = json.loads(response.text)
        try:
            description = jdata["InformationList"]["Information"][1]["Description"]
        except:
            pass
        try:
            descriptionURL = jdata["InformationList"]["Information"][1]["DescriptionURL"]
        except:
            pass

    drug, created = Drug.objects.get_or_create(cid=cid)
    if not created:
        print("it exists, updating ...", end="")
    drug.title = title
    drug.description = description
    drug.description_url = descriptionURL
    drug.molecular_formula = molecular_formula
    drug.save()

    print("done.")

    return drug


def handle_ds_files(inputfile):
    # The following import directive must be left here
    from side_effects.models import Drug, Effect, Interaction

    with open(inputfile, "r") as file:
        for line in file:
            words = line.split(",")

            if not words[0].startswith("CID"):
                continue  # Header?

            cid = words[0].replace("CID", "")
            cui = words[1].replace("C", "")

            # Get or create the  effect in the db
            effect = Effect.objects.get_or_create(cui=cui)[0]
            effect.name = words[2].strip().title()
            effect.save()

            drug = get_or_create_drug_by_cid(cid)
            drug.effects.add(effect)
            drug.save()


def handle_dds_files(inputfile):
    # The following import directive must be left here
    from side_effects.models import Drug, Effect, Interaction

    with open(inputfile, "r") as file:
        for line in file:
            words = line.split(",")

            if not words[0].startswith("CID"):
                continue  # Header?

            cid1 = words[0].replace("CID", "")
            cid2 = words[1].replace("CID", "")
            cui = words[2].replace("C", "")

            # Get or create the  effect in the db
            effect = Effect.objects.get_or_create(cui=cui)[0]
            effect.name = words[3].strip().title()
            effect.save()

            drug_a = get_or_create_drug_by_cid(cid1)
            drug_b = get_or_create_drug_by_cid(cid2)

            Interaction.objects.get_or_create(drug_a=drug_a, drug_b=drug_b, effect=effect)


def main():
    parser = argparse.ArgumentParser(description='Populates DB with drug side-effects. Data are taken from CVS files such as the ones available in the BIOSNAP databases at http://snap.stanford.edu/biodata/index.html')
    parser.add_argument('--debug_cid', type=str, help="CID to execute the script in 'debug' mode on a specific CID")
    parser.add_argument('--input', type=str, default="",
                        help='Path to the .csv SNAP file with "drug, side-effect" data or "drug, drug, side-effect". If the input is not specified the program will search for "ChSe-Decagon_monopharmacy.csv" (drug, side-effect) and "ChChSe-Decagon_polypharmacy.csv" (drug, drug, side-effect) files in the running folder and will import data from those files')
    parser.add_argument('--type', type=str,
                        help='Can be either ds (drug, side-effect) or dds (drug, drug, side-effect)')
    parser.add_argument('--django_project_path', type=str,
                        help='This is the django project local path. It is required to connect to the django database and populate it.')

    args = parser.parse_args()
    # print(args.accumulate(args.integers))

    sys.path.append(args.django_project_path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

    django.setup()

    # dir_path = os.path.dirname(os.path.realpath(__file__))
    # print(dir_path)

    if args.debug_cid != None:
        get_or_create_drug_by_cid(args.debug_cid.replace("CID", ""))

    if args.input == "":
        inputfile = "ChSe-Decagon_monopharmacy.csv"
        if not os.path.exists(inputfile):
            print("Input file", args.input, "does not exist. Quitting.")
        else:
            handle_ds_files(inputfile)

        inputfile = "ChChSe-Decagon_polypharmacy.csv"
        if not os.path.exists(inputfile):
            print("Input file", args.input, "does not exist. Quitting.")
        else:
            handle_dds_files(inputfile)


    # Check if the input file exists
    if not os.path.exists(args.input):
        print("Input file", args.input, "does not exist. Quitting.")

    if args.type == "ds":
        handle_ds_files(args.input)

    elif args.type == "dds":
        handle_dds_files(args.input)


if __name__ == "__main__":
    main()
