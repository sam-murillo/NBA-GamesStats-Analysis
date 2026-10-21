
import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
 
st.set_page_config(page_title="What Wins NBA Games?", layout="wide")
st.title("What Wins NBA Games?")
 
# Every stat column except win and the date
STATS = ["teamScore", "opponentScore", "threePointersMade", "threePointersAttempted",
         "turnovers", "assistPercentage", "assistToTurnoverRatio", "reboundPercentage",
         "pointsOffTurnovers", "percentPoints3Point", "percentPointsOffTurnovers",
         "threePointersPercentage"]
 
# Game types to keep (check exact spelling with df["gameType"].value_counts())
GAME_TYPES = ["Regular Season", "Playoffs"]
 
@st.cache_data
def load_data():
    # slimmed, compressed copy of TeamStatisticsExtended.csv (see README)
    #df = pd.read_csv("nba_games.csv.gz")
    df = pd.read_csv("TeamStatisticsExtended.csv")
    df2 = df[["win"] + STATS + ["gameDateTimeEst", "gameType"]].copy()
 
    # keep only regular season and playoff games
    df2 = df2[df2["gameType"].isin(GAME_TYPES)].copy()
 
    # converting date time to year, month, day for later analysis :)
    date = df2["gameDateTimeEst"].astype(str)
    df2["year"] = date.str[:4].astype(int)
    month = date.str[5:7].astype(int)
    day = date.str[8:10].astype(int)
 
    # season = the year it starts (2015 means 2015-16)
    # games from mid-October onward belong to the new season
    starts_new_season = (month > 10) | ((month == 10) & (day >= 15))
    df2["season"] = df2["year"].where(starts_new_season, df2["year"] - 1)
    df2.drop(columns=["gameDateTimeEst"], inplace=True)
 
    # grouping seasons into eras (10 seasons each)
    df2["era"] = pd.cut(df2["season"],
                        bins=[1995, 2005, 2015, 2026],
                        labels=["1996–97 to 2005–06",
                                "2006–07 to 2015–16",
                                "2016–17 to present"])
 
    df2["win"] = df2["win"].astype(int)
    df2["result"] = df2["win"].map({1: "Win", 0: "Loss"})
    return df2
 
df2 = load_data()
 
# ---------- Sidebar: season filter ----------
st.sidebar.header("Filters")
min_season, max_season = int(df2["season"].min()), int(df2["season"].max())
season_range = st.sidebar.slider("Seasons (by starting year)", min_season, max_season,
                                 (min_season, max_season))
filtered = df2[df2["season"].between(season_range[0], season_range[1])]
st.sidebar.write(f"{len(filtered):,} games selected")
 
# ---------- Tabs ----------
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Wins vs. Losses", "Stat Relationships",
                                        "How the Game Has Changed",
                                        "Playoffs vs. Regular Season", "About"])
 
# ---------- Tab 1: What influences winning? ----------
with tab1:
    st.header("Wins vs. Losses")
    st.write("Average of each stat in wins compared to losses.")
 
    comparison = filtered.groupby("result")[STATS].mean().T
    comparison["Difference"] = comparison["Win"] - comparison["Loss"]
    st.dataframe(comparison.round(3), use_container_width=True)
 
    stat = st.selectbox("See the full distribution of a stat", STATS)
    fig_box = px.box(filtered, x="result", y=stat, color="result")
    st.plotly_chart(fig_box, use_container_width=True)
 
# ---------- Tab 2: How are stats correlated? ----------
with tab2:
    st.header("How Stats Relate to Each Other")
 
    chosen = st.multiselect("Stats to include", STATS, default=STATS)
    if len(chosen) >= 2:
        corr = filtered[chosen + ["win"]].corr()
        fig_heat = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r",
                             zmin=-1, zmax=1, aspect="auto")
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("Pick at least two stats.")
 
    col1, col2 = st.columns(2)
    x_stat = col1.selectbox("X axis", STATS, index=STATS.index("threePointersAttempted"))
    y_stat = col2.selectbox("Y axis", STATS, index=STATS.index("threePointersPercentage"))
 
    sample = filtered.sample(min(5000, len(filtered)), random_state=42)
    fig_scatter = px.scatter(sample, x=x_stat, y=y_stat, color="result", opacity=0.4)
    st.plotly_chart(fig_scatter, use_container_width=True)
 
# ---------- Tab 3: How has the game changed? ----------
with tab3:
    st.header("How the Game Has Changed")
 
    trend_stat = st.selectbox("Stat to track over time", STATS,
                              index=STATS.index("threePointersAttempted"))
    yearly = filtered.groupby("season")[trend_stat].mean().reset_index()
    fig_trend = px.line(yearly, x="season", y=trend_stat, markers=True)
    for boundary in [2005.5, 2015.5]:
        fig_trend.add_vline(x=boundary, line_dash="dash", line_color="gray")
    st.plotly_chart(fig_trend, use_container_width=True)
 
    era_stat = st.selectbox("Stat to compare across eras", STATS,
                            index=STATS.index("threePointersPercentage"))
    era_comp = (filtered.groupby(["era", "result"], observed=True)[era_stat]
                .mean().reset_index())
    fig_era = px.bar(era_comp, x="era", y=era_stat, color="result", barmode="group")
    st.plotly_chart(fig_era, use_container_width=True)
 
# ---------- Tab 4: Playoffs vs. regular season ----------
with tab4:
    st.header("Playoffs vs. Regular Season")
 
    rs = filtered[filtered["gameType"] == "Regular Season"]
    po = filtered[filtered["gameType"] == "Playoffs"]
 
    c1, c2 = st.columns(2)
    c1.metric("Regular season games", f"{len(rs):,}")
    c2.metric("Playoff games", f"{len(po):,}")
 
    if len(po) == 0 or len(rs) == 0:
        st.warning("The selected seasons need both regular season and playoff games.")
    else:
        # Part 1: are the stats themselves different?
        st.subheader("Are the stats different in the playoffs?")
        rows = []
        for s in STATS:
            rs_mean, po_mean = rs[s].mean(), po[s].mean()
            rows.append({
                "Stat": s,
                "Regular Season": rs_mean,
                "Playoffs": po_mean,
                "% Difference": (po_mean - rs_mean) / rs_mean * 100
            })
        type_comp = pd.DataFrame(rows).set_index("Stat")
        st.dataframe(type_comp.round(3), use_container_width=True)
 
        playoff_stat = st.selectbox("Compare a stat's distribution", STATS,
                                    index=STATS.index("teamScore"))
 
        # seaborn box plot
        fig_sns, ax = plt.subplots(figsize=(8, 5))
        sns.boxplot(data=filtered, x="gameType", y=playoff_stat, order=GAME_TYPES,
                    hue="gameType", palette="Set2", legend=False, ax=ax)
        ax.set_title(f"{playoff_stat}: Regular Season vs. Playoffs")
        ax.set_xlabel("")
        st.pyplot(fig_sns)
        plt.close(fig_sns)
 
        # Part 2: does what wins change in the playoffs?
        st.subheader("Does what wins change in the playoffs?")
        st.write("Correlation of each stat with winning, by game type.")
        win_corr = pd.DataFrame({
            "Regular Season": rs[STATS].corrwith(rs["win"]),
            "Playoffs": po[STATS].corrwith(po["win"]),
        })
        win_corr = win_corr.reset_index().rename(columns={"index": "Stat"})
        win_corr_long = win_corr.melt(id_vars="Stat", var_name="Game Type",
                                      value_name="Correlation with Winning")
        fig_wc = px.bar(win_corr_long, x="Correlation with Winning", y="Stat",
                        color="Game Type", barmode="group", orientation="h",
                        height=600)
        st.plotly_chart(fig_wc, use_container_width=True)
 
        # Part 3: heatmap of stat relationships
        st.subheader("How stats relate to each other in the playoffs")
        heat_stats = st.multiselect("Stats for the playoff heatmap", STATS,
                                    default=STATS, key="playoff_heat_stats")
        view = st.radio("Show", ["Playoffs", "Regular Season",
                                 "Difference (Playoffs − Regular Season)"],
                        horizontal=True)
 
        if len(heat_stats) >= 2:
            cols = heat_stats + ["win"]
            po_corr = po[cols].corr()
            rs_corr = rs[cols].corr()
 
            if view == "Playoffs":
                matrix, limit = po_corr, 1
            elif view == "Regular Season":
                matrix, limit = rs_corr, 1
            else:
                matrix = po_corr - rs_corr
                limit = matrix.abs().max().max()
 
            fig_po_heat = px.imshow(matrix, text_auto=".2f",
                                    color_continuous_scale="RdBu_r",
                                    zmin=-limit, zmax=limit, aspect="auto")
            st.plotly_chart(fig_po_heat, use_container_width=True)
        else:
            st.info("Pick at least two stats.")
 
# ---------- Tab 5: About ----------
with tab5:
    st.header("About This Project")
 
    st.subheader("Data Source")
    st.markdown("""
    My data was sourced from the Kaggle dataset at this link: https://www.kaggle.com/datasets/eoinamoore/historical-nba-data-and-player-box-scores/data . This app uses `TeamStatisticsExtended.csv`, which contains team statistics for each NBA game from 1996 onward.
    """)
 
    st.subheader("AI-Use Disclosure")
    st.markdown("""
    I used Claude Opus 5.5 to write and explain the code for this app, and to debug errors. The direction and decisions in this app are my own.

    """)
