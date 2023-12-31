# -*- coding: utf-8 -*-
"""
@author: hina
"""
print ()

import string
import re
from nltk.corpus import stopwords
from stemming.porter2 import stem
import networkx

# open file to read amazon product metadata 
# Dataset: http://snap.stanford.edu/data/amazon-meta.html
fhr = open('./amazon-meta.txt', 'r', encoding='utf-8', errors='ignore')

# initialize a nested product dictionary that will hold cleaned up amazon product data
# key = ASIN; value = MetaData associated with ASIN
amazonProducts = {}

# read the data from the amazon-meta file;
# populate amazonProducts nested dicitonary;
(Id, ASIN, Title, Categories, Group, Copurchased, SalesRank, TotalReviews, AvgRating, DegreeCentrality, ClusteringCoeff) = \
    ("", "", "", "", "", "", 0, 0, 0.0, 0, 0.0)
for line in fhr:
    line = line.strip()
    # a product block started
    if(line.startswith("Id")):
        Id = line[3:].strip()
    elif(line.startswith("ASIN")):
        ASIN = line[5:].strip()
    elif(line.startswith("title")):
        Title = line[6:].strip()
        Title = ' '.join(Title.split())
    elif(line.startswith("group")):
        Group = line[6:].strip()
    elif(line.startswith("salesrank")):
        SalesRank = line[10:].strip()
    elif(line.startswith("similar")):
        ls = line.split()
        Copurchased = ' '.join([c for c in ls[2:]])
    elif(line.startswith("categories")):
        ls = line.split()
        Categories = ' '.join((fhr.readline()).lower() for i in range(int(ls[1].strip())))
        Categories = re.compile('[%s]' % re.escape(string.digits+string.punctuation)).sub(' ', Categories)
        Categories = ' '.join(set(Categories.split())-set(stopwords.words("english")))        
        Categories = ' '.join(stem(word) for word in Categories.split())
    elif(line.startswith("reviews")):
        ls = line.split()
        TotalReviews = ls[2].strip()
        AvgRating = ls[7].strip()
    # a product block ended
    # write out fields to amazonProducts Dictionary
    elif (line==""):
        try:
            MetaData = {}
            if (ASIN != ""):
                amazonProducts[ASIN]=MetaData
            MetaData['Id'] = Id            
            MetaData['Title'] = Title
            MetaData['Categories'] = ' '.join(set(Categories.split()))
            MetaData['Group'] = Group
            MetaData['Copurchased'] = Copurchased
            MetaData['SalesRank'] = int(SalesRank)
            MetaData['TotalReviews'] = int(TotalReviews)
            MetaData['AvgRating'] = float(AvgRating)
            MetaData['DegreeCentrality'] = DegreeCentrality
            MetaData['ClusteringCoeff'] = ClusteringCoeff
        except NameError:
            continue
        (Id, ASIN, Title, Categories, Group, Copurchased, SalesRank, TotalReviews, AvgRating, DegreeCentrality, ClusteringCoeff) = \
            ("", "", "", "", "", "", 0, 0, 0.0, 0, 0.0)
fhr.close()

# create books-specific dictionary exclusively for books
amazonBooks = {}
for asin,metadata in amazonProducts.items():
    if (metadata['Group']=='Book'):
        amazonBooks[asin] = amazonProducts[asin]
    
# remove any copurchased items from copurchase list 
# if we don't have metadata associated with it 
for asin, metadata in amazonBooks.items(): 
    amazonBooks[asin]['Copurchased'] = \
        ' '.join([cp for cp in metadata['Copurchased'].split() \
            if cp in amazonBooks.keys()])

# create a product copurchase graph for analysis
# where the graph nodes are product ASINs;
# and graph edge exists if two products were copurchased,
# with edge weight being a measure of category similarity between ASINs
copurchaseGraph = networkx.Graph()
for asin,metadata in amazonBooks.items():
    copurchaseGraph.add_node(asin)
    for a in metadata['Copurchased'].split():
        copurchaseGraph.add_node(a.strip())
        similarity = 0        
        n1 = set((amazonBooks[asin]['Categories']).split())
        n2 = set((amazonBooks[a]['Categories']).split())
        n1In2 = n1 & n2
        n1Un2 = n1 | n2
        if (len(n1Un2)) > 0:
            similarity = round(len(n1In2)/len(n1Un2),2)
        copurchaseGraph.add_edge(asin, a.strip(), weight=similarity)

# get degree centrality and clustering coefficients 
# of each ASIN and add it to amazonBooks metadata
dc = networkx.degree(copurchaseGraph)
for asin in networkx.nodes(copurchaseGraph):
    metadata = amazonBooks[asin]
    metadata['DegreeCentrality'] = int(dc[asin])
    ego = networkx.ego_graph(copurchaseGraph, asin, radius=1)
    metadata['ClusteringCoeff'] = round(networkx.average_clustering(ego),2)
    amazonBooks[asin] = metadata

# write amazonBooks data to file
# (all except copurchase data - becuase that data is now in the graph)
fhw = open('./amazon-books.txt', 'w', encoding='utf-8', errors='ignore')
fhw.write("Id\t" + "ASIN\t" + "Title\t" + 
        "Categories\t" + "Group\t" #+ "Copurchased\t" + 
        "SalesRank\t" + "TotalReviews\t" + "AvgRating\t"
        "DegreeCentrality\t" + "ClusteringCoeff\n")
for asin,metadata in amazonBooks.items():
    fhw.write(metadata['Id'] + "\t" + \
            asin + "\t" + \
            metadata['Title'] + "\t" + \
            metadata['Categories'] + "\t" + \
            metadata['Group'] + "\t" + \
            str(metadata['SalesRank']) + "\t" + \
            str(metadata['TotalReviews']) + "\t" + \
            str(metadata['AvgRating']) + "\t" + \
            str(metadata['DegreeCentrality']) + "\t" + \
            str(metadata['ClusteringCoeff']) + "\n")
fhw.close()

# write copurchaseGraph data to file
fhw=open("amazon-books-copurchase.edgelist",'wb')
networkx.write_weighted_edgelist(copurchaseGraph, fhw)
fhw.close()

print('File ran!')