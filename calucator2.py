# streamlit_calculator.py

import streamlit as st

# Set page title
st.set_page_config(page_title="Simple Calculator")

st.title("🧮 Simple Calculator")

# Initialize session state for expression
if "expression" not in st.session_state:
    st.session_state.expression = ""

# Display current expression
st.text_input("Display", st.session_state.expression, key="display", disabled=True)

# Button click handler
def on_button_click(value):
    st.session_state.expression += str(value)

def on_clear():
    st.session_state.expression = ""

def on_equal():
    try:
        result = str(eval(st.session_state.expression))
        st.session_state.expression = result
    except Exception:
        st.session_state.expression = "Error"

# Layout: Buttons in a grid
button_rows = [
    ["C", "/",],
    ["7", "8", "9", "*"],
    ["4", "5", "6", "-"],
    ["1", "2", "3", "+"],
    ["0", ".", "="]
]

# Render buttons
for row in button_rows:
    cols = st.columns(len(row))
    for i, label in enumerate(row):
        with cols[i]:
            if st.button(label, use_container_width=True):
                if label == "C":
                    on_clear()
                elif label == "=":
                    on_equal()
                else:
                    on_button_click(label)
