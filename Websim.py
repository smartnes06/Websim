import requests
from bs4 import BeautifulSoup
import openai
import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

def scrape_website(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return f"Error: Unable to fetch {url}"

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract key elements
        title = soup.title.string if soup.title else "No Title"
        headings = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])]
        links = [a['href'] for a in soup.find_all('a', href=True)]
        buttons = [btn.get_text(strip=True) for btn in soup.find_all('button')]

        return {
            "title": title,
            "headings": headings,
            "links": links,
            "buttons": buttons
        }
    except Exception as e:
        return str(e)


def simulate_user_interaction(website_data, persona):
    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = f"""
    You are an AI simulating a {persona} interacting with a website.

    Website Title: {website_data['title']}
    Headings: {', '.join(website_data['headings'])}
    Links: {', '.join(website_data['links'])}
    Buttons: {', '.join(website_data['buttons'])}

    Describe the user's journey, what they click on, where they might struggle, and suggest improvements.
    Format your response as follows:

    **User Behavior:**
    - (Describe what they do step by step)

    **Pain Points:**
    - (List where they get confused or frustrated)

    **Actionable Recommendations:**
    - (Provide clear improvements for the website)
    """

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a UX and marketing expert providing structured website analysis."},
            {"role": "user", "content": prompt}
        ]
    )

    return completion.choices[0].message.content


st.title("Website AI Simulator")
st.write("Analyze how different personas interact with your website")

url_input = st.text_input("Enter Website URL:")
persona_selection = st.selectbox("Select a Persona:", ["Gen Z Shopper", "Busy Professional", "Bargain Hunter"])

if st.button("Run Analysis"):
    if url_input:
        st.write("Scraping website...")
        website_data = scrape_website(url_input)
        st.write("Simulating user behavior...")
        interaction_results = simulate_user_interaction(website_data, persona_selection)
        st.subheader("AI-Generated Insights")
        st.write(interaction_results)
    else:
        st.error("Please enter a valid website URL.")
