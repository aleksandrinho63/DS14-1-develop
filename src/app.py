import os

import streamlit as st
from dotenv import load_dotenv
from typing import List, Set, Optional, Any
from api.omdb import OMDBApi
from recsys import ContentBaseRecSys

TOP_K = 5
load_dotenv()

# переменные для окружения
API_KEY = os.getenv("API_KEY") # comment delete
MOVIES = os.getenv("MOVIES")
DISTANCE = os.getenv("DISTANCE")

omdbapi = OMDBApi(API_KEY) # comment delete


recsys = ContentBaseRecSys(
    movies_dataset_filepath=MOVIES,
    distance_filepath=DISTANCE,
)

st.markdown(
    "<h1 style='text-align: center; color: white;'>Портал рекомендаций фильмов</h1>",
    unsafe_allow_html=True
)

selected_movie = st.selectbox(
    "Напиши или выбери фильм который тебе нравится:",
    recsys.get_title()
)

selected_genre = st.multiselect("Фильтровать по жанру", list(recsys.get_genres()))
selected_director = st.text_input('Фильтровать по режиссёру')

if st.button('ПОЕХАЛИ!', key='Show Recommendation', help='Нажми чтобы начать поиск рекомендаций', on_click=None, args=None, kwargs=None):
    st.write("Рекомендуемые фильмы:")
    
    recommended_movie_names = recsys.recommendation(selected_movie, top_k=TOP_K, genres=selected_genre, director=selected_director)
    recommended_movie_posters = omdbapi.get_posters(recommended_movie_names)
    if recommended_movie_names:
        columns = st.columns(TOP_K)
        for index in range(min(len(recommended_movie_names), TOP_K)):
            with columns[index]:
                st.subheader(recommended_movie_names[index])
                st.image(recommended_movie_posters[index]) # comment delete
    else:
        st.write("С такими настройками нет рекомендаций")

