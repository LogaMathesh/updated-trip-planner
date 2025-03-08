from flask import Flask, render_template, request, redirect, session
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Used for session management

# Excel file setup
USER_DB = "users.xlsx"
LOCATION_DB = "locations.xlsx"

# Check if the user database exists, if not create it
if not os.path.exists(USER_DB):
    df = pd.DataFrame(columns=["Name", "UserID", "Password", "Favorites", "RecentlyViewed"])
    df.to_excel(USER_DB, index=False)

if not os.path.exists(LOCATION_DB):
    df_locations = pd.DataFrame({"Location": ["Paris", "Tokyo", "New York"], "Rating": [5, 4.8, 4.7]})
    df_locations.to_excel(LOCATION_DB, index=False)

# Home Page
@app.route("/")
def home():
    # Load locations
    df_locations = pd.read_excel(LOCATION_DB)
    most_rated = df_locations.sort_values(by="Rating", ascending=False).to_dict(orient="records")

    if "user" in session:
        user_id = session["user"]
        df = pd.read_excel(USER_DB)
        user_data = df[df["UserID"] == user_id].iloc[0]
        
        favorites = user_data["Favorites"].split(",") if pd.notna(user_data["Favorites"]) else []
        recent = user_data["RecentlyViewed"].split(",") if pd.notna(user_data["RecentlyViewed"]) else []

        return render_template("index.html", most_rated=most_rated, user=session["user"], favorites=favorites, recent=recent)
    
    return render_template("index.html", most_rated=most_rated, user=None)

# Signup Page
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        user_id = request.form["user_id"]
        password = request.form["password"]

        df = pd.read_excel(USER_DB)

        if user_id in df["UserID"].values:
            return "User ID already exists. Try another one!"

        new_user = pd.DataFrame([[name, user_id, password, "", ""]], columns=df.columns)
        df = pd.concat([df, new_user], ignore_index=True)
        df.to_excel(USER_DB, index=False)

        return redirect("/")
    
    return render_template("signup.html")

# Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form["user_id"]
        password = request.form["password"]

        df = pd.read_excel(USER_DB)
        user = df[(df["UserID"] == user_id) & (df["Password"] == password)]

        if not user.empty:
            session["user"] = user_id
            return redirect("/")
        else:
            return "Invalid Credentials!"
    
    return render_template("login.html")

# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
