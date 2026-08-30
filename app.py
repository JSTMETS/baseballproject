#cd "/Users/computer/Desktop/비즈니스/2026 5~8 it/Data 6~8월/8월/project" && /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 -m streamlit run app.py

import streamlit as st
import pandas as pd
from pathlib import Path


# ==========================================
# 1. 기본 설정
# ==========================================

st.set_page_config(
    page_title="EV-LA Batting Dashboard",
    layout="wide"
)


# ==========================================
# 2.데이터 불러오기
# ==========================================

base_dir = Path(__file__).resolve().parent
csv_path = base_dir / "player_result_2025.csv"

df = pd.read_csv(csv_path)

# 컬럼명 앞뒤 공백 제거
df.columns = df.columns.str.strip()


# ==========================================
# 3. 사이드바
# ==========================================

st.sidebar.title("EV-LA Dashboard")

page = st.sidebar.radio(
    "Page",
    ["Lobby", "Player"]
)


# 최소 PA 필터

def set_qualified():
    st.session_state["min_pa"] = 502


st.sidebar.button(
    "Q",
    on_click=set_qualified
)

min_pa = st.sidebar.slider(
    "최소 PA (Qualified : 502)",
    min_value=0,
    max_value=int(df["PA"].max()),
    value=502,
    step=10,
    key="min_pa"
)

filtered_df = df[
    df["PA"] >= min_pa
].copy()


# ==========================================
# 4. Lobby
# ==========================================

if page == "Lobby":

    st.title("EV-LA Batting Dashboard")

    st.write(
        "Exit Velocity와 Launch Angle을 이용해 "
        "타구 결과의 기대 생산성을 계산합니다."
    )


    # ======================================
    # Leaderboard
    # ======================================

    st.subheader("Leaderboard")

    ranking = (
    filtered_df[
        [
            "EVLA_xOPS+",
            "OPS_minus_xOPS",
            "player_name",
            "team",
            "position",
            "PA",
            "BA",
            "xBA",
            "OPS",
            "xOPS"
        ]
    ]
        .sort_values(
            "EVLA_xOPS+",
            ascending=False
        )
        .reset_index(drop=True)
    )

    ranking.index = ranking.index + 1

    st.dataframe(
        ranking,
        use_container_width=True
    )


# ==========================================
# 5. Player
# ==========================================

elif page == "Player":

    st.title("Player")


    # ======================================
    # 팀 / 선수 선택
    # ======================================

    col_team, col_player = st.columns(2)


    # 팀 목록
    team_list = (
        ["전체"]
        + sorted(
            filtered_df["team"]
            .dropna()
            .unique()
            .tolist()
        )
    )


    # 팀 선택
    with col_team:
        selected_team = st.selectbox(
            "팀 선택",
            team_list
        )


    # 선택한 팀에 따라 선수 후보 제한
    player_filter_df = filtered_df.copy()

    if selected_team != "전체":
        player_filter_df = player_filter_df[
            player_filter_df["team"] == selected_team
        ]


    # 선수 목록
    player_list = sorted(
        player_filter_df["player_name"]
        .dropna()
        .unique()
        .tolist()
    )


    # 해당 조건에 선수가 없을 경우
    if len(player_list) == 0:
        st.warning("해당 조건에 맞는 선수가 없습니다.")
        st.stop()


    # 선수 선택
    with col_player:
        player = st.selectbox(
            "선수 선택",
            player_list
        )


    # ======================================
    # ★ 여기부터 col_player 밖
    # 선택된 선수 데이터
    # ======================================

    player_data = player_filter_df[
        player_filter_df["player_name"] == player
    ].iloc[0]


    # ======================================
    # 선수 기본 정보
    # ======================================

    st.subheader(
        f'{player} | {player_data["team"]}'
    )


    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "PA(타석)",
            int(player_data["PA"])
        )

    with col2:
        st.metric(
            "BBE(인플레이 타구)",
            int(player_data["BBE"])
        )

    with col3:
        st.metric(
            "EV-LA xOPS+(예측된 OPS+ 기대값)",
            f'{player_data["EVLA_xOPS+"]:.2f}'
        )


    # ======================================
    # Actual vs Expected
    # ======================================

    st.subheader("Actual vs Expected")


    col1, col2, col3, col4 = st.columns(4)


    with col1:
        st.metric(
            "BA(실제 타율)",
            f'{player_data["BA"]:.3f}'
        )

        st.metric(
            "xBA(기대 타율)",
            f'{player_data["xBA"]:.3f}'
        )


    with col2:
        st.metric(
            "OBP(실제 출루율)",
            f'{player_data["OBP"]:.3f}'
        )

        st.metric(
            "xOBP(기대 출루율)",
            f'{player_data["xOBP"]:.3f}'
        )


    with col3:
        st.metric(
            "SLG(실제 장타율)",
            f'{player_data["SLG"]:.3f}'
        )

        st.metric(
            "xSLG(기대 장타율)",
            f'{player_data["xSLG"]:.3f}'
        )


    with col4:
        st.metric(
            "OPS(실제 OPS)",
            f'{player_data["OPS"]:.3f}'
        )

        st.metric(
            "xOPS(기대 OPS)",
            f'{player_data["xOPS"]:.3f}'
        )


    # ======================================
    # Actual - Expected
    # ======================================

    st.subheader("Actual - Expected")


    difference_df = pd.DataFrame({
        "Metric": [
            "BA",
            "SLG",
            "OPS"
        ],

        "Difference": [
            player_data["BA_minus_xBA"],
            player_data["SLG_minus_xSLG"],
            player_data["OPS_minus_xOPS"]
        ]
    })


    st.dataframe(
        difference_df,
        hide_index=True,
        use_container_width=True
    )


    # ======================================
    # OPS vs xOPS
    # ======================================

    st.subheader("OPS vs xOPS")

    st.scatter_chart(
        filtered_df,
        x="OPS",
        y="xOPS",
        size="PA"
    )


    # ======================================
    # BA vs xBA
    # ======================================

    st.subheader("BA vs xBA")

    st.scatter_chart(
        filtered_df,
        x="BA",
        y="xBA",
        size="PA"
    )


    # ======================================
    # SLG vs xSLG
    # ======================================

    st.subheader("SLG vs xSLG")

    st.scatter_chart(
        filtered_df,
        x="SLG",
        y="xSLG",
        size="PA"
    )