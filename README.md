# Using-Amazon-data-to-generate-book-recommendations
Using the Amazon Meta-Data Set maintained on the SNAP site, generate a composite measure on the basis of which, generate Top 5 recommendations (ASIN, and associated Title, Sales Rank, TotalReviews, AvgRating, DegreeCentrality, ClusteringCoeff). 

### The Dataset:
This data set is comprised of product and review metdata on 548,552 different products and was collected in 2006 by crawling the Amazon website.
The following information is available for each product in this dataset:
•	Id: Product id (number 0, ..., 548551)
•	ASIN: Amazon Standard Identification Number. 
The Amazon Standard Identification Number (ASIN) is a 10-character alphanumeric unique identifier assigned by Amazon.com for product identification. You can lookup products by ASIN using following link: https://www.amazon.com/product-reviews/<ASIN> 
•	title: Name/title of the product
•	group: Product group. The product group can be Book, DVD, Video or Music.
•	salesrank: Amazon Salesrank
The Amazon sales rank represents how a product is selling in comparison to other products in its primary category. The lower the rank, the better a product is selling. 
•	similar: ASINs of co-purchased products (people who buy X also buy Y)
•	categories: Location in product category hierarchy to which the product belongs (separated by |, category id in [])
•	reviews: Product review information: total number of reviews, average rating, as well as individual customer review information including time, user id, rating, total number of votes on the review, total number of helpfulness votes (how many people found the review to be helpful)

Using the co-purchase data in amazonBooks Dictionary, I created the copurchaseGraph Structure as follows:
- Nodes: the ASINs are Nodes in the Graph
- Edges: an Edge exists between two Nodes (ASINs) if the two ASINs were co-purchased
- Edge Weight (based on Category Similarity): Attempting to make book recommendations based on co-purchase information, I created a measure of Similarity for each ASIN (Node) pair that was co-purchased (existence of Edge between the Nodes) - using which as the Edge Weight between the Node pair that was co-purchased, to potentially create such a Similarity measure by using the “Categories” data, where the Similarity measure between any two ASINs that were co-purchased is calculated as follows:
    Similarity = (Number of words that are common between Categories of connected Nodes)/
		(Total Number of words in both Categories of connected Nodes)

The Similarity ranges from 0 (most dissimilar) to 1 (most similar).

Using ASIN, I generate DegreeCentrality and ClusterCoefficient associated with each node and then generate book recommendations. 
