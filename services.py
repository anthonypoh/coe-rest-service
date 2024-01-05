import csv
import glob
import io
import json
import os
import zipfile
from flask import jsonify
from matplotlib import pyplot as plt
import pandas as pd
import requests
from sklearn.linear_model import LinearRegression


def download(url, destination):
    # Extract the directory path from the destination
    directory = os.getcwd() + destination

    # directory = os.path.dirname(destination)

    # Check if the directory exists, and create it if not
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Download the file
    response = requests.get(url)
    with open(directory + "/file.zip", "wb") as file:
        file.write(response.content)


def unzip(zip_file_path, csv_file_pattern):
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        matching_files = [
            file
            for file in zip_ref.namelist()
            if glob.fnmatch.fnmatch(file, csv_file_pattern)
        ]
        if matching_files:
            # Assuming there's only one matching file, use the first one
            csv_file_name = matching_files[0]

            # Extract the CSV file
            with zip_ref.open(csv_file_name) as csv_file:
                # Read the CSV content
                csv_content = csv_file.read().decode("utf-8")

                df = pd.read_csv(io.StringIO(csv_content))

                return df


def correlation(df):
    categories = df["vehicle_class"].unique()
    latest_month = pd.to_datetime(df["month"].max(), format="%Y-%m")
    start_month = (latest_month - pd.DateOffset(months=5)).strftime("%Y-%m")
    filtered_df = df[df["month"] >= start_month]
    print(filtered_df)
    result_dict = {}
    for category in categories:
        category_data = filtered_df[filtered_df["vehicle_class"] == category]
        correlation = category_data["quota"].corr(category_data["premium"])
        result_dict[category] = correlation

    return result_dict


def predict(df, quota, cat):
    categories = ["A", "B", "C", "D", "E"]
    if cat not in categories:
        return "Category does not exist"

    category = "Category " + cat
    
    latest_month = pd.to_datetime(df["month"].max(), format="%Y-%m")
    start_month = (latest_month - pd.DateOffset(months=2)).strftime("%Y-%m")
    filtered_df = df[(df["vehicle_class"] == category) & (df["month"] >= start_month)]

    print(filtered_df)

    # Reshape the data
    X = filtered_df["quota"].values.reshape(-1, 1)
    y = filtered_df["premium"].values

    # Train a linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # Predict premium based on the chosen category, last 3 months, and quota using the trained model
    predicted_premium = model.predict([[quota]])[0]

    print(
        f"Predicted premium for {category} with quota {quota} in the last 3 months: {predicted_premium}"
    )

    # return f"Predicted premium for {category} with quota {quota} in the last 3 months: {predicted_premium}"
    return predicted_premium
