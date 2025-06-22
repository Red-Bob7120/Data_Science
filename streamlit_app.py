import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.font_manager as fm
import os
import urllib.request

# 페이지 설정
st.set_page_config(
    page_title="교통사고 및 면허 자진반납 분석",
    page_icon="🚗",
    layout="wide"
)

# 한글 폰트 설정 함수
@st.cache_resource
def setup_korean_font():
    """한글 폰트를 설정하는 함수"""
    try:
        font_url = "https://github.com/naver/nanumfont/raw/master/fonts/NanumGothic.ttf"
        font_path = "NanumGothic.ttf"
        
        if not os.path.exists(font_path):
            urllib.request.urlretrieve(font_url, font_path)
        
        fm.fontManager.addfont(font_path)
        plt.rcParams['font.family'] = 'NanumGothic'
        plt.rcParams['axes.unicode_minus'] = False
        return True
    except Exception as e:
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.unicode_minus'] = False
        st.warning(f"한글 폰트 설정 실패: {str(e)}")
        return False

# 폰트 설정 실행
font_success = setup_korean_font()

# 교통사고 데이터
@st.cache_data
def load_accident_data():
    """교통사고 연령별 가해자 비율 데이터"""
    data = {
        '연령대': ['20대', '30대', '40대', '50대', '60대', '65세 이상'],
        '비율': [0.006338831, 0.005378732, 0.005727822, 0.007673245, 0.007163389, 0.009960251],
        '퍼센트': [0.63, 0.54, 0.57, 0.77, 0.72, 1.00]
    }
    return pd.DataFrame(data)

# CSV 파일에서 면허 자진반납 데이터 로드
@st.cache_data
def load_license_return_data():
    """CSV 파일에서 면허 자진반납 데이터 로드"""
    try:
        # CSV 파일 읽기 (UTF-8 먼저 시도)
        df = pd.read_csv('data/경찰청_시도 경찰청별 고령운전자 자진반납 현황.csv', encoding='utf-8')
    except:
        try:
            # 인코딩으로 재시도
            df = pd.read_csv('data/경찰청_시도 경찰청별 고령운전자 자진반납 현황.csv', encoding='euc-kr')
        except Exception as e:
            st.error(f"CSV 파일을 읽을 수 없습니다: {str(e)}")
            st.stop()
    
    # 컬럼명 정리
    df.columns = df.columns.str.strip()
    
    # 2023년 데이터 추출 및 정리
    license_data = {
        '지역': df['지방청'].tolist(),
        '65세_이상': df['2023 65세이상'].tolist(),
        '전체': df['2023 전체'].tolist()
    }
    
    result_df = pd.DataFrame(license_data)
    result_df['자진반납률'] = (result_df['65세_이상'] / result_df['전체'] * 100).round(2)
    
    return result_df

# 연도별 추이 데이터 (CSV에서 추출)
@st.cache_data
def load_yearly_trend_data():
    """CSV 파일에서 연도별 추이 데이터 생성"""
    try:
        # CSV 파일 읽기
        df = pd.read_csv('data/경찰청_시도 경찰청별 고령운전자 자진반납 현황.csv', encoding='utf-8')
    except:
        try:
            df = pd.read_csv('data/경찰청_시도 경찰청별 고령운전자 자진반납 현황.csv', encoding='cp949')
        except Exception as e:
            st.error(f"CSV 파일을 읽을 수 없습니다: {str(e)}")
            st.stop()
    
    # 연도별 전국 합계 계산
    years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
    yearly_data = []
    
    for year in years:
        # 컬럼명 패턴 처리 (2023년은 다른 형식)
        if year == 2023:
            elderly_col = f'{year} 65세이상'
        else:
            elderly_col = f'{year} 65세 이상'
        total_col = f'{year} 전체'
        
        if elderly_col in df.columns and total_col in df.columns:
            elderly_sum = df[elderly_col].sum()
            total_sum = df[total_col].sum()
            rate = (elderly_sum / total_sum * 100) if total_sum > 0 else 0
            
            yearly_data.append({
                '연도': year,
                '65세_이상': elderly_sum,
                '전체': total_sum,
                '자진반납률': round(rate, 2)
            })
    
    return pd.DataFrame(yearly_data)

# 데이터 로드
accident_df = load_accident_data()
license_df = load_license_return_data()
yearly_df = load_yearly_trend_data()

# 메인 타이틀
st.title("🚗 교통사고 및 면허 자진반납 종합 분석 대시보드")
st.markdown("---")

# 전체 개요 섹션
st.header("📊 주요 지표 요약")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📈 교통사고 최고위험 연령대",
        value="65세 이상",
        delta="1.00%"
    )

with col2:
    st.metric(
        label="🔄 2023년 전국 자진반납",
        value=f"{yearly_df['전체'].iloc[-1]:,}건",
        delta=f"+{yearly_df['전체'].iloc[-1] - yearly_df['전체'].iloc[-2]:,}건"
    )

with col3:
    st.metric(
        label="👥 65세 이상 자진반납률",
        value=f"{yearly_df['자진반납률'].iloc[-1]:.2f}%",
        delta=f"{yearly_df['자진반납률'].iloc[-1] - yearly_df['자진반납률'].iloc[-2]:+.2f}%p"
    )

with col4:
    st.metric(
        label="🏆 최고 자진반납 지역",
        value=license_df.loc[license_df['전체'].idxmax(), '지역'],
        delta=f"{license_df['전체'].max():,}건"
    )

# 탭 생성
tab1, tab2, tab3, tab4 = st.tabs(["📊 교통사고 분석", "🔄 면허 자진반납 현황", "📈 연도별 추이", "🗂️ 데이터 테이블"])

# 탭 1: 교통사고 분석
with tab1:
    st.header("🚨 연령별 교통사고 가해자 비율 분석")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 연령대별 사고 가해자 비율")
        
        fig_bar, ax_bar = plt.subplots(figsize=(10, 6))
        colors = ['#ff4757' if x == accident_df['퍼센트'].max() else '#3742fa' for x in accident_df['퍼센트']]
        bars = ax_bar.bar(accident_df['연령대'], accident_df['퍼센트'], color=colors, alpha=0.8)
        
        # 막대 위에 값 표시
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax_bar.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                       f'{height:.2f}%', ha='center', va='bottom', fontweight='bold')
        
        ax_bar.set_title("연령대별 교통사고 가해자 비율", fontsize=14, pad=20)
        ax_bar.set_xlabel("연령대", fontsize=12)
        ax_bar.set_ylabel("비율 (%)", fontsize=12)
        ax_bar.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        st.pyplot(fig_bar)
    
    with col2:
        st.subheader("🥧 연령대별 사고 비율 분포")
        
        fig_pie, ax_pie = plt.subplots(figsize=(8, 8))
        colors = plt.cm.Set3(np.linspace(0, 1, len(accident_df)))
        
        wedges, texts, autotexts = ax_pie.pie(
            accident_df['퍼센트'], 
            labels=accident_df['연령대'],
            autopct='%1.2f%%',
            colors=colors,
            startangle=90,
            explode=[0.1 if x == accident_df['퍼센트'].max() else 0 for x in accident_df['퍼센트']]
        )
        
        ax_pie.set_title("연령대별 교통사고 가해자 비율 분포", fontsize=14, pad=20)
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        st.pyplot(fig_pie)
    
    # 분석 결과
    st.info("""
    **🔍 교통사고 분석 결과:**
    - **65세 이상**: 1.00% (최고 위험군)
    - **30대**: 0.54% (최저 위험군)
    - **50대 이후**: 연령 증가에 따른 사고 비율 상승 경향
    - **위험도 격차**: 0.46%p (65세 이상 vs 30대)
    """)

# 탭 2: 면허 자진반납 현황
with tab2:
    st.header("🔄 2023년 지역별 면허 자진반납 현황")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏙️ 지역별 자진반납 건수 TOP 10")
        
        # 상위 10개 지역
        top_10 = license_df.nlargest(10, '전체')
        
        fig_bar, ax_bar = plt.subplots(figsize=(12, 8))
        
        x = np.arange(len(top_10))
        width = 0.35
        
        bars1 = ax_bar.bar(x - width/2, top_10['65세_이상'], width, 
                          label='65세 이상', color='#ff6b6b', alpha=0.8)
        bars2 = ax_bar.bar(x + width/2, top_10['전체'], width, 
                          label='전체', color='#4ecdc4', alpha=0.8)
        
        ax_bar.set_title("지역별 면허 자진반납 건수 TOP 10", fontsize=14, pad=20)
        ax_bar.set_xlabel("지역", fontsize=12)
        ax_bar.set_ylabel("건수", fontsize=12)
        ax_bar.set_xticks(x)
        ax_bar.set_xticklabels(top_10['지역'], rotation=45, ha='right')
        ax_bar.legend()
        ax_bar.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        st.pyplot(fig_bar)
    
    with col2:
        st.subheader("📊 지역별 자진반납률 순위")
        
        # 자진반납률 기준 정렬
        sorted_rate_df = license_df.sort_values('자진반납률', ascending=True)
        
        fig_rate, ax_rate = plt.subplots(figsize=(10, 10))
        
        colors = ['#ff9f43' if rate >= 95 else '#70a1ff' for rate in sorted_rate_df['자진반납률']]
        bars = ax_rate.barh(range(len(sorted_rate_df)), sorted_rate_df['자진반납률'], color=colors, alpha=0.8)
        
        # 막대 끝에 값 표시
        for i, (bar, rate) in enumerate(zip(bars, sorted_rate_df['자진반납률'])):
            width = bar.get_width()
            ax_rate.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                        f'{rate:.2f}%', ha='left', va='center', fontweight='bold')
        
        ax_rate.set_title("지역별 면허 자진반납률", fontsize=14, pad=20)
        ax_rate.set_xlabel("자진반납률 (%)", fontsize=12)
        ax_rate.set_yticks(range(len(sorted_rate_df)))
        ax_rate.set_yticklabels(sorted_rate_df['지역'])
        ax_rate.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        st.pyplot(fig_rate)

# 탭 3: 연도별 추이
with tab3:
    st.header("📈 면허 자진반납 연도별 추이 분석")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 연도별 자진반납 건수 추이")
        
        fig_trend, ax_trend = plt.subplots(figsize=(12, 8))
        
        ax_trend.plot(yearly_df['연도'], yearly_df['전체'], marker='o', 
                     linewidth=4, markersize=10, label='전체', color='#4ecdc4')
        ax_trend.plot(yearly_df['연도'], yearly_df['65세_이상'], marker='s', 
                     linewidth=4, markersize=10, label='65세 이상', color='#ff6b6b')
        
        # 데이터 포인트에 값 표시
        for i, row in yearly_df.iterrows():
            if row['연도'] in [2019, 2023]:  # 주요 연도만 표시
                ax_trend.annotate(f"{row['전체']:,}", 
                                (row['연도'], row['전체']), 
                                textcoords="offset points", xytext=(0,10), ha='center')
        
        ax_trend.set_title("연도별 면허 자진반납 건수 추이", fontsize=16, pad=20)
        ax_trend.set_xlabel("연도", fontsize=12)
        ax_trend.set_ylabel("건수", fontsize=12)
        ax_trend.legend(fontsize=12)
        ax_trend.grid(True, alpha=0.3)
        
        # y축 포맷팅
        ax_trend.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
        
        plt.tight_layout()
        st.pyplot(fig_trend)
    
    with col2:
        st.subheader("📊 연도별 자진반납률 변화")
        
        fig_rate_trend, ax_rate_trend = plt.subplots(figsize=(12, 8))
        
        colors = ['#ff9f43' if year >= 2019 else '#70a1ff' for year in yearly_df['연도']]
        bars = ax_rate_trend.bar(yearly_df['연도'], yearly_df['자진반납률'], 
                                color=colors, alpha=0.8)
        
        # 막대 위에 값 표시
        for i, (bar, rate) in enumerate(zip(bars, yearly_df['자진반납률'])):
            height = bar.get_height()
            ax_rate_trend.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                              f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        ax_rate_trend.set_title("연도별 면허 자진반납률 변화", fontsize=16, pad=20)
        ax_rate_trend.set_xlabel("연도", fontsize=12)
        ax_rate_trend.set_ylabel("자진반납률 (%)", fontsize=12)
        ax_rate_trend.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        st.pyplot(fig_rate_trend)
    
    # 추이 분석 결과
    col1, col2 = st.columns(2)
    
    with col1:
        st.success(f"""
        **📈 주요 증가 구간 (2018→2019):**
        - 전체: {yearly_df[yearly_df['연도']==2018]['전체'].iloc[0]:,} → {yearly_df[yearly_df['연도']==2019]['전체'].iloc[0]:,}건
        - 증가율: {((yearly_df[yearly_df['연도']==2019]['전체'].iloc[0] / yearly_df[yearly_df['연도']==2018]['전체'].iloc[0] - 1) * 100):.1f}%
        """)
    
    with col2:
        st.info(f"""
        **📊 최근 현황 (2023년):**
        - 전체 자진반납: {yearly_df['전체'].iloc[-1]:,}건
        - 65세 이상 비율: {yearly_df['자진반납률'].iloc[-1]:.2f}%
        - 전년 대비: {yearly_df['전체'].iloc[-1] - yearly_df['전체'].iloc[-2]:+,}건
        """)

# 탭 4: 데이터 테이블
with tab4:
    st.header("🗂️ 상세 데이터 테이블")
    
    tab4_1, tab4_2, tab4_3 = st.tabs(["교통사고 데이터", "지역별 자진반납", "연도별 추이"])
    
    with tab4_1:
        st.subheader("📊 교통사고 연령별 가해자 비율")
        st.dataframe(
            accident_df.style.format({'비율': '{:.6f}', '퍼센트': '{:.2f}%'}),
            use_container_width=True
        )
    
    with tab4_2:
        st.subheader("🔄 2023년 지역별 면허 자진반납 현황")
        display_df = license_df.copy()
        display_df = display_df.sort_values('전체', ascending=False)
        
        st.dataframe(
            display_df.style.format({
                '65세_이상': '{:,}',
                '전체': '{:,}',
                '자진반납률': '{:.2f}%'
            }),
            use_container_width=True
        )
    
    with tab4_3:
        st.subheader("📈 연도별 면허 자진반납 추이")
        st.dataframe(
            yearly_df.style.format({
                '65세_이상': '{:,}',
                '전체': '{:,}',
                '자진반납률': '{:.2f}%'
            }),
            use_container_width=True
        )

# 종합 분석 결과
st.markdown("---")
st.header("📈 종합 분석 결과 및 정책 제언")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🔍 주요 발견사항")
    st.markdown("""
    **교통사고 분석:**
    - 65세 이상 연령층의 사고 가해자 비율이 가장 높음 (1.00%)
    - 30대가 가장 안전한 연령층 (0.54%)
    - 50대 이후 연령 증가에 따른 위험도 상승 추세
    
    **면허 자진반납 분석:**
    - 2019년 이후 급격한 증가 (약 9배 증가)
    - 65세 이상이 전체 자진반납의 99% 이상 차지
    - 지역별 편차 존재 (서울, 경기 지역 높은 비율)
    """)

with col2:
    st.subheader("📋 정책 제언")
    st.markdown("""
    **단기 정책:**
    - 고령 운전자 대상 안전 교육 강화
    - 면허 자진반납 인센티브 확대
    - 지역별 맞춤형 홍보 전략 수립
    
    **장기 정책:**
    - 고령 친화적 교통 인프라 구축
    - 대중교통 접근성 개선
    - 자율주행 기술 도입 준비
    - 정기적 적성검사 강화
    """)

# 경고 및 참고사항
st.warning("""
⚠️ **데이터 해석 시 주의사항:**
- 교통사고 데이터는 연령별 인구 대비 비율이며, 절대 건수가 아닙니다.
- 면허 자진반납 증가는 제도 개선 및 사회적 인식 변화의 결과일 수 있습니다.
- 지역별 차이는 인구 구조, 교통 환경 등 다양한 요인이 복합적으로 작용한 결과입니다.
""")

# 사이드바 정보
st.sidebar.header("📊 대시보드 정보")
st.sidebar.info(f"""
**데이터 현황:**
- 교통사고: 연령별 가해자 비율 데이터
- 면허 자진반납: 경찰청 공식 통계 (2015-2023)
- 분석 기준: 2023년 최신 데이터

**포함 지역:** {len(license_df)}개 시도
**분석 기간:** 2015-2023년 (9년간)
""")

st.sidebar.header("🛠️ 주요 기능")
st.sidebar.success("""
✅ 실제 CSV 데이터 활용
✅ 연령별 교통사고 위험도 분석
✅ 지역별 자진반납 현황 비교
✅ 연도별 추이 분석
✅ 상세 데이터 테이블 제공
✅ 정책 제언 포함
""")

# 푸터
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 12px;'>
    🚗 교통안전 종합 분석 대시보드 v3.0 | 
    경찰청 공식 통계 기반 분석 도구<br>
    데이터 출처: 경찰청 교통사고 통계, 고령운전자 자진반납 현황
    </div>
    """, 
    unsafe_allow_html=True
)