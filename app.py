import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="기아 원가차이 분석 도구", page_icon="🚗", layout="wide")

st.markdown("""
<style>
.block-container{padding-top:1.4rem;max-width:1450px}
h1,h2,h3{letter-spacing:-.03em}
div[data-testid="stMetric"]{background:#f7f7f8;border:1px solid #e7e7ea;padding:14px;border-radius:12px}
.box{padding:16px 18px;border-radius:12px;background:#f7f7f8;border-left:5px solid #222;margin:10px 0 18px}
.note{padding:14px 18px;border-radius:12px;background:#fff8e8;border-left:5px solid #e0a000;margin:10px 0 18px}
.real{padding:14px 18px;border-radius:12px;background:#eef7ff;border-left:5px solid #3578c8;margin:10px 0 18px}
</style>
""", unsafe_allow_html=True)

st.title("기아 원가차이 분석 도구")
st.caption("관리회계 표준원가 차이분석을 자동차 제조 원가관리 업무에 적용")

st.markdown("""
<div class="note"><b>중요 — 데이터 사용 원칙</b><br>
이 프로그램은 기아의 비공개 표준원가·실제원가·표준투입량·실제투입량을 임의로 추정하지 않습니다.
기아에서 공개한 수치는 <b>공개자료</b> 탭에만 표시하며, 가격차이·수량차이·임률차이·능률차이는
<b>사용자가 직접 입력한 값</b>으로 계산합니다. 입력창의 초기값은 모두 0이며 기아의 실제 수치를 의미하지 않습니다.
</div>
""", unsafe_allow_html=True)

with st.expander("📘 처음 사용하는 분을 위한 사용법", expanded=True):
    st.markdown("""
**이 프로그램의 목적**은 원가가 계획과 달라졌을 때 단순히 증감액을 보는 것이 아니라,
그 차이를 **가격·수량·임률·능률**로 나누어 원인을 찾는 것입니다.

1. **① 공개자료**에서 실제로 공개된 기아의 원재료 사용량과 손익 흐름을 확인합니다.
2. **② 재료원가 차이분석**에서 분석하려는 품목의 표준단가·실제단가·표준수량·실제수량을 직접 입력합니다.
3. 프로그램이 **가격차이와 수량차이**를 자동 계산합니다.
4. **③ 노무원가 차이분석**에서 표준임률·실제임률·표준시간·실제시간을 입력하면 **임률차이와 능률차이**를 계산합니다.
5. **④ 종합진단**에서 재료비와 노무비 차이를 함께 보고 어떤 요인을 먼저 확인해야 하는지 판단합니다.
6. **⑤ 손익 연결**에서 입력한 생산량을 기준으로 차량당 차이가 전체 제조원가에 미치는 영향을 계산합니다.

**해석 원칙**
- 가격차이 불리 → 구매단가·계약조건·원재료 가격 등 확인
- 수량차이 불리 → 실제 투입량·스크랩·폐기·불량·재작업 등 확인
- 임률차이 불리 → 인력구성·시간당 인건비 등 확인
- 능률차이 불리 → 작업시간·라인 병목·설비정지·재작업 등 확인

계산 결과는 **사용자가 입력한 값에 대한 분석 결과**일 뿐 기아의 실제 원가차이가 아닙니다.
""")

# -----------------------------
# Confirmed public Kia data only
# -----------------------------
public_raw = pd.DataFrame({
    "연도":[2023, 2024, 2025],
    "주요 원재료 총 사용량(ton)":[281528.8, 279539.1, 246167.0],
    "사용 집약도(kg/대)":[208.1, 217.3, 184.4]
})

public_fin = pd.DataFrame({
    "연도":[2023, 2024, 2025],
    "매출액(십억원)":[99808, 107449, 114141],
    "영업이익(십억원)":[11608, 12667, 9078]
})
public_fin["영업이익률(%)"] = public_fin["영업이익(십억원)"] / public_fin["매출액(십억원)"] * 100

# session defaults: user input only, no invented Kia figures
for k, v in {
    "mat_output":0.0, "sp":0.0, "ap":0.0, "sq":0.0, "aq":0.0,
    "lab_output":0.0, "sr":0.0, "ar":0.0, "sh":0.0, "ah":0.0
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

tabs = st.tabs([
    "① 공개자료",
    "② 재료원가 차이분석",
    "③ 노무원가 차이분석",
    "④ 종합진단",
    "⑤ 손익 연결",
    "⑥ 분석 기준"
])

with tabs[0]:
    st.subheader("실제로 확인 가능한 기아 공개자료")
    st.markdown("""
<div class="real"><b>공개자료와 내부 원가 데이터를 분리했습니다.</b><br>
아래 수치는 기아가 공개한 전사·국내 범위의 자료입니다. 공장별 표준원가나 실제원가를 의미하지 않습니다.
따라서 아래 자료만으로 가격차이·수량차이·능률차이를 계산하지 않습니다.
</div>
""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 국내 주요 원재료")
        st.dataframe(public_raw, hide_index=True, use_container_width=True)
        fig = px.line(public_raw, x="연도", y="사용 집약도(kg/대)", markers=True,
                      title="주요 원재료 사용 집약도")
        st.plotly_chart(fig, use_container_width=True)
        change = (184.4 / 217.3 - 1) * 100
        st.info(f"2024→2025 주요 원재료 사용 집약도 변화: {change:.1f}%")
        st.caption("범위: 국내 / 주요 원재료: 철, 시너, 페인트, 알루미늄")

    with c2:
        st.markdown("#### 연결 손익")
        st.dataframe(public_fin.style.format({
            "매출액(십억원)":"{:,.0f}",
            "영업이익(십억원)":"{:,.0f}",
            "영업이익률(%)":"{:.1f}%"
        }), hide_index=True, use_container_width=True)
        fig2 = px.line(public_fin, x="연도", y="영업이익률(%)", markers=True,
                       title="연결 영업이익률")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
<div class="box"><b>여기서 생긴 질문</b><br>
2025년 국내 주요 원재료 사용 집약도는 감소했지만, 이것만으로 제조원가가 개선됐다고 결론 내릴 수 없습니다.
원가관리 실무에서는 실제원가가 계획과 달라졌다면 <b>단가 때문인지, 투입량 때문인지, 작업시간 때문인지</b>
추가 내부 데이터로 구분해야 합니다. 다음 탭은 그 분석 방법을 계산 도구로 구현했습니다.
</div>
""", unsafe_allow_html=True)

with tabs[1]:
    st.subheader("재료원가: 가격차이와 수량차이")
    st.caption("아래 값은 사용자가 직접 입력합니다. 기아 실제 데이터가 아닙니다.")

    c1, c2, c3 = st.columns(3)
    with c1:
        mat_output = st.number_input("실제 생산량(대)", min_value=0.0, value=st.session_state.mat_output,
                                     step=1000.0, key="mat_output_input")
        st.session_state.mat_output = mat_output
    with c2:
        sp = st.number_input("표준단가(원/단위)", min_value=0.0, value=st.session_state.sp,
                             step=100.0, key="sp_input")
        st.session_state.sp = sp
        ap = st.number_input("실제단가(원/단위)", min_value=0.0, value=st.session_state.ap,
                             step=100.0, key="ap_input")
        st.session_state.ap = ap
    with c3:
        sq_per = st.number_input("표준투입량(단위/대)", min_value=0.0, value=st.session_state.sq,
                                 step=0.1, key="sq_input")
        st.session_state.sq = sq_per
        aq_total = st.number_input("실제 총투입량(단위)", min_value=0.0, value=st.session_state.aq,
                                   step=1000.0, key="aq_input")
        st.session_state.aq = aq_total

    sq_allowed = sq_per * mat_output
    standard_cost = sp * sq_allowed
    actual_cost = ap * aq_total
    price_var = (ap - sp) * aq_total
    qty_var = (aq_total - sq_allowed) * sp
    total_var = actual_cost - standard_cost

    st.markdown("#### 계산 결과")
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("표준허용수량", f"{sq_allowed:,.1f}")
    m2.metric("가격차이", f"{price_var/100_000_000:,.2f}억원")
    m3.metric("수량차이", f"{qty_var/100_000_000:,.2f}억원")
    m4.metric("총 재료원가 차이", f"{total_var/100_000_000:,.2f}억원")

    if mat_output == 0 or sp == 0 or ap == 0 or sq_per == 0 or aq_total == 0:
        st.warning("분석할 실제 값을 직접 입력하면 결과가 계산됩니다. 초기값 0은 기아의 실제 수치가 아닙니다.")
    else:
        rows = pd.DataFrame({
            "구분":["가격차이","수량차이"],
            "금액(억원)":[price_var/1e8, qty_var/1e8],
            "판정":["불리" if price_var > 0 else "유리" if price_var < 0 else "차이 없음",
                   "불리" if qty_var > 0 else "유리" if qty_var < 0 else "차이 없음"]
        })
        st.dataframe(rows.style.format({"금액(억원)":"{:+,.2f}"}), hide_index=True, use_container_width=True)

        if price_var > 0:
            st.write("• 가격차이가 불리합니다 → 구매단가·계약조건·원재료 가격 변동 등을 확인합니다.")
        if qty_var > 0:
            st.write("• 수량차이가 불리합니다 → 실제 투입량·스크랩·폐기·불량·재작업 등을 확인합니다.")
        if price_var <= 0 and qty_var <= 0:
            st.write("• 입력값 기준 가격·수량 측면에서 불리한 차이가 없습니다.")

with tabs[2]:
    st.subheader("노무원가: 임률차이와 능률차이")
    st.caption("아래 값 역시 사용자가 직접 입력합니다. 기아 실제 데이터가 아닙니다.")

    c1, c2, c3 = st.columns(3)
    with c1:
        lab_output = st.number_input("실제 생산량(대) ", min_value=0.0, value=st.session_state.lab_output,
                                     step=1000.0, key="lab_output_input")
        st.session_state.lab_output = lab_output
    with c2:
        sr = st.number_input("표준임률(원/시간)", min_value=0.0, value=st.session_state.sr,
                             step=100.0, key="sr_input")
        st.session_state.sr = sr
        ar = st.number_input("실제임률(원/시간)", min_value=0.0, value=st.session_state.ar,
                             step=100.0, key="ar_input")
        st.session_state.ar = ar
    with c3:
        sh_per = st.number_input("표준작업시간(시간/대)", min_value=0.0, value=st.session_state.sh,
                                 step=0.1, key="sh_input")
        st.session_state.sh = sh_per
        ah_total = st.number_input("실제 총작업시간(시간)", min_value=0.0, value=st.session_state.ah,
                                   step=1000.0, key="ah_input")
        st.session_state.ah = ah_total

    sh_allowed = sh_per * lab_output
    std_labor = sr * sh_allowed
    act_labor = ar * ah_total
    rate_var = (ar - sr) * ah_total
    eff_var = (ah_total - sh_allowed) * sr
    labor_total_var = act_labor - std_labor

    st.markdown("#### 계산 결과")
    l1,l2,l3,l4 = st.columns(4)
    l1.metric("표준허용시간", f"{sh_allowed:,.1f}시간")
    l2.metric("임률차이", f"{rate_var/100_000_000:,.2f}억원")
    l3.metric("능률차이", f"{eff_var/100_000_000:,.2f}억원")
    l4.metric("총 노무원가 차이", f"{labor_total_var/100_000_000:,.2f}억원")

    if lab_output == 0 or sr == 0 or ar == 0 or sh_per == 0 or ah_total == 0:
        st.warning("분석할 실제 값을 직접 입력하면 결과가 계산됩니다.")
    else:
        if rate_var > 0:
            st.write("• 임률차이가 불리합니다 → 인력구성·시간당 인건비 등의 변화를 확인합니다.")
        if eff_var > 0:
            st.write("• 능률차이가 불리합니다 → 작업시간·병목·설비정지·재작업 등의 원인을 확인합니다.")
        if rate_var <= 0 and eff_var <= 0:
            st.write("• 입력값 기준 임률·능률 측면에서 불리한 차이가 없습니다.")

with tabs[3]:
    st.subheader("재료·노무 차이를 한 번에 확인")
    diag = pd.DataFrame({
        "차이요인":["재료 가격차이","재료 수량차이","노무 임률차이","노무 능률차이"],
        "금액(억원)":[price_var/1e8, qty_var/1e8, rate_var/1e8, eff_var/1e8]
    })
    fig3 = px.bar(diag, x="차이요인", y="금액(억원)", text_auto=".2f",
                  title="사용자 입력값 기준 원가차이")
    st.plotly_chart(fig3, use_container_width=True)
    st.dataframe(diag.style.format({"금액(억원)":"{:+,.2f}"}), hide_index=True, use_container_width=True)

    if diag["금액(억원)"].abs().sum() == 0:
        st.info("②·③ 탭에 데이터를 입력하면 여기에서 차이요인을 비교할 수 있습니다.")
    else:
        worst = diag.loc[diag["금액(억원)"].idxmax()]
        if worst["금액(억원)"] > 0:
            st.markdown(f"""
<div class="box"><b>우선 확인할 항목</b><br>
현재 입력값에서는 <b>{worst['차이요인']}</b>이 가장 큰 불리한 차이입니다.
다만 이 결과는 원인을 확정하는 것이 아니라 <b>어떤 현장 데이터를 먼저 확인할지 정하는 출발점</b>입니다.
</div>
""", unsafe_allow_html=True)

    st.markdown("""
| 차이 | 우선 확인할 데이터 | 관련 영역 |
|---|---|---|
| 재료 가격차이 | 구매단가, 계약조건, 원재료 가격 | 구매·재경 |
| 재료 수량차이 | 실투입량, 스크랩, 폐기, 불량·재작업 | 생산·품질·생기 |
| 노무 임률차이 | 인력구성, 시간당 인건비 | 생산·인사·재경 |
| 노무 능률차이 | 실제공수, 병목, 설비정지, 재작업 | 생산·생기·설비 |
""")

with tabs[4]:
    st.subheader("원가차이를 생산량·손익 관점으로 연결")
    st.caption("별도의 임의 절감률을 넣지 않고, 사용자가 입력한 차이분석 결과만 사용합니다.")

    combined = total_var + labor_total_var
    output_for_unit = mat_output if mat_output > 0 and mat_output == lab_output else 0

    s1,s2,s3 = st.columns(3)
    s1.metric("재료원가 총차이", f"{total_var/1e8:,.2f}억원")
    s2.metric("노무원가 총차이", f"{labor_total_var/1e8:,.2f}억원")
    s3.metric("합계", f"{combined/1e8:,.2f}억원")

    if mat_output > 0 and lab_output > 0 and mat_output != lab_output:
        st.warning("재료와 노무 분석의 실제 생산량이 서로 다릅니다. 차량당 합계 계산을 위해 두 탭의 생산량을 동일하게 입력해 주세요.")
    elif output_for_unit > 0:
        unit_gap = combined / output_for_unit
        st.metric("차량당 재료+노무 원가차이", f"{unit_gap:,.0f}원/대")
        st.markdown("""
<div class="box"><b>손익 연결 해석</b><br>
불리한 차이는 동일 생산량에서 제조원가를 높이는 방향, 유리한 차이는 제조원가를 낮추는 방향으로 작용합니다.
실무에서는 여기에 제조간접비 등 추가 원가요인을 함께 분석해야 하지만, 공개되지 않은 값을 임의로 넣지 않기 위해
이 도구는 사용자가 입력한 재료비·노무비까지만 계산합니다.
</div>
""", unsafe_allow_html=True)
    else:
        st.info("②·③ 탭에 동일한 생산량과 분석 데이터를 입력하면 차량당 원가차이를 계산합니다.")

with tabs[5]:
    st.subheader("계산식과 데이터 범위")
    st.markdown("""
### 재료원가
- **가격차이** = (실제단가 − 표준단가) × 실제수량
- **수량차이** = (실제수량 − 표준허용수량) × 표준단가
- **표준허용수량** = 실제생산량 × 차량당 표준투입량

### 노무원가
- **임률차이** = (실제임률 − 표준임률) × 실제작업시간
- **능률차이** = (실제작업시간 − 표준허용시간) × 표준임률
- **표준허용시간** = 실제생산량 × 차량당 표준작업시간

### 데이터 원칙
**기아 실제 공개자료**
- 2023~2025 국내 주요 원재료 총 사용량·사용 집약도
- 2023~2025 연결 매출액·영업이익

**프로그램이 임의로 만들지 않는 데이터**
- 공장별 표준원가·실제원가
- 부품별 표준단가·실제단가
- 차량별 표준투입량·실제투입량
- 표준공수·실제공수
- 불량률·스크랩률·재작업률

이 값들은 공개자료에서 확인되지 않으므로 **사용자가 확보한 실제 데이터를 직접 입력**하도록 설계했습니다.
""")

    st.markdown("""
<div class="box"><b>직무 연결</b><br>
이 도구의 핵심은 '원가가 올랐다'에서 끝나지 않고, 관리회계에서 배운 차이분석을 이용해
<b>단가·투입량·임률·작업시간 중 어디에서 차이가 발생했는지 구분하고 다음 확인 데이터를 정하는 것</b>입니다.
이는 공장 손익관리와 제조원가 경쟁력 확보를 위한 원가관리 업무의 분석 흐름을 연습하기 위한 도구입니다.
</div>
""", unsafe_allow_html=True)
