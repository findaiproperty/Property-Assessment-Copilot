import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import plotly.express as px
from utils.auth import AuthSystem
from utils.ai_helpers import PropertyAIAnalyzer, get_free_apis

# Page configuration
st.set_page_config(
    page_title="Property AI Analyzer",
    page
