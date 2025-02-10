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
            return f"Feil: Kunne ikke hente {url}"

        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string if soup.title else "Ingen tittel"
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
    Du er en AI som simulerer hvordan en {persona} bruker vil samhandle med nettstedet.
    
    Nettstedstittel: {website_data['title']}
    Overskrifter: {', '.join(website_data['headings'])}
    Lenker: {', '.join(website_data['links'])}
    Knapper: {', '.join(website_data['buttons'])}
    
    Simuler hvordan en typisk {persona} bruker ville navigere nettstedet:
    - Hva de klikker på først.
    - Hvor de kan bli forvirret eller miste interesse.
    - Hvilke områder som fanger mest oppmerksomhet.
    - Hva kan forbedres for å øke konverteringer.
    
    Gi anbefalinger for å forbedre brukeropplevelsen.
    Svar på norsk.
    """

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Du er en UX- og markedsføringsekspert som gir strukturerte analyser av nettsteder."},
            {"role": "user", "content": prompt}
        ]
    )

    return completion.choices[0].message.content

st.title("AI Nettstedssimulator")
st.write("Analyser hvordan forskjellige brukere samhandler med nettstedet ditt")

url_input = st.text_input("Skriv inn nettstedets URL:")
persona_selection = st.selectbox("Velg en brukerprofil:", ["Gen Z Shopper", "Travle Profesjonelle", "Tilbudsjeger"])

if st.button("Analyser nettstedet"):
    if url_input:
        st.write("Henter nettstedets data...")
        website_data = scrape_website(url_input)
        st.write("Simulerer brukeropplevelse...")
        interaction_results = simulate_user_interaction(website_data, persona_selection)
        st.subheader("AI-genererte innsikter")
        st.write(interaction_results)
    else:
        st.error("Vennligst skriv inn en gyldig URL.")
