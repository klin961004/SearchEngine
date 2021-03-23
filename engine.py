from invertedIndex import *
from pymemcache.client import base
from merge import read_info
from collections import defaultdict


# -----------------------------GLOBAL VARIABLES-----------------------------
query_index = dict()
id_map = dict()
index_info = dict()
dictionary = dict()
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# prompt user for query
# --------------------------------------------------------------------------
def prompt_query():
    query = ""
    while(query == ""):
        query = input("Please enter your query: ")

    return query


# --------------------------------------------------------------------------
# tokenize the query
# --------------------------------------------------------------------------
def tokenize_query(query):
    global query_index

    tokens = nltk.word_tokenize(query.lower())

    for token in tokens:
        clean_token = cleanThisToken(token)
        if clean_token not in query_index.keys():
            query_index[clean_token] = (1.0 + math.log((0.17)))
        else:
            query_index[clean_token] = query_index[clean_token] + (1.0 + math.log((0.17)))


def seekPosting(pos):
    file = open("inverted_index.txt", 'r')
    file.seek(pos)
    postings = OrderedDict()

    line = file.readline()

    if line != "":
        if len(line.split(":--", 1)) >= 2:
            postings = eval(line.split(":--", 1)[1])

    return postings


def cosSim(query_vector, posting_vector):
    score = 0.0

    for i in range(len(query_vector)):
        score += query_vector[i] * posting_vector[i]

    return score


def result_out(ranking):
    global id_map
    i = 1
    file = open("ranking.txt", 'w')
    dict = sorted(ranking.items(), key=lambda post:post[1])

    for posting in dict[0:9]:
        key = str(posting[0])

        print("{}. {}".format(i, id_map[key][1]))
        print("URL: {}".format(id_map[key][0]))

        file.write(str(i) + ". " + str(id_map[key][1]) + "\n")
        file.write("URL: " + str(id_map[key][0]) + "\n")
        i += 1


def read_dict(filename):
    global dictionary

    file = open(filename, 'r')

    line = file.readline()

    while file:
        if line == "":
            break

        key = line.split(":", 1)[0]
        value = eval(line.split(": ", 1)[1])
        dictionary[key] = value
        line = file.readline()

    file.close()


if __name__ == "__main__":
    id_map = read_info("ID.txt")
    index_info = read_info("report.txt")
    read_dict("dictionary.txt")
    #client = base.Client(('localhost', 11211))

    query = prompt_query()
    timer = time.time()
    tokenize_query(query)
    postings = OrderedDict()
    query_vector = []
    query_bank = dict()
    posting_list = set()
    ranking = dict()

    for token in sorted(query_index.keys()):
        '''if client.get(token):
            postings = client.get(token)
        elif token in dictionary.keys():
            postings = seekPosting(dictionary[token])
            client.set(token, postings, time = 43200)'''
        if token in dictionary.keys():
            postings = seekPosting(dictionary[token][1])
        else:
            postings = OrderedDict()

        if len(postings) > 0:
            idf = (math.log(index_info["Collection size"] / (len(postings) / 1.0)))
            query_vector.append(query_index[token] * idf)

        if token not in query_bank.keys():
            query_bank[token] = postings
        else:
            query_bank[token] = query_bank[token].update(postings)

        for posting in postings.keys():
            posting_list.add(posting)

    for posting in posting_list:
        posting_vectors = []

        for token in query_bank.keys():
            if posting in query_bank[token].keys():
                posting_vectors.append(query_bank[token][posting])
            else:
                posting_vectors.append(0.0)

        if posting not in ranking.keys():
            if len(query_vector) == len(posting_vectors):
                ranking[posting] = cosSim(query_vector, posting_vectors)

    result_out(ranking)

    print("Program run time: {} s".format(time.time() - timer))
