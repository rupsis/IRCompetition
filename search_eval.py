import math
import sys
import time
import metapy
import pytoml
from xml.dom import minidom
import string

stop_words = {'ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there', 'about', 
'once', 'during', 'out', 'very', 'having', 'with', 'they', 'own', 'an', 'be', 'some', 'for', 
'do', 'its', 'yours', 'such', 'into', 'of', 'most', 'itself', 'other', 'off', 'is', 's', 'am', 
'or', 'who', 'as', 'from', 'him', 'each', 'the', 'themselves', 'until', 'below', 'are', 'we', 
'these', 'your', 'his', 'through', 'don', 'nor', 'me', 'were', 'her', 'more', 'himself', 'this', 
'down', 'should', 'our', 'their', 'while', 'above', 'both', 'up', 'to', 'ours', 'had', 'she', 
'all', 'no', 'when', 'at', 'any', 'before', 'them', 'same', 'and', 'been', 'have', 'in', 'will',
 'on', 'does', 'yourselves', 'then', 'that', 'because', 'what', 'over', 'why', 'so', 'can', 'did', 
 'not', 'now', 'under', 'he', 'you', 'herself', 'has', 'just', 'where', 'too', 'only', 'myself', 
 'which', 'those', 'i', 'after', 'few', 'whom', 't', 'being', 'if', 'theirs', 'my', 'against', 'a', 
 'by', 'doing', 'it', 'how', 'further', 'was', 'here', 'than'}




def ndcg_ev(cfg, results):
    with open(sys.argv[1], 'r') as fin:
        cfg_d = pytoml.load(fin)

    with open('{}/qrels.txt'.format(cfg_d['dataset'])) as qrels:
        for line in qrels:
            words = line.split(line)

def word_expand(wordSet, expandSet):
    # if query wors is in expandSet, add expansion
    for word in wordSet:
        if word in expandSet:
            return wordSet.union(expandSet)

    return wordSet

def expand_query(query):
    # Filtering common stop words

    # remove punctuation
    exclude = set('!"#$%&\'()*+,./:;<=>?@[\]^_`{|}~')
    query = ''.join(ch for ch in query if ch not in exclude)
    query_words = set(query.lower().split())

    # Filtering common stop words
    query_words = set([w for w in query_words if not w in stop_words])

    # Simple approach to query expansion
    # After tweaking, these yielded the best results
    covid_synonyms = {'covid-19', 'coronavirus'} 

    # Another common tense, is test (tests, testing)
    test_synonyms = {'test', 'testing', 'tests'}

    query_words = word_expand(query_words, covid_synonyms)
    query_words= word_expand(query_words, test_synonyms)



    # Return query string
    return ' '.join(query_words)

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
        # items.append(
        #     (topic.getAttribute('number'), 
        #     # Get first element in the topic xml. 
        #     expand_query(topic.getElementsByTagName('query')[0].firstChild.data) + 
        #     expand_query(topic.getElementsByTagName('question')[0].firstChild.data))
        # )

        items.append(
            (topic.getAttribute('number'), 
            # Get first element in the topic xml. 
            expand_query(topic.getElementsByTagName('query')[0].firstChild.data))
        )

    # Return tuple array (queryId, query)
    return items


def load_ranker(cfg_file):
    """
    Use this function to return the Ranker object to evaluate, 
    The parameter to this function, cfg_file, is the path to a
    configuration file used to load the index.
    """
    # return metapy.index.OkapiBM25(k1=1.2,b=0.75, k3=1000)
    return metapy.index.OkapiBM25()
    # return metapy.index.AbsoluteDiscount(0.7)



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
    score = 0.0


    prediction_results = []

    print("starting queries...")
    for query_num, line in queries:

        query.content(line.strip())
        results = ranker.score(idx, query, top_k)

        for doc in results:
            prediction_results.append((query_num, idx.metadata(doc[0]).get('uid'), doc[1]))
            score += doc[1]
    
        ndcg += ev.ndcg(results, query_start + int(query_num), top_k)
        num_queries+=1

    ndcg= ndcg / num_queries
    
    print("Average score: {}".format(score / len(prediction_results)))
    print("MAP: {}".format(ev.map()))
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
