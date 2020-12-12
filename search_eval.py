import math
import sys
import time
import metapy
import pytoml
from xml.dom import minidom


# 
def load_queries():

    with open(sys.argv[1], 'r') as fin:
        cfg_d = pytoml.load(fin)

    query_Doc = minidom.parse('{}/queries.xml'.format(cfg_d['dataset']))
    # Can change the name of the tag to retrive any desired 
    # tag from the queries.xml (query, question, narrative)
    topics = query_Doc.getElementsByTagName('topic')
    items = []

    for topic in topics:
        items.append(
            (topic.getAttribute('number'), 
            # Get first element in the topic xml. 
            topic.getElementsByTagName('query')[0].firstChild.data)
        )

    # Return tuple array (queryId, query)
    return items


def load_ranker(cfg_file):
    """
    Use this function to return the Ranker object to evaluate, 
    The parameter to this function, cfg_file, is the path to a
    configuration file used to load the index.
    """
    # return metapy.index.OkapiBM25(k1=1.2,b=0.75,k3=0.0111)
    return metapy.index.AbsoluteDiscount(0.7)


def saveResults(prediction_results):
    print("saving results")

    with open("predictions.txt", 'w+') as results:
        for result in prediction_results:
           results.write(str(result[0]) + ' ' + str(result[1]) + ' ' + str(result[2]) + "\n")


def runQueries(queries):
    cfg = sys.argv[1]

    print('Building or loading index...')
    idx = metapy.index.make_inverted_index(cfg)
    
    ranker = load_ranker(cfg)
    ev = metapy.index.IREval(cfg)

    with open(cfg, 'r') as fin:
        cfg_d = pytoml.load(fin)

    query_cfg = cfg_d['query-runner']
    if query_cfg is None:
        print("query-runner table needed in {}".format(cfg))
        sys.exit(1)

    start_time = time.time()
    top_k = 1000
    query_path = query_cfg.get('query-path', 'queries.txt')
    query_start = query_cfg.get('query-id-start', 0)

    query = metapy.index.Document()
    ndcg = 0.0
    num_queries = 0

    # Build index mapping


    prediction_results = []

    print("starting queries...")
    for query_num, line in queries:

        query.content(line.strip())
        results = ranker.score(idx, query, top_k)

        for doc in results:
            prediction_results.append((query_num, idx.metadata(doc[0]).get('uid'), doc[1]))
    
        ndcg += ev.ndcg(results, query_start + int(query_num), top_k)
        num_queries+=1

    ndcg= ndcg / num_queries
    
    
    print("NDCG@{}: {}".format(top_k, ndcg))
    print("Elapsed: {} seconds".format(round(time.time() - start_time, 4)))

    saveResults(prediction_results)


if __name__ == '__main__':

    results = []

    if len(sys.argv) != 2:
        print("Usage: {} config.toml".format(sys.argv[0]))
        sys.exit(1)


    queries = load_queries()

    runQueries(queries)
