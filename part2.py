import streamlit as st
from pandas import read_csv
from scipy.stats import randint
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import RandomizedSearchCV, train_test_split

features = [
    "temperature",
    "humidity",
    "wind_speed",
    "precipitation",
    "vegetation_index",
    "human_activity_index",
]
st.write("Hello World!")
file = st.file_uploader("Upload a file")


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
    st.write(data)
    st.map(data, color="color")
