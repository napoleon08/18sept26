import streamlit as st
import pandas as pd
import plotly.express as px


# =========================================================
# 기본 설정
# =========================================================

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2",
    page_icon="🎬",
    layout="wide"
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


# =========================================================
# 데이터 불러오기
# =========================================================

@st.cache_data
def load_data():

    df = pd.read_csv(DATA_URL)

    numeric_columns = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # 첫 번째 장르
    df["장르"] = (
        df["genre"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 첫 번째 국가
    df["제작국가"] = (
        df["nation"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    return df


df = load_data()


# =========================================================
# 제목
# =========================================================

st.title("🎬 영화 데이터 그래프 도감 2")
st.subheader("분포와 관계 — 영화산업과 역사적 맥락")

st.write(
    "KOBIS 영화 데이터를 활용하여 영화의 흥행 구조, "
    "배급 규모, 장기 흥행, 국가별 차이와 장르별 관객 분포를 분석한다."
)

st.divider()


# =========================================================
# 데이터 개요
# =========================================================

st.header("📊 데이터 개요")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "분석 영화",
        f"{len(df):,}편"
    )

with c2:
    st.metric(
        "장르",
        f"{df['장르'].nunique()}개"
    )

with c3:
    st.metric(
        "제작 국가",
        f"{df['제작국가'].nunique()}개"
    )

with c4:
    st.metric(
        "최대 총 관객",
        f"{df['total_audi'].max():,.0f}명"
    )


# =========================================================
# 필수 그래프 1
# =========================================================

st.divider()

st.header("1. 장르 구성 — 도넛 그래프")

st.markdown(
    """
**질문**

> 10위권에 든 영화의 장르 구성은 어떠한가?
"""
)

genre_count = (
    df["장르"]
    .value_counts()
    .reset_index()
)

genre_count.columns = [
    "장르",
    "영화 수"
]

fig1 = px.pie(
    genre_count,
    names="장르",
    values="영화 수",
    hole=0.45
)

fig1.update_layout(
    title="TOP10 영화의 장르 구성",
    height=600
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

st.text_area(
    "이 그래프로 알 수 있는 것",
    value="장르별 영화 편수의 차이를 통해 TOP10 영화에서 어떤 장르가 많이 나타나는지 확인할 수 있다.",
    key="mandatory_answer_1"
)


# =========================================================
# 필수 그래프 2
# =========================================================

st.divider()

st.header("2. 장르 안에서 어떤 영화가 컸나 — 트리맵")

st.markdown(
    """
**질문**

> 장르 안에서 어떤 영화가 큰 흥행 규모를 차지하는가?
"""
)

fig2 = px.treemap(
    df,
    path=["장르", "movieNm"],
    values="total_audi",
    hover_name="movieNm"
)

fig2.update_layout(
    title="장르별 영화의 총 관객 규모",
    height=650
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.text_area(
    "이 그래프로 알 수 있는 것",
    value="같은 장르 안에서도 영화별 총 관객 규모에 큰 차이가 있으며 일부 영화가 높은 흥행을 차지한다.",
    key="mandatory_answer_2"
)

st.info(
    "도넛 그래프는 '영화 편수'를 기준으로 하지만, "
    "트리맵은 '총 관객 수'를 기준으로 영역의 크기를 결정한다."
)


# =========================================================
# 필수 그래프 3
# =========================================================

st.divider()

st.header("3. 총 관객 분포 — 히스토그램")

st.markdown(
    """
**질문**

> 영화 대부분은 관객이 몇 명쯤인가?
"""
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

st.write(
    f"전체 {len(df)}편 중 "
    f"{under_1m}편이 총 관객 100만 명 미만이다."
)

st.text_area(
    "이 그래프로 알 수 있는 것",
    value="많은 영화가 상대적으로 낮은 관객 구간에 몰려 있으며 소수의 대작 영화가 매우 높은 관객 수를 기록한다.",
    key="mandatory_answer_3"
)


# =========================================================
# 필수 그래프 4
# =========================================================

st.divider()

st.header("4. 스크린 수와 흥행 — 산점도")

st.markdown(
    """
**질문**

> 스크린을 많이 받은 영화가 관객도 많은가?
"""
)

fig4 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="장르",
    hover_name="movieNm",
    hover_data=[
        "first_scrn",
        "total_audi"
    ]
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

st.text_area(
    "이 그래프로 알 수 있는 것",
    value="개봉일에 많은 스크린을 확보한 영화가 높은 총 관객을 기록하는 경향이 있는지 확인할 수 있다.",
    key="mandatory_answer_4"
)


# =========================================================
# 5개의 새로운 연구 질문
# =========================================================

st.divider()

st.header("🔎 나만의 영화산업 연구 — 5개의 질문")

st.write(
    "다음 5개의 질문은 단순한 관객 수 비교가 아니라 "
    "영화의 배급 구조, 장기 흥행, 국가별 영화산업, "
    "초기 흥행과 장르의 관계를 분석하기 위한 질문이다."
)


# =========================================================
# 질문 1
# =========================================================

st.divider()

st.header("연구 질문 1")

st.markdown(
    """
### 역사적 흥행 구조

**오랜 기간 TOP10에 머문 영화일수록 총 관객 수가 많은가?**

영화의 장기적인 대중성을 TOP10 체류 기간과 총 관객의 관계를 통해 살펴본다.
"""
)

fig5 = px.scatter(
    df,
    x="days_in_top10",
    y="total_audi",
    color="장르",
    hover_name="movieNm",
    trendline="ols"
)

fig5.update_layout(
    title="TOP10 체류 기간과 총 관객의 관계",
    xaxis_title="TOP10에 머문 날수",
    yaxis_title="총 관객",
    height=650
)

st.plotly_chart(
    fig5,
    use_container_width=True
)

st.text_area(
    "이 그래프로 알 수 있는 것",
    value="TOP10에 오래 머문 영화와 총 관객 수 사이에 어떤 관계가 나타나는지 확인할 수 있다.",
    key="research_answer_1"
)


# =========================================================
# 질문 2
# =========================================================

st.divider()

st.header("연구 질문 2")

st.markdown(
    """
### 할리우드·볼리우드와 같은 국가별 영화산업 비교

**제작 국가에 따라 영화의 흥행 규모와 TOP10 체류 기간에 차이가 나타나는가?**

국가별 영화산업의 대중적 성과를 영화 데이터의 관객 규모와 체류 기간을 통해 비교한다.
"""
)

country_df = df.copy()

country_df["제작국가_표시"] = country_df["제작국가"]

# 영화가 적은 국가는 기타로 묶음
country_counts = country_df["제작국가"].value_counts()

country_df["국가그룹"] = country_df["제작국가"].apply(
    lambda x: x if country_counts.get(x, 0) >= 5 else "기타"
)

fig6 = px.box(
    country_df,
    x="국가그룹",
    y="total_audi",
    points="outliers",
    hover_name="movieNm"
)

fig6.update_layout(
    title="제작 국가별 총 관객 분포",
    xaxis_title="제작 국가",
    yaxis_title="총 관객",
    height=650
)

st.plotly_chart(
    fig6,
    use_container_width=True
)

st.text_area(
    "이 그래프로 알 수 있는 것",
    value="제작 국가에 따라 영화의 총 관객 분포와 흥행 규모가 어떻게 다른지 비교할 수 있다.",
    key="research_answer_2"
)


# =========================================================
# 질문 3
# =========================================================

st.divider()

st.header("연구 질문 3")

st.markdown(
    """
### 영화산업의 배급 구조

**개봉 첫날 확보한 스크린 수가 영화의 최종 흥행 규모와 어떤 관계가 있는가?**

개봉 초기의 배급 규모가 영화의 장기적인 흥행 성과와 어떤 관계를 갖는지 분석한다.
"""
)

fig7 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="제작국가",
    size="first_week_audi",
    size_max=40,
    hover_name="movieNm"
)

fig7.update_layout(
    title="초기 스크린 확보와 최종 흥행",
    xaxis_title="개봉일 스크린 수",
    yaxis_title="총 관객",
    height=700
)

st.plotly_chart(
    fig7,
    use_container_width=True
)

st.text_area(
    "이 그래프로 알 수 있는 것",
    value="개봉 초기 스크린 확보 규모와 최종 총 관객 사이의 관계를 국가별로 비교할 수 있다.",
    key="research_answer_3"
)


# =========================================================
# 질문 4
# =========================================================

st.divider()

st.header("연구 질문 4")

st.markdown(
    """
### 초기 흥행과 장기 흥행

**개봉 첫 주 관객 수가 많은 영화는 최종적으로도 높은 흥행을 기록하는가?**

초기 관객 동원력이 장기적인 흥행 성과와 연결되는지를 살펴본다.
"""
)

fig8 = px.scatter(
    df,
    x="first_week_audi",
    y="total_audi",
    color="장르",
    hover_name="movieNm",
    trendline="ols"
)

fig8.update_layout(
    title="첫 주 관객과 총 관객의 관계",
    xaxis_title="첫 주 관객",
    yaxis_title="총 관객",
    height=650
)

st.plotly_chart(
    fig8,
    use_container_width=True
)

st.text_area(
    "이 그래프로 알 수 있는 것",
    value="첫 주 관객이 많은 영화가 최종 총 관객에서도 높은 수치를 기록하는 경향이 있는지 확인할 수 있다.",
    key="research_answer_4"
)


# =========================================================
# 질문 5
# =========================================================

st.divider()

st.header("연구 질문 5")

st.markdown(
    """
### 장르와 대중성

**장르에 따라 영화의 흥행 규모와 관객 분포가 다르게 나타나는가?**

장르가 영화의 대중적 성과와 어떤 관계를 보이는지 통계적으로 비교한다.
"""
)

genre_big = df[
    df["장르"].isin(
        df["장르"].value_counts()[
            df["장르"].value_counts() >= 10
        ].index
    )
]

fig9 = px.box(
    genre_big,
    x="장르",
    y="total_audi",
    points="outliers",
    hover_name="movieNm"
)

fig9.update_layout(
    title="장르별 총 관객 분포 비교",
    xaxis_title="장르",
    yaxis_title="총 관객",
    height=700
)

st.plotly_chart(
    fig9,
    use_container_width=True
)

st.text_area(
    "이 그래프로 알 수 있는 것",
    value="장르별로 총 관객의 중앙값과 분포 범위가 달라지는지 비교할 수 있다.",
    key="research_answer_5"
)


# =========================================================
# 연구 질문 전체 정리
# =========================================================

st.divider()

st.header("📚 연구 질문 정리")

summary = pd.DataFrame(
    {
        "번호": [
            "1",
            "2",
            "3",
            "4",
            "5"
        ],
        "연구 분야": [
            "역사적 흥행 구조",
            "국가별 영화산업",
            "배급 구조",
            "초기·장기 흥행",
            "장르와 대중성"
        ],
        "핵심 변수": [
            "TOP10 체류 기간 ↔ 총 관객",
            "제작 국가 ↔ 총 관객",
            "스크린 수 ↔ 총 관객",
            "첫 주 관객 ↔ 총 관객",
            "장르 ↔ 총 관객"
        ],
        "그래프": [
            "산점도",
            "박스플롯",
            "버블",
            "산점도",
            "박스플롯"
        ]
    }
)

st.dataframe(
    summary,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# 데이터 확인
# =========================================================

st.divider()

with st.expander("📋 원본 데이터 확인"):

    display_df = df[
        [
            "movieNm",
            "장르",
            "제작국가",
            "first_scrn",
            "first_show",
            "first_week_audi",
            "total_audi",
            "days_in_top10"
        ]
    ].copy()

    display_df.columns = [
        "영화명",
        "장르",
        "제작 국가",
        "개봉일 스크린 수",
        "개봉일 상영 횟수",
        "첫 주 관객",
        "총 관객",
        "TOP10 체류 일수"
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# 최종 체크
# =========================================================

st.divider()

st.header("✅ 제출 전 최종 체크")

a = st.checkbox(
    "필수 4종 그래프를 완성했다."
)

b = st.checkbox(
    "필수 4종 그래프에 각각 분석 문장을 작성했다."
)

c = st.checkbox(
    "도넛과 트리맵의 기준 차이를 설명했다."
)

d = st.checkbox(
    "영화산업과 관련된 나만의 연구 질문 5개를 만들었다."
)

e = st.checkbox(
    "5개의 질문에 각각 적절한 그래프를 연결했다."
)

f = st.checkbox(
    "5개의 그래프에서 분석 결과를 한 문장씩 작성했다."
)

if all([a, b, c, d, e, f]):

    st.success(
        "🎉 모든 제출 조건을 완료했습니다!"
    )

else:

    count = sum(
        [a, b, c, d, e, f]
    )

    st.info(
        f"현재 {count}/6개의 제출 조건을 완료했습니다."
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "영화 데이터 그래프 도감 2 — 분포와 관계"
)

st.caption(
    "데이터 출처: 영화진흥위원회 KOBIS"
)
