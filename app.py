import streamlit as st
import json
import os
import numpy as np
from docx import Document
# import pdfplumber
import matplotlib.colors as mcolors
from operator import index
import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
import string
from dotenv import load_dotenv
import docx
from PIL import Image
from openai import OpenAI
import base64

load_dotenv()


session_state = st.session_state
if "user_index" not in st.session_state:
    st.session_state["user_index"] = 0


def signup(json_file_path="data.json"):
    st.title("Signup Page")
    with st.form("signup_form"):
        st.write("Fill in the details below to create an account:")
        name = st.text_input("Name:")
        email = st.text_input("Email:")
        age = st.number_input("Age:", min_value=0, max_value=120)
        sex = st.radio("Sex:", ("Male", "Female", "Other"))
        password = st.text_input("Password:", type="password")
        confirm_password = st.text_input("Confirm Password:", type="password")

        if st.form_submit_button("Signup"):
            if password == confirm_password:
                user = create_account(name, email, age, sex, password, json_file_path)
                session_state["logged_in"] = True
                session_state["user_info"] = user
            else:
                st.error("Passwords do not match. Please try again.")


def check_login(username, password, json_file_path="data.json"):
    try:
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)

        for user in data["users"]:
            if user["email"] == username and user["password"] == password:
                session_state["logged_in"] = True
                session_state["user_info"] = user
                st.success("Login successful!")
                render_dashboard(user)
                return user

        st.error("Invalid credentials. Please try again.")
        return None
    except Exception as e:
        st.error(f"Error checking login: {e}")
        return None


def initialize_database(json_file_path="data.json"):
    try:
        # Check if JSON file exists
        if not os.path.exists(json_file_path):
            # Create an empty JSON structure
            data = {"users": []}
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file)
    except Exception as e:
        print(f"Error initializing database: {e}")


def create_account(name, email, age, sex, password, json_file_path="data.json"):
    try:
        # Check if the JSON file exists or is empty
        if not os.path.exists(json_file_path) or os.stat(json_file_path).st_size == 0:
            data = {"users": []}
        else:
            with open(json_file_path, "r") as json_file:
                data = json.load(json_file)

        # Append new user data to the JSON structure
        user_info = {
            "name": name,
            "email": email,
            "age": age,
            "sex": sex,
            "password": password,
            "test_cases": None,
            "program": None,
        }
        data["users"].append(user_info)

        # Save the updated data to JSON
        with open(json_file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

        st.success("Account created successfully! You can now login.")
        return user_info
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON: {e}")
        return None
    except Exception as e:
        st.error(f"Error creating account: {e}")
        return None


def login(json_file_path="data.json"):
    st.title("Login Page")
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    login_button = st.button("Login")

    if login_button:
        user = check_login(username, password, json_file_path)
        if user is not None:
            session_state["logged_in"] = True
            session_state["user_info"] = user
        else:
            st.error("Invalid credentials. Please try again.")


def get_user_info(email, json_file_path="data.json"):
    try:
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)
            for user in data["users"]:
                if user["email"] == email:
                    return user
        return None
    except Exception as e:
        st.error(f"Error getting user information: {e}")
        return None


def render_dashboard(user_info, json_file_path="data.json"):
    try:
        st.title(f"Welcome to the Dashboard, {user_info['name']}!")
        st.subheader("User Information:")
        st.write(f"Name: {user_info['name']}")
        st.write(f"Sex: {user_info['sex']}")
        st.write(f"Age: {user_info['age']}")
    except Exception as e:
        st.error(f"Error rendering dashboard: {e}")

def get_travel_advisory(City, Type, Days, Purpose=None, Activities=None, Budget=None, Requirements=None):
    try:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        prompt = f"You are a Travel Advisor, help me plan my trip to {City} for {Days} days. I want to go {Type}."
        if Purpose:
            prompt += f" My trip is for {Purpose}."
        if Activities:
            prompt += f" I'm interested in {Activities}."
        if Budget:
            prompt += f" My budget is {Budget}."
        if Requirements:
            prompt += f" I have the following requirements: {Requirements}."
            
        messages = [{"role": "system", "content": prompt}]
        response = client.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo-0125",
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None



def main(json_file_path="data.json"):
    st.sidebar.title("Tourism Recommendation System")
    page = st.sidebar.radio(
        "Go to",
        ("Signup/Login", "Dashboard", "Get Travel Recommendation"),
        key="Travel",
    )

    if page == "Signup/Login":
        st.title("Signup/Login Page")
        login_or_signup = st.radio(
            "Select an option", ("Login", "Signup"), key="login_signup"
        )
        if login_or_signup == "Login":
            login(json_file_path)
        else:
            signup(json_file_path)

    elif page == "Dashboard":
        if session_state.get("logged_in"):
            render_dashboard(session_state["user_info"], json_file_path)
        else:
            st.warning("Please login/signup to view the dashboard.")

    elif page == "Get Travel Recommendation":
        if session_state.get("logged_in"):
            st.title("Travel Recommendation System")
            City = st.text_input("City", "")
            Type = st.selectbox("Type of Trip", ["Business", "Leisure"])
            Days = st.number_input("Number of Days", min_value=1, max_value=365, step=1)
            Purpose = st.text_input("Purpose", "")
            Activities = st.text_input("Activities", "")
            Budget = st.number_input("Budget", min_value=0, step=1)
            Requirements = st.text_area("Requirements", "")

            if st.button("Generate Travel Recommendation"):
                travel_recommendation = get_travel_advisory(City, Type, Days, Purpose, Activities, Budget, Requirements)
                st.write("Travel Recommendation:")
                st.write(travel_recommendation)

        else:
            st.warning("Please login/signup to view the dashboard.")

if __name__ == "__main__":
    initialize_database()
    main()
