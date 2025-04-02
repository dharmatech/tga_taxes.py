import pandas as pd
import treasury_gov_pandas.datasets.deposits_withdrawals_operating_cash.load
import treasury_gov_pandas.datasets.deposits_withdrawals_operating_cash.update
import streamlit as st
import plotly
import plotly.express
import streamlit as st
import plotly.express as px

@st.cache_data
def load_dataframe():
    df = treasury_gov_pandas.datasets.deposits_withdrawals_operating_cash.load.load()
    df['record_date'] = pd.to_datetime(df['record_date'])
    df['transaction_today_amt'] = pd.to_numeric(df['transaction_today_amt'])
    df['transaction_mtd_amt']   = pd.to_numeric(df['transaction_mtd_amt'])
    df['transaction_fytd_amt']  = pd.to_numeric(df['transaction_fytd_amt'])
    return df

df = load_dataframe()

tmp = df.query('transaction_type == "Deposits"')

tmp = tmp.query('transaction_catg.str.contains("Tax") or transaction_catg.str.contains("FTD")')

amount_type = st.sidebar.selectbox('Property', ['transaction_mtd_amt', 'transaction_fytd_amt'])

tbl = tmp.groupby('record_date')[amount_type].sum().reset_index()

tbl['year'] = tbl['record_date'].dt.year

tbl['record_date_'] = tbl['record_date'].apply(lambda x: x.replace(year=2000))

pivot = tbl.pivot(index='record_date_', columns='year', values=amount_type)

melted = pivot.reset_index().melt(id_vars='record_date_', var_name='year', value_name=amount_type)

melted = melted.dropna()

melted[amount_type] = melted[amount_type] * 1_000_000

fig = px.line(melted, x='record_date_', y=amount_type, color='year', title='TGA Deposits : Taxes')

fig.update_xaxes(tickformat='%b %d')

st.plotly_chart(fig)


md = """
Using the following to select tax related categories:

```
tmp = df.query('transaction_type == "Deposits"')

tmp = tmp.query('transaction_catg.str.contains("Tax") or transaction_catg.str.contains("FTD")')
```
"""

st.markdown(md)

st.markdown('## Categories in dataset')

st.dataframe(pd.DataFrame(tmp['transaction_catg'].unique()))

md = """
Source code for this page:

https://github.com/dharmatech/tga_taxes.py/blob/main/tga_taxes_year_compare_streamlit.py
"""

st.markdown(md)

st.button(label='Clear Cache', on_click= lambda: load_dataframe.clear())