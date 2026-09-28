import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title='기아 AutoLand 원가개선 분석', page_icon='🚗', layout='wide')
st.markdown('''<style>
.block-container{padding-top:1.4rem;max-width:1450px} h1,h2,h3{letter-spacing:-.03em}
div[data-testid="stMetric"]{background:#f7f7f8;border:1px solid #e7e7ea;padding:14px;border-radius:12px}
.box{padding:16px 18px;border-radius:12px;background:#f7f7f8;border-left:5px solid #222;margin:10px 0 18px}
.note{padding:14px 18px;border-radius:12px;background:#fff8e8;border-left:5px solid #e0a000;margin:10px 0 18px}
</style>''', unsafe_allow_html=True)

st.title('기아 AutoLand 원가개선 분석')
st.caption('재경 관점 | 계획원가 → 실제원가 → 차이 → 원인 → 개선 → 공장 손익')
st.markdown('''<div class="box"><b>핵심 질문</b><br>생산량을 늘리는 것만으로 원가경쟁력이 좋아질까? 차량 1대당 실제 투입이 계획과 왜 달라졌는지를 찾아야 한다.</div>''', unsafe_allow_html=True)
st.markdown('''<div class="note"><b>데이터 기준</b><br>기아 공개자료로 확인 가능한 생산전략·손익은 실제 공개정보를 사용합니다. 차량별 계획원가, 공정시간, 불량률 등 비공개 내부 데이터는 직무 이해를 위한 <b>가상 시뮬레이션</b>이며 기아의 실제 수치가 아닙니다.</div>''', unsafe_allow_html=True)

# illustrative internal cost simulation
base = pd.DataFrame({
    '원가항목':['재료·부품비','직접노무비','에너지·설비비','품질·폐기비'],
    '계획원가(만원/대)':[2100,120,150,30],
    '실제원가(만원/대)':[2165,128,157,45]
})
base['차이(만원/대)']=base['실제원가(만원/대)']-base['계획원가(만원/대)']
base['차이율(%)']=base['차이(만원/대)']/base['계획원가(만원/대)']*100

cause = pd.DataFrame({
    '원인':['부품·원재료 단가','차량당 투입량','작업시간','불량·폐기','에너지·설비','기타'],
    '원가차이(만원/대)':[38,27,8,15,7,-5]
})

actions = pd.DataFrame({
    '원인':['단가 상승','투입량 증가','작업시간 증가','불량·폐기 증가','에너지·설비비 증가'],
    '확인 데이터':['구매단가·계약조건','BOM·실투입량·스크랩','표준공수·실제공수','불량률·재작업·폐기량','가동률·전력·보전비'],
    '협업 부서':['구매','생산·생기','생산·생기','품질·생산','생산·설비'],
    '개선 방향':['단가협상·현지조달','공정손실·투입량 개선','병목·대기시간 축소','재작업·폐기 감소','가동률·에너지 효율 개선']
})

tabs=st.tabs(['① 직무 구조','② 계획 vs 실제','③ 원인 분해','④ 개선 시뮬레이션','⑤ 공장 손익 연결','⑥ 최종 결론'])

with tabs[0]:
    st.subheader('원가개선은 숫자를 줄이는 일이 아니라 차이의 이유를 찾는 일')
    stages=['계획원가','실제 생산','차이 확인','원인 분해','현업 개선','손익 반영']
    desc=['생산량·표준원가 설정','실제 투입·비용 집계','계획과 실제 비교','단가·수량·효율 구분','구매·생산·품질 협업','차량당 원가와 공장손익 확인']
    cols=st.columns(6)
    for c,s,d in zip(cols,stages,desc):
        c.markdown(f'### {s}')
        c.caption(d)
    st.markdown('''<div class="box"><b>공개자료에서 확인한 방향</b><br>기아는 광명·화성 EVO Plant의 전기차 생산효율을 극대화해 볼륨 차종의 가격경쟁력을 확보하고, 차세대 시스템·배터리 구조 단순화와 공급망 현지화 등을 원가·제조혁신 방향으로 제시했습니다.</div>''', unsafe_allow_html=True)

with tabs[1]:
    st.subheader('계획원가와 실제원가 비교')
    prod=st.slider('가상 생산량(대)',50000,150000,100000,5000)
    plan=base['계획원가(만원/대)'].sum(); actual=base['실제원가(만원/대)'].sum(); gap=actual-plan
    c1,c2,c3,c4=st.columns(4)
    c1.metric('계획원가',f'{plan:,.0f}만원/대')
    c2.metric('실제원가',f'{actual:,.0f}만원/대')
    c3.metric('차량당 차이',f'+{gap:,.0f}만원',f'{gap/plan*100:.1f}%')
    c4.metric('생산량',f'{prod:,}대')
    fig=px.bar(base,x='원가항목',y=['계획원가(만원/대)','실제원가(만원/대)'],barmode='group')
    st.plotly_chart(fig,use_container_width=True)
    st.dataframe(base.style.format({'계획원가(만원/대)':'{:,.0f}','실제원가(만원/대)':'{:,.0f}','차이(만원/대)':'{:+,.0f}','차이율(%)':'{:+.1f}%'}),use_container_width=True)

with tabs[2]:
    st.subheader('원가가 올랐다면 먼저 가격과 수량·효율을 분리')
    fig=px.bar(cause,x='원인',y='원가차이(만원/대)',text_auto='.0f')
    st.plotly_chart(fig,use_container_width=True)
    st.markdown('''<div class="box"><b>진단 논리</b><br>재료비 증가가 구매단가 상승 때문이라면 구매조건을, 차량당 투입량 증가 때문이라면 공정손실·스크랩을 봐야 합니다. 같은 원가 상승이라도 원인에 따라 개선 담당 부서와 방법이 달라집니다.</div>''', unsafe_allow_html=True)
    st.dataframe(actions,use_container_width=True,hide_index=True)

with tabs[3]:
    st.subheader('개선과제의 효과를 차량당 원가로 환산')
    price=st.slider('단가요인 개선(만원/대)',0,38,20)
    qty=st.slider('투입량요인 개선(만원/대)',0,27,15)
    labor=st.slider('공정시간 개선(만원/대)',0,8,4)
    quality=st.slider('불량·폐기 개선(만원/대)',0,15,8)
    energy=st.slider('에너지·설비 개선(만원/대)',0,7,3)
    saving=price+qty+labor+quality+energy
    new_cost=actual-saving
    c1,c2,c3=st.columns(3)
    c1.metric('개선 전 실제원가',f'{actual:,.0f}만원/대')
    c2.metric('예상 절감',f'{saving:,.0f}만원/대')
    c3.metric('개선 후 예상원가',f'{new_cost:,.0f}만원/대')
    st.caption('※ 사용자가 조정하는 가상 시뮬레이션입니다. 실제 기아 원가절감액이 아닙니다.')

with tabs[4]:
    st.subheader('차량당 개선을 공장 손익으로 연결')
    total_save_100m=saving*10000*prod/100_000_000
    st.metric('가상 연간 원가개선 효과',f'{total_save_100m:,.0f}억원')
    st.markdown(f'''<div class="box"><b>연결 방식</b><br>{prod:,}대를 생산한다고 가정할 때 차량당 {saving:,.0f}만원의 원가개선은 공장 전체 제조원가 감소로 이어집니다. 재경 담당자는 개선활동 자체보다 <b>실제 차량당 원가와 공장 손익이 얼마나 개선됐는지</b>까지 확인해야 합니다.</div>''', unsafe_allow_html=True)

with tabs[5]:
    st.subheader('프로그램에서 얻은 결론')
    st.markdown('''
**1. 생산량 증가만으로 원가경쟁력을 판단할 수 없다.** 차량 1대당 투입량과 비용을 계획 대비 확인해야 한다.  
**2. 원가차이는 원인별로 분해해야 한다.** 단가, 투입량, 작업시간, 불량·폐기, 설비·에너지 등으로 나눠야 개선 방향이 보인다.  
**3. 재경은 현장 데이터를 돈으로 연결한다.** 생산·구매·품질의 변화가 차량당 원가와 공장 손익에 미치는 영향을 계산한다.  
**4. 개선 결과를 다음 계획에 반영한다.** 계획 → 실적 → 차이 → 원인 → 개선 → 다음 계획의 순환이 원가관리의 핵심이다.
''')
    st.markdown('''<div class="box"><b>지원 직무 연결</b><br>숫자가 올랐다는 결과에 그치지 않고 어떤 요인이 숫자를 바꾸었는지 찾아, 현업의 개선활동을 공장 손익으로 연결하는 재경 담당자가 되겠습니다.</div>''', unsafe_allow_html=True)
