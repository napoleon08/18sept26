import streamlit as st
import pandas as pd
import plotly.express as px


# =========================================================
# 1. НАСТРОЙКА СТРАНИЦЫ
# =========================================================

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)


# =========================================================
# 2. ЗАГРУЗКА ДАННЫХ
# =========================================================

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():

    df = pd.read_csv(DATA_URL)

    # 숫자 데이터
    number_columns = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for column in number_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # 장르가 여러 개면 첫 번째 장르만 사용
    df["장르"] = (
        df["genre"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 국가가 여러 개면 첫 번째 국가만 사용
    df["대표국가"] = (
        df["nation"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 개봉일
    df["개봉일"] = pd.to_datetime(
        df["openDt"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    return df


df = load_data()


# =========================================================
# 3. 제목
# =========================================================

st.title("🎬 영화 데이터 그래프 도감 2")
st.subheader("분포와 관계")

st.write(
    "영화 216편의 장르·국가·스크린 수·첫 주 관객·총 관객·"
    "TOP10 체류 일수를 그래프로 분석합니다."
)

st.divider()


# =========================================================
# 4. 데이터 기본 정보
# =========================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "영화 수",
        f"{len(df):,}편"
    )

with col2:
    st.metric(
        "장르 수",
        f"{df['장르'].nunique():,}개"
    )

with col3:
    st.metric(
        "제작 국가 수",
        f"{df['대표국가'].nunique():,}개"
    )

with col4:
    st.metric(
        "최대 총 관객",
        f"{df['total_audi'].max():,.0f}명"
    )


# =========================================================
# 5. 그래프 1 — 도넛
# =========================================================

st.divider()

st.header("1. 장르별 영화 편수 — 도넛")

st.write(
    "질문: **10위권에 든 영화의 장르 구성은 어떠한가?**"
)

genre_count = (
    df["장르"]
    .value_counts()
    .reset_index()
)

genre_count.columns = [
    "장르",
    "편수"
]

fig1 = px.pie(
    genre_count,
    names="장르",
    values="편수",
    hole=0.45
)

fig1.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "편수: %{value}편<br>"
        "비율: %{percent}"
        "<extra></extra>"
    )
)

fig1.update_layout(
    title="장르별 영화 구성",
    height=600
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

st.text_input(
    "이 그래프로 알 수 있는 것",
    value="애니메이션과 드라마가 많은 비중을 차지한다.",
    key="answer1"
)


# =========================================================
# 6. 그래프 2 — 트리맵
# =========================================================

st.divider()

st.header("2. 장르 안에서 어떤 영화가 컸나 — 트리맵")

st.write(
    "질문: **장르 안에서 어떤 영화가 큰 비중을 차지하는가?**"
)

fig2 = px.treemap(
    df,
    path=["장르", "movieNm"],
    values="total_audi",
    hover_name="movieNm"
)

fig2.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "총 관객: %{value:,.0f}명"
        "<extra></extra>"
    )
)

fig2.update_layout(
    title="장르 → 영화별 총 관객",
    height=650
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.text_input(
    "이 그래프로 알 수 있는 것",
    value="총 관객이 많은 대작 영화가 각 장르에서 큰 영역을 차지한다.",
    key="answer2"
)


# =========================================================
# 7. 도넛과 트리맵 비교
# =========================================================

st.info(
    "💡 **도넛과 트리맵의 기준 차이:** "
    "도넛은 영화의 **편수**를 기준으로 장르 구성을 보여 주고, "
    "트리맵은 영화의 **총 관객 수(total_audi)**를 기준으로 "
    "각 영화와 장르의 크기를 보여 줍니다."
)


# =========================================================
# 8. 그래프 3 — 히스토그램
# =========================================================

st.divider()

st.header("3. 총 관객의 분포 — 히스토그램")

st.write(
    "질문: **영화 대부분은 관객이 몇 명쯤인가?**"
)

fig3 = px.histogram(
    df,
    x="total_audi",
    nbins=40
)

fig3.update_layout(
    title="영화별 총 관객 분포",
    xaxis_title="총 관객",
    yaxis_title="영화 수",
    height=600
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

under_1m = (
    df["total_audi"] < 1_000_000
).sum()

best_movie = df.loc[
    df["total_audi"].idxmax()
]

st.write(
    f"**{len(df)}편 가운데 {under_1m}편이 "
    f"총 관객 100만 명 미만입니다.** "
    f"가장 많은 관객을 기록한 영화는 "
    f"**{best_movie['movieNm']}** "
    f"({best_movie['total_audi']:,.0f}명)입니다."
)

st.text_input(
    "이 그래프로 알 수 있는 것",
    value="대부분의 영화가 낮은 관객 구간에 몰려 있고 일부 대작 영화의 관객 수가 매우 크다.",
    key="answer3"
)


# =========================================================
# 9. 그래프 4 — 산점도
# =========================================================

st.divider()

st.header("4. 개봉일 스크린 수와 총 관객 — 산점도")

st.write(
    "질문: **스크린을 많이 받은 영화가 관객도 많은가?**"
)

fig4 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="장르",
    hover_name="movieNm",
    hover_data={
        "first_scrn": ":,.0f",
        "total_audi": ":,.0f"
    }
)

fig4.update_layout(
    title="개봉일 스크린 수와 총 관객의 관계",
    xaxis_title="개봉일 스크린 수",
    yaxis_title="총 관객",
    height=650
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

st.text_input(
    "이 그래프로 알 수 있는 것",
    value="개봉일 스크린 수가 많은 영화가 총 관객도 많은 경향이 있는지 확인할 수 있다.",
    key="answer4"
)


# =========================================================
# 10. 그래프 5 — 박스플롯
# =========================================================

st.divider()

st.header("5. 장르별 총 관객 — 박스플롯")

st.write(
    "영화가 10편 이상인 장르만 비교합니다."
)

genre_counts = df["장르"].value_counts()

selected_big_genres = genre_counts[
    genre_counts >= 10
].index

box_df = df[
    df["장르"].isin(selected_big_genres)
].copy()

fig5 = px.box(
    box_df,
    x="장르",
    y="total_audi",
    points="outliers",
    hover_name="movieNm"
)

fig5.update_layout(
    title="장르별 총 관객 분포",
    xaxis_title="장르",
    yaxis_title="총 관객",
    height=650
)

st.plotly_chart(
    fig5,
    use_container_width=True
)

st.text_input(
    "이 그래프로 알 수 있는 것",
    placeholder="직접 한 문장으로 적어 보세요.",
    key="answer5"
)


# =========================================================
# 11. 그래프 6 — 버블
# =========================================================

st.divider()

st.header("6. 첫 주 관객을 넣은 버블 그래프")

st.write(
    "질문: **첫 주 관객까지 넣으면 무엇이 더 보이는가?**"
)

bubble_df = df.copy()

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
        "first_week_audi": ":,.0f",
        "total_audi": ":,.0f"
    }
)

fig6.update_layout(
    title="스크린 수 · 총 관객 · 첫 주 관객",
    xaxis_title="개봉일 스크린 수",
    yaxis_title="총 관객",
    height=700
)

st.plotly_chart(
    fig6,
    use_container_width=True
)

st.text_input(
    "이 그래프로 알 수 있는 것",
    placeholder="직접 한 문장으로 적어 보세요.",
    key="answer6"
)


# =========================================================
# 12. 그래프 7 — 선버스트
# =========================================================

st.divider()

st.header("7. 국가에서 장르로 — 선버스트")

st.write(
    "질문: **제작 국가에서 장르로 내려가면 무엇이 보이는가?**"
)

sunburst_df = (
    df.groupby(
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
    values="편수"
)

fig7.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 수: %{value}편"
        "<extra></extra>"
    )
)

fig7.update_layout(
    title="제작 국가 → 장르 구성",
    height=700
)

st.plotly_chart(
    fig7,
    use_container_width=True
)

st.text_input(
    "이 그래프로 알 수 있는 것",
    placeholder="직접 한 문장으로 적어 보세요.",
    key="answer7"
)


# =========================================================
# 13. 나만의 8번째 질문
# =========================================================

st.divider()

st.header("8. 나만의 질문 — 직접 만들고 분석하기")

st.write(
    "그래프를 먼저 고르지 말고 **질문을 먼저 만든 뒤** "
    "그 질문에 어울리는 그래프를 선택합니다."
)

st.markdown(
    """
### 💡 질문을 만들 때 사용할 수 있는 열

`openDt` · `genre` · `nation` · `first_scrn` ·
`first_show` · `first_week_audi` · `total_audi` ·
`days_in_top10`
"""
)

question = st.text_area(
    "① 나만의 질문",
    placeholder=(
        "예: 10위권에 오래 머문 영화는 총 관객도 많은가?"
    ),
    height=100
)

graph = st.selectbox(
    "② 이 질문에 어울리는 그래프",
    [
        "산점도",
        "버블",
        "히스토그램",
        "박스플롯",
        "도넛",
        "트리맵",
        "선버스트"
    ]
)

st.markdown("### ③ 나만의 질문에 대한 그래프")

if graph == "산점도":

    fig8 = px.scatter(
        df,
        x="days_in_top10",
        y="total_audi",
        color="장르",
        hover_name="movieNm"
    )

    fig8.update_layout(
        title="TOP10 체류 일수와 총 관객",
        xaxis_title="10위권에 머문 날수",
        yaxis_title="총 관객",
        height=650
    )

    st.plotly_chart(
        fig8,
        use_container_width=True
    )

elif graph == "버블":

    temp = df.copy()

    temp["버블크기"] = (
        temp["first_week_audi"]
        .fillna(1)
        .clip(lower=1)
    )

    fig8 = px.scatter(
        temp,
        x="days_in_top10",
        y="total_audi",
        size="버블크기",
        color="장르",
        size_max=45,
        hover_name="movieNm"
    )

    fig8.update_layout(
        title="TOP10 체류 일수 · 총 관객 · 첫 주 관객",
        xaxis_title="10위권에 머문 날수",
        yaxis_title="총 관객",
        height=650
    )

    st.plotly_chart(
        fig8,
        use_container_width=True
    )

elif graph == "히스토그램":

    fig8 = px.histogram(
        df,
        x="days_in_top10",
        nbins=30
    )

    fig8.update_layout(
        title="TOP10 체류 일수 분포",
        xaxis_title="10위권에 머문 날수",
        yaxis_title="영화 수",
        height=600
    )

    st.plotly_chart(
        fig8,
        use_container_width=True
    )

elif graph == "박스플롯":

    fig8 = px.box(
        df,
        x="장르",
        y="days_in_top10",
        points="outliers",
        hover_name="movieNm"
    )

    fig8.update_layout(
        title="장르별 TOP10 체류 일수",
        xaxis_title="장르",
        yaxis_title="TOP10 체류 일수",
        height=650
    )

    st.plotly_chart(
        fig8,
        use_container_width=True
    )

elif graph == "도넛":

    data8 = (
        df["대표국가"]
        .value_counts()
        .reset_index()
    )

    data8.columns = [
        "국가",
        "편수"
    ]

    fig8 = px.pie(
        data8,
        names="국가",
        values="편수",
        hole=0.45
    )

    fig8.update_layout(
        title="제작 국가별 영화 구성",
        height=600
    )

    st.plotly_chart(
        fig8,
        use_container_width=True
    )

elif graph == "트리맵":

    fig8 = px.treemap(
        df,
        path=["대표국가", "movieNm"],
        values="total_audi",
        hover_name="movieNm"
    )

    fig8.update_layout(
        title="국가별 영화와 총 관객",
        height=650
    )

    st.plotly_chart(
        fig8,
        use_container_width=True
    )

elif graph == "선버스트":

    fig8 = px.sunburst(
        sunburst_df,
        path=["대표국가", "장르"],
        values="편수"
    )

    fig8.update_layout(
        title="제작 국가 → 장르",
        height=650
    )

    st.plotly_chart(
        fig8,
        use_container_width=True
    )


st.markdown("### ④ 이 그래프로 알 수 있는 것")

answer8 = st.text_area(
    "한 문장으로 분석 결과를 적어 보세요.",
    placeholder=(
        "예: 10위권에 오래 머문 영화일수록 총 관객도 많은 경향이 나타나는지 확인할 수 있다."
    ),
    height=100
)


# =========================================================
# 14. 오늘의 체크
# =========================================================

st.divider()

st.header("✅ 오늘의 체크")

check1 = st.checkbox(
    "필수 4종(도넛·트리맵·히스토그램·산점도)을 완성하고, 각각 「이 그래프로 알 수 있는 것」을 한 문장씩 적었다."
)

check2 = st.checkbox(
    "도넛과 트리맵의 구성이 왜 다른지 기준의 차이로 설명할 수 있다."
)

check3 = st.checkbox(
    "나만의 8번째 질문을 만들고, 어울리는 그래프로 답한 뒤 「이 그래프로 알 수 있는 것」 한 문장을 기록했다."
)

if check1 and check2 and check3:
    st.success(
        "🎉 오늘의 체크를 모두 완료했습니다!"
    )
else:
    completed = sum(
        [check1, check2, check3]
    )

    st.info(
        f"현재 {completed}/3 항목을 완료했습니다."
    )


# =========================================================
# 15. 원본 데이터 확인
# =========================================================

st.divider()

with st.expander("📋 216편 원본 데이터 보기"):

    show_df = df[
        [
            "movieNm",
            "openDt",
            "장르",
            "대표국가",
            "first_scrn",
            "first_show",
            "first_week_audi",
            "total_audi",
            "days_in_top10"
        ]
    ].copy()

    show_df.columns = [
        "영화명",
        "개봉일",
        "장르",
        "제작 국가",
        "개봉일 스크린 수",
        "개봉일 상영 횟수",
        "첫 주 관객",
        "총 관객",
        "TOP10 체류 일수"
    ]

    st.dataframe(
        show_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "영화 데이터 그래프 도감 2 - 분포와 관계"
)

st.caption(
    "데이터 원출처: 영화진흥위원회 KOBIS"
)
