import pandas as pd
import treasury_gov_pandas

from bokeh.plotting import figure, show
from bokeh.models   import NumeralTickFormatter, HoverTool
import bokeh.models

import bokeh.palettes
import bokeh.transform

# ----------------------------------------------------------------------
df = treasury_gov_pandas.update_records(
    url = 'https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/dts/deposits_withdrawals_operating_cash')

df['record_date'] = pd.to_datetime(df['record_date'])

df['transaction_today_amt'] = pd.to_numeric(df['transaction_today_amt'])

# ----------------------------------------------------------------------

tmp = df[(df['transaction_type'] == 'Deposits') &   ((df['transaction_catg'].str.contains('Tax'))   |   (df['transaction_catg'].str.contains('FTD')))   ]

# tmp.drop(columns=['table_nbr', 'table_nm', 'src_line_nbr', 'record_fiscal_year', 'record_fiscal_quarter', 'record_calendar_year', 'record_calendar_quarter', 'record_calendar_month', 'record_calendar_day', 'transaction_mtd_amt', 'transaction_fytd_amt', 'transaction_catg_desc', 'account_type', 'transaction_type'])

# tmp.tail(20).drop(columns=['table_nbr', 'table_nm', 'src_line_nbr', 'record_fiscal_year', 'record_fiscal_quarter', 'record_calendar_year', 'record_calendar_quarter', 'record_calendar_month', 'record_calendar_day', 'transaction_mtd_amt', 'transaction_fytd_amt', 'transaction_catg_desc', 'account_type', 'transaction_type'])

# ----------------------------------------------------------------------

tmp_agg = tmp.groupby(['record_date', 'transaction_catg'])['transaction_today_amt'].sum().reset_index()

tmp_agg['record_date'] = tmp_agg['record_date'].dt.date

pivot_df = tmp_agg.pivot(index='record_date', columns='transaction_catg', values='transaction_today_amt').fillna(0)

pivot_df.index = pd.to_datetime(pivot_df.index)

pivot_df = pivot_df.groupby(pd.Grouper(freq='Y')).sum()

p = figure(title='TGA Taxes : grouped by year', sizing_mode='stretch_both', x_axis_type='datetime', x_axis_label='record_date', y_axis_label='amt')

p.add_tools(HoverTool(tooltips=[
    ('record_date',    '@record_date{%F}')
    ],
    formatters={ '@record_date' : 'datetime' }
    ))

width = pd.Timedelta(days=300)

p.vbar_stack(stackers=pivot_df.columns, x='record_date', width=width, source=pivot_df, color=bokeh.palettes.Category20[15], legend_label=pivot_df.columns.tolist())

p.xaxis.ticker = bokeh.models.DatetimeTicker(desired_num_ticks=30)

p.legend.click_policy = 'hide'

p.legend.location = 'top_left'

p.yaxis.formatter = NumeralTickFormatter(format='$0a')

show(p)
