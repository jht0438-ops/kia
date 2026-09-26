import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="기아 원가경쟁력 진단", page_icon="🚗", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1450px;}
h1, h2, h3 {letter-spacing: -0.03em;}
div[data-testid="stMetric"] {
    background: #f7f7f8; border: 1px solid #e8e8ea; padding: 14px 16px;
    border-radius: 12px;
}
.small-note {color:#666; font-size:0.88rem;}
.insight {
    padding:16px 18px; border-radius:12px; background:#f7f7f8;
    border-left:5px solid #222; margin:10px 0 18px 0;
}
.warn {
    padding:14px 18px; border-radius:12px; background:#fff8e8;
    border-left:5px solid #e0a000; margin:10px 0 18px 0;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Data
# -----------------------------
cost = pd.DataFrame({
    "연도":[2023, 2024, 2025],
    "매출액":[99.8084, 107.4488, 114.1410],
    "영업이익":[11.6079, 12.6671, 9.0780],
    "영업이익률":[11.6, 11.8, 8.0],
    "매출원가율":[77.3, 76.9, 80.3],
})

material = pd.DataFrame({
    "원재료":["철","알루미늄","페인트","시너"],
    "2023":[153.1,37.9,14.0,3.0],
    "2024":[158.9,42.6,13.1,2.7],
    "2025":[160.2,8.5,12.8,2.9],
})
material["24→25 증감"] = material["2025"] - material["2024"]
material["24→25 증감률(%)"] = (material["2025"]/material["2024"]-1)*100

purchase = pd.DataFrame({
    "구분":["부품","원재료","기타"],
    "2024":[43.7773,4.6309,0.0776],
    "2025":[48.7286,4.5177,0.0524],
})
purchase["증감액"] = purchase["2025"]-purchase["2024"]
purchase["증감률(%)"] = (purchase["2025"]/purchase["2024"]-1)*100

bridge = pd.DataFrame({
    "요인":["2024 영업이익","판매량","가격","환율","미국 관세","인센티브","제품 구성","기타비용","2025 영업이익"],
    "금액":[12.6671,0.15,0.39,1.555,-3.093,-1.506,-0.460,-0.631,9.078]
})

# -----------------------------
# Header
# -----------------------------
st.title("기아 원가경쟁력 진단")
st.caption("공개자료 기반 | 생산 투입 → 구매구조 → 손익 → 외부비용을 연결한 재경 관점 분석")
st.markdown("""
<div class="insight">
<b>분석 질문</b><br>
2025년 차량 1대당 주요 원재료 사용량은 15.1% 감소했는데, 왜 매출원가율은 오히려 3.4%p 상승했을까?
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["① 핵심 진단","② 원재료 투입","③ 구매구조","④ 외부비용","⑤ 종합 결론","⑥ 분석 기준"])

# -----------------------------
# 1
# -----------------------------
with tabs[0]:
    st.subheader("수익성 이상징후부터 출발")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("2025 매출액","114.14조원","+6.2% YoY")
    c2.metric("2025 영업이익","9.08조원","-28.3% YoY")
    c3.metric("매출원가율","80.3%","+3.4%p YoY", delta_color="inverse")
    c4.metric("대당 주요 원재료","184.4kg","-15.1% YoY")

    left,right = st.columns([1.2,1])
    with left:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=cost["연도"].astype(str), y=cost["영업이익률"], name="영업이익률"))
        fig.add_trace(go.Scatter(x=cost["연도"].astype(str), y=cost["매출원가율"],
                                 name="매출원가율", mode="lines+markers", yaxis="y2"))
        fig.update_layout(title="영업이익률 vs 매출원가율",
                          yaxis=dict(title="영업이익률(%)"),
                          yaxis2=dict(title="매출원가율(%)",overlaying="y",side="right",range=[70,85]),
                          legend=dict(orientation="h"), height=430)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown("### 첫 번째 판단")
        st.markdown("""
        **원재료 사용량 감소만으로 원가경쟁력을 판단할 수 없다.**

        2025년에는 매출이 증가했지만 매출원가율과 영업이익률은 악화됐다.
        따라서 물리적 투입량을 원재료별로 분해한 뒤, 구매비용과 외부비용까지 연결해 확인한다.
        """)
        st.markdown("""
        <div class="warn">
        <b>주의</b><br>
        ‘대당 주요 원재료 -15.1%’를 곧바로 ‘제조원가 -15.1%’ 또는
        ‘생산효율 +15.1%’로 해석하지 않는다.
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# 2
# -----------------------------
with tabs[1]:
    st.subheader("15.1% 감소를 원재료별로 분해")
    c1,c2,c3 = st.columns(3)
    c1.metric("전체","217.3 → 184.4kg","-32.9kg")
    c2.metric("알루미늄","42.6 → 8.5kg","-80.0%")
    c3.metric("알루미늄 제외","174.7 → 175.9kg","+0.7%", delta_color="inverse")

    long = material.melt(id_vars="원재료", value_vars=["2023","2024","2025"],
                         var_name="연도", value_name="kg/대")
    fig = px.bar(long, x="연도", y="kg/대", color="원재료", barmode="stack",
                 title="차량 1대당 주요 원재료 사용량 분해")
    fig.update_layout(height=470, legend_title="")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(material.style.format({
        "2023":"{:.1f}","2024":"{:.1f}","2025":"{:.1f}",
        "24→25 증감":"{:+.1f}","24→25 증감률(%)":"{:+.1f}%"
    }), use_container_width=True, hide_index=True)

    st.markdown("""
    <div class="insight">
    <b>결론 ①</b><br>
    전체 -32.9kg보다 알루미늄 감소폭(-34.1kg)이 더 크다.
    철과 시너는 증가했고 페인트 감소는 작다. 따라서 15.1% 감소는
    전반적인 생산효율 개선이 아니라 <b>알루미늄 사용량의 구조적 변화</b>가 만든 결과다.<br><br>
    기아 지속가능경영보고서는 2025년 알루미늄 사용량 감소 배경으로
    <b>‘소재공장 합리화’</b>를 제시한다. 공개자료만으로 합리화의 세부 실행방식까지
    확정할 수 없으므로 외주화·공정폐쇄 등으로 단정하지 않는다.
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# 3
# -----------------------------
with tabs[2]:
    st.subheader("물리적 투입 감소가 실제 구매비용 감소로 이어졌는가?")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("원재료 구매액","4.52조원","-2.4%")
    c2.metric("부품 구매액","48.73조원","+11.3%", delta_color="inverse")
    c3.metric("총 구매액","53.30조원","+9.9%", delta_color="inverse")
    c4.metric("부품 비중","91.4%","+1.2%p", delta_color="inverse")

    long_p = purchase.melt(id_vars="구분", value_vars=["2024","2025"],
                           var_name="연도", value_name="구매액(조원)")
    fig = px.bar(long_p, x="구분", y="구매액(조원)", color="연도", barmode="group",
                 title="국내 공장 구매구조 변화")
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="insight">
    <b>결론 ②</b><br>
    원재료 구매액은 감소했지만 부품 구매액은 약 4.95조원 증가했다.
    따라서 소재공장 합리화와 알루미늄 직접 사용량 감소를 곧바로 전체 원가절감으로 볼 수 없다.
    공개자료는 ‘소재공장 합리화 → 부품 외부조달 증가’의 인과관계를 직접 입증하지 않으므로,
    프로그램은 이를 <b>비용구조 이동 가능성</b>으로 표시한다.
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# 4
# -----------------------------
with tabs[3]:
    st.subheader("공장 밖에서 발생한 비용 충격까지 확인")
    c1,c2,c3 = st.columns(3)
    c1.metric("미국 관세 영향","-3.09조원")
    c2.metric("실제 영업이익 감소","-3.59조원")
    c3.metric("관세 영향 규모","약 86%","실제 이익 감소액 대비")

    # Waterfall uses the official bridge factors as displayed figures.
    fig = go.Figure(go.Waterfall(
        name="영업이익 브리지",
        orientation="v",
        measure=["absolute","relative","relative","relative","relative","relative","relative","relative","total"],
        x=bridge["요인"],
        y=bridge["금액"],
        text=[f"{v:+.2f}" if i not in [0,8] else f"{v:.2f}" for i,v in enumerate(bridge["금액"])],
        textposition="outside",
        connector={"line":{"width":1}}
    ))
    fig.update_layout(title="2024 → 2025 영업이익 변동 요인 (조원)", height=500, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="warn">
    <b>86%의 의미</b><br>
    관세 영향 -3.09조원이 실제 영업이익 감소액 3.59조원의 약 86%에 해당한다는
    <b>규모 비교</b>다. ‘영업이익 감소의 86%가 관세 때문’이라는 기여율로 해석하지 않는다.
    가격·환율 등 상쇄요인이 동시에 존재하기 때문이다.
    </div>
    """, unsafe_allow_html=True)

    tariff_ex_op = 9.078 + 3.093
    tariff_ex_margin = tariff_ex_op / 114.141 * 100
    st.markdown(f"""
    관세 영향만 단순 가산한 참고 시나리오에서는 영업이익이 **약 {tariff_ex_op:.2f}조원**,
    영업이익률은 **약 {tariff_ex_margin:.1f}%**다. 이는 회사가 공시한 조정 영업이익이 아니라
    관세 영향액만 제거한 **단순 민감도 분석**이다.
    """)

# -----------------------------
# 5
# -----------------------------
with tabs[4]:
    st.subheader("재경 관점 최종 진단")
    st.markdown("""
    ### 숫자를 한 줄로 연결하면

    **매출 증가(+6.2%)**  
    → 그런데 **매출원가율 76.9% → 80.3%**  
    → 원재료 과다투입 여부 확인  
    → 주요 원재료 **217.3 → 184.4kg/대**  
    → 분해 결과 알루미늄 **42.6 → 8.5kg/대**가 감소의 핵심  
    → 보고서상 배경은 **소재공장 합리화**  
    → 구매구조 확인 결과 **원재료 -2.4%, 부품 +11.3%**  
    → 동시에 공식 IR상 **미국 관세 -3.09조원**의 영업이익 부담
    """)

    st.markdown("""
    <div class="insight">
    <b>최종 결론</b><br><br>
    원가경쟁력은 원재료 사용량 하나만 줄여서는 판단할 수 없다.
    생산방식 변화로 직접 투입하는 원재료가 감소하더라도 구매부품 등 다른 비용이 증가할 수 있으며,
    관세와 같은 외부비용도 최종 손익에 큰 영향을 줄 수 있다.<br><br>
    따라서 원가개선 담당자는 <b>생산 투입량 → 구매구조 → 외부비용 → 매출원가 → 영업이익</b>을
    연결해 비용의 이동과 최종 손익 효과를 확인해야 한다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 원가개선 담당자로서 추가 확인할 내부 데이터")
    st.markdown("""
    - 소재공장 합리화 전후의 공정별 직접재료비·가공비·구매부품비
    - 차종별 표준원가와 실제원가 차이, 원재료 사용량 및 스크랩률
    - 부품별 국내·해외 조달단가와 관세 포함 총조달원가
    - 생산량·가동률 변화에 따른 고정비 배부 효과
    - 원가개선 활동별 절감액이 실제 손익에 반영됐는지 여부
    """)

# -----------------------------
# 6
# -----------------------------
with tabs[5]:
    st.subheader("분석 기준과 해석 제한")
    st.markdown("""
    **사용한 공개자료**
    - 기아 사업보고서 및 반기보고서
    - 기아 2024·2025·2026 지속가능경영보고서
    - 기아 2025년 실적 IR 자료

    **해석 원칙**
    1. 차량당 주요 원재료 지표와 연결 재무제표의 범위가 다를 수 있어 직접적인 인과관계로 단정하지 않는다.
    2. 구매액은 당기 매출원가와 동일하지 않다. 재고 시점 차이가 존재할 수 있다.
    3. 소재공장 합리화의 세부 방식은 공개자료에서 확인되지 않아 외주화로 단정하지 않는다.
    4. 미국 관세 -3.09조원은 회사가 제시한 영업이익 영향이며, 86%는 실제 영업이익 감소액과의 규모 비교다.
    5. 프로그램의 목적은 내부 원가를 추정하는 것이 아니라 공개자료에서 이상징후를 찾고,
       원가 담당자가 추가 확인해야 할 데이터를 구조화하는 것이다.
    """)
