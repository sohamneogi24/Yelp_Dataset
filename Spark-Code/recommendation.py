from pyspark.sql import SparkSession

import json
from pyspark.mllib.recommendation import ALS, MatrixFactorizationModel, Rating
import math
import os
import shutil



def execute(spark, path, state_name, dir_name):
    df = spark.read.json(path)
    df = df.select('*', (df.review_stars * 2).alias('rescaled_rating'))
    df.createOrReplaceTempView("user_business_review")
    ratingsDf = spark.sql("Select user_unique_user_id, unique_business_id, rescaled_rating from user_business_review")
    (training, testing) = ratingsDf.randomSplit([0.8, 0.2])
    ratings = training.rdd.map(lambda l: Rating(int(l[0]), int(l[1]), float(l[2])))
    rank = 100
    numIterations = 15
    model = ALS.train(ratings, rank, numIterations)
    testdata = testing.rdd.map(lambda p: (p[0], p[1]))
    predictions = model.predictAll(testdata)
    p = predictions.toDF()
    p.createOrReplaceTempView("outcome")
    out = spark.sql(
        "Select u.rescaled_rating, p.* from user_business_review u,"
        " outcome p where p.user=u.user_unique_user_id and u.unique_business_id=p.product")

    print("**********", math.sqrt(out.rdd.map(lambda x: (x[0] - x[3]) ** 2).mean()), " ********** ")
    model_name = dir_name + "/" + state_name + ".parquet"
    model.save(spark.sparkContext, model_name)
    print("********* SAVED MODEL ****** ", model_name)



if __name__ == "__main__":

    spark = SparkSession.builder.appName("YelpRecommendation").getOrCreate()

    properties = json.load(open('application-properties.json'))
    if os.path.exists('als-models'):
        shutil.rmtree('als-models')
    os.mkdir('als-models')
    for file_location in properties['data'] :
        print('PROCESSING :', file_location['path'])
        concat_path = properties['base_path'] + file_location['path']
        dir_name = 'als-models/' + file_location['path'].split('.')[0]
        os.mkdir(dir_name)
        execute(spark, concat_path, file_location['path'].split('.')[0],dir_name)






