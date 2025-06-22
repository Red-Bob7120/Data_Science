import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title="연령별 교통사고 가해자 비율 분석",
    page_icon="🚗",
    layout="wide"
)

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 준비
@st.cache_data
def load_data():
    data = {
        '연령대': ['20대', '30대', '40대', '50대', '60대', '65세 이상'],
        '비율': [0.006338831, 0.005378732, 0.005727822, 0.007673245, 0.007163389, 0.009960251],
        '퍼센트': [0.63, 0.54, 0.57, 0.77, 0.72, 1.00]
    }
    return pd.DataFrame(data)

df = load_data()

# 타이틀 및 설명
st.title("🚗 연령별 교통사고 가해자 비율 분석 대시보드")
st.markdown("---")

# 개요 섹션
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="최고 위험 연령대",
        value="65세 이상",
        delta="1.00%"
    )

with col2:
    st.metric(
        label="최저 위험 연령대", 
        value="30대",
        delta="0.54%"
    )

with col3:
    st.metric(
        label="전체 평균",
        value=f"{df['퍼센트'].mean():.2f}%"
    )

with col4:
    st.metric(
        label="위험도 격차",
        value=f"{df['퍼센트'].max() - df['퍼센트'].min():.2f}%p"
    )

st.markdown("---")

# 차트 섹션
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 연령대별 사고 가해자 비율")
    
    # 막대 차트
    fig_bar, ax_bar = plt.subplots(figsize=(10, 6))
    bars = ax_bar.bar(df['연령대'], df['퍼센트'], color='red', alpha=0.7)
    
    # 막대 위에 값 표시
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax_bar.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{height:.2f}%', ha='center', va='bottom')
    
    ax_bar.set_title("연령대별 교통사고 가해자 비율 (%)", fontsize=14, pad=20)
    ax_bar.set_xlabel("연령대", fontsize=12)
    ax_bar.set_ylabel("비율 (%)", fontsize=12)
    ax_bar.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    st.pyplot(fig_bar)

with col2:
    st.subheader("🥧 연령대별 구성 비율")
    
    # 파이 차트
    fig_pie, ax_pie = plt.subplots(figsize=(8, 8))
    colors = plt.cm.Reds(np.linspace(0.3, 0.8, len(df)))
    
    wedges, texts, autotexts = ax_pie.pie(
        df['퍼센트'], 
        labels=df['연령대'],
        autopct='%1.2f%%',
        colors=colors,
        startangle=90
    )
    
    ax_pie.set_title("연령대별 교통사고 가해자 비율 분포", fontsize=14, pad=20)
    
    # 텍스트 스타일 개선
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    st.pyplot(fig_pie)

# 상세 데이터 테이블
st.markdown("---")
st.subheader("📋 상세 데이터")

# 데이터 테이블 스타일링
styled_df = df.copy()
styled_df['비율'] = styled_df['비율'].apply(lambda x: f"{x:.6f}")
styled_df['퍼센트'] = styled_df['퍼센트'].apply(lambda x: f"{x:.2f}%")

st.dataframe(
    styled_df,
    use_container_width=True,
    hide_index=True
)

# 분석 결과 섹션
st.markdown("---")
st.subheader("📈 주요 분석 결과")

col1, col2 = st.columns(2)

with col1:
    st.info("""
    **🔍 핵심 인사이트:**
    - 65세 이상 연령층이 가장 높은 사고 가해자 비율 (1.00%)
    - 30대가 가장 낮은 사고 가해자 비율 (0.54%)
    - 50대 이후 연령층에서 사고 비율이 증가하는 경향
    """)

with col2:
    st.warning("""
    **⚠️ 주의사항:**
    - 고령층의 교통안전 교육 강화 필요
    - 연령대별 맞춤형 안전 정책 수립 고려
    - 지속적인 모니터링과 분석 필요
    """)

# 필터링 기능
st.markdown("---")
st.subheader("🔍 데이터 필터링")

selected_ages = st.multiselect(
    "분석하고 싶은 연령대를 선택하세요:",
    df['연령대'].tolist(),
    default=df['연령대'].tolist()
)

if selected_ages:
    filtered_df = df[df['연령대'].isin(selected_ages)]
    
    # 필터링된 데이터 차트
    fig_filtered, ax_filtered = plt.subplots(figsize=(10, 5))
    
    ax_filtered.plot(filtered_df['연령대'], filtered_df['퍼센트'], 
                    marker='o', linewidth=3, markersize=8, 
                    color='red', markerfacecolor='darkred')
    
    # 포인트에 값 표시
    for i, (x, y) in enumerate(zip(filtered_df['연령대'], filtered_df['퍼센트'])):
        ax_filtered.annotate(f'{y:.2f}%', (x, y), 
                           textcoords="offset points", 
                           xytext=(0,10), ha='center')
    
    ax_filtered.set_title("선택된 연령대별 사고 가해자 비율 추이", fontsize=14, pad=20)
    ax_filtered.set_xlabel("연령대", fontsize=12)
    ax_filtered.set_ylabel("비율 (%)", fontsize=12)
    ax_filtered.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    st.pyplot(fig_filtered)

# 사이드바 정보
st.sidebar.header("📊 대시보드 정보")
st.sidebar.info("""
이 대시보드는 연령별 면허 소지자 대비 
교통사고 가해자 비율을 분석합니다.

**데이터 출처:** 업로드된 CSV 파일
**분석 기준:** 연령대별 사고 가해자 비율
""")

st.sidebar.header("🛠️ 기능")
st.sidebar.success("""
✅ 연령대별 비율 시각화
✅ 상세 데이터 테이블
✅ 주요 통계 지표
✅ 필터링 기능
✅ 분석 결과 요약
""")

# 푸터
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    🚗 교통안전 분석 대시보드 | 
    데이터 기반 의사결정을 위한 시각화 도구
    </div>
    """, 
    unsafe_allow_html=True
)