from dotenv import load_dotenv
load_dotenv()

import requests
from premai import Prem
import streamlit as st
import time
import os

# Instead of hardcoding the keys
prem_api_key = os.getenv('PREM_API_KEY')
api_key = os.getenv('GODADDY_API_KEY')
api_secret = os.getenv('GODADDY_API_SECRET')


models = ["gpt-3.5-turbo", "gpt-4", "claude-3-opus-20240229"]

client = Prem(
    api_key=prem_api_key
)

tlds = ['.com', '.net', '.io', '.tech', '.dev', '.me']

headers = {
    'Authorization': f'sso-key {api_key}:{api_secret}',
}

def check_domain_availability(base_domain):
    available_domains = []
    for tld in tlds:
        domain = f'{base_domain}{tld}'
        url = f'https://api.godaddy.com/v1/domains/available?domain={domain}&checkType=FULL'
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data['available']:
                    available_domains.append(domain)
        except Exception as e:
            st.error(f"An error occurred while checking {domain}: {str(e)}")
    return available_domains


def generate_brand_names(topic, model):
    prompt = f"I want to find a good brand name for a company related to {topic}. I need a list of brand names words that are inspired by or related to {topic}. Generate a list of keywords composed by only one word. Prepare the list with names divided only by a comma, only write the words in a list, don't write any introduction."
    messages = [{"role": "user", "content": prompt}]

    system_prompt = "You are a helpful assistant." # Optional
    session_id = "my-session" # Optional: a unique identifier to maintain session context
    project_id = 391 # Ensure this matches your OpenAI project ID
    
    response = client.chat.completions.create(
        project_id=project_id,
        messages=messages,
        model=model,
        session_id=session_id,
        system_prompt=system_prompt,
        stream=False
    )
    
    brand_names_text = response.choices[0].message.content.strip()
    brand_names = [name.lower().replace('.', '') for name in brand_names_text.split(', ')]
    
    return brand_names

def output(brand_names):          
    total_brands = len(brand_names)
    if total_brands > 0:
        progress_increment = 1.0 / total_brands
    else:
        progress_increment = 0
    current_progress = 0

    progress_bar = st.progress(current_progress)
    
    with st.spinner('Checking domain availability...'):
        for i, base_domain in enumerate(brand_names, start=1):
            available_domains = check_domain_availability(base_domain)
            if available_domains:
                domain_links_html = ""
                for domain in available_domains:
                    godaddy_url = f"https://www.godaddy.com/domainsearch/find?checkAvail=1&domainToCheck={domain}"
                    domain_links_html += f"<a href='{godaddy_url}' target='_blank' style='color: #1a73e8; margin-right: 10px;'>{domain}</a>"
                
                st.markdown(f"""<div style='background-color: #d4edda; padding: 10px; border-radius: 8px; margin-bottom: 20px;'>
                                <p style='color: #155724; margin: 0;'>{base_domain} available domains: {domain_links_html}</p>
                                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div style='background-color: #f8d7da; padding: 10px; border-radius: 8px; margin-bottom: 20px;'>
                                <p style='color: #721c24; margin: 0;'>No available domains found for {base_domain}</p>
                                </div>""", unsafe_allow_html=True)
            
            # Update the progress bar
            current_progress += progress_increment
            progress_bar.progress(min(int(current_progress * 100), 100))

    


st.title('BrandName Domain')

st.markdown("""
**Author:** [Filippo Caliò](https://www.linkedin.com/in/filippo-calio/)

""", unsafe_allow_html=True)


st.markdown("""
BrandName Domain is a streamlined web app for brand name generation and domain availability checking. Ideal for entrepreneurs, marketers, and creatives looking to secure a digital brand identity. Key features:

- **Brand Name Generation**: Leverages the [Prem API](https://www.premai.io) to generate unique brand names based on user-defined topics.
- **Custom Brand Names**: Users can input and check their own list of brand names.
- **Domain Availability**: Checks real-time domain availability via GoDaddy API for both generated and custom brand names, with direct links for easy registration.
- **User-Friendly Interface**: Designed for quick and intuitive use.

""", unsafe_allow_html=True)

st.markdown("""
---
#### **Let's Get Started!**

Choose one of the options below to begin exploring brand names and checking domain availability.
""", unsafe_allow_html=True)

st.write('Supported Domains:')
st.write(', '.join(tlds))
option = st.radio("Choose your option:", (f'Generate brand names using Generative AI', 'Insert a list of brand names'))


if option == f'Generate brand names using Generative AI':
    selected_model = st.selectbox('Choose a model for brand name generation:', models)
    topic = st.text_input('Enter the topic for brand name generation:', '')

    if st.button('Generate Brand Names'):
        with st.spinner('Generating brand names...'):
            # Initialize progress bar
            progress_bar = st.progress(0)
            for percent_complete in range(100):
                time.sleep(0.01)  # Simulate processing time
                progress_bar.progress(percent_complete + 1)
            brand_names = generate_brand_names(topic, selected_model)
            progress_bar.empty()  # Clear progress bar after completion

        if brand_names:
            st.write('Generated brand names:')
            st.write(', '.join(brand_names))
            output(brand_names)
            if st.button('Start Over'):
                st.rerun()

else:
    brand_names_str = st.text_area("Enter a comma-separated list of brand names:")
    brand_names = [name.strip().lower() for name in brand_names_str.split(',')] if brand_names_str else []
    if st.button('Confirm'):
        if brand_names:
            st.write('Brand names to check:')
            st.write(', '.join(brand_names))
            output(brand_names)
            if st.button('Start Over'):
                    st.rerun()
    
        


