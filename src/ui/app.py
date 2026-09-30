import sys
from pathlib import Path

# Add project root to path for Streamlit module imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from src.pipeline.directions import TranslationPipeline
from src.config import TOURISM_CATEGORIES
from src.transliteration.ml_to_mg import manglish_to_malayalam

# Page Configuration per Design.md
st.set_page_config(
    page_title="Malayalam Tourist Translator",
    page_icon="🌴",
    layout="wide"
)

# Custom Color Palette & Styles per Design.md
st.markdown("""
    <style>
    .stApp {
        background-color: #FAFAF7;
        color: #212121;
    }
    .stButton>button {
        background-color: #00695C !important;
        color: white !important;
        border-radius: 4px;
        font-weight: 500;
    }
    .category-chip {
        display: inline-block;
        background-color: #F9A825;
        color: #212121;
        padding: 4px 12px;
        border-radius: 16px;
        font-weight: bold;
        font-size: 0.9em;
        margin-bottom: 12px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌴 Malayalam Tourist Translator")
st.caption("College NLP Mini-Project — Tourism Communication Tool for Kerala")

# Initialize Pipeline
@st.cache_resource
def load_pipeline():
    return TranslationPipeline()

pipeline = load_pipeline()

DIRECTION_MAP = {
    "English → Malayalam": ("D1", "Malayalam"),
    "Malayalam → English": ("D2", "English"),
    "Manglish → English": ("D3", "English"),
    "English → Manglish": ("D4", "Manglish (Romanized Malayalam)"),
}

# Clear Button Callback Handler
def clear_input():
    st.session_state["user_input"] = ""

# Direction Selector
selected_direction_label = st.selectbox(
    "Translation Direction",
    options=list(DIRECTION_MAP.keys()),
    index=0
)

direction_code, target_lang_label = DIRECTION_MAP[selected_direction_label]

# Tourism Category Override Dropdown
col_cat, _ = st.columns([1, 1])
with col_cat:
    manual_category = st.selectbox(
        "Tourism Category (Auto / Override)",
        options=["Auto"] + TOURISM_CATEGORIES,
        index=0
    )

st.divider()

# Layout: Two Columns (Input | Output)
col_input, col_output = st.columns(2)

with col_input:
    st.subheader("INPUT")
    
    # Text area bound to session_state key for editable/clearable behavior
    input_text = st.text_area(
        "Enter sentence:",
        placeholder="e.g., I need a taxi to the airport or എനിക്ക് ഒരു ടാക്സി വേണം.",
        height=180,
        key="user_input"
    )
    
    col_b1, col_b2 = st.columns([1, 1])
    with col_b1:
        translate_button = st.button("Translate", type="primary", use_container_width=True)
    with col_b2:
        st.button("Clear", on_click=clear_input, use_container_width=True)

with col_output:
    st.subheader(f"OUTPUT ({target_lang_label})")
    
    if translate_button:
        if not input_text.strip():
            st.warning("Please enter a sentence.")
            st.text_area("Translation Output", value="", height=180, disabled=True, key="out_empty")
            st.markdown("**Detected Category:** —")
            st.markdown("#### Detected Entities")
            st.info("None detected")
        else:
            with st.spinner("Translating…"):
                result = pipeline.translate(input_text, direction=direction_code)
            
            # Show Transliterated Intermediate Step for D3
            if direction_code == "D3":
                norm_ml = manglish_to_malayalam(input_text)
                with st.expander("Show normalized Malayalam script"):
                    st.write(norm_ml)

            # Translation Output Text Box
            st.text_area(
                label="Translation Output",
                value=result["translated_text"],
                height=180,
                disabled=True,
                key="out_translated"
            )
            
            # Category Chip Display
            active_cat = manual_category if manual_category != "Auto" else result["category"]
            st.markdown(f"**Detected Category:** <span class='category-chip'>{active_cat}</span>", unsafe_allow_html=True)
            
            # Entity List Display
            st.markdown("#### Detected Entities")
            if result["entities"]:
                for entity in result["entities"]:
                    st.markdown(f"- **{entity['label']}**: `{entity['text']}`")
            else:
                st.info("None detected")
    else:
        st.text_area(
            label="Translation Output",
            value="",
            placeholder="Translation will appear here...",
            height=180,
            disabled=True,
            key="out_idle"
        )
        st.markdown("**Detected Category:** —")
        st.markdown("#### Detected Entities")
        st.info("None detected")

st.divider()
st.caption("Offline-capable • Powered by IndicTrans2 & Course NLP Engines")