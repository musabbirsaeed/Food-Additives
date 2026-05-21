import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(page_title="Food Nutrition Analyzer", page_icon="🍎", layout="wide")
st.title("🍎 Food Nutrition Analyzer")
st.caption("Enter a food name to get calories, macro/micro nutrients, fiber, and plots.")

backend_url = st.sidebar.text_input("Backend URL", value="http://localhost:8000")
food_query = st.text_input("Food name", value="banana")
search_btn = st.button("Analyze")


@st.cache_data(ttl=3600)
def fetch_data(base_url: str, food: str):
    response = requests.get(
        f"{base_url}/nutrition", params={"food": food, "page_size": 5}, timeout=25
    )
    if response.status_code != 200:
        return None, f"{response.status_code}: {response.text}"
    return response.json(), None


if search_btn and food_query.strip():
    with st.spinner("Fetching nutrition data..."):
        payload, err = fetch_data(backend_url.strip(), food_query.strip())

    if err:
        st.error(f"Error from backend: {err}")
        st.stop()

    results = payload.get("results", [])
    if not results:
        st.warning("No results found.")
        st.stop()

    labels = [f"{i + 1}. {item.get('food', 'Unknown')}" for i, item in enumerate(results)]
    selected_label = st.selectbox("Select a food match", labels)
    selected_index = labels.index(selected_label)
    selected = results[selected_index]

    st.subheader(selected.get("food", "Unknown food"))
    st.write(f"**FDC ID:** {selected.get('fdc_id')}")
    if selected.get("brand"):
        st.write(f"**Brand:** {selected.get('brand')}")
    if selected.get("serving_size"):
        st.write(
            f"**Serving Size:** {selected.get('serving_size')} {selected.get('serving_size_unit', '')}"
        )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Calories (kcal)", f"{selected.get('calories_kcal', 0):.1f}")
    c2.metric("Protein (g)", f"{selected['macros_g'].get('protein', 0):.1f}")
    c3.metric("Carbs (g)", f"{selected['macros_g'].get('carbs', 0):.1f}")
    c4.metric("Fat (g)", f"{selected['macros_g'].get('fat', 0):.1f}")

    c5, c6 = st.columns(2)
    c5.metric("Fiber (g)", f"{selected['macros_g'].get('fiber', 0):.1f}")
    c6.metric("Sugars (g)", f"{selected['macros_g'].get('sugars', 0):.1f}")

    st.markdown("---")
    st.markdown("## Plots")

    macro_df = pd.DataFrame(
        {
            "Nutrient": ["Protein", "Carbs", "Fat", "Fiber", "Sugars"],
            "Amount (g)": [
                selected["macros_g"].get("protein", 0),
                selected["macros_g"].get("carbs", 0),
                selected["macros_g"].get("fat", 0),
                selected["macros_g"].get("fiber", 0),
                selected["macros_g"].get("sugars", 0),
            ],
        }
    )
    macro_df = macro_df[macro_df["Amount (g)"] > 0]

    micro_data = selected.get("micros", {})
    micro_df = pd.DataFrame({"Nutrient": list(micro_data.keys()), "Value": list(micro_data.values())})
    micro_df = micro_df[micro_df["Value"] > 0].sort_values("Value", ascending=False)

    col_left, col_right = st.columns(2)

    with col_left:
        st.write("### Macro breakdown")
        if macro_df.empty:
            st.info("No macro data available.")
        else:
            fig_macro = px.pie(macro_df, names="Nutrient", values="Amount (g)", hole=0.35)
            st.plotly_chart(fig_macro, use_container_width=True)

    with col_right:
        st.write("### Micro nutrients")
        if micro_df.empty:
            st.info("No micro nutrient data available.")
        else:
            fig_micro = px.bar(
                micro_df,
                x="Nutrient",
                y="Value",
                title="Micro Nutrients (mixed units: mg/µg)",
            )
            fig_micro.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_micro, use_container_width=True)

    st.markdown("---")
    st.write("### Raw JSON (selected result)")
    st.json(selected)
