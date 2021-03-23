from collections import OrderedDict
import fileinput
import sys

# -----------------------------GLOBAL VARIABLES-----------------------------
inverted_index = dict()
# starting character: seek position of the character
dictionary = dict()
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# read the dictionary information from the filename
# return a dictionary type object
# --------------------------------------------------------------------------
def read_info(filename):
    file = open(filename, 'r')

    map = dict()
    line = file.readline()

    while file:
        if line == "":
            break

        key = line.split(":", 1)[0]
        value = eval(line.split(":", 1)[1])
        map[key] = value
        line = file.readline()

    file.close()

    return map


# --------------------------------------------------------------------------
# obtain the partition file names and insert into the dictionary
# --------------------------------------------------------------------------
def start_merge(idx_count):
    for i in range(idx_count):
        print('starting ' + str(i))
        if i == 0:
            with open('inverted_index0.txt', 'r') as file:
                with open('inverted_index_full.txt', 'w') as full:
                    for line in file:
                        tok = getLine(line)[0]
                        #save the line in the file and the tell
                        dictionary[tok] = [len(dictionary), full.tell()]
                        full.write(line)

        else:
            with open('inverted_index'+str(i)+'.txt', 'r') as file:
                for n_line in file:
                    newLine = getLine(n_line)
                    if newLine[0] in dictionary:
                        # sys.stderr.write('entered existing token\n')
                        with fileinput.FileInput('inverted_index_full.txt', inplace = True, backup = '.bak') as full:
                            for i,og_line in enumerate(full):
                                if i == dictionary[newLine[0]][0]:
                                    sys.stderr.write('updating!\n')
                                    originalLine = getLine(og_line)
                                    sys.stderr.write(str(originalLine) + '\n')
                                    sys.stderr.write(str(newLine) + '\n')
                                    updatedDict = OrderedDict(list(newLine[1].items()) + list(originalLine[1].items()))
                                    sys.stderr.write(str(updatedDict)+'\n\n')
                                    print(originalLine[0] + ":--" + str(updatedDict),end='\n')
                                else:
                                    print(og_line, end='')
                    else:
                        dictionary[newLine[0]] = [len(dictionary),0]
                        full = open('inverted_index_full.txt')
                        full.seek(0,2)
                        dictionary[newLine[0]][1] = full.tell()
                        # print('Tell: ' + str(dictionary[newLine[0]][1]))
                        full.close()
                        with open('inverted_index_full.txt','a') as full:
                            print('new item!')
                            print(newLine[0] + ':--' + str(newLine[1]) + '\n\n')
                            full.write(newLine[0] + ':--' + str(newLine[1]) + '\n')


# --------------------------------------------------------------------------
# parse the input line
# --------------------------------------------------------------------------
def getLine(line):
    if line == "":
        return (None, None)
    else:
        token = line.split(":--", 1)[0]
        postings = eval(line.split(":--", 1)[1])
        return (token, postings)




if __name__ == "__main__":
    index_info = read_info("report.txt")
    #initialize the new inverted index
    with open('inverted_indexFull.txt','w') as fp:
        pass

    start_merge(index_info["Total index partitions"])

    with open('dictionary.txt', 'a+') as file:
        for key, value in dictionary.items():
            file.write(key + ': ' + str(value) + '\n')
    # print(dictionary)
    # while True:
    #     if len(files) == 0:
    #         break
    #     else:
    #         for file in files.keys():
    #             print("Reading line from: {}".format(file))
    #             token, postings = getLine(file, files[file])
    #
    #             if token and postings:
    #                 if token not in inverted_index.keys():
    #                     inverted_index[token] = postings
    #                 else:
    #                     for id, score in postings.items():
    #                         inverted_index[token][id] = score

    # dump()
