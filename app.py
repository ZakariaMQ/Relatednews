import streamlit as st
from news import News


def home_page():
    st.set_page_config(page_title="interesting News")
    st.markdown(
            """
            <style>
            #MainMenu {
                visibility: hidden;
            }
            footer {
                visibility: hidden;
            }
            </style>
            """,
            unsafe_allow_html=True
                    )
    news = News()
    st.components.v1.html(news.get_news(), height=1000, scrolling=True)

if __name__ == "__main__":
    home_page()