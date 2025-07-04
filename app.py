import streamlit as st
import pandas as pd

# Load data
@st.cache_data
def load_data():
    anime = pd.read_csv('anime.csv')
    rating = pd.read_csv('rating.csv')
    anime = anime.dropna(subset=['genre'])  # remove rows with missing genre
    anime['episodes'] = pd.to_numeric(anime['episodes'], errors='coerce')  # convert episodes to numeric
    return anime, rating


anime_df, rating_df = load_data()

# Clean data
def clean_text(text):
    text = str(text).lower().strip()
    return text

anime_df['genre'] = anime_df['genre'].apply(clean_text)
anime_df['type'] = anime_df['type'].apply(clean_text)
anime_df['rating'] = anime_df['rating'].fillna(0)

# Genre options from dataset
all_genres = sorted({g.strip() for genres in anime_df['genre'].dropna() for g in genres.split(',')})
all_types = anime_df['type'].dropna().unique()

# Streamlit App UI
st.title("🎌 Anime Preference Quiz — Recommendation System")

st.subheader("Answer a few questions to get personalized anime suggestions!")

selected_genres = st.multiselect("Which anime genres do you enjoy?", all_genres)
selected_type = st.selectbox("What type of anime do you prefer?", list(all_types))
min_rating = st.slider("Minimum acceptable community rating (out of 10)", 0.0, 10.0, 7.0)
max_episodes = st.slider("Preferred maximum number of episodes", 1, 1000, 50)

if st.button("🎯 Get Recommendations"):
    st.write("🔍 Finding anime based on your preferences...")

    # Filter by user preferences
    def matches_preferences(row):
        genre_match = any(g.strip() in row['genre'] for g in selected_genres)
        type_match = row['type'] == selected_type
        rating_match = row['rating'] >= min_rating
        episode_match = row['episodes'] <= max_episodes if pd.notna(row['episodes']) else True
        return genre_match and type_match and rating_match and episode_match


    filtered_anime = anime_df[anime_df.apply(matches_preferences, axis=1)]

    if not filtered_anime.empty:
        top_recommendations = filtered_anime[['name', 'genre', 'type', 'episodes', 'rating']].sort_values(
            by='rating', ascending=False).head(10)

        st.success(f"Found {len(filtered_anime)} matching anime! Showing top {len(top_recommendations)}:")
        st.dataframe(top_recommendations.reset_index(drop=True))

    else:
        st.warning("No anime matched all your preferences. Try relaxing a filter or two.")
