import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from time import sleep
import random

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload




### App Set Up ###

st.set_page_config(layout="wide")
st.title('Codenames Dataset')
st.subheader('Instructions')
st.write("""
Read the list of words below. Can you think for a clue that links to them together and meets the following criteria?
- It must be a single word
- The clue cannot be one of the actual words
- The clue cannot be only rhyming

For example, a good clue for the words: Football, London and Stadium would be Arsenal. For Poison, Bow and Fire, a good clue would be Arrow.""")
st.write("")
st.write("""
Use the form below to select how many words you are linking together. More words is more difficult, but if you think you have a good clue, go for it!
Once you've selected your words, a box will appear for you to enter the clue. Make sure you press the 'submit your clue' button when you are happy.
""")
st.subheader('Your Words')

### Load words ###


if "random_number" not in st.session_state:
    st.session_state["random_number"] = random.randint(0,99999)
if "words" not in st.session_state:
    words = pd.read_csv(Path(__file__).parents[0] / 'word_list.csv').sample(n=5, random_state=st.session_state.random_number).values
    st.session_state["words"] = [i[0] for i in words]

def change_number():
    st.session_state["random_number"] = random.randint(0,99999)
    words = pd.read_csv(Path(__file__).parents[0] / 'word_list.csv').sample(n=5, random_state=st.session_state.random_number).values
    st.session_state["words"] = [i[0] for i in words]
    return


col1,col2,col3,col4,col5 = st.columns(5)
st.write(st.session_state.random_number)
col1.write(st.session_state.words[0])
col2.write(st.session_state.words[1])
col3.write(st.session_state.words[2])
col4.write(st.session_state.words[3])
col5.write(st.session_state.words[4])

### Skip Button ###
st.write("")
st.button("Skip words?", on_click=change_number)
st.write("")

### Select words ###
with st.form("my_form", clear_on_submit=False):
    st.write("Select your words")

    word1 = st.checkbox(label = st.session_state.words[0])
    #word2 = st.checkbox(label = words[1])
    #word3 = st.checkbox(label = words[2])
    #word4 = st.checkbox(label = words[3])
    #word5 = st.checkbox(label = words[4])

    clue = st.text_input(label='Enter your single word clue:', value="")
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.write(word1)
        time.sleep(5)
        change_number()

a = st.button('press to continue')
if a:
    selections = [word1,word2,word3,word4,word5]

    st.write(selections)

    selected_words = ';'.join(
        [k for k,v in zip(words, selections) if v ==True])
    unselected_words = ';'.join(
        [k for k,v in zip(words, selections) if v ==False])
    st.write(selections)
    st.write("selected", selected_words, "unselected", unselected_words, "clue",clue)
    datetimenow = datetime.now().strftime("%Y%m%d%H%M%S")
    results = {
        'selected_words':selected_words,
        'unselected_words': unselected_words,
        'clue':clue}
    results = json.dumps(results)
    file_name = 'data_{}.json'.format(datetimenow)
    file_from = Path(__file__).parents[0] / file_name
    with open(file_from, 'w') as f:
        json.dump(results, f)

    #try:
    creds = Credentials(token=st.secrets['token'],
                        refresh_token = st.secrets['refresh_token'],
                        token_uri = st.secrets['token_uri'],
                        client_id=st.secrets['client_id'],
                        client_secret=st.secrets['client_secret'],
                        scopes=st.secrets['scopes'],
                        expiry=datetime.strptime(st.secrets['expiry'], "%Y-%m-%dT%H:%M:%S"))


    service = build('drive', 'v3', credentials=creds)
    file_metadata = {'name': file_name,
                     'parents': ['150dCgltvQa5gKum45F-fPlhKZ_tG0347']}
    media = MediaFileUpload(file_from)
    file = service.files().create(body=file_metadata,
                                  media_body=media,
                                  fields='id').execute()




