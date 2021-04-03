ABOUT
-------------------------
This is the implementation of a full inverted index and search engine
by 
# Michelle Lin

CONFIGURATION
-------------------------

### Step 1: Install dependencies

If you do not have Python 3.6+:

Windows: https://www.python.org/downloads/windows/

Linux: https://docs.python-guide.org/starting/install3/linux/

MAC: https://docs.python-guide.org/starting/install3/osx/

Check if pip is installed by opening up a terminal/command prompt and typing
the commands `python3 -m pip`. This should show the help menu for all the
commands possible with pip. If it does not, then get pip by following the
instructions at https://pip.pypa.io/en/stable/installing/

To install the dependencies for this project run the following two commands
after ensuring pip is installed for the version of python you are using.
Admin privileges might be required to execute the commands. Also make sure
that the terminal is at the root folder of this project.
```
pip install nltk
pip install bs4
pip install psutil
```


### Step 2: Change directory

modify
```
root_directory = "./DEV"
```

in main.py to the path where the documents are located


### Step 3: Check memory capacity
modify
```
global variable mem_cap = 35.0
```
in invertedIndex.py to the percentage of memory remaining before off
loading you desired 

### Step 4: Indexing
locate to the rootdirectory, run
```
python3 main.py
```
to start indexing the documents

### Step 5: Merging
locate to the rootdirectory, run
```
python3 merge.py
```
to start merging all the partitions of inverted indexes into one

### Step 6: query
locate to the rootdirectory, run
```
python3 engine.py
```
a user prompt will appear, type in your query
your result will be printed with the highest ranking from top to bottom
along with the title of the page and the url of the page

ARCHITECTURE
-------------------------

### FLOW

The code will parse through all the json documents in the root directory and
calculate the TF-IDF scoring of the token in each documents.

The code provide memory dictation which will offload the scraped data to the
hard disk if the available memory for the operating machine is less than
mem_cap percent(default=35.0).

Launching merge.py then merge all the inverted index partitions into one by
processing portions of each partitions at a time. A token map will also be
recorded at this stage to optimize search time when handling the queries.

engine.py is mainly for users which users can launch it to dispatch queries
against the document collection. The code will parse the query using same
parsing step when parsing the documents, utilize the token map to locate
the position of the token is stored inside the inverted index. Then obtaining
both query vector and document vector for each document that are related to
the query tokens.
# SearchEngine
