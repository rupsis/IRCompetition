import math
import sys
import time
import metapy
import pytoml
from xml.dom import minidom



def load_queries():
    query_Doc = minidom.parse('train/queries.xml')
    # Can change the name of the tag to retrive any desired 
    # tag from the queries.xml (query, question, narrative)
    xmlElements = query_Doc.getElementsByTagName('query')
    items = []

    for item in xmlElements:
        items.append(item.firstChild.data)
    return items


def load_ranker(cfg_file):
    """
    Use this function to return the Ranker object to evaluate, 
    The parameter to this function, cfg_file, is the path to a
    configuration file used to load the index.
    """
    return metapy.index.OkapiBM25(k1=1.2,b=0.75,k3=0.0111)


def runQueries(queries):
    cfg = sys.argv[1]

    print('Building or loading index...')
    idx = metapy.index.make_inverted_index(cfg)

    
    ranker = load_ranker_test(cfg, param)
    ev = metapy.index.IREval(cfg)

    with open(cfg, 'r') as fin:
        cfg_d = pytoml.load(fin)

    query_cfg = cfg_d['query-runner']
    if query_cfg is None:
        print("query-runner table needed in {}".format(cfg))
        sys.exit(1)

    start_time = time.time()
    top_k = 10
    query_path = query_cfg.get('query-path', 'queries.txt')
    query_start = query_cfg.get('query-id-start', 0)

    query = metapy.index.Document()
    ndcg = 0.0
    num_queries = 0

    if print_on:
        print('Running queries')
    with open(query_path) as query_file:
        for query_num, line in enumerate(query_file):
            query.content(line.strip())
            results = ranker.score(idx, query, top_k)
            ndcg += ev.ndcg(results, query_start + query_num, top_k)
            num_queries+=1
    ndcg= ndcg / num_queries
    
    if print_on:
        print("NDCG@{}: {}".format(top_k, ndcg))
        print("Elapsed: {} seconds".format(round(time.time() - start_time, 4)))

    return(ndcg, param)


def testModel():


    for i in range(1, 100):
        results.append(runQueries(i, print_on=False))
        print("{} out of {}".format(i, 10000))

    results_sorted = sorted(results, reverse=True)
    print("BM25 results: ")
    for k in results_sorted[:100]:
        print("{}, k = {}".format(k[0], k[1]))


if __name__ == '__main__':

    results = []

    if len(sys.argv) != 2:
        print("Usage: {} config.toml".format(sys.argv[0]))
        sys.exit(1)


    queries = load_queries()

    runQueries(queries)

# Save top You should submit the scores for the top 1000 documents per query
    #  topic/query_id doc_uid relevance_score