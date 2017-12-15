from flask import Flask, request, Response, render_template, redirect, jsonify
import json
from pyspark.mllib.recommendation import ALS, MatrixFactorizationModel, Rating
from pyspark.sql import SparkSession
import pickle
from pymongo import MongoClient

spark = SparkSession.builder.appName("YelpRecommendationWeb").getOrCreate()
app = Flask(__name__)

# for CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST') # Put any other methods you need here
    return response


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/recommendations/<int:user_id>', methods = ['GET'])
def get_recommendations_html():
    #recommendation = fetchRecommendations()
    return render_template('recommendation.html', )


@app.route('/signin', methods = ['POST'])
def signIn():
    print('request :', request)

    user_name = request.form['existingUserId']
    print("user_name  :", user_name )
    password = request.form['existingUserInputPassword']
    user_obj = validate_credentials(user_name, password)
    print(user_obj)
    if user_obj['status'] == 'ok':
        reco = get_recommendations_existing_user(user_obj)

        return render_template('recommendation.html', reco = reco)
    return '<h1>User Authentication Failed</h1>'

@app.route('/signup', methods = ['POST'])
def signUp():
    # fix this
    user_detail = request.json['credentials']
    client = MongoClient('localhost', 27017)
    db = client['user_info']
    collection = db['user']
    document = dict()
    document['user_name'] = user_detail['user_name']
    document['password'] = user_detail['password']
    document['user_id'] = 987654
    document['cold_start_status'] = True
    document['state'] = user_detail['state']
    collection.insert(document, check_keys=False)
    return jsonify(document)



@app.route('/sentiment', methods = ['GET'])
def sentiment():
    # fix this
    business_id = 36402#request.form['businessId']

    #rest_corpus_data = pickle.load(open("sentiment-models/NC/nc_sentiment_corpus.json", "rb"))
    #sentiments = rest_corpus_data[business_id]
    #print('sentiments :', sentiments)
    return get_sentiment_data(business_id, 'NC')



def get_sentiment_data(business_id, state):
    client = MongoClient('localhost', 27017)

    db = client['business_info']
    collection_name = state.lower()
    collection = db[collection_name]
    business_info = collection.find_one({'business_id' : business_id})

    db = client['sentiment_data']
    collection_name = state.lower() + "_sentiment_corpus"
    collection = db[collection_name]
    corpus_data = collection.find_one({'business_id': business_id})

    collection_name = state.lower() + "_sentiment_dict"
    collection = db[collection_name]
    dict_data = collection.find_one({'business_id': business_id})


    response = dict()
    response['business_id'] = business_id
    response['business_name'] = business_info['name']
    response['business_address'] = business_info['address'] + ", " + business_info['city']
    response['business_categories'] = business_info['categories']
    response['business_stars'] = business_info['stars']

    response['sentiments'] = corpus_data['business_data']

    all_reviews = dict_data['business_data']
    business_reviews = []
    for review in all_reviews :
        color = None
        if review['polarity'] < 0 :
            color = 'red'
        else :
            color = 'green'
        business_reviews.append({
            'text' : review['review_text'],
            'polarity' : review['polarity'],
            'color' : color

        })
    response['business_text'] = business_reviews

    return jsonify(response)

@app.route('/existingRecommendations/<int:userId>/<string:state>', methods = ['GET'])
def get_existing_user_reco(userId, state) :
    user_detail = dict()
    user_detail['state'] = state
    user_detail['user_id'] = userId
    return get_recommendations_existing_user(user_detail)


@app.route('/coldStartRecommendations', methods = ['POST'])
def get_coldstart_user_reco() :
    request_dict = request.json['coldstart']
    return get_cold_start_reco(request_dict)


@app.route('/recommendProductForProducts', methods = ['POST'])
def get_product_for_products_reco() :
    request_dict = request.json['products']
    file_name = request_dict['state'] + '.parquet'
    model = loadALSModel(file_name)
    users_suggested = model.recommendUsers(request_dict['business_id'], 3)
    suggestions = []
    final_recommendations = []
    for u in users_suggested:
        product_suggested = model.recommendProducts(u[0], 3)
        for p in product_suggested:
            if p[1] not in suggestions:
                suggestions.append(p[1])
                final_recommendations.append(p)

    final_reco = sorted(final_recommendations, key=lambda x: x[2])
    return get_recommendation_response(final_reco, request_dict)



def get_cold_start_reco(user_detail) :
    state = user_detail['state']
    tastes = user_detail['taste']

    file_name = state + '.parquet'
    model = loadALSModel(file_name)
    suggestions = []
    final_recommendations = []
    for taste in tastes :
        users_suggested = model.recommendUsers(taste, 3)

        for u in users_suggested :
            product_suggested = model.recommendProducts(u[0], 3)
            for p in product_suggested :
                if p[1] not in suggestions :
                    suggestions.append(p[1])
                    final_recommendations.append(p)


    final_reco  = sorted(final_recommendations, key=lambda x : x[2])
    return get_recommendation_response(final_reco, user_detail)








def loadALSModel(file_name) :
    return MatrixFactorizationModel.load(sc=spark.sparkContext,
                                          path='als-models/' + file_name)

def get_recommendations_existing_user(user_detail) :

    user_state = user_detail['state']
    file_name = user_state  + '.parquet'
    model = loadALSModel(file_name)

    user_id = user_detail['user_id']
    recommendations = model.recommendProducts(user_id, 10)

    return get_recommendation_response(recommendations, user_detail)

def get_recommendation_response(recommendations, user_detail) :
    result = dict()
    client = MongoClient('localhost', 27017)
    user_state = user_detail['state']

    db = client['business_info']
    collection_name = user_state.lower()
    reco_arr = []
    for reco in recommendations :
        print('reco :' , reco)
        user= reco[0]
        product = reco[1]

        response = dict()
        response['business_id'] = product
        response['rating'] = reco[2]
        response['user_id'] = user
        collection = db[collection_name]
        business_info = collection.find_one({'business_id': product})
        response['state'] = user_state
        response['business_id'] = product
        response['business_name'] = business_info['name']
        response['business_address'] = business_info['address'] + ", " + business_info['city']
        response['business_categories'] = business_info['categories']
        response['business_stars'] = business_info['stars']
        reco_arr.append(response)
    result['recommendations'] = reco_arr
    return jsonify(result)

def validate_credentials(user_name, password) :
    client = MongoClient('localhost', 27017)
    db = client['user_info']
    collection = db['user']
    resp = collection.find_one({'user_name' : user_name, 'password' : password})
    if resp is not None :
        return resp
    return {'status': 'authentication failed'}



@app.route('/recommendation')
def recommendation():
    return render_template('recommendation.html')

if __name__ == '__main__':
    app.run(debug= True, port = 8000, host ='0.0.0.0')