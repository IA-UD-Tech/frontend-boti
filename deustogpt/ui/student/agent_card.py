"""
Agent card component for the student dashboard.
"""

import streamlit as st
from typing import Dict, Any, Callable


def display_agent_card(agent: Dict[str, Any], on_chat_clicked: Callable[[str], None]):
    """
    Display an attractive black card for an agent.
    
    Args:
        agent: Agent data to display
        on_chat_clicked: Callback function when chat button is clicked
    """
    # Define header color based on agent ID to ensure consistency
    colors = ["#0068c9", "#83c9ff", "#ff4b4b", "#ffbd45", "#37b8bf"]
    color_index = int(str(agent["id"])[-1]) if isinstance(agent["id"], int) else hash(str(agent["id"]))
    color = colors[color_index % len(colors)]
    
    # Card container with shadow and border
    with st.container():
        # Header with icon, name and colored background
        st.markdown(f"""
        <div style="
            background-color:{color}; 
            padding:10px 15px; 
            border-radius:10px 10px 0 0;
            display:flex;
            align-items:center;
            ">
            <div style="font-size:28px; margin-right:10px;">{agent.get('icon', '🤖')}</div>
            <h3 style="color:white; margin:0">{agent['name']}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Card body with teacher name, description, and last used - now with black background
        st.markdown(f"""
        <div style="
            border:1px solid {color}; 
            border-top:none; 
            padding:15px; 
            border-radius:0 0 10px 10px; 
            margin-bottom:15px;
            background-color:#121212;
            color:white;
            ">
            <p><strong style="color:#e0e0e0;">👨‍🏫 {agent['teacher']}</strong></p>
            <p style="color:#9e9e9e; font-size:0.8rem;">Último uso: {agent['last_used']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Chat button below the card - make it stand out against the dark background
        if st.button("💬 Chatear ahora", key=f"chat_{agent['id']}", 
                    type="primary", use_container_width=True):
            on_chat_clicked(agent["id"])