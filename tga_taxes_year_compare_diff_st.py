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



# df.iloc[0]

# df['transaction_catg'].unique()


columns_to_drop = [

    'table_nbr',
    'table_nm',
    'src_line_nbr',
    'record_fiscal_year',
    'record_fiscal_quarter',
    'record_calendar_year',
    'record_calendar_quarter',
    'record_calendar_month',
    'record_calendar_day'
]

# df.drop(columns=columns_to_drop)



# print(df['transaction_catg'].unique())

# remove rows where `transaction_catg` contains text "Change in Balance of Uncollected Funds"


tmp = df[df['transaction_type'] == 'Withdrawals']

# tmp = tmp[~tmp['transaction_catg'].str.contains("Change in Balance of Uncollected Funds")]

# tmp['transaction_catg'].unique()

# len(tmp['transaction_catg'].unique())

# len(df['transaction_catg'].unique())


# len(df                                         ['transaction_catg'].unique()) # 511
# len(df[df['transaction_type'] == 'Deposits'   ]['transaction_catg'].unique()) # 414
# len(df[df['transaction_type'] == 'Withdrawals']['transaction_catg'].unique()) # 162


# rows where `transaction_catg` contains text "taxes"

# tmp = df.query('transaction_type == "Withdrawals"')
# tmp = tmp.query('transaction_catg.str.contains("taxes")')
# tmp = tmp.query('transaction_catg.str.contains("Tax") or transaction_catg.str.contains("FTD")')
# tmp = tmp.query('transaction_catg.str.contains("Tax") or transaction_catg.str.contains("FTD")')
# tmp = tmp.query('transaction_catg.str.contains("Tax") or transaction_catg.str.contains("FTD")')
# tmp = tmp.query('transaction_catg.str.contains("Tax") or transaction_catg.str.contains("FTD")')


# alt = tmp[tmp['transaction_catg'].str.contains("Tax")]

# alt['transaction_catg'].unique()

# alt = tmp[tmp['transaction_catg'].str.contains("Refund")]

# alt['transaction_catg'].unique()


tmp = tmp[tmp['transaction_catg'].str.contains("Tax")]

# tmp.drop(columns=columns_to_drop)






# ----------------------------------------------------------------------
# Deposits
# ----------------------------------------------------------------------

tmp = df.query('transaction_type == "Deposits"')

tmp = tmp.query('transaction_catg.str.contains("Tax") or transaction_catg.str.contains("FTD")')

amount_type = st.sidebar.selectbox('Property', ['transaction_mtd_amt', 'transaction_fytd_amt'])

tbl = tmp.groupby('record_date')[amount_type].sum().reset_index()

tbl['year'] = tbl['record_date'].dt.year

tbl['record_date_'] = tbl['record_date'].apply(lambda x: x.replace(year=2000))

pivot = tbl.pivot(index='record_date_', columns='year', values=amount_type)

melted = pivot.reset_index().melt(id_vars='record_date_', var_name='year', value_name=amount_type)

melted = melted.dropna()

# melted[amount_type] = melted[amount_type] * 1_000_000

melted_deposits = melted.copy()

# melted_deposits[amount_type]

melted_deposits = melted_deposits.rename(columns={amount_type: 'deposits'})

# ----------------------------------------------------------------------
# Withdrawals
# ----------------------------------------------------------------------

tmp = df.query('transaction_type == "Withdrawals"')

tmp = tmp.query('transaction_catg.str.contains("Tax")')

# amount_type = st.sidebar.selectbox('Property', ['transaction_mtd_amt', 'transaction_fytd_amt'])

tbl = tmp.groupby('record_date')[amount_type].sum().reset_index()

tbl['year'] = tbl['record_date'].dt.year

tbl['record_date_'] = tbl['record_date'].apply(lambda x: x.replace(year=2000))

pivot = tbl.pivot(index='record_date_', columns='year', values=amount_type)

melted = pivot.reset_index().melt(id_vars='record_date_', var_name='year', value_name=amount_type)

melted = melted.dropna()

# melted[amount_type] = melted[amount_type] * 1_000_000

melted_withdrawals = melted.copy()

melted_withdrawals = melted_withdrawals.rename(columns={amount_type: 'withdrawals'})
# ----------------------------------------------------------------------

# melted_deposits[melted_deposits['year'] >= 2012]


merged = pd.merge(left=melted_deposits, right=melted_withdrawals, how='outer', on=['record_date_', 'year'])

merged = merged.sort_values(by=['year', 'record_date_'])

# remove rows where 'withdrawals' is NaN

merged = merged[~merged['withdrawals'].isna()]


merged['diff'] = merged['deposits'] - merged['withdrawals']

selected_property = st.sidebar.selectbox('Chart', ['deposits', 'withdrawals', 'diff'])

# ----------------------------------------------------------------------
fig = px.line(merged, x='record_date_', y=selected_property, color='year', title=f'TGA Taxes : {selected_property}')
fig.update_xaxes(tickformat='%b %d')

st.plotly_chart(fig)

# ----------------------------------------------------------------------
# fig = px.line(melted, x='record_date_', y=amount_type, color='year', title='TGA Deposits : Taxes')

# fig.update_xaxes(tickformat='%b %d')

# st.plotly_chart(fig)
# ----------------------------------------------------------------------

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