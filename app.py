import streamlit as st
import pickle
import pandas as pd
import requests


def fetch_poster(movie_id):
    try:
        resp = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=080f3d356eaaa18e7dee61058c56d0c9', timeout=5)
        resp.raise_for_status()
        data = resp.json()
        path = data.get('poster_path')
        if path:
            return "https://image.tmdb.org/t/p/w500/" + path
    except Exception:
        return None
    return None


def recommend(movie, status_placeholder=None):
    if status_placeholder:
        status_placeholder.info(f"Finding recommendations for {movie}...")

    movie_index = movies[movies["title"] == movie].index[0]
    similarities = similarity[movie_index]
    movies_list = sorted(list(enumerate(similarities)), reverse=True, key=lambda x: x[1])[1:6]

    rec_movies = []
    rec_posters = []

    if status_placeholder:
        progress = st.progress(0)

    for idx, item in enumerate(movies_list, start=1):
        movie_id = movies.iloc[item[0]].id
        rec_movies.append(movies.iloc[item[0]].title)
        poster = fetch_poster(movie_id)
        rec_posters.append(poster)

        if status_placeholder:
            status_placeholder.info(f"Fetching posters... ({idx}/{len(movies_list)})")
            progress.progress(int(idx / len(movies_list) * 100))

    if status_placeholder:
        progress.empty()
        status_placeholder.success("Posters fetched")

    return rec_movies, rec_posters


movies = pd.DataFrame(pickle.load(open('movies_dict.pkl', 'rb')))
similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title("Movie Recommender System")
st.write("Welcome to the Movie Recommender System! Please select a movie from the dropdown below to get recommendations.")

selected_movie = st.selectbox("Select a movie", options=movies['title'].values)

PLACEHOLDER_POSTER = "https://via.placeholder.com/300x450?text=No+Image"

if st.button("Get Recommendations"):
    status_placeholder = st.empty()
    with st.spinner("Finding recommendations..."):
        recommended_movies, recommended_movies_posters = recommend(selected_movie, status_placeholder=status_placeholder)
    status_placeholder.success("Here are some movies you might like")

    cols = st.columns(5)
    for i in range(len(recommended_movies)):
        poster_url = recommended_movies_posters[i] or PLACEHOLDER_POSTER
        cols[i].image(poster_url)
        cols[i].write(recommended_movies[i])

