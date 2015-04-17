import re
import collections
import datetime as dt

rdate = re.compile(r"BLOG06-(\d+)-.+?", re.DOTALL | re.IGNORECASE)


def docno2date(docno):
    datestring = rdate.search(docno).group(1).strip()
    if int(datestring[0]) > 2:
        datestring = "19" + datestring
    date = dt.date(int(datestring[0:4]), int(datestring[4:6]), int(datestring[6:8]))
    return date


def readInQrels(fname, maxelem=250):
    queries2documents = collections.defaultdict(lambda: {})
    for l in file(fname):
        qid, dummy, docno, rank, value, name = l.strip().split()
        if not int(rank) > maxelem:
            queries2documents[qid][rank] = (docno, docno2date(docno), value)
    return queries2documents


def rankedList2Set(queries2documents):
    queries2sets = collections.defaultdict(lambda: {})
    queries2setsrelevance = collections.defaultdict(lambda: {})
    for q, rankedlist in queries2documents.iteritems():
        for doc in rankedlist.values():
            queries2sets[q][doc[0]] = doc[1]
            queries2setsrelevance[q][doc[0]] = float(doc[2])
    return queries2sets, queries2setsrelevance
