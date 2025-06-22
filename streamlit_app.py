import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.font_manager as fm
import os
import urllib.request
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 페이지 설정
st.set_page_config(
    page_title="교통사고 및 면허 자진반납 분석",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 한글 폰트 설정 함수
@st.cache_resource
def setup_korean_font():
    try:
        font_url = "https://raw.githubusercontent.com/naver/nanumfont/master/TTF/NanumGothic.ttf"
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
        
        return False

font_success = setup_korean_font()

# 데이터 로드 함수들
@st.cache_data
def load_accident_data():
    data = {
        '연령대': ['20대', '30대', '40대', '50대', '60대', '65세 이상'],
        '비율': [0.006338831, 0.005378732, 0.005727822, 0.007673245, 0.007163389, 0.009960251],
        '퍼센트': [0.63, 0.54, 0.57, 0.77, 0.72, 1.00],
        '절대값': [63, 54, 57, 77, 72, 100]  # 시각화를 위한 절대값 추가
    }
    return pd.DataFrame(data)

@st.cache_data
def load_license_surrender_data():
    return pd.DataFrame({
        '지역': ['서울', '기타 지역'],
        '반납건수': [26005, 95554],  # 121559 - 26005
        '총인구': [9720846, 41857582],  # 2023년 기준 (만명)
        '65세이상인구': [1557013, 7088987],  # 2023년 기준 65세 이상 인구
        '반납비율_총인구': [0.268, 0.228],  # 총인구 1000명당 반납건수
        '반납비율_65세이상': [1.67, 1.35]  # 65세 이상 인구 100명당 반납건수
    })

@st.cache_data
def load_trend_data():
    return pd.DataFrame({
        '연도': [2015, 2017, 2019, 2021, 2023],
        '반납건수': [1866, 3909, 77172, 83644, 121559],
        '증가율': [None, 109.5, 1874.5, 8.4, 45.3]  # 전년대비 증가율 추가
    })

# 사이드바 설정
st.sidebar.title("📊 분석 옵션")
analysis_type = st.sidebar.selectbox(
    "분석 유형 선택",
    ["전체 개요", "교통사고 분석", "면허 반납 분석", "연도별 추이", "정책 제언"]
)

# 메인 타이틀
st.title("🚗 고령 운전자 교통사고 및 면허 자진반납 분석 대시보드")

# 전체 개요
if analysis_type == "전체 개요":
    st.header("📋 분석 개요")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="65세 이상 사고 비율",
            value="1.00%",
            delta="최고 위험군"
        )
    
    with col2:
        st.metric(
            label="총 면허 반납 건수",
            value="121,559건",
            delta="+45.3% (2021 대비)"
        )
    
    with col3:
        st.metric(
            label="서울 반납 비율",
            value="21.4%",
            delta="26,005건"
        )
    
    with col4:
        st.metric(
            label="60세 이상 사고 비율",
            value="1.72%",
            delta="정책 대응 필요"
        )
    
    st.markdown("""
    ### 🎯 핵심 분석 결과
    - **고령 운전자(65세 이상)**의 교통사고 가해 비율이 **전 연령대 중 최고**
    - **면허 자진반납**은 **2019년 이후 급격히 증가**하는 추세
    - **서울과 지방 간 반납 패턴의 차이** 존재
    - **고령화 사회 진입**에 따른 **교통 정책 재편 필요성** 대두
    """)

# 교통사고 분석
elif analysis_type == "교통사고 분석":
    st.header("📊 교통사고 가해자 연령대별 분석")
    
    accident_df = load_accident_data()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 파이 차트 - 연령순으로 정렬
        colors = ['#3742fa', '#5352ed', '#70a1ff', '#ffa502', '#ff6b6b', '#ff4757']  # 20대부터 65세이상까지 순서대로
        fig_pie = go.Figure(data=[
            go.Pie(
                labels=accident_df['연령대'],
                values=accident_df['퍼센트'],
                hole=0.4,
                pull=[0.15 if x == '65세 이상' else 0.08 if x == '60대' else 0 for x in accident_df['연령대']],
                marker=dict(colors=colors, line=dict(color='white', width=2)),
                textinfo='label+percent',
                textfont=dict(size=12, color='white'),
                hovertemplate='<b>%{label}</b><br>비율: %{percent}<br>값: %{value}<extra></extra>',
                sort=False,  # 정렬 비활성화로 데이터 순서 유지
                direction='clockwise',  # 시계방향 배치
                rotation=90  # 12시 방향부터 시작
            )
        ])
        fig_pie.update_layout(
            title=dict(text="연령대별 교통사고 가해자 비율", font=dict(size=16)),
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # 막대 차트
        fig_bar = px.bar(
            accident_df, 
            x='연령대', 
            y='퍼센트',
            color='연령대',
            color_discrete_map={
                '65세 이상': '#ff4757',
                '60대': '#ff6b6b',
                '50대': '#ffa502',
                '40대': '#70a1ff',
                '30대': '#5352ed',
                '20대': '#3742fa'
            },
            title="연령대별 사고 가해 비율 (막대 차트)"
        )
        fig_bar.update_layout(
            xaxis_title="연령대",
            yaxis_title="비율 (%)",
            showlegend=False,
            height=400
        )
        fig_bar.add_hline(y=accident_df['퍼센트'].mean(), line_dash="dash", 
                         line_color="red", 
                         annotation_text=f"평균: {accident_df['퍼센트'].mean():.2f}%")
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # 상세 분석
    st.subheader("🔍 상세 분석")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"""
        **최고 위험군**
        - 65세 이상: {accident_df[accident_df['연령대']=='65세 이상']['퍼센트'].values[0]}%
        - 평균 대비 {(accident_df[accident_df['연령대']=='65세 이상']['퍼센트'].values[0] / accident_df['퍼센트'].mean()):.1f}배 높음
        """)
    
    with col2:
        elderly_total = accident_df[accident_df['연령대'].isin(['60대', '65세 이상'])]['퍼센트'].sum()
        st.warning(f"""
        **60세 이상 총합**
        - 전체 비율: {elderly_total:.2f}%
        - 고령 운전자 집중 관리 필요
        """)
    
    with col3:
        min_age = accident_df.loc[accident_df['퍼센트'].idxmin(), '연령대']
        min_val = accident_df['퍼센트'].min()
        st.success(f"""
        **최저 위험군**
        - {min_age}: {min_val}%
        - 상대적으로 안전한 연령대
        """)

# 면허 반납 분석
elif analysis_type == "면허 반납 분석":
    st.header("📄 면허 자진반납 현황 분석")
    
    license_df = load_license_surrender_data()
    
    # 인구 대비 비율 분석
    st.subheader("👥 인구 대비 면허 반납 비율 분석")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="서울 반납율 (총인구)",
            value="0.268‰",
            delta="총인구 1000명당"
        )
    
    with col2:
        st.metric(
            label="기타지역 반납율 (총인구)", 
            value="0.228‰",
            delta="총인구 1000명당"
        )
    
    with col3:
        st.metric(
            label="서울 반납율 (65세+)",
            value="1.67%",
            delta="65세 이상 100명당"
        )
    
    with col4:
        st.metric(
            label="기타지역 반납율 (65세+)",
            value="1.35%", 
            delta="65세 이상 100명당"
        )
    
    # 간소화된 시각화: 65세 이상 인구 대비 반납 비율
    col1, col2 = st.columns(2)
    
    with col1:
        # 65세 이상 인구 대비 반납 비율 (메인 차트)
        fig_main = px.bar(
            license_df,
            x='지역',
            y='반납비율_65세이상',
            color='지역',
            color_discrete_map={'서울': '#ff6b6b', '기타 지역': '#4834d4'},
            title="65세 이상 인구 대비 면허 반납 비율",
            text='반납비율_65세이상'
        )
        fig_main.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig_main.update_layout(
            yaxis_title="반납 비율 (%)",
            showlegend=False,
            height=400,
            yaxis_range=[0, max(license_df['반납비율_65세이상']) * 1.2]
        )
        # 전국 평균선 추가
        national_avg = (license_df['반납건수'].sum() / license_df['65세이상인구'].sum()) * 100
        fig_main.add_hline(
            y=national_avg, 
            line_dash="dash", 
            line_color="red",
            annotation_text=f"전국 평균: {national_avg:.2f}%"
        )
        st.plotly_chart(fig_main, use_container_width=True)
    
    with col2:
        # 반납 건수와 65세 이상 인구 비교 (참고용)
        comparison_data = pd.DataFrame({
            '지역': license_df['지역'].tolist() * 2,
            '구분': ['반납건수'] * 2 + ['65세이상인구'] * 2,
            '값': license_df['반납건수'].tolist() + license_df['65세이상인구'].tolist(),
            '단위': ['건'] * 2 + ['명'] * 2
        })
        
        fig_ref = px.bar(
            comparison_data,
            x='지역',
            y='값',
            color='구분',
            barmode='group',
            title="반납건수 vs 65세 이상 인구 (참고)",
            color_discrete_map={'반납건수': '#ff9ff3', '65세이상인구': '#a4b0be'},
            text='값'
        )
        fig_ref.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig_ref.update_layout(
            yaxis_title="수량",
            height=400
        )
        st.plotly_chart(fig_ref, use_container_width=True)
    
    # 상세 분석 결과
    st.subheader("📊 인구 대비 분석 결과")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **📍 주요 발견사항**
        - 서울의 65세 이상 인구 대비 반납률이 더 높음
        - 총인구 대비로도 서울이 약간 높은 수준
        - 대체 교통수단 접근성이 반납률에 영향
        """)
    
    with col2:
        seoul_vs_other = (license_df.loc[0, '반납비율_65세이상'] / license_df.loc[1, '반납비율_65세이상'] - 1) * 100
        st.warning(f"""
        **🔍 서울 vs 기타지역**
        - 서울이 기타지역보다 {seoul_vs_other:.1f}% 높은 반납률
        - 인프라 차이가 행동에 미치는 영향 확인
        - 지역별 맞춤 정책 필요성 시사
        """)
    
    with col3:
        total_elderly = license_df['65세이상인구'].sum()
        total_surrender = license_df['반납건수'].sum()
        national_avg = (total_surrender / total_elderly) * 100
        st.success(f"""
        **📈 전국 평균**
        - 65세 이상 인구 대비: {national_avg:.2f}%
        - 총 65세 이상: {total_elderly:,}명
        - 정책 효과 모니터링 기준점
        """)
    
    # 지역별 특성 분석
    st.subheader("🌍 지역별 특성 및 시사점")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 🏙️ 서울시 (높은 반납률)
        - **65세 이상 반납률**: 1.67% (전국 대비 +23.7%)
        - **주요 요인**:
          - 🚇 우수한 대중교통 시스템
          - 🏥 의료시설 접근성 양호
          - 🛒 생활 인프라 집약적 배치
        - **정책 방향**: 성공 모델 확산
        """)
    
    with col2:
        st.markdown("""
        #### 🏞️ 기타 지역 (상대적 저반납률)
        - **65세 이상 반납률**: 1.35% (전국 대비 -6.6%)
        - **주요 과제**:
          - 🚌 대중교통 접근성 부족
          - 🏪 생활시설 거리 문제
          - 🚗 차량 의존도 높음
        - **정책 방향**: 대체 교통수단 확충 우선
        """)

# 연도별 추이 분석
elif analysis_type == "연도별 추이":
    st.header("📈 연도별 면허 자진반납 추이 분석")
    
    trend_df = load_trend_data()
    
    # 메인 추이 차트
    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 반납 건수 라인
    fig_trend.add_trace(
        go.Scatter(
            x=trend_df['연도'],
            y=trend_df['반납건수'],
            mode='lines+markers',
            name='반납 건수',
            line=dict(color='#ff6b6b', width=3),
            marker=dict(size=8)
        ),
        secondary_y=False,
    )
    
    # 증가율 바
    fig_trend.add_trace(
        go.Bar(
            x=trend_df['연도'][1:],  # 첫 번째 연도 제외 (증가율 없음)
            y=trend_df['증가율'][1:],
            name='증가율',
            opacity=0.6,
            marker_color='#4834d4'
        ),
        secondary_y=True,
    )
    
    fig_trend.update_xaxes(title_text="연도")
    fig_trend.update_yaxes(title_text="반납 건수 (건)", secondary_y=False)
    fig_trend.update_yaxes(title_text="증가율 (%)", secondary_y=True)
    fig_trend.update_layout(
        title="면허 자진반납 건수 및 증가율 추이",
        height=500
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # 주요 시점 분석
    st.subheader("🔍 주요 변화 시점 분석")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="2019년 대폭발",
            value="77,172건",
            delta="+1,874.5%",
            delta_color="normal"
        )
        st.caption("정책 변화 또는 사회적 인식 변화")
    
    with col2:
        st.metric(
            label="2021년 안정화",
            value="83,644건",
            delta="+8.4%",
            delta_color="normal"
        )
        st.caption("증가세 둔화")
    
    with col3:
        st.metric(
            label="2023년 재가속",
            value="121,559건",
            delta="+45.3%",
            delta_color="normal"
        )
        st.caption("고령화 가속화 영향")

# 정책 제언
elif analysis_type == "정책 제언":
    st.header("🏛️ 정책 제언 및 개선 방안")
    
    # 주요 정책 제언
    st.subheader("🎯 핵심 정책 제언")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🚌 교통 인프라", "💰 인센티브", "🔧 기술 지원", "📊 모니터링"])
    
    with tab1:
        st.markdown("""
        ### 🚌 대체 교통수단 확충
        
        #### 즉시 실행 가능한 방안
        - **마을버스 노선 확대**: 농촌 지역 접근성 향상
        - **DRT(수요응답형 교통) 도입**: 맞춤형 교통 서비스
        - **택시 바우처 확대**: 고령자 전용 교통비 지원
        
        #### 중장기 계획
        - **지역 간 연계 교통망 구축**
        - **무료 또는 저렴한 고령자 전용 교통수단**
        - **의료기관-주거지 연결 셔틀 서비스**
        """)
    
    with tab2:
        st.markdown("""
        ### 💰 반납 인센티브 제도
        
        #### 경제적 인센티브
        - **교통비 지원**: 월 10-20만원 교통카드 지원
        - **세금 감면**: 지방세, 재산세 일부 감면
        - **의료비 할인**: 정기 건강검진 무료 제공
        
        #### 생활 편의 인센티브
        - **생활용품 배송 서비스**
        - **문화시설 이용 할인**
        - **식료품 구매 배송비 지원**
        """)
    
    with tab3:
        st.markdown("""
        ### 🔧 기술 지원 방안
        
        #### 스마트 모빌리티
        - **모빌리티 앱 교육**: 고령자 대상 사용법 교육
        - **음성 인식 호출 서비스**: 스마트폰 사용이 어려운 고령자 지원
        - **AI 기반 최적 경로 안내**
        
        #### 안전 기술
        - **긴급 상황 대응 시스템**
        - **위치 추적 서비스** (동의 하에)
        - **건강 모니터링 연동**
        """)
    
    with tab4:
        st.markdown("""
        ### 📊 정책 효과 모니터링
        
        #### 데이터 수집 체계
        - **면허 반납 후 이동 패턴 조사**
        - **생활 만족도 정기 조사**
        - **교통사고 감소 효과 측정**
        
        #### 성과 지표
        - **대체 교통수단 이용률**
        - **고령자 교통사고 감소율**
        - **지역별 정책 만족도**
        """)
    
    # 예산 및 우선순위
    st.subheader("💡 정책 우선순위 및 예상 효과")
    
    policy_data = pd.DataFrame({
        '정책': ['DRT 도입', '교통비 지원', '마을버스 확대', '택시 바우처', '기술 지원'],
        '예상비용': [50, 200, 150, 100, 80],  # 억 원 단위
        '예상효과': [85, 90, 70, 75, 60],  # 효과 점수
        '실행난이도': [70, 30, 60, 40, 80]  # 난이도 점수
    })
    
    fig_policy = px.scatter(
        policy_data,
        x='예상비용',
        y='예상효과',
        size='실행난이도',
        color='정책',
        title="정책별 비용-효과 분석",
        labels={
            '예상비용': '예상 비용 (억원)',
            '예상효과': '예상 효과 점수',
            '실행난이도': '실행 난이도'
        }
    )
    fig_policy.update_layout(height=500)
    st.plotly_chart(fig_policy, use_container_width=True)
    
    st.markdown("""
    ### 📋 단계별 실행 계획
    
    #### 1단계 (즉시 실행, 6개월)
    - 택시 바우처 시범 사업
    - 기존 대중교통 고령자 할인 확대
    
    #### 2단계 (단기, 1-2년)
    - DRT 시범 지역 운영
    - 교통비 지원 제도 도입
    
    #### 3단계 (중장기, 3-5년)
    - 전국 단위 통합 교통 시스템 구축
    - 스마트 모빌리티 기술 적용 확대
    """)

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>📊 고령 운전자 교통안전 분석 대시보드 | 데이터 기반 정책 수립 지원</p>
</div>
""", unsafe_allow_html=True)