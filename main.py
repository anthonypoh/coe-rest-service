from flask import Flask, jsonify
import os
from services import download, unzip, correlation, predict, latest, differences

app = Flask(__name__)

LTA_COE_BIDDING_RESULT = "https://datamall.lta.gov.sg/content/dam/datamall/datasets/Facts_Figures/Vehicle%20Registration/COE%20Bidding%20Results.zip"
directory = os.getcwd()


@app.route("/")
def index():
    zip_file_path = directory + "/data/file.zip"
    csv_file_pattern = "*-coe_results.csv"

    download(LTA_COE_BIDDING_RESULT, "/data")
    df = unzip(zip_file_path, csv_file_pattern)

    last_5_rows = latest(df)
    return last_5_rows.to_json(orient="records")
    # return df.to_json(orient="records")


@app.route("/api/get-difference")
def getDifference():
    zip_file_path = directory + "/data/file.zip"
    csv_file_pattern = "*-coe_results.csv"

    download(LTA_COE_BIDDING_RESULT, "/data")
    df = unzip(zip_file_path, csv_file_pattern)

    difference = differences(df)
    return jsonify(difference=difference)


@app.route("/api/get-prediction/<int:quota>/<string:cat>", methods=["GET"])
def getPrediction(quota, cat):
    zip_file_path = directory + "/data/file.zip"
    csv_file_pattern = "*-coe_results.csv"

    download(LTA_COE_BIDDING_RESULT, "/data")
    df = unzip(zip_file_path, csv_file_pattern)

    prediction = predict(df, quota, cat)

    return jsonify(quota=quota, category=cat, prediction=prediction)


@app.route("/api/get-correlation", methods=["GET"])
def getCorrelation():
    zip_file_path = directory + "/data/file.zip"
    csv_file_pattern = "*-coe_results.csv"

    download(LTA_COE_BIDDING_RESULT, "/data")
    df = unzip(zip_file_path, csv_file_pattern)

    corr = correlation(df)

    return jsonify(correlation=corr)


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000))
