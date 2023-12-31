import streamlit as st
from streamlit_lottie import st_lottie
import pandas as pd
from datetime import date
import json
import pandas as pd
import hume
from apps.home import load_lottiefile
import nltk
from nltk.corpus import wordnet
from nltk.corpus import sentiwordnet as swn
nltk.download('wordnet')
nltk.download('sentiwordnet')

def add_habit(new_habit):
    global habit_list
    habit_list.append(new_habit)

habit_list = []

def app():
    col1, col2 = st.columns(2)

    #--------------song generation----------------
    with col1:
        st.title("let's pick a song for you!")

        def calculate_correlation(word1, word2):
            synsets1 = wordnet.synsets(word1)
            synsets2 = wordnet.synsets(word2)

            # Calculate the correlation score
            correlation = 0
            for synset1 in synsets1:
                for synset2 in synsets2:
                    correlation += swn.senti_synset(synset1.name()).pos_score() * swn.senti_synset(synset2.name()).pos_score()
                    correlation += swn.senti_synset(synset1.name()).neg_score() * swn.senti_synset(synset2.name()).neg_score()

            return correlation

        def load_data():
            songs = pd.read_csv("data/spotify.csv")
            return songs

        my_word = st.text_input('describe how you are feeling in one word:')
        list_of_features = ["danceability", "energy", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo"]
        #list_of_features = ["energy", "loudness", "liveness", "valence", "tempo"]
        songs = load_data()
        columns = songs.columns

        if my_word: 
            correlation_scores = []
            for feature in list_of_features:
                if feature in columns:
                    correlation_scores.append(calculate_correlation(my_word, feature))
                else:
                    correlation_scores.append(None)

            # Display the correlation scores
            feature_score = {}
            for i, feature in enumerate(list_of_features):
                feature_score[feature] = correlation_scores[i]
                # if correlation_scores[i] is not None:
                #     st.write(f"Correlation between '{my_word}' and '{feature}': {correlation_scores[i]}")
                # else:
                #     st.write(f"'{feature}' not found in the DataFrame.")
            sorted_dict = dict(sorted(feature_score.items(), key=lambda x: x[1], reverse=True))
            top_3_features = ['uri'] + list(sorted_dict.keys())[:3]
            st.markdown("#### your top 3 features that influenced this song choice: ")
            st.markdown("#### " + str(top_3_features[1:4]))
            
            #finding the song 
            new_df = songs[top_3_features]
            new_df['sum'] = new_df.iloc[:, -3:].mean(axis=1)
            sorted_df = new_df.sort_values(by='sum', ascending=False)
            uri = sorted_df.iloc[0, new_df.columns.get_loc('uri')]

            st.header("a song for you based on your mood!")
            spotify_uri_t = uri.split(":")[-1]+'?'
            #spotify_uri_t = '1Ukxccao1BlWrPhYkcXbwZ?'
            #st.write(spotify_uri_t)
            st.write(f'<iframe src="https://open.spotify.com/embed/track/{spotify_uri_t}utm_source=generator" width="500" height="250" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>', unsafe_allow_html=True)

    #--------------animation----------------
    lottie_home = load_lottiefile("data/home-2.json")

    with col2:
        st_lottie(
            lottie_home,
            speed=0.5,
            reverse=False,
            loop=True,
            quality="medium",
            height=None,
            width=None,
            key="lottie_home"
        )

    #--------------habit tracker----------------
    habits_data = pd.read_csv("data/habits-data.csv")

    def habit_tracker():
        st.header("today's habit tracker")
        c1, c2, c3, c4 = st.columns(4)

        new_habit = st.text_input("add a habit! (e.g. sleep 8+ hours, eat 3 meals, walk 10k steps)", key="new_habit")
        
        b1, b2, b3 = st.columns([1, 2, 3])
        with b1:
            add_button = st.button("add", on_click=add_habit, args=(new_habit,))
        
        def add_to_log():
            new_habits = []
            for habit in habit_list:
                if habit not in list(habits_data)[1:]:
                        new_habits.append(habit)
            
            today = [str(date.today())]
            for old_habit in list(habits_data)[1:]:
                if old_habit in habit_list:
                    today.append(True)
                else:
                    today.append(False)
            new_habits_data = pd.concat([habits_data, pd.DataFrame([today], columns=list(habits_data))])
            
            for new_habit in new_habits:
                new_habits_data[new_habit] = [False] * len(habits_data) + [True]
            new_habits_data.to_csv("data/habits-data.csv", index=False)
        with b2:
            st.button("add habits to log", on_click=add_to_log)

        if add_button:
            pass

        counter = 1
        col = 0
        for habit in habit_list:
            if col == 0:
                curr = c1
            if col == 1:
                curr = c2
            elif col == 2:
                curr = c3
            if col == 3:
                curr = c4

            with curr:
                st.checkbox(habit, key = f"box{counter}")
            col = (col + 1) % 4
            counter += 1
    habit_tracker()

#--------------journaling----------------
    st.header("write all your thoughts here:")

    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.write(" ")
        st.write(" ")
        st.write(" ")
        st.write(" ")
        type = st.radio("how would you like to document today's journal entry?",
                        ('text box','image'))
    
    with col1:
        st.write(f"date: {date.today()}")
        if type == 'text box':
            entry = st.text_area("today's journal entry", height=300)
            full = {
                "date": str(date.today()),
                "entry": entry
            }
            with open("data/sample.json", "w") as outfile:
                json.dump(full, outfile)

        elif type == 'image':
            st.header("today's entry")

            # doesn't really work yet
            uploaded_file = st.file_uploader("Upload an Image Here!")

            if uploaded_file != None:
                ##st.image(uploaded_file)
                col1, col2 = st.columns([1, 3])
                client = hume.HumeBatchClient("Insert Your API Key")
                urls = ["https://media.istockphoto.com/id/1200561508/photo/tired-young-woman-fall-asleep-working-at-laptop.jpg?s=1024x1024&w=is&k=20&c=GwdF1IdZb93rrBb6cU8g2Jlm-uaXCDmFbFywg0-cwCo="]
                config = hume.models.config.FaceConfig()
                job = client.submit_job(urls, [config])
                details = job.await_complete()
                predictions = job.get_predictions()
                predictions1 = predictions[0]['results']['predictions'][0]['models']['face']['grouped_predictions'][0]['predictions'][0]['emotions']
                ##st.write(predictions[0]['results']['predictions'][0]['models']['face']['grouped_predictions'][0]['predictions'][0]['emotions'])
                df = pd.DataFrame.from_records(predictions1)
                undated = df.set_index('name').T
                undated.to_csv('data/emotions_image.csv', mode='a', index=False, header=False)

                df = df.sort_values(by='score', ascending=False).set_index('name')
                edited_df = col1.dataframe(df.head(9)) 
                col2.write("today's analytics")
                col2.bar_chart(df.head(5))

#--------------journal chart----------------

    st.header("your journaling analytics")
    st.area_chart(pd.read_csv("data/emotions_log.csv"))