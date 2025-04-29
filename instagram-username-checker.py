import streamlit as st
import requests
import random
import string
import time
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
from io import BytesIO
import json
import base64

class InstagramChecker:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'X-IG-App-ID': '936619743392459',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://www.instagram.com',
            'DNT': '1',
            'Connection': 'keep-alive',
        }

    def get_profile_pic(self, url):
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return BytesIO(response.content)
            return None
        except:
            return None

    def check_username(self, username):
        try:
            url = f'https://www.instagram.com/api/v1/users/web_profile_info/?username={username}'
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                user = data['data']['user']
                
                # Get profile picture
                profile_pic = None
                if user['profile_pic_url']:
                    profile_pic = self.get_profile_pic(user['profile_pic_url'])
                
                return {
                    'available': False,
                    'profile': {
                        'username': user['username'],
                        'full_name': user['full_name'],
                        'followers': user['edge_followed_by']['count'],
                        'following': user['edge_follow']['count'],
                        'posts': user['edge_owner_to_timeline_media']['count'],
                        'bio': user.get('biography', ''),
                        'is_private': user['is_private'],
                        'is_verified': user.get('is_verified', False),
                        'profile_pic': profile_pic,
                        'external_url': user.get('external_url', '')
                    }
                }
            elif response.status_code == 404:
                return {'available': True, 'profile': None}
            else:
                return {'available': None, 'profile': None}
        except Exception as e:
            st.error(f"Error checking username: {str(e)}")
            return {'available': None, 'profile': None}

    def generate_username(self, length=None, prefix='', suffix=''):
        if not length:
            length = random.randint(4, 15)
        
        chars = string.ascii_lowercase + string.digits + '_'
        username = prefix
        
        remaining_length = length - len(prefix) - len(suffix)
        if remaining_length > 0:
            username += ''.join(random.choice(chars) for _ in range(remaining_length))
        
        username += suffix
        return username

def main():
    st.set_page_config(
        page_title="Instagram Username Checker",
        page_icon="📸",
        layout="wide"
    )

    # Custom CSS
    st.markdown("""
        <style>
        .stApp {
            background-color: #0b211e;
        }
        .main {
            padding: 2rem;
        }
        .profile-card {
            background-color: black;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            margin: 1rem 0;
        }
        .stat-box {
            text-align: center;
            padding: 1rem;
            background: #1d211d;
            border-radius: 8px;
            margin: 0.5rem 0;
        }
        .username-box {
            background: #1d211d;
            padding: 0.5rem;
            border-radius: 4px;
            margin: 0.25rem 0;
        }
        .verified-badge {
            color: #3897f0;
            font-size: 1.2rem;
        }
        </style>
    """, unsafe_allow_html=False)

    st.title("📸 Instagram Username Checker")
    st.markdown("---")

    if 'checker' not in st.session_state:
        st.session_state.checker = InstagramChecker()

    tabs = st.tabs(["Username Checker", "Username Generator"])

    # Username Checker Tab
    with tabs[0]:
        st.header("Check Username Availability")
        username = st.text_input("Enter Instagram Username", placeholder="username")
        
        if st.button("🔍 Check Username", use_container_width=True):
            if username:
                with st.spinner("Checking username..."):
                    result = st.session_state.checker.check_username(username)
                    
                    if result['available'] is True:
                        st.success(f"Username '@{username}' is available! 🎉")
                    elif result['available'] is False:
                        st.error(f"Username '@{username}' is taken! ❌")
                        
                        profile = result['profile']
                        st.markdown('<div class="profile-card">', unsafe_allow_html=True)
                        
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            if profile['profile_pic']:
                                st.image(profile['profile_pic'], width=200)
                            else:
                                st.image("https://www.instagram.com/static/images/anonymousUser.jpg", width=200)
                        
                        with col2:
                            st.markdown(f"### @{profile['username']} {' ✓' if profile['is_verified'] else ''}")
                            st.markdown(f"**{profile['full_name']}**")
                            
                            # Stats in columns
                            stats_cols = st.columns(3)
                            with stats_cols[0]:
                                st.markdown(f"**{profile['posts']:,}** posts")
                            with stats_cols[1]:
                                st.markdown(f"**{profile['followers']:,}** followers")
                            with stats_cols[2]:
                                st.markdown(f"**{profile['following']:,}** following")
                            
                            st.markdown("---")
                            if profile['bio']:
                                st.markdown(f"**Bio:**\n{profile['bio']}")
                            if profile['external_url']:
                                st.markdown(f"**Website:** {profile['external_url']}")
                            st.markdown(f"**Account Status:** {'🔒 Private' if profile['is_private'] else '🔓 Public'}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.warning("Could not check username availability. Please try again later.")
            else:
                st.warning("Please enter a username")

    # Username Generator Tab
    with tabs[1]:
        st.header("Username Generator")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            prefix = st.text_input("Prefix (optional)", "")
        with col2:
            suffix = st.text_input("Suffix (optional)", "")
        with col3:
            length = st.number_input("Username Length", min_value=4, max_value=30, value=8)
        
        amount = st.slider("Number of usernames to generate", min_value=1, max_value=100, value=10)
        
        if st.button("🎲 Generate Usernames", use_container_width=True):
            st.markdown("### Generated Usernames")
            
            usernames = []
            with st.spinner("Generating usernames..."):
                for _ in range(amount):
                    username = st.session_state.checker.generate_username(length, prefix, suffix)
                    usernames.append(username)
            
                # Display usernames in a grid
                cols = st.columns(5)
                for idx, username in enumerate(usernames):
                    with cols[idx % 5]:
                        st.markdown(f'<div class="username-box">@{username}</div>', unsafe_allow_html=True)
            
            if st.button("✨ Check Availability for Generated Usernames"):
                results = []
                progress = st.progress(0)
                
                for idx, username in enumerate(usernames):
                    result = st.session_state.checker.check_username(username)
                    results.append({
                        'Username': f'@{username}',
                        'Status': '✅ Available' if result['available'] is True else '❌ Taken' if result['available'] is False else '⚠️ Unknown'
                    })
                    progress.progress((idx + 1) / len(usernames))
                    time.sleep(1)  # Avoid rate limiting
                
                st.markdown("### Availability Results")
                df = pd.DataFrame(results)
                st.dataframe(
                    df,
                    hide_index=True,
                    column_config={
                        "Username": st.column_config.TextColumn("Username", width="medium"),
                        "Status": st.column_config.TextColumn("Status", width="medium")
                    }
                )

if __name__ == "__main__":
    main()

