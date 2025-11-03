import streamlit as st

smart_report_page = st.Page("pages/smart_report.py", title="Отчет за месяц", icon="📈")
currency_rate_page = st.Page("pages/currency_rate.py", title="Курс валют", icon="💲")

pg = st.navigation([smart_report_page, currency_rate_page])
st.set_page_config(page_title="Assistant", page_icon="👩🏼‍💻")
pg.run()
