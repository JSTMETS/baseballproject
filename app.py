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
    ["Lobby", "Player", "Compare"]
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

# ==========================================
# 6.Compare
# ==========================================

elif page == "Compare":

    st.title("Player Comparison")

    st.write(
        "두 선수를 선택하여 실제 성적과 "
        "EV-LA 기반 기대 성적을 비교합니다."
    )


    # ======================================
    # 선수 A / 선수 B 영역
    # ======================================

    left, right = st.columns(2)


    # ======================================
    # 선수 A
    # ======================================

    with left:

        st.subheader("Player A")

        team_list_a = (
            ["전체"]
            + sorted(
                filtered_df["team"]
                .dropna()
                .unique()
                .tolist()
            )
        )

        team_a = st.selectbox(
            "팀 선택",
            team_list_a,
            key="compare_team_a"
        )


        player_df_a = filtered_df.copy()

        if team_a != "전체":
            player_df_a = player_df_a[
                player_df_a["team"] == team_a
            ]


        player_list_a = sorted(
            player_df_a["player_name"]
            .dropna()
            .unique()
            .tolist()
        )


        player_a = st.selectbox(
            "선수 선택",
            player_list_a,
            key="compare_player_a"
        )


    # ======================================
    # 선수 B
    # ======================================

    with right:

        st.subheader("Player B")

        team_list_b = (
            ["전체"]
            + sorted(
                filtered_df["team"]
                .dropna()
                .unique()
                .tolist()
            )
        )

        team_b = st.selectbox(
            "팀 선택",
            team_list_b,
            key="compare_team_b"
        )


        player_df_b = filtered_df.copy()

        if team_b != "전체":
            player_df_b = player_df_b[
                player_df_b["team"] == team_b
            ]


        player_list_b = sorted(
            player_df_b["player_name"]
            .dropna()
            .unique()
            .tolist()
        )


        player_b = st.selectbox(
            "선수 선택",
            player_list_b,
            key="compare_player_b"
        )


    # ======================================
    # 선택 선수 데이터
    # ======================================

    data_a = player_df_a[
        player_df_a["player_name"] == player_a
    ].iloc[0]


    data_b = player_df_b[
        player_df_b["player_name"] == player_b
    ].iloc[0]


    st.divider()


    # ======================================
    # 선수 이름 / 팀 / 포지션
    # ======================================

    left, right = st.columns(2)


    with left:

        st.subheader(
            f'{player_a} | '
            f'{data_a["team"]} | '
            f'{data_a["position"]}'
        )


    with right:

        st.subheader(
            f'{player_b} | '
            f'{data_b["team"]} | '
            f'{data_b["position"]}'
        )


    # ======================================
    # 핵심 지표
    # ======================================

    st.subheader("Key Metrics")


    left, right = st.columns(2)


    with left:

        st.metric(
            "EV-LA xOPS+",
            f'{data_a["EVLA_xOPS+"]:.2f}'
        )

        st.metric(
            "OPS",
            f'{data_a["OPS"]:.3f}'
        )

        st.metric(
            "xOPS",
            f'{data_a["xOPS"]:.3f}'
        )



    with right:

        st.metric(
            "EV-LA xOPS+",
            f'{data_b["EVLA_xOPS+"]:.2f}'
        )

        st.metric(
            "OPS",
            f'{data_b["OPS"]:.3f}'
        )

        st.metric(
            "xOPS",
            f'{data_b["xOPS"]:.3f}'
        )


    # ======================================
    # 상세 비교표
    # ======================================

    st.subheader("Detailed Comparison")


    compare_metrics = [
        "PA",
        "EVLA_xOPS+",
        "xBA",
        "xOBP",
        "xSLG",
        "xOPS",
        "BA",
        "OBP",
        "SLG",
        "OPS",
        "OPS_minus_xOPS"
    ]


    comparison = pd.DataFrame({
        "Metric": compare_metrics,

        player_a: [
            data_a[metric]
            for metric in compare_metrics
        ],

        player_b: [
            data_b[metric]
            for metric in compare_metrics
        ]
    })


    comparison["Difference (A - B)"] = (
        comparison[player_a]
        - comparison[player_b]
    )


    # 소수점 정리
    comparison[
        [
            player_a,
            player_b,
            "Difference (A - B)"
        ]
    ] = comparison[
        [
            player_a,
            player_b,
            "Difference (A - B)"
        ]
    ].round(3)


    st.dataframe(
        comparison,
        hide_index=True,
        use_container_width=True
    )
