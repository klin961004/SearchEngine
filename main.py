from invertedIndex import *


# --------------------------------------------------------------------------
# this will later be used in search engine
# --------------------------------------------------------------------------
def readId():
    file = open("ID.txt", 'r')

    id_map = dict()
    line = file.readline()

    while file:
        if line == "":
            break

        id = line.split(":", 1)[0]
        url = eval(line.split(":", 1)[1])
        id_map[id] = url
        line = file.readline()

    file.close()


if __name__ == "__main__":
    timer = time.time()
    root_directory = "./DEV"

    filepaths = retrieve_files(root_directory)
    for filepath in filepaths:
        print("Reading file path: {}".format(filepath))
        read_file(filepath)

    # dumping the last portion of inverted index into disk
    dump()
    get_scoring()
    dumpId()
    write_report()

    print("Program run time: {} s".format(time.time() - timer))
