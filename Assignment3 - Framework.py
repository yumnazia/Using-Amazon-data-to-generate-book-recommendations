# -*- coding: utf-8 -*-
"""
@author: hina
"""
print ()

import networkx
import operator
import matplotlib.pyplot as plt

# Read the data from the amazon-books.txt;
# populate amazonProducts nested dicitonary;
# key = ASIN; value = MetaData associated with ASIN
fhr = open('./amazon-books.txt', 'r', encoding='utf-8', errors='ignore')
amazonBooks = {}
fhr.readline()
for line in fhr:
    cell = line.split('\t')
    MetaData = {}
    MetaData['Id'] = cell[0].strip() 
    ASIN = cell[1].strip()
    MetaData['Title'] = cell[2].strip()
    MetaData['Categories'] = cell[3].strip()
    MetaData['Group'] = cell[4].strip()
    MetaData['SalesRank'] = int(cell[5].strip())
    MetaData['TotalReviews'] = int(cell[6].strip())
    MetaData['AvgRating'] = float(cell[7].strip())
    MetaData['DegreeCentrality'] = int(cell[8].strip())
    MetaData['ClusteringCoeff'] = float(cell[9].strip())
    amazonBooks[ASIN] = MetaData
fhr.close()

# Read the data from amazon-books-copurchase.adjlist;
# assign it to copurchaseGraph weighted Graph;
# node = ASIN, edge= copurchase, edge weight = category similarity
fhr=open("amazon-books-copurchase.edgelist", 'rb')
copurchaseGraph=networkx.read_weighted_edgelist(fhr)
fhr.close()

# Now let's assume a person is considering buying the following book;
# what else can we recommend to them based on copurchase behavior 
# we've seen from other users?
print ("Looking for Recommendations for Customer Purchasing this Book:")
print ("--------------------------------------------------------------")
purchasedAsin = '0805047905'

# Let's first get some metadata associated with this book
print ("ASIN = ", purchasedAsin) 
print ("Title = ", amazonBooks[purchasedAsin]['Title'])
print ("SalesRank = ", amazonBooks[purchasedAsin]['SalesRank'])
print ("TotalReviews = ", amazonBooks[purchasedAsin]['TotalReviews'])
print ("AvgRating = ", amazonBooks[purchasedAsin]['AvgRating'])
print ("DegreeCentrality = ", amazonBooks[purchasedAsin]['DegreeCentrality'])
print ("ClusteringCoeff = ", amazonBooks[purchasedAsin]['ClusteringCoeff'])
    
# Now let's look at the ego network associated with purchasedAsin in the
# copurchaseGraph - which is esentially comprised of all the books 
# that have been copurchased with this book in the past
# (1) YOUR CODE HERE: 

#     Get the depth-1 ego network of purchasedAsin from copurchaseGraph,
#     and assign the resulting graph to purchasedAsinEgoGraph.
#purchasedAsinEgoGraph = networkx.Graph()
#purchasedAsinEgoGraph = networkx.ego_graph(copurchaseGraph, purchasedAsin, radius=1)
purchasedAsinEgoGraph = networkx.ego_graph(copurchaseGraph,purchasedAsin,radius=1)
pos = networkx.spring_layout(purchasedAsinEgoGraph)  
plt.figure(figsize=(30,30))
networkx.draw_networkx_labels(purchasedAsinEgoGraph,pos,font_size=20)
networkx.draw(purchasedAsinEgoGraph, pos=pos, node_size=1000, node_color='b', edge_color='b', style='solid')
plt.show()

# Next, recall that the edge weights in the copurchaseGraph is a measure of
# the similarity between the books connected by the edge. So we can use the 
# island method to only retain those books that are highly simialr to the 
# purchasedAsin
# (2) YOUR CODE HERE: 
#     Use the island method on purchasedAsinEgoGraph to only retain edges with 
#     threshold >= 0.5, and assign resulting graph to purchasedAsinEgoTrimGraph

threshold = 0.5
purchasedAsinEgoTrimGraph = networkx.Graph()
for f,t,e in purchasedAsinEgoGraph.edges(data=True):
    if e['weight']>=threshold:
        purchasedAsinEgoTrimGraph.add_edge(f,t,weight=e['weight'])
print('island graph done')
#print(purchasedAsinEgoTrimGraph)


# Next, recall that given the purchasedAsinEgoTrimGraph you constructed above, 
# you can get at the list of nodes connected to the purchasedAsin by a single 
# hop (called the neighbors of the purchasedAsin) 
# (3) YOUR CODE HERE: 
#     Find the list of neighbors of the purchasedAsin in the 
#     purchasedAsinEgoTrimGraph, and assign it to purchasedAsinNeighbors
purchasedAsinNeighbors = [i for i in purchasedAsinEgoTrimGraph.neighbors(purchasedAsin)]
print('neighbours found successfully:')
print(purchasedAsinNeighbors)
print()

# Next, let's pick the Top Five book recommendations from among the 
# purchasedAsinNeighbors based on one or more of the following data of the 
# neighboring nodes: SalesRank, AvgRating, TotalReviews, DegreeCentrality, 
# and ClusteringCoeff
# (4) YOUR CODE HERE: 
#     Note that, given an asin, you can get at the metadata associated with  
#     it using amazonBooks (similar to lines 49-56 above).
#     Now, come up with a composite measure to make Top Five book 
#     recommendations based on one or more of the following metrics associated 
#     with nodes in purchasedAsinNeighbors: SalesRank, AvgRating, 
#     TotalReviews, DegreeCentrality, and ClusteringCoeff. Feel free to compute
#     and include other measures. 
rating = {}
DC, SalesRank={},{}

for ASIN in purchasedAsinNeighbors:
    DC[ASIN] = amazonBooks[ASIN]['DegreeCentrality']
    SalesRank[ASIN] = amazonBooks[ASIN]['SalesRank']
    rating[ASIN] = amazonBooks[ASIN]['AvgRating']
    
DCmax =(max(DC.items(), key=operator.itemgetter(1)))[1]
print(DCmax)
maxSalesRank = (max(SalesRank.items(), key=operator.itemgetter(1)))[1]
print(maxSalesRank)
maxrating =(max(rating.items(), key=operator.itemgetter(1)))[1]
print(maxrating)

ratings ={}
for ASIN in purchasedAsinNeighbors:
    ratings[ASIN]=((maxSalesRank-amazonBooks[ASIN]['SalesRank']/maxSalesRank)+(amazonBooks[ASIN]['DegreeCentrality']/DCmax)+(amazonBooks[ASIN]['AvgRating']/maxrating))/3

compositeRatings = dict(reversed(sorted(ratings.items(), key=operator.itemgetter(1))))

# Print Top 5 recommendations (ASIN, and associated Title, Sales Rank, 
# TotalReviews, AvgRating, DegreeCentrality, ClusteringCoeff)
# (5) YOUR CODE HERE:  

print('Recommendations:', end='\n')
counter=0
for key in compositeRatings:
    counter+=1
    if(counter<=5):
        print('Title: ',amazonBooks[key]['Title'])
        print('Sales Rank: ',amazonBooks[key]['SalesRank'])
        print('Average Rating: ',amazonBooks[key]['AvgRating'])
        print('Total Reviews: ',amazonBooks[key]['TotalReviews'])
        print('Degree Centrality: ',amazonBooks[key]['DegreeCentrality'])
        print('Clustering Coefficient: ',amazonBooks[key]['ClusteringCoeff'])
        print()
    else:
        break
