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
    Du er en KI som simulerer {persona} brukere samhandling med et nettsted. 
    
    Nettstedstittel: {website_data['title']}
    Overskrifter: {', '.join(website_data['headings'])}
    Lenker: {', '.join(website_data['links'])}
    Knapper: {', '.join(website_data['buttons'])}
    
    Simuler 100 brukere som samhandler med nettsiden.  
    Tildeldiggjør atferd: noen scroller, andre klikker knapper, noen forlater tidlig.  
    Gi en oppsummering av **mønstre** (hvilke områder som får mest oppmerksomhet).  
    Gi annbefalinger for forbedring av konverteringer basert på resultatene.
    Svar på norsk.

Svar på en strukturert format:
**Bruker Opplevelse Innsikt:**
- [Mest klikker elementer]
- [Mest ignorerte områder]
- [Vanligste forvirrelse områder]

**Konvertering Optimalisering Forslag:**
- [Spesifikke nettside forbedringer]
"""


    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Du er en UX og markedsførings ekspert som gir strukturerte nettside analyser."},
            {"role": "user", "content": prompt}
        ]
    )

    return completion.choices[0].message.content


st.title("AI Nettstedsanalytiker")
st.write("Analyser hvordan forskjellige brukere samhandler med nettsiden din")

url_input = st.text_input("Skriv inn nettstedets URL:")
persona_selection = st.selectbox("Velg en brukerprofil:", ["Gen Z Shopper", "Travle Profesjonelle", "Tilbudsjeger"])

if st.button("Analyser nettstedet"):
    if url_input:
        st.write("Henter nettstedets data...")
        website_data = scrape_website(url_input)
        st.write("Simulerer brukeropplevelse...")
        interaction_results = simulate_user_interaction(website_data, persona_selection)
        st.subheader("KI-genererte innsikter")
        st.write(interaction_results)
        
        click_data = np.random.randint(0, 100, (100, 2))
        x = click_data[:, 0]
        y = click_data[:, 1]

        fig, ax = plt.subplots(figsize=(8, 6))
        sns.kdeplot(x, y, cmap="coolwarm", shade=True, bw_adjust=0.5, ax=ax)
        ax.set_title("Brukerinteraksjon Heatmap")
        ax.set_xlabel("Sidebredde")
        ax.set_ylabel("Sidehøyde")

        st.pyplot(fig)
    else:
        st.error("Vennligst skriv inn en gyldig URL.")
