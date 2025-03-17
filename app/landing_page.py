#
# landing_page.py
# IA-UD-Tech
#
# Created by Diego Revilla on 02/02/2024
# Copyright © 2024 Deusto Institute of Technology. All rights reserved.
#

import streamlit as st

st.set_page_config(
    page_title="Coming Soon",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

with open('front_end/static/metalic_apple.html', 'r') as file:
    metallic_apple_css = file.read()

st.markdown(metallic_apple_css, unsafe_allow_html=True)

with open('front_end/static/logo.html', 'r') as file:
    logo = file.read()

st.markdown(logo, unsafe_allow_html=True)


with open('front_end/static/hide_menu.html', 'r') as file:
    hide_menu = file.read()
st.markdown(hide_menu, unsafe_allow_html=True)