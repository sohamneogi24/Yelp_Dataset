Live URL :

http://35.227.37.113:8000

Existing User


username : test1


password : ""

Cold Start User


username : <username>
 
 
password : <password>
 

Overview

Yelp.com is the go-to website for anybody looking for recommendations about local businesses. Over the period of time, it has become quite popular for restaurant recommendations as users find it easier to judge a local business by reading reviews about that business posted by other users. In addition to writing reviews and rating local businesses, user can react to reviews, plan events or start up a discussion forum. Yelp has about 135 million monthly customers and 95 million reviews.


Goals

The Yelp dataset is open sourced and it has enough information about each local business, reviews about those businesses , tips written by the user about a local business and photos uploaded by the user about the local business. This dataset can help us summarize useful information about most popular and unpopular restaurants classified by food genre and user reviews. For each restaurant we can analyze all the reviews pertaining to a restaurant and derive inherent topics.

Use Cases

A. Recommend Restaurants to existing user using ALS Matrix Factorization Model
B. Recommend Restaurants to cold start user after getting an idea about the initial taste of the user
C. Perform Sentiment Analysis on each review and calculate the polarity score of each restaurant
D.Finally, give a high level view of peole's opinions that can be found when each restaurant review is mined for topic modelling.



Data

1.  Yelp Dataset: http://www.yelp.com/dataset
We will work with the Yelp Dataset available online.



Process Outline

1. Data Preprocessing
●      Data Cleaning, handling missing values
●      Joining Business.json, Reviews.json, User.json, Tips.json and Image.json
2. Exploratory Data Analysis
3. Understanding Apache Spark, ALS Rating, SVD and LDA that we would like to use for building a recommendation engine with will also showcase sentiment analysis done on text reviews.
4. Build a flask application that can serve real time recommendations to cold-start and existing users
5. Deploy the Model on AWS or Google Cloud Computing Platform




Deployment / Infrastructure Details

1)    Language: Python, Java
2)    Framework: Apache Spark
3)    Cloud Tools/Platforms: Google Cloud Platform
5)    Tools for Analysis: Pandas / Seaborn / Matplotlib




Reference Sources

https://www.yelp.com/dataset/documentation/json


Video URL

https://www.youtube.com/watch?v=nudb7iET7Q0
