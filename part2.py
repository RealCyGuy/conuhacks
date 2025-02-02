import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import streamlit as st
from pandas import read_csv
from scipy.stats import randint
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import RandomizedSearchCV, train_test_split


# Load credentials from config.json
def load_credentials():
    with open("config.json", "r") as file:
        return json.load(file)


features = [
    "temperature",
    "humidity",
    "wind_speed",
    "precipitation",
    "vegetation_index",
    "human_activity_index",
]
st.write("Predictive Modeling for Future Fire Occurances!")
file = st.file_uploader("Upload environmental data csv:", type="csv")


def send_email(sender, recipients, subject, body):
    """
    Sends an email to multiple recipients using SMTP.
    :param recipients: List of email addresses.
    :param subject: Email subject.
    :param body: Email body.
    """
    SMTP_SERVER = "smtp.gmail.com"  # Change as per provider
    SMTP_PORT = 587
    SENDER_EMAIL = sender["email"]  # Use environment variable for security
    SENDER_PASSWORD = sender["password"]

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        for recipient in recipients:
            msg = MIMEMultipart()
            msg["From"] = SENDER_EMAIL
            msg["To"] = recipient
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            server.sendmail(SENDER_EMAIL, recipient, msg.as_string())

            print(f"✅ Email sent successfully to {recipient}")

        server.quit()
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")


@st.cache_resource
def train_model():
    wildfires = read_csv("historical_wildfiredata.csv")
    environment = read_csv("historical_environmental_data.csv")
    merged = environment.merge(wildfires, how="left")
    clf = RandomForestClassifier()
    param_dist = {"n_estimators": randint(1, 10)}
    rand_search = RandomizedSearchCV(clf, param_distributions=param_dist, n_iter=10)
    X = merged[features]
    y = merged["severity"].fillna("none")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    rand_search.fit(X_train, y_train)

    # print best parameters and classification report
    # st.write(rand_search.best_params_)
    # y_pred = rand_search.predict(X_test)
    # st.write(classification_report(y_test, y_pred))

    return rand_search


clf = train_model()

if file is not None:
    data = read_csv(file)
    data["severity"] = clf.predict(data[features])
    data["longitude"] = data["longitude"].astype(float)
    data["latitude"] = data["latitude"].astype(float)
    data["color"] = data["severity"].map(
        {"low": "#00FF00", "medium": "#FFFF00", "high": "#FF0000"}
    )
    data = data[data["color"].notnull()]
    st.map(data, color="color")
    st.write(data)

    severe_cases = data[data["severity"] == "high"]

    if not severe_cases.empty:
        sender = load_credentials()
        recipients = ["testdummy20240102@gmail.com"]
        subject = "🔥 Wildfire Alert: High Severity Predictions Generated!"

        # Create Google Maps links for each location
        location_details = "\n".join(
            [
                f"Latitude: {row['latitude']}, Longitude: {row['longitude']} - View on Map: https://www.google.com/maps?q={row['latitude']},{row['longitude']}"
                for _, row in severe_cases.iterrows()
            ]
        )
        body = f"Hello,\n\nThe wildfire prediction model has detected high severity fires in the following locations:\n\n{location_details}\n\nPlease take necessary actions.\n\nBest,\nDEVFIGHTERS Team"

        send_email(sender, recipients, subject, body)
        st.success("Email notification sent successfully for high severity fires! ✅")
