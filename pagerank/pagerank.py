import os
import random
import re
import sys

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
    print(f"PageRank Results from Iteration")
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
    """
    probability_distribution = dict()

    if page is None or len(corpus.get(page)) == 0:
        #probabilities are all the same
        probability = 1 / len(corpus.keys())
        for key in corpus.keys():
            probability_distribution.update({key : probability})
    
    else:
        #probabilities are weighted
        probability = (1 - damping_factor) / len(corpus.keys())
        linked_pages = corpus.get(page)
        linked_probability = damping_factor / len(linked_pages)
        for key in corpus.keys():
            if linked_pages.issuperset({key}):
                probability_distribution.update({key : probability + linked_probability})
            else:
                probability_distribution.update({key : probability})

    return probability_distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_rank = dict()

    #initialize all probabilities
    for key in corpus.keys():
        page_rank.update({key : (1 - damping_factor) / len(corpus.keys())})

    selected_page = None

    for i in range(n):
        #surfer chooses random page based off probabilities
        model = transition_model(corpus, selected_page, damping_factor)
        selected_key = sample_distribution(model)

        #update the chosen page to the page_rank
        page_rank[selected_key] += damping_factor / n

    return page_rank


def sample_distribution(probability_distribution):
    """
    Parameter: probability_distribution is a dictionary where each key
    maps to a probability value. The probability value should be a float
    where 0 <= float <= 1.

    Precondition: all values in probability_distribution add up to 1.
        
    Return a key from the dictionary
    """
    random_distribution = []
    cumulative_probability = 0
    keys = probability_distribution.keys()
    for key in keys:
        random_distribution.append(cumulative_probability + probability_distribution[key])
        cumulative_probability += probability_distribution[key]

    if cumulative_probability <= 0.999 or cumulative_probability >= 1.001:
        print("Probability does not accumalate to 1")
        raise

    del cumulative_probability

    random_number = random.random()

    i = 0
    for key in keys:
        if random_number < random_distribution[i]:
            return key
        else:
            i += 1


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    #initalize page ranks
    page_ranks = dict()
    for key in corpus.keys():
        page_ranks.update({key : 1 / len(corpus.keys())})

    while True:
        old_page_ranks = page_ranks.copy()

        for key in corpus.keys():
            #determine what keys are linked to this key
            linked_keys = None
            if len(corpus[key]) == 0:
                linked_keys = []
                for key in page_ranks.keys():
                    linked_keys.append(key)
            else:
                values = corpus[key]
                linked_keys = []
                for value in values:
                    linked_keys.append(value)

            #calculate new rank value for this key
            page_rank_value = (1 - damping_factor) / len(corpus.keys())
            len_linked_keys = len(linked_keys)
            
            for linked_key in linked_keys:
                page_rank_value += damping_factor * page_ranks[linked_key] / len_linked_keys

            page_ranks.update({key : page_rank_value})

        #break out of while loop if no page changed by > 0.001
        break_loop = True

        for key in corpus.keys():
            difference = old_page_ranks[key] - page_ranks[key]
            if difference < -0.001 or difference > 0.001:
                break_loop = False
                break

        if break_loop:
            break

    return page_ranks


if __name__ == "__main__":
    main()
