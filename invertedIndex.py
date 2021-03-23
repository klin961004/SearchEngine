import os, re, sys, nltk, psutil, json, math, time, gc
from collections import defaultdict
from collections import OrderedDict
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer # stemmer recommended by project write up
from nltk.corpus import stopwords


# ------------------------------TF-IDF SCORING------------------------------
# w_(t, d) = (1 + log(term frequency in this document)) * (log(size of the collection[how many documents in the collection]/the number of documents contain this term))
# --------------------------------------------------------------------------


# -----------------------------GLOBAL VARIABLES-----------------------------
# number of partitions used to off load data
index_count = 0
# total number of documents in the collection
collection_size = 0
# {id: tuple(posting url, posting page title)}
id_map = dict()
# {token: posting_id}
inverted_index = dict()
# set(each unique token)
tokens_bank = set()

mem_cap = 35.0
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# returns a list of all json filepaths in the given root directory
# --------------------------------------------------------------------------
def retrieve_files(root_directory):
    filepaths = []

    for (root, dirs, files) in os.walk(root_directory, topdown=True):
        for file in files:
            filepath = os.path.join(root, file)
            if filepath.endswith('json'):
                filepaths.append(filepath)

    return filepaths


# --------------------------------------------------------------------------
# returns the percentage of available memory of the machine
# --------------------------------------------------------------------------
# psutil.virtual_memory().total
def check_Memory():
    print((psutil.virtual_memory().available / psutil.virtual_memory().total) * 100)
    return (psutil.virtual_memory().available / psutil.virtual_memory().total) * 100
    #return psutil.virtual_memory().total == (16*(1024.0 ** 3))
    #print(psutil.virtual_memory().used / (1024.0 ** 3))
    #print((((10*(1024.0 ** 3)) - psutil.virtual_memory().used) / (10*(1024.0 ** 3))) * 100)
    #return ((((10*(1024.0 ** 3)) - psutil.virtual_memory().used) / (10*(1024.0 ** 3))) * 100)


# --------------------------------------------------------------------------
# open the json file with the given file path
# --------------------------------------------------------------------------
def read_file(filepath):
    global collection_size, tokens_bank

    with open(filepath, 'r') as file:
        collection_size += 1
        count = 0
        title = []
        tokens_freq = defaultdict(int)

        json_file = json.load(file)
        document = BeautifulSoup(json_file["content"], 'lxml')
        boldTags = get_this_tag(document, 'b')
        headTags = get_this_tag(document, re.compile('^h[1-6]$'))

        # remove fragments of the url before storing as a posting
        url = json_file["url"].split('#')[0]
        id = hash(url)

        if document.title:
            if document.title.string:
                # obtain list of tokens in the title
                title = nltk.word_tokenize(document.title.string)
                # create posting tuple for id_map
                posting = (url, document.title.string)
            else:
                posting = (url, "")
        else:
            posting = (url, "")


        # add id of the posting to the bank
        if addToMap(id, posting):
            tokens = nltk.word_tokenize(document.get_text())

            # calculate the frequency of each token appears in this document
            for token in tokens:
                clean_token = cleanThisToken(token)

                if len(clean_token) >= 2:
                    weights = 0.0
                    if clean_token in title:
                        weights = 0.25
                    elif clean_token in boldTags:
                        weights = 0.23
                    elif clean_token in headTags:
                        weights = 0.21
                    elif clean_token in set(stopwords.words("english")):
                        weights = 0.14
                    else:
                        weights = 0.17

                    tokens_freq[clean_token] += weights
                    tokens_bank.add(clean_token)

            beautifyTokens(tokens_freq, id)


# --------------------------------------------------------------------------
# return a set of tokens in the given tag
# --------------------------------------------------------------------------
def get_this_tag(document, tag):
    tags = set()
    for token in document.find_all(tag):
        tag = nltk.word_tokenize(token.text.lower())

        for t in tag:
            if len(cleanThisToken(t)) >= 2:
                tags.add(cleanThisToken(t))

    return tags

# --------------------------------------------------------------------------
# parse token
# --------------------------------------------------------------------------
def cleanThisToken(token):
    clean_token = token

    if not check_numeric(token):
        clean_token = token_stripper(token)
    else:
        clean_token = token

    return clean_token


# --------------------------------------------------------------------------
# strips the tokens of unnecessary characters that are observed while reading the textual content.
# next we keep only the alphanumeric words and contractions after stripping the tokens.
# --------------------------------------------------------------------------
def token_stripper(token):
    porter = PorterStemmer()
    new_token = re.sub(r"(\\\\r|\\r|\\\\n|\\n|\\\\t|\\t|[^a-zA-Z\d\s\']|'|[0-9]*|:)", '', token)
    if re.match(r'^[^a-zA-Z\d\s]+$',new_token) or new_token.isnumeric():
        return ''
    else:
        return porter.stem(new_token.lower()) #CHECK HERE IF WE ACTUALLY WANT TO DO LOWER


# --------------------------------------------------------------------------
# if this token is a year or a percentage number
# --------------------------------------------------------------------------
def check_numeric(token):
    if token.isnumeric() and len(token) == 4:
        if int(token) <= 2500 and int(token[0]) != 0:
            return True
    elif token[-1] == "%" and token[0:-1].isnumeric():
        return True
    else:
        return False

# --------------------------------------------------------------------------
# add the hashid and the posting pair to the id_map
# --------------------------------------------------------------------------
def addToMap(id, posting):
    global id_map

    if id not in id_map.keys():
        id_map[id] = posting

        return True
    else:
        return False


# --------------------------------------------------------------------------
# this will initialize our txt file that will be storing the inverted_index
# --------------------------------------------------------------------------
def initIndex():
    file = open("inverted_index" + str(index_count) + ".txt", 'w')
    file.close()


# --------------------------------------------------------------------------
# dump current inverted index to disk
# --------------------------------------------------------------------------
def dump():
    global index_count, inverted_index, mem_cap
    before_dump = check_Memory() - 1.0

    try:
        with open("inverted_index" + str(index_count) + ".txt", 'w') as file:
            for token, postings in sorted(inverted_index.items(), key=lambda index: index[0]):
                file.write(str(token) + ":" + str(postings) + "\n")

            print("Percentage of available memory before dump: {}".format(check_Memory()))
            inverted_index.clear()
            gc.collect()
            index_count += 1
            print("Percentage of available memory after dump: {}".format(check_Memory()))

            #print("MEM_CAP is: {} and MEM is: {}".format(mem_cap, check_Memory()))
            file.close()


        while check_Memory() < mem_cap:
            print("Cleaning RAM")
            time.sleep(15)
    except:
        print("Dump error")


# --------------------------------------------------------------------------
# TEST FUNCTION IGNORE THIS
# --------------------------------------------------------------------------
def read_index():
    try:
        with open("inverted_index" + str(0) + ".txt", 'r') as file:
            line = file.readline()

            while file:
                if line == "":
                    break

                print(line)
                print(line.split(":", 1))
                line = file.readline()

        file.close()
    except:
        print("Reading error")


# --------------------------------------------------------------------------
# add the posting with the frquency of the tokens to the inverted index
# program will offload the index if the oeperating machine's available
# memory is less than 25%
# --------------------------------------------------------------------------
def beautifyTokens(tokens, id):
    global inverted_index, mem_cap

    for token, tf in tokens.items():
        if check_Memory() < mem_cap:
            print("DUMPING")
            dump()

        if token in inverted_index.keys():
            inverted_index[token][id] = float(tf)
        else:
            makePosting = OrderedDict()
            makePosting[id] = tf
            inverted_index[token] = makePosting



    # this is the sorting function for the inverted_index
    '''for token, postings in inverted_index.items():
        print("{} originally has: {}".format(token, postings))

        # currently sort by term frequency
        # change x[1] to x[0] if want to sort by id
        inverted_index[token] = OrderedDict(sorted(postings.items(), key=lambda posting: posting[1], reverse=True))
        print("{} NOW has: {}".format(token, inverted_index[token]))'''


# --------------------------------------------------------------------------
# this will read into all partitions of inverted index and replace tf with
# tf-idf scoring
# --------------------------------------------------------------------------
def get_scoring():
    global index_count, collection_size

    index_id = 0

    while index_id < index_count:
        file = open("inverted_index" + str(index_id) + ".txt", 'r')
        invertedIndex = dict()
        read_line = file.readline()

        while file:
            if read_line == "":
                break

            line = read_line.split(":", 1)
            token = line[0]
            postings = eval(line[1])

            for posting, tf in postings.items():
                tf_idf = (1.0 + math.log((float(tf) / 1.0))) * (math.log(collection_size / (len(postings) / 1.0)))

                if token not in invertedIndex.keys():
                    makePosting = OrderedDict()
                    makePosting[posting] = tf_idf
                    invertedIndex[token] = makePosting

                else:
                    invertedIndex[token][posting] = tf_idf

            read_line = file.readline()
        file.close()

        file = open("inverted_index" + str(index_id) + ".txt", 'w')
        for key, value in invertedIndex.items():
            value = OrderedDict(sorted(value.items(), key=lambda k:k[0]))
            file.write(key + ":" + str(value) + "\n")

        invertedIndex.clear()
        index_id += 1

        file.close()


# --------------------------------------------------------------------------
# dump id:posting map to txt file
# --------------------------------------------------------------------------
def dumpId():
    global id_map
    file = open("ID.txt", 'w')

    for id, url in id_map.items():
        file.write(str(id) + ":" + str(url) + "\n")

    id_map.clear()
    file.close()


# --------------------------------------------------------------------------
# write index information to txt file
# --------------------------------------------------------------------------
def write_report():
    global collection_size, index_count, tokens_bank
    file = open("report.txt", 'w')

    file.write("Collection size:" + str(collection_size) + "\n")
    file.write("Total tokens count:" + str(len(tokens_bank)) + "\n")
    file.write("Total index partitions:" + str(index_count) + "\n")

    file.close()
