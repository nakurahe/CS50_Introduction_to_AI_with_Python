# One test I can't get through. So referred to others' solution, as follows:
# https://github.com/PLCoster/cs50ai-week2-pagerank/blob/2b6b17ba4861dd05300206826d4ab97cb1e42726/pagerank.py#L90

import os
import random
import re
import sys
from collections import Counter

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print("PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.

    >>> transition_model({'1': {'2'}, '2': {'1', '3'}, '3': {'2', '4'}, '4': {'2'}}, '1', 0.85)
    {'1': 0.037500000000000006, '2': 0.8875, '3': 0.037500000000000006, '4': 0.037500000000000006}
    """
    result_dict = dict()
    additional_probability = (1 - damping_factor) / len(corpus)

    if len(corpus.get(page)) == 0:
        same_probability_for_other_page = additional_probability
    else:
        same_probability_for_other_page = damping_factor / \
            len(corpus.get(page)) + additional_probability

    for corpu in corpus:
        if corpu in corpus.get(page):
            result_dict.update({corpu: same_probability_for_other_page})
        else:
            result_dict.update({corpu: additional_probability})
    return result_dict


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    current_page = random.choice(list(corpus.keys()))
    result_container = list()

    while n > 0:
        result_container.append(current_page)
        current_transition_model = transition_model(corpus, current_page, damping_factor)
        current_page = random.choices(list(current_transition_model.keys()), weights=list(
            current_transition_model.values()), k=1)[0]
        n -= 1

    result = {key: value / sum(Counter(result_container).values())
              for key, value in Counter(result_container).items()}

    return result


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    n = len(corpus)
    constant = (1 - damping_factor) / n

    result = {key: (1 / n) for key in corpus.keys()}
    new_result = {key: 0 for key in corpus.keys()}
    max_change = 1 / n

    while max_change > 0.001:
        max_change = 0
        for page in corpus:
            sigma_of_linked_page = 0
            for each_other_page in corpus:
                if len(corpus.get(each_other_page)) == 0:
                    sigma_of_linked_page += result.get(each_other_page) / n
                elif page in corpus.get(each_other_page):
                    sigma_of_linked_page += result.get(each_other_page) / \
                        len(corpus.get(each_other_page))
            new_pr = constant + damping_factor * sigma_of_linked_page
            new_result[page] = new_pr

        # Normalize the new page ranks:
        norm_factor = sum(new_result.values())
        new_result = {page: (pr / norm_factor) for page, pr in new_result.items()}

        for page in corpus:
            if abs(result.get(page) - new_result.get(page)) > max_change:
                max_change = abs(result.get(page) - new_result.get(page))

        # Why is this necessary to have a shallow
        result = new_result.copy()

    return result


# def iterate_pagerank(corpus, damping_factor):
#     """
#     Return PageRank values for each page by iteratively updating
#     PageRank values until convergence.

#     Return a dictionary where keys are page names, and values are
#     their estimated PageRank value (a value between 0 and 1). All
#     PageRank values should sum to 1.
#     """

#     # Calculate some constants from the corpus for further use:
#     num_pages = len(corpus)
#     init_rank = 1 / num_pages
#     random_choice_prob = (1 - damping_factor) / len(corpus)
#     iterations = 0

#     # Initial page_rank gives every page a rank of 1/(num pages in corpus)
#     page_ranks = {page_name: init_rank for page_name in corpus}
#     new_ranks = {page_name: None for page_name in corpus}
#     max_rank_change = init_rank

#     # Iteratively calculate page rank until no change > 0.001
#     while max_rank_change > 0.001:

#         iterations += 1
#         max_rank_change = 0

#         for page_name in corpus:
#             surf_choice_prob = 0
#             for other_page in corpus:
#                 # If other page has no links it picks randomly any corpus page:
#                 if len(corpus[other_page]) == 0:
#                     surf_choice_prob += page_ranks[other_page] * init_rank
#                 # Else if other_page has a link to page_name, it randomly picks from all links on other_page:
#                 elif page_name in corpus[other_page]:
#                     surf_choice_prob += page_ranks[other_page] / len(corpus[other_page])
#             # Calculate new page rank
#             new_rank = random_choice_prob + (damping_factor * surf_choice_prob)
#             new_ranks[page_name] = new_rank

#         # Normalise the new page ranks:
#         norm_factor = sum(new_ranks.values())
#         new_ranks = {page: (rank / norm_factor) for page, rank in new_ranks.items()}

#         # Find max change in page rank:
#         for page_name in corpus:
#             rank_change = abs(page_ranks[page_name] - new_ranks[page_name])
#             if rank_change > max_rank_change:
#                 max_rank_change = rank_change

#         # Update page ranks to the new ranks:
#         page_ranks = new_ranks.copy()

#     return page_ranks


if __name__ == "__main__":
    main()
