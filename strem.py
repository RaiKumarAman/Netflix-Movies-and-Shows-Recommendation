import streamlit as st
import pickle
import pandas as pd
import requests
import gzip
import pickle
import os

@st.cache_data(show_spinner="Loading similarity matrix...")
def download_gzip_pickle(url, save_as='similarity.pkl.gz'):
    if not os.path.exists(save_as):
        r = requests.get(url)
        with open(save_as, 'wb') as f:
            f.write(r.content)
    with gzip.open(save_as, 'rb') as f:
        return pickle.load(f)

# ✅ Load similarity from Hugging Face
huggingface_url = "https://huggingface.co/datasets/KungFuBear/netflix-similarity/resolve/main/similarity.pkl.gz"
similarity = download_gzip_pickle(huggingface_url)
# Load pickled data
netflix = pd.DataFrame(pickle.load(open('netflix_rec.pkl', 'rb')))


# OMDb API Key
OMDB_API_KEY = '14312b18'  # Use your personal API key

# Fetch poster using OMDb API
def fetch_poster(title):
    try:
        url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get("Response") == "True":
            poster_url = data.get("Poster", "")
            if poster_url and poster_url != "N/A":
                return poster_url.replace("http://", "https://")  # Use HTTPS for safety

        # Fallback placeholder if no valid poster
        return f"https://via.placeholder.com/300x450.png?text={'+'.join(title.split())}"
    except Exception as e:
        print(f"Poster fetch error for '{title}': {e}")
        return "https://via.placeholder.com/300x450.png?text=Error"

# Recommendation logic
def recommend(input_title):
    index = netflix[netflix["title"] == input_title].index[0]
    distance = similarity[index]
    similar_items = sorted(list(enumerate(distance)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_titles = []
    poster_urls = []

    for i in similar_items:
        title = netflix.iloc[i[0]].title
        poster = fetch_poster(title)
        recommended_titles.append(title)
        poster_urls.append(poster)

    return recommended_titles, poster_urls

# Streamlit App
st.title("🎬 Netflix Recommender System")
option = st.selectbox("Choose a Movie or Show", netflix["title"].values)

if st.button("Recommend"):
    rec_titles, posters = recommend(option)
    cols = st.columns(5)
    ffor i in range(5):
        with cols[i]:
            title = rec_titles[i]
            poster = posters[i]
            netflix_url = f"https://www.netflix.com/search?q={'+'.join(title.split())}"
            st.markdown(
                f"[![{title}]({poster})]({netflix_url})",
                unsafe_allow_html=True
            )
            st.caption(title)
