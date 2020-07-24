import csv
import itertools
import sys
import random

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    joint_probability = 1

    people_keys = people.keys()

    people_set = set()

    for person in people_keys:
        people_set.add(person)

    no_genes = people_set.difference(one_gene).difference(two_genes)
    no_trait = people_set.difference(have_trait)

    #Probability of person having no genes
    for person in no_genes:
        mother = people[person]["mother"]
        father = people[person]["father"]

        #Parents are not given
        if mother is None or mother == "" or father is None or father == "":
            joint_probability *= PROBS["gene"][0]

        #Parents are given
        else:
            #probability of mother and father not passing gene
            #Mother has no genes
            mother_no_pass_gene = None
            father_no_pass_gene = None

            if no_genes.issuperset({mother}):
                mother_no_pass_gene = 1 - PROBS["mutation"]
            elif one_gene.issuperset({mother}):
                mother_no_pass_gene = 0.5
            else:
                mother_no_pass_gene = PROBS["mutation"]

            if no_genes.issuperset({father}):
                father_no_pass_gene = 1 - PROBS["mutation"]
            elif one_gene.issuperset({father}):
                father_no_pass_gene = 0.5
            else:
                father_no_pass_gene = PROBS["mutation"]

            joint_probability *= mother_no_pass_gene * father_no_pass_gene

        #Get probability of showing or not showing trait
        joint_probability *= PROBS["trait"][0][have_trait.issuperset({person})]

    #Probability of person having one genes
    for person in one_gene:
        mother = people[person]["mother"]
        father = people[person]["father"]

        #Parents are not given
        if mother is None or mother == "" or father is None or father == "":
            joint_probability *= PROBS["gene"][1]

        #Parents are given
        else:
            #probability of mother and father not passing gene
            #### ATTENTION ####
            #Mother has no genes
            mother_no_pass_gene = None
            father_no_pass_gene = None

            if no_genes.issuperset({mother}):
                mother_no_pass_gene = 1 - PROBS["mutation"]
            elif one_gene.issuperset({mother}):
                mother_no_pass_gene = 0.5
            else:
                mother_no_pass_gene = PROBS["mutation"]

            if no_genes.issuperset({father}):
                father_no_pass_gene = 1 - PROBS["mutation"]
            elif one_gene.issuperset({father}):
                father_no_pass_gene = 0.5
            else:
                father_no_pass_gene = PROBS["mutation"]

            mother_pass_gene = 1 - mother_no_pass_gene
            father_pass_gene = 1 - father_no_pass_gene

            joint_probability *= mother_no_pass_gene * father_pass_gene + mother_pass_gene * father_no_pass_gene

        #Get probability of showing or not showing trait
        joint_probability *= PROBS["trait"][1][have_trait.issuperset({person})]

    #Probability of person having two genes
    for person in two_genes:
        mother = people[person]["mother"]
        father = people[person]["father"]

        #Parents are not given
        if mother is None or mother == "" or father is None or father == "":
            joint_probability *= PROBS["gene"][2]

        #Parents are given
        else:
            #probability of mother and father not passing gene
            #### ATTENTION ####
            #Mother has no genes
            mother_pass_gene = None
            father_pass_gene = None

            if no_genes.issuperset({mother}):
                mother_pass_gene = PROBS["mutation"]
            elif one_gene.issuperset({mother}):
                mother_pass_gene = 0.5
            else:
                mother_pass_gene = 1 - PROBS["mutation"]

            if no_genes.issuperset({father}):
                father_pass_gene = PROBS["mutation"]
            elif one_gene.issuperset({father}):
                father_pass_gene = 0.5
            else:
                father_pass_gene = 1 - PROBS["mutation"]

            joint_probability *= mother_pass_gene * father_pass_gene

        #Get probability of showing or not showing trait
        joint_probability *= PROBS["trait"][2][have_trait.issuperset({person})]

    return joint_probability



def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    raise NotImplementedError


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    raise NotImplementedError

    probability_sum = 0

    for key in probabilities.keys():
        probabilitiy_sum += probabilities[key]

    for key in probabilities.keys():
        probabilities[key] /= probabilitiy_sum


if __name__ == "__main__":
    main()
