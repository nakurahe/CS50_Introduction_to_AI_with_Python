# A lot left for optimization ...

import csv
import itertools
import sys

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


def joint_probability(people, one_gene, two_genes, have_trait) -> float:
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.

    >>> joint_probability({'Harry': {'name': 'Harry', 'mother': 'Lily', 'father': 'James', 'trait': None},'James': {'name': 'James', 'mother': None, 'father': None, 'trait': True},'Lily': {'name': 'Lily', 'mother': None, 'father': None, 'trait': False}}, {"Harry"}, {"James"}, {"James"})
    0.0026643247488
    """
    result = 1

    for person in people:
        # If person is without parents, use PROBS["gene"].
        if people.get(person).get("mother") is None:
            # If person is in one_gene set:
            if person in one_gene:
                result *= PROBS["gene"][1]
                # If person has trait:
                if person in have_trait:
                    result *= PROBS["trait"][1][True]
                else:
                    result *= PROBS["trait"][1][False]
            elif person in two_genes:
                result *= PROBS["gene"][2]
                if person in have_trait:
                    result *= PROBS["trait"][2][True]
                else:
                    result *= PROBS["trait"][2][False]
            else:
                result *= PROBS["gene"][0]
                if person in have_trait:
                    result *= PROBS["trait"][0][True]
                else:
                    result *= PROBS["trait"][0][False]

        else:
            mother = people.get(person).get("mother")
            father = people.get(person).get("father")

            if person in one_gene:
                if person in have_trait:
                    result *= PROBS["trait"][1][True]
                else:
                    result *= PROBS["trait"][1][False]

                if mother in two_genes and father in two_genes:
                    # AA * AA -> Aa:
                    # one unmutated * one mutated * 2.
                    result *= PROBS["mutation"] * (1 - PROBS["mutation"]) * 2
                elif mother in one_gene and father in one_gene:
                    # Aa * Aa -> Aa:
                    # AA, one from mother and the other from father is mutated and vice versa,
                    # Aa, both unmutated,
                    # aa, one unmutated and one mutated.
                    result *= (0.5 * (1 - PROBS["mutation"]) * 0.5 * PROBS["mutation"] * 2 +
                               0.5 * (1 - PROBS["mutation"]) * 0.5 * (1 - PROBS["mutation"]) * 2 +
                               0.5 * (1 - PROBS["mutation"]) * 0.5 * PROBS["mutation"] * 2)
                elif ((mother in two_genes and father in one_gene) or (mother in one_gene and father in two_genes)):
                    # A1A2 * Aa -> Aa:
                    # A1 * A (one of them is mutated) + A2 * A -> AA
                    # A1 * a (both unmutated) + A2 * a -> Aa
                    # Aa (both mutated)
                    result *= ((1 - PROBS["mutation"]) * 0.5 * PROBS["mutation"] * 2 +
                               (1 - PROBS["mutation"]) * 0.5 * (1 - PROBS["mutation"]) +
                               PROBS["mutation"] * 0.5 * (1 - PROBS["mutation"]))
                elif ((mother in two_genes and father not in two_genes and father not in one_gene) or
                        (father in two_genes and mother not in two_genes and mother not in one_gene)):
                    # AA * aa:
                    # Aa, Both unmutated.
                    # Aa -> aA, Both mutated.
                    result *= ((1 - PROBS["mutation"]) * (1 - PROBS["mutation"]) +
                               PROBS["mutation"] * PROBS["mutation"])
                elif ((mother in one_gene and father not in two_genes and father not in one_gene) or
                        (father in one_gene and mother not in two_genes and mother not in one_gene)):
                    # Aa * aa:
                    # 0.5 * Both unmutated.
                    # 0.5 * one mutated * one unmutated * 2.
                    result *= (0.5 * (1 - PROBS["mutation"]) * (1 - PROBS["mutation"]) +
                               0.5 * (1 - PROBS["mutation"]) * PROBS["mutation"] * 2)
                else:
                    # aa * aa:
                    # one mutated * one unmutated * 2.
                    result *= (1 - PROBS["mutation"]) * PROBS["mutation"] * 2

            elif person in two_genes:
                if person in have_trait:
                    result *= PROBS["trait"][2][True]
                else:
                    result *= PROBS["trait"][2][False]

                if mother in two_genes and father in two_genes:
                    # AA * AA -> AA:
                    # Both unmutated.
                    result *= (1 - PROBS["mutation"]) * (1 - PROBS["mutation"])
                elif mother in one_gene and father in one_gene:
                    # Aa * Aa -> AA:
                    # AA, both unmutated.
                    # Aa -> AA, one unmutated one mutated, multiply by 2
                    # aa -> AA, both mutated.
                    result *= (0.5 * (1 - PROBS["mutation"]) * 0.5 * (1 - PROBS["mutation"]) +
                               0.5 * (1 - PROBS["mutation"]) * 0.5 * PROBS["mutation"] * 2 +
                               0.5 * PROBS["mutation"] * 0.5 * PROBS["mutation"])
                elif (mother in two_genes and father in one_gene) or (mother in one_gene and father in two_genes):
                    # AA * Aa -> AA:
                    # AA, both unmutated.
                    # Aa -> AA, one unmutated and one mutated.
                    result *= ((1 - PROBS["mutation"]) * 0.5 * (1 - PROBS["mutation"]) +
                               (1 - PROBS["mutation"]) * 0.5 * PROBS["mutation"])
                elif ((mother in two_genes and father not in two_genes and father not in one_gene) or
                      (father in two_genes and mother not in two_genes and mother not in one_gene)):
                    # AA * aa -> AA:
                    # Aa -> AA, one unmutated one mutated.
                    result *= ((1 - PROBS["mutation"]) * PROBS["mutation"])
                elif ((mother in one_gene and father not in two_genes and father not in one_gene) or
                      (father in one_gene and mother not in two_genes and mother not in one_gene)):
                    # Aa * aa:
                    # Aa -> AA, 0.5 * one unmutated * one mutated.
                    # aa -> AA, 0.5 * one mutated * one mutated.
                    result *= (0.5 * (1 - PROBS["mutation"]) * PROBS["mutation"] +
                               0.5 * PROBS["mutation"] * PROBS["mutation"])
                else:
                    # aa * aa:
                    # aa -> AA, both unmutated.
                    result *= PROBS["mutation"] * PROBS["mutation"]

            else:
                if person in have_trait:
                    result *= PROBS["trait"][0][True]
                else:
                    result *= PROBS["trait"][0][False]

                if mother in two_genes and father in two_genes:
                    # AA * AA -> aa:
                    # Both unmutated.
                    result *= (1 - PROBS["mutation"]) * (1 - PROBS["mutation"])
                elif mother in one_gene and father in one_gene:
                    # Aa * Aa -> aa:
                    # aa, both unmutated.
                    # Aa -> aa, one unmutated one mutated, multiply by 2
                    # AA -> aa, both mutated.
                    result *= (0.5 * (1 - PROBS["mutation"]) * 0.5 * (1 - PROBS["mutation"]) +
                               0.5 * (1 - PROBS["mutation"]) * 0.5 * PROBS["mutation"] * 2 +
                               0.5 * PROBS["mutation"] * 0.5 * PROBS["mutation"])
                elif (mother in two_genes and father in one_gene) or (mother in one_gene and father in two_genes):
                    # AA * Aa -> aa:
                    # AA -> aa, both mutated.
                    # Aa -> aa, one mutated and one unmutated.
                    result *= (PROBS["mutation"] * 0.5 * PROBS["mutation"] +
                               (1 - PROBS["mutation"]) * 0.5 * PROBS["mutation"])
                elif ((mother in two_genes and father not in two_genes and father not in one_gene) or
                      (father in two_genes and mother not in two_genes and mother not in one_gene)):
                    # AA * aa -> aa:
                    # Aa -> aa, one unmutated one mutated.
                    result *= ((1 - PROBS["mutation"]) * PROBS["mutation"])
                elif ((mother in one_gene and father not in two_genes and father not in one_gene) or
                      (father in one_gene and mother not in two_genes and mother not in one_gene)):
                    # Aa * aa -> aa:
                    # Aa -> aa, 0.5 * one unmutated * one mutated.
                    # aa, 0.5 * both unmutated.
                    result *= (0.5 * (1 - PROBS["mutation"]) * PROBS["mutation"] +
                               0.5 * (1 - PROBS["mutation"]) * (1 - PROBS["mutation"]))
                else:
                    # aa * aa -> aa:
                    # aa -> aa, both unmutated.
                    result *= (1 - PROBS["mutation"]) * (1 - PROBS["mutation"])
    return result


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.

    >>> update({"H": {"gene": {2: 0, 1: 0, 0: 0}, "trait": {True: 0, False: 0}}}, {}, {"H"}, {"H"}, 0.1)
    {'H': {'gene': {2: 0.1, 1: 0, 0: 0}, 'trait': {True: 0.1, False: 0}}}
    """
    for person in probabilities:
        if person in one_gene:
            probabilities.get(person).get("gene")[1] += p
            if person in have_trait:
                probabilities.get(person).get("trait")[True] += p
            else:
                probabilities.get(person).get("trait")[False] += p
        elif person in two_genes:
            probabilities.get(person).get("gene")[2] += p
            if person in have_trait:
                probabilities.get(person).get("trait")[True] += p
            else:
                probabilities.get(person).get("trait")[False] += p
        else:
            probabilities.get(person).get("gene")[0] += p
            if person in have_trait:
                probabilities.get(person).get("trait")[True] += p
            else:
                probabilities.get(person).get("trait")[False] += p

    # print(probabilities)


def normalize(probabilities: dict):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).

    >>> normalize({"H": {"gene": {2: 0.1, 1: 0, 0: 0.3}, "trait": {True: 0.1, False: 0.3}}})
    {'H': {'gene': {2: 0.25, 1: 0.0, 0: 0.7499999999999999}, 'trait': {True: 0.25, False: 0.7499999999999999}}}
    """
    for each_person in probabilities:
        person = probabilities.get(each_person)
        for each_item in person:
            gene_or_trait = person.get(each_item)
            original_sum = sum(gene_or_trait.values())
            for value in gene_or_trait:
                gene_or_trait[value] /= original_sum

    # print(probabilities)


if __name__ == "__main__":
    main()
