import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np


# =========================================================
# НАСТРОЙКИ СТРАНИЦЫ
# =========================================================

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# СТИЛЬ САЙТА
# =========================================================

st.markdown("""
<style>

    .main {
        background-color: #f7f8fa;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1400px;
    }

    .hero {
        padding: 2rem 2.2rem;
        border-radius: 24px;
        background: linear-gradient(135deg, #111827, #374151);
        color: white;
        margin-bottom: 1.5rem;
    }

    .hero h1 {
        font-size: 2.4rem;
        margin-bottom: 0.5rem;
    }

    .hero p {
        font-size: 1.05rem;
        color: #d1d5db;
        margin-bottom: 0;
    }

    .card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
    }

    .question-card {
        background: #ffffff;
        border-left: 5px solid #111827;
        padding: 1rem 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
    }

    .answer-card {
        background: #f3f4f6;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-top: 0.7rem;
    }

    .small-label {
        color: #6b7280;
        font-size: 0.85rem;
        font-weight: 600;
    }

    .metric-number {
        font-size: 1.8rem;
        font-weight: 700;
        color: #111827;
    }

    .metric-label {
        color: #6b7280;
        font-size: 0.9rem;
    }

    .section-title {
        font-size: 1.65rem;
        font-weight: 700;
        margin-top: 2rem;
        margin-bottom: 0.5rem;
    }

    .section-description {
        color: #6b7280;
        margin-bottom: 1rem;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #e5e7eb;
        padding: 1rem;
        border-radius: 16px;
    }

</style>
""", unsafe_allow_html=True)


# =========================================================
# DATA
# =========================================================

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/main/"
    "data/kobis_movies.csv"
)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 숫자형 열 변환
    numeric_columns = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 개봉일
    df["openDt"] = df["openDt"].astype(str).str.replace(
        ".0", "", regex=False
    )

    df["개봉일"] = pd.to_datetime(
        df["openDt"],
        format="%Y%m%d",
        errors="coerce"
    )

    # 여러 장르가 있으면 첫 번째 장르
    df["장르"] = (
        df["genre"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 여러 국가가 있으면 첫 번째 국가
    df["대표국가"] = (
        df["nation"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 빈 값 처리
    df["장르"] = df["장르"].replace("", "미상")
    df["대표국가"] = df["대표국가"].replace("", "미상")

    return df


try:
    df = load_data()
except Exception as e:
    st.error("데이터를 불러오지 못했습니다.")
    st.code(str(e))
    st.stop()


# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="hero">
    <h1>🎬 영화 데이터 그래프 도감 2</h1>
    <p>분포와 관계 · KOBIS 영화 데이터 216편 분석</p>
</div>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🎛️ 분석 설정")

st.sidebar.markdown(
    "### 데이터"
)

st.sidebar.write(
    f"현재 데이터: **{len(df)}편**"
)

st.sidebar.divider()

# 장르 필터
genre_options = sorted(df["장르"].dropna().unique().tolist())

selected_genres = st.sidebar.multiselect(
    "장르 선택",
    genre_options,
    default=genre_options
)

# 국가 필터
country_options = sorted(df["대표국가"].dropna().unique().tolist())

selected_countries = st.sidebar.multiselect(
    "제작 국가 선택",
    country_options,
    default=country_options
)

st.sidebar.divider()

st.sidebar.caption(
    "원본 데이터: 영화진흥위원회 KOBIS"
)

st.sidebar.caption(
    "데이터: greatsong/modudata/kobis_movies.csv"
)


# =========================================================
# FILTERED DATA
# =========================================================

filtered_df = df[
    df["장르"].isin(selected_genres)
    & df["대표국가"].isin(selected_countries)
].copy()


# =========================================================
# TOP METRICS
# =========================================================

st.markdown(
    '<div class="section-title">📊 데이터 한눈에 보기</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "영화 수",
        f"{len(filtered_df):,}편"
    )

with c2:
    st.metric(
        "총 관객 최대",
        f"{filtered_df['total_audi'].max():,.0f}명"
        if len(filtered_df) else "0명"
    )

with c3:
    st.metric(
        "평균 총 관객",
        f"{filtered_df['total_audi'].mean():,.0f}명"
        if len(filtered_df) else "0명"
    )

with c4:
    st.metric(
        "평균 TOP10 일수",
        f"{filtered_df['days_in_top10'].mean():.1f}일"
        if len(filtered_df) else "0일"
    )


st.divider()


# =========================================================
# GRAPH 1
# =========================================================

st.markdown(
    '<div class="section-title">1. 장르별 영화 편수 — 도넛</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    '질문: <b>10위권에 든 영화의 장르 구성은 어떠한가?</b>'
    '</div>',
    unsafe_allow_html=True
)

genre_count = (
    filtered_df["장르"]
    .value_counts()
    .reset_index()
)

genre_count.columns = ["장르", "편수"]

fig1 = px.pie(
    genre_count,
    names="장르",
    values="편수",
    hole=0.48,
    title="장르별 영화 편수"
)

fig1.update_traces(
    textposition="inside",
    textinfo="percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 수: %{value}편<br>"
        "비율: %{percent}"
        "<extra></extra>"
    )
)

fig1.update_layout(
    height=550,
    margin=dict(l=20, r=20, t=70, b=20)
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

st.text_input(
    "이 그래프로 알 수 있는 것",
    placeholder="예: 애니메이션과 드라마가 많은 비중을 차지한다.",
    key="note1"
)


st.divider()


# =========================================================
# GRAPH 2
# =========================================================

st.markdown(
    '<div class="section-title">2. 장르 안의 영화 — 트리맵</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    '질문: <b>장르 안에서 어떤 영화가 큰 비중을 차지하는가?</b>'
    '</div>',
    unsafe_allow_html=True
)

fig2 = px.treemap(
    filtered_df,
    path=["장르", "movieNm"],
    values="total_audi",
    color="total_audi",
    hover_name="movieNm",
    hover_data={
        "total_audi": ":,.0f"
    }
)

fig2.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "총 관객: %{value:,.0f}명"
        "<extra></extra>"
    )
)

fig2.update_layout(
    height=650,
    margin=dict(l=10, r=10, t=30, b=10)
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.text_input(
    "이 그래프로 알 수 있는 것",
    placeholder="예: 일부 대작 영화가 전체 관객에서 매우 큰 비중을 차지한다.",
    key="note2"
)


st.divider()


# =========================================================
# GRAPH 3
# =========================================================

st.markdown(
    '<div class="section-title">3. 총 관객의 분포 — 히스토그램</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    '질문: <b>영화 대부분은 관객이 몇 명쯤인가?</b>'
    '</div>',
    unsafe_allow_html=True
)

fig3 = px.histogram(
    filtered_df,
    x="total_audi",
    nbins=40,
    labels={
        "total_audi": "총 관객"
    }
)

fig3.update_layout(
    height=550,
    xaxis_title="총 관객",
    yaxis_title="영화 수",
    bargap=0.05
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

under_1m = (
    filtered_df["total_audi"] < 1_000_000
).sum()

if len(filtered_df) > 0:
    best_movie = filtered_df.loc[
        filtered_df["total_audi"].idxmax()
    ]

    st.info(
        f"현재 선택된 {len(filtered_df)}편 가운데 "
        f"**{under_1m}편**이 총 관객 100만 명 미만입니다. "
        f"가장 많은 관객을 기록한 영화는 "
        f"**{best_movie['movieNm']}** "
        f"({best_movie['total_audi']:,.0f}명)입니다."
    )

st.text_input(
    "이 그래프로 알 수 있는 것",
    placeholder="예: 대부분의 영화가 낮은 관객 구간에 몰려 있다.",
    key="note3"
)


st.divider()


# =========================================================
# GRAPH 4
# =========================================================

st.markdown(
    '<div class="section-title">4. 개봉일 스크린 수와 총 관객 — 산점도</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    '질문: <b>스크린을 많이 받은 영화가 관객도 많은가?</b>'
    '</div>',
    unsafe_allow_html=True
)

fig4 = px.scatter(
    filtered_df,
    x="first_scrn",
    y="total_audi",
    color="장르",
    hover_name="movieNm",
    hover_data={
        "first_scrn": ":,.0f",
        "total_audi": ":,.0f"
    },
    labels={
        "first_scrn": "개봉일 스크린 수",
        "total_audi": "총 관객"
    }
)

fig4.update_layout(
    height=650
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

st.text_input(
    "이 그래프로 알 수 있는 것",
    placeholder="예: 개봉일 스크린 수가 많은 영화일수록 총 관객도 높은 경향이 나타난다.",
    key="note4"
)


st.divider()


# =========================================================
# GRAPH 5
# =========================================================

st.markdown(
    '<div class="section-title">5. 장르별 총 관객 — 박스플롯</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    '영화가 10편 이상인 장르만 비교합니다.'
    '</div>',
    unsafe_allow_html=True
)

genre_sizes = filtered_df["장르"].value_counts()

large_genres = genre_sizes[
    genre_sizes >= 10
].index

box_df = filtered_df[
    filtered_df["장르"].isin(large_genres)
].copy()

fig5 = px.box(
    box_df,
    x="장르",
    y="total_audi",
    points="outliers",
    hover_name="movieNm",
    color="장르",
    labels={
        "장르": "장르",
        "total_audi": "총 관객"
    }
)

fig5.update_layout(
    height=650,
    showlegend=False
)

st.plotly_chart(
    fig5,
    use_container_width=True
)

st.text_input(
    "이 그래프로 알 수 있는 것",
    placeholder="예: 장르마다 총 관객의 중앙값과 분포가 서로 다르다.",
    key="note5"
)


st.divider()


# =========================================================
# GRAPH 6
# =========================================================

st.markdown(
    '<div class="section-title">6. 첫 주 관객을 넣은 버블 그래프</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    '질문: <b>첫 주 관객까지 넣으면 무엇이 더 보이는가?</b>'
    '</div>',
    unsafe_allow_html=True
)

bubble_df = filtered_df.copy()

# Plotly 버블 크기에서 0 또는 음수 문제가 생기지 않도록 처리
bubble_df["버블크기"] = (
    bubble_df["first_week_audi"]
    .fillna(1)
    .clip(lower=1)
)

fig6 = px.scatter(
    bubble_df,
    x="first_scrn",
    y="total_audi",
    color="장르",
    size="버블크기",
    size_max=45,
    hover_name="movieNm",
    hover_data={
        "first_scrn": ":,.0f",
        "total_audi": ":,.0f",
        "first_week_audi": ":,.0f"
    },
    labels={
        "first_scrn": "개봉일 스크린 수",
        "total_audi": "총 관객",
        "first_week_audi": "첫 주 관객"
    }
)

fig6.update_layout(
    height=700
)

st.plotly_chart(
    fig6,
    use_container_width=True
)

st.text_input(
    "이 그래프로 알 수 있는 것",
    placeholder="예: 첫 주 관객이 많은 영화는 큰 원으로 나타나며 총 관객과의 관계를 함께 볼 수 있다.",
    key="note6"
)


st.divider()


# =========================================================
# GRAPH 7
# =========================================================

st.markdown(
    '<div class="section-title">7. 국가에서 장르로 — 선버스트</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    '질문: <b>제작 국가에서 장르로 내려가면 어떤 구성이 보이는가?</b>'
    '</div>',
    unsafe_allow_html=True
)

sunburst_df = (
    filtered_df
    .groupby(
        ["대표국가", "장르"],
        as_index=False
    )
    .agg(
        편수=("movieNm", "count")
    )
)

fig7 = px.sunburst(
    sunburst_df,
    path=["대표국가", "장르"],
    values="편수",
    hover_data={
        "편수": True
    }
)

fig7.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 수: %{value}편"
        "<extra></extra>"
    )
)

fig7.update_layout(
    height=700
)

st.plotly_chart(
    fig7,
    use_container_width=True
)

st.text_input(
    "이 그래프로 알 수 있는 것",
    placeholder="예: 국가별로 많이 등장하는 장르의 구성이 서로 다르다.",
    key="note7"
)


st.divider()


# =========================================================
# 8번째 질문
# =========================================================

st.markdown(
    '<div class="section-title">8. 나만의 질문 — 직접 분석하기</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="question-card">
        <b>이제 그래프가 아니라 질문부터 만듭니다.</b><br><br>
        지금까지의 7개 그래프는 수업에서 질문과 그래프가 정해져 있었습니다.
        여기서는 내가 직접 질문을 만들고, 그 질문에 맞는 그래프를 선택합니다.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("### 💡 질문 만들기")

question = st.text_area(
    "나만의 질문",
    placeholder=(
        "예: 10위권에 오래 머문 영화는 총 관객도 많은가?"
    ),
    height=100
)

graph_type = st.selectbox(
    "어울리는 그래프 선택",
    [
        "히스토그램",
        "박스플롯",
        "도넛",
        "트리맵",
        "산점도",
        "버블",
        "선버스트"
    ]
)

if question.strip():
    st.markdown(
        f"""
        <div class="answer-card">
            <b>나의 질문</b><br>
            {question}
            <br><br>
            <b>선택한 그래프</b><br>
            {graph_type}
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# 8번째 질문용 자동 분석 예시
# =========================================================

st.markdown("### 🔎 질문 분석 도구")

analysis_choice = st.selectbox(
    "분석하고 싶은 항목",
    [
        "10위권에 머문 날수",
        "개봉일 스크린 수와 총 관객",
        "첫 주 관객과 총 관객",
        "개봉일 상영횟수와 총 관객",
        "제작 국가별 영화 수"
    ]
)


if analysis_choice == "10위권에 머문 날수":

    fig8 = px.histogram(
        filtered_df,
        x="days_in_top10",
        nbins=30,
        labels={
            "days_in_top10": "10위권에 머문 날수"
        },
        title="영화별 10위권 체류 일수 분포"
    )

    st.plotly_chart(
        fig8,
        use_container_width=True
    )

    median_days = filtered_df["days_in_top10"].median()

    st.info(
        f"현재 데이터에서 10위권 체류 일수의 중앙값은 "
        f"**{median_days:.1f}일**입니다."
    )


elif analysis_choice == "개봉일 스크린 수와 총 관객":

    fig8 = px.scatter(
        filtered_df,
        x="first_scrn",
        y="total_audi",
        color="장르",
        hover_name="movieNm",
        trendline="ols",
        labels={
            "first_scrn": "개봉일 스크린 수",
            "total_audi": "총 관객"
        }
    )

    st.plotly_chart(
        fig8,
        use_container_width=True
    )


elif analysis_choice == "첫 주 관객과 총 관객":

    fig8 = px.scatter(
        filtered_df,
        x="first_week_audi",
        y="total_audi",
        color="장르",
        hover_name="movieNm",
        trendline="ols",
        labels={
            "first_week_audi": "첫 주 관객",
            "total_audi": "총 관객"
        }
    )

    st.plotly_chart(
        fig8,
        use_container_width=True
    )


elif analysis_choice == "개봉일 상영횟수와 총 관객":

    fig8 = px.scatter(
        filtered_df,
        x="first_show",
        y="total_audi",
        color="장르",
        hover_name="movieNm",
        trendline="ols",
        labels={
            "first_show": "개봉일 상영횟수",
            "total_audi": "총 관객"
        }
    )

    st.plotly_chart(
        fig8,
        use_container_width=True
    )


elif analysis_choice == "제작 국가별 영화 수":

    country_count = (
        filtered_df["대표국가"]
        .value_counts()
        .reset_index()
    )

    country_count.columns = [
        "국가",
        "영화수"
    ]

    fig8 = px.pie(
        country_count,
        names="국가",
        values="영화수",
        hole=0.45,
        title="제작 국가별 영화 구성"
    )

    fig8.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>"
            "영화 수: %{value}편<br>"
            "비율: %{percent}"
            "<extra></extra>"
        )
    )

    st.plotly_chart(
        fig8,
        use_container_width=True
    )


# =========================================================
# DATA TABLE
# =========================================================

st.divider()

st.markdown(
    '<div class="section-title">📋 원본 영화 데이터</div>',
    unsafe_allow_html=True
)

show_columns = [
    "movieNm",
    "개봉일",
    "장르",
    "대표국가",
    "first_scrn",
    "first_show",
    "first_week_audi",
    "total_audi",
    "days_in_top10"
]

display_df = filtered_df[show_columns].copy()

display_df.columns = [
    "영화명",
    "개봉일",
    "장르",
    "제작 국가",
    "개봉일 스크린",
    "개봉일 상영",
    "첫 주 관객",
    "총 관객",
    "TOP10 일수"
]

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# DOWNLOAD
# =========================================================

csv = display_df.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    label="⬇️ 현재 필터 데이터 CSV 다운로드",
    data=csv,
    file_name="kobis_movies_filtered.csv",
    mime="text/csv"
)


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "영화 데이터 그래프 도감 2 · 분포와 관계"
)

st.caption(
    "데이터 원출처: 영화진흥위원회 KOBIS"
)
