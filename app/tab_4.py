import streamlit as st
import plotly.express as px
import importlib

from src import rice_scoring
importlib.reload(rice_scoring)


def renderPrioritizationTab(reviews):
    st.markdown("<h2 style='text-align: center; color: #00000;'></h2>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #00000;'>🎯 Feature Prioritization (RICE) 🎯</h2>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #00000;'></h2>", unsafe_allow_html=True)

    st.write("""
    This tab converts raw review scores into a **prioritized improvement backlog** using a
    **RICE framework** (Reach × Impact × Confidence ÷ Effort). Reach, Impact, and Confidence
    are calculated directly from the review data; Effort is a judgment call you can adjust
    below to reflect real implementation cost — exactly how a PM would scope a real backlog.
    """)

    st.markdown("##### ⚙️ Adjust Effort (1 = quick fix, 5 = major rebuild)")
    col1, col2, col3 = st.columns(3)
    with col1:
        effort_food = st.slider("Food Quality", 1, 5, 2, key="effort_food")
    with col2:
        effort_service = st.slider("Service", 1, 5, 2, key="effort_service")
    with col3:
        effort_atmosphere = st.slider("Ambience", 1, 5, 3, key="effort_atmosphere")

    effort_overrides = {
        'food_score': effort_food,
        'service_score': effort_service,
        'atmosphere_score': effort_atmosphere
    }

    rice_df = rice_scoring.compute_rice_table(reviews, effort_overrides)

    if rice_df.empty:
        st.warning("Not enough aspect-level score data found to compute RICE priorities for this dataset.")
        return

    fig = px.bar(
        rice_df.sort_values('RICE Score'),
        x='RICE Score', y='Aspect', orientation='h',
        text='RICE Score', color='RICE Score',
        color_continuous_scale='Blues',
        title="Prioritized Improvement Backlog (Higher RICE Score = Fix First)"
    )
    fig.update_layout(showlegend=False, yaxis_title="", xaxis_title="RICE Score")
    st.plotly_chart(fig, use_container_width=True, key="fig_rice_priority")

    st.markdown("##### 📋 Prioritization Breakdown")
    st.dataframe(rice_df.set_index('Priority Rank'), use_container_width=True)

    top = rice_df.iloc[0]
    st.success(
        f"**Recommended first fix:** {top['Aspect']} — affects {top['Reach (%)']}% of reviewers, "
        f"RICE score {top['RICE Score']}."
    )
