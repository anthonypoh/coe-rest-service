import csv
import glob
import io
import json
import os
import zipfile
import pandas as pd
import requests
from sklearn.linear_model import LinearRegression


def download(url, destination):
    directory = os.getcwd() + destination

    if not os.path.exists(directory):
        os.makedirs(directory)

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
            csv_file_name = matching_files[0]

            with zip_ref.open(csv_file_name) as csv_file:
                csv_content = csv_file.read().decode("utf-8")

                df = pd.read_csv(io.StringIO(csv_content))

                return df


def correlation(df):
    categories = df["vehicle_class"].unique()
    latest_month = pd.to_datetime(df["month"].max(), format="%Y-%m")
    start_month = (latest_month - pd.DateOffset(months=5)).strftime("%Y-%m")
    filtered_df = df[df["month"] >= start_month]
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

    X = filtered_df["quota"].values.reshape(-1, 1)
    y = filtered_df["premium"].values

    model = LinearRegression()
    model.fit(X, y)

    predicted_premium = model.predict([[quota]])[0]

    print(
        f"Predicted premium for {category} with quota {quota} in the last 3 months: {predicted_premium}"
    )

    return predicted_premium


def latest(df):
    df["bids_received"] = pd.to_numeric(
        df["bids_received"].str.replace(",", ""), errors="coerce"
    )
    return df.tail(5)


def differences(df):
    df["bids_received"] = pd.to_numeric(
        df["bids_received"].str.replace(",", ""), errors="coerce"
    )

    last_10_rows = df.tail(10)
    grouped = last_10_rows.groupby("vehicle_class")
    differences_dict = {}

    drop = ["month", "bidding_no"]
    for category, group in grouped:
        difference = group.drop(["month", "bidding_no", "vehicle_class"], axis=1).diff()

        differences_dict[category] = difference.tail(1).to_dict()

    return differences_dict
