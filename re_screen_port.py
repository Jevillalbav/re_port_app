#pip install -r requirements.txt
import pandas as pd 
import numpy as np
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

data_model_a = pd.read_csv("data_model.csv", index_col = 0)
data_model_a['period'] = pd.to_datetime(data_model_a['period'])

forecasts_database_a = pd.read_csv("forecasts_database.csv",  index_col = 0)
forecasts_database_a.index = pd.to_datetime(forecasts_database_a.index)

expected_irr_a = pd.read_csv("expected_irr.csv",  index_col = 0)
expected_irr_a['date_forecast'] = pd.to_datetime(expected_irr_a['date_forecast'])

irr_real_a = pd.read_csv("irr_real.csv",  index_col = 0)
irr_real_a['date'] = pd.to_datetime(irr_real_a['date'])

scenarios_markets_a = pd.read_csv("scenarios_markets.csv",  index_col = 0)
scenarios_markets_a['date'] = pd.to_datetime(scenarios_markets_a['date'])

leverage_a = pd.read_csv("leverage.csv",  index_col = 0)

sets = expected_irr_a.melt(id_vars = ['date_forecast', 'k']).dropna()[['k', 'variable']].sort_values('k').drop_duplicates().copy()
sets['variable_m'] = sets['variable'].str.replace('sd', 'severe_d').str.replace('rates', 'rate_s')

main_set = sets['k'].unique().tolist()
sub_set = dict(zip(main_set, [list(dict.fromkeys(['mean', 'lower', 'upper'] +  sets.query('k == @i ')['variable'].unique().tolist())) for i in main_set]))

################################################################################################################################
fig = go.Figure()
fig.update_layout(xaxis_title="Date", 
                  xaxis = dict(  domain=[0.05, 0.98],
                                                    title="Date",
                                                    titlefont=dict(color="black"),
                                                    tickfont=dict(color="black"),
                                                    showgrid=False,dtick='M12', 
                                                    ticks="outside", tickcolor="black")
    ,
    yaxis=dict(title="Price - USD" #+ data_model_f['yax'].unique()[0]
               ,titlefont=dict(color="black",size = 20),
                                    tickfont=dict(color="black"), tickformat = '$,.0f', 
                                    showgrid=False,position=0.04) #overlaying="y",
                                    #range=[0,int((data_model_f['price'].max()*1.2)/100)*100],
                                    #dtick=int((data_model_f['price'].max()*1.2)/100)*5)
                                    #gridcolor='white',
                                    #gridwidth=0.5 
    ,
    yaxis2=dict(title='',titlefont=dict(color="black", size = 15),                    
                                                    tickfont=dict(color="black"), anchor="free", showgrid=False, showticklabels=False,  
                                                    side="left",position=0.14, overlaying="y",
                                                    tickformat =',.2%',# ',.0%',
                                                    range=[-0.35, 3.8])
    ,
    yaxis3=dict(title="", titlefont=dict(color="#204a01", size = 15),
                                    tickfont=dict(color="#204a01"),anchor="free",
                                    side="left",position=0.08,  overlaying="y",
                                    showgrid=False,tickformat ='.2%',# ',.0%',
                                    #zeroline=True,
                                    range = [-0.2,0.4],
                                    dtick=0.03,
                                    #gridcolor='white',
                                    showticklabels=False)
    ,
    legend=dict(x=0.4,y=1.12, traceorder="normal", font=dict(family="sans-serif",size=12, color="black"), bgcolor="white", bordercolor="black", borderwidth=1)
    ,
    autosize=False,  legend_orientation="h",margin=dict(l=50,r=50,b=100,t=100,pad=4)
    ,
    )   
fig.update_layout(width = 1600, height = 800)
## change theme 
fig.update_layout(template = 'plotly_white')
app = dash.Dash(__name__)
server = app.server
app.layout = html.Div([
    html.Label('Select a RE market of the company portfolio:'),
    # Dropdown for selecting category
    dcc.Dropdown(
        id='main_set_dropdown',
        options= [{'label': x, 'value': x} for x in main_set],
        value= main_set[0],
        multi=False,
    ), 
    
    html.Label('Select an scenario to test:')
    ,
    ## the default values is 'mean' always 
    dcc.Dropdown(
        id='sub_set_dropdown',
        options= [{'label': x , 'value': x} for x in sub_set[main_set[0]]],
        value= ['mean'],
        multi=True,

    )
    ,
    # Plotly chart
    dcc.Graph(
        id='chart',
        figure=fig  # Use the figure you created earlier

    )
    
])

# Callback to update the chart based on the selected category
@app.callback(
    Output('chart', 'figure'),
    Output('sub_set_dropdown', 'options'),
    Output('sub_set_dropdown', 'value'),
    Input('main_set_dropdown', 'value'),
    Input('sub_set_dropdown', 'value')
)

def update_output( category , subs):

    categories_options = [{'label': x, 'value': x} for x in sub_set[category]]
    subcategories = [x for x in sub_set[category] if x in subs]

    #[sub_set[category][0]] if not subs else subs

    data_model_f = data_model_a.loc[data_model_a['name'] == category].copy()

    price_f = scenarios_markets_a.loc[(scenarios_markets_a['k'] == category ) & (scenarios_markets_a['var'] == 'price')].copy().pivot_table( index = 'date', columns = 'type', values = 'value')
    rent_f = scenarios_markets_a.loc[(scenarios_markets_a['k'] == category ) & (scenarios_markets_a['var'] == 'r')].copy().pivot_table( index = 'date', columns = 'type', values = 'value')
    noi_f = (rent_f*6) / price_f

    expected_irr_f = expected_irr_a.loc[(expected_irr_a['k'] == category )].drop(columns = [ 'k']).set_index('date_forecast')

    irr_real_f = irr_real_a.loc[(irr_real_a['k'] == category )].dropna()

    leverage_f = str((leverage_a.loc[leverage_a['name'] == category].copy()['leverage'].values[0]*100).round(1)) + '%'


    data_model_f = data_model_a.loc[data_model_a['name'] == category].copy()

    price_f = scenarios_markets_a.loc[(scenarios_markets_a['k'] == category ) & (scenarios_markets_a['var'] == 'price')].copy().pivot_table( index = 'date', columns = 'type', values = 'value')
    rent_f = scenarios_markets_a.loc[(scenarios_markets_a['k'] == category ) & (scenarios_markets_a['var'] == 'r')].copy().pivot_table( index = 'date', columns = 'type', values = 'value')
    noi_f = (rent_f*6) / price_f

    expected_irr_f = expected_irr_a.loc[(expected_irr_a['k'] == category )].dropna(axis=1).drop(columns = [ 'k']).set_index('date_forecast')

    irr_real_f = irr_real_a.loc[(irr_real_a['k'] == category )].dropna()

    leverage_f = str((leverage_a.loc[leverage_a['name'] == category].copy()['leverage'].values[0]*100).round(1)) + '%'

    fig = go.Figure()
    fig.update_layout(xaxis_title="Date", 
                    
        xaxis = dict(  domain=[0.05, 0.98],
                                                        title="Date",
                                                        titlefont=dict(color="black"),
                                                        tickfont=dict(color="black"),
                                                        showgrid=False,dtick='M12', 
                                                        ticks="outside", tickcolor="black", 
                                                        gridcolor='rgba(0,0,0,0.05)')
        ,
        yaxis=dict(title="Price - USD" + data_model_f['yax'].unique()[0]
                ,titlefont=dict(color="black",size = 20),
                                        tickfont=dict(color="black"), tickformat = '$,.0f', 
                                        showgrid=False,position=0.04, #overlaying="y",
                                        range=[0,int((data_model_f['price'].max()*1.2)/100)*100],
                                        dtick=int((data_model_f['price'].max()*1.2)/100)*5,
                                        gridcolor='rgba(0,0,0,0.05)')
                                        #gridwidth=0.5
                                        
        ,
        yaxis2=dict(title='',titlefont=dict(color="black", size = 15),                    
                                                        tickfont=dict(color="black"), anchor="free", showgrid=False, showticklabels=False,  
                                                        side="left",position=0.14, overlaying="y",
                                                        tickformat =',.2%',# ',.0%',
                                                        range=[-0.35, 3.8])
        ,
        yaxis3=dict(title="", titlefont=dict(color="#204a01", size = 15),
                                        tickfont=dict(color="#204a01"),anchor="free",
                                        side="left",position=0.08,  overlaying="y",
                                        showgrid=False,tickformat ='.2%',# ',.0%',
                                        #zeroline=True,
                                        range = [-0.2,0.4],
                                        dtick=0.03,
                                        #gridcolor='white',
                                        showticklabels=False)
        ,
        legend=dict(x=0.4,y=1.12, traceorder="normal", font=dict(family="sans-serif",size=12, color="black"), bgcolor="white", bordercolor="black", borderwidth=1)
        ,
        autosize=False,  legend_orientation="h",margin=dict(l=50,r=50,b=100,t=100,pad=4)
        ,
        )   
    fig.update_layout(width = 1600, height = 800, title = category)
    ## change theme 
    fig.update_layout(template = 'plotly_white')

    ## PRECIO DE LA VIVIENDA
    fig.add_trace(go.Scatter(x=data_model_f['period'], y=data_model_f['price'], name='Market Sale Price', line_color='purple', mode='lines+markers', line = dict(color = 'blue', width = 1), marker= dict(size = 2), showlegend= True , hovertemplate= '%{x|%Y-%m-%d}<br>Value: $%{y:,.0f}'))

    # para cada subcategoria en el dropdown, graficar la linea de forecast
    for i in subcategories:
        fig.add_trace(go.Scatter(x=price_f.index, y=price_f[i], mode='lines', line = dict( width = 1, dash = 'dot'), showlegend= False , name=i, hovertemplate= '%{x|%Y-%m-%d}<br>Value: $%{y:,.0f}'))

    ## NOI
    fig.add_trace(go.Scatter(x=data_model_f['period'], y=data_model_f['rate'], name='Rate +  Spread', line_color='rgba(255, 0, 0,0.2)' , mode='lines' , fill= 'tozeroy', fillcolor= 'rgba(255, 0, 0,0.1)', showlegend= True, yaxis='y3', line=dict(width=1) , hovertemplate=  '%{x|%Y-%m-%d}<br>Rate: %{y:.2%}'))
    fig.add_trace(go.Scatter( x = data_model_f['period'], y = data_model_f['yld'] , name='Rate' , line_color= 'rgba(255, 0, 0,0.2)' , mode='lines' , fill= 'tozeroy', fillcolor= 'rgba(255, 0, 0,0.1)', showlegend= False, yaxis='y3', line=dict(width=1), hovertemplate= '%{x|%Y-%m-%d}<br>Rate: %{y:.2%}'))
    fig.add_trace(go.Scatter( x = data_model_f['period'], y = data_model_f['noi'], name='NOI' , line_color='rgba(12, 171, 57,0.2)', mode='lines' , fill= 'tozeroy', fillcolor= 'rgba(12, 171, 57,0.2)', showlegend= True, yaxis='y3' , line=dict(width=1), hovertemplate= '%{x|%Y-%m-%d}<br>Rate: %{y:.2%}'))
    #
    #fig.add_trace(go.Scatter( x = noi_f.index, y = noi_f['mean'], name='NOI Forecast' , line_color='#0ead53', mode='lines' , showlegend= False, yaxis='y3' , line=dict(width=1, dash="dot"), fill= 'tozeroy', fillcolor= 'rgba(14, 173, 83,0.04)', hovertemplate= '%{x|%Y-%m-%d}<br>NOI: %{y:.2%}'))
    for i in subcategories: 
        fig.add_trace(go.Scatter(x=noi_f.index, y=noi_f[i], mode='lines',  yaxis='y3' , line = dict( width = 1, dash = 'dot'), showlegend= False , name=i, hovertemplate= '%{x|%Y-%m-%d}<br>IRR: %{y:.2%}'))

    fig.add_trace(go.Bar( x = irr_real_f['date'], y = irr_real_f['irr'],  name="IRR Current", opacity=1, yaxis='y2' , marker_color = '#055f73', hovertemplate= '%{x|%Y-%m-%d}<br>IRR: %{y:.2%}'))




    for i in subcategories:
        fig.add_trace(go.Scatter(x=expected_irr_f.index, y=expected_irr_f[i], mode='lines', line = dict( width = 1, dash = 'dot'), yaxis='y2', showlegend= False , name=i, hovertemplate= '%{x|%Y-%m-%d}: %{y:.2%}'))



    # OTHERS
    fig.add_annotation(x=0.05, y= -0.13, text="** Assumptions:    1- Expenses at 50% of the net operating income. 2- Spread over the 10 Years Yield of 200 Basis Points. 3- Housing prices given in US dollars", showarrow=False, arrowhead=1, ax=0, ay=-40, bgcolor="white", bordercolor="black", borderwidth=1,  yref='paper',xref = 'paper', font=dict(size=11, color='black')  )
    ################################################################################################################################

    current_price = data_model_f['price'].iloc[-1]
    current_noi = data_model_f['noi'].iloc[-1]
    current_yld = data_model_f['yld'].iloc[-1]
    current_rate = data_model_f['rate'].iloc[-1]

    current_price_s = format(current_price, ',.0f')
    current_noi_s = format(current_noi, '.2%')
    current_yld_s = format(current_yld, '.2%')
    current_rate_s = format(current_rate, '.2%')

    current_price_l = data_model_f['period'].iloc[-1]
    current_noi_l = data_model_f['period'].iloc[-1]
    current_yld_l = data_model_f['period'].iloc[-1]
    current_rate_l = data_model_f['period'].iloc[-1]

    fig.add_annotation(x=current_price_l, y=current_price, text="Current Price : $" +  current_price_s, showarrow=True, arrowhead=1, ax=-70, ay=10, bgcolor="white", bordercolor="black", borderwidth=1,  yref='y1')
    fig.add_annotation(x=current_noi_l, y=current_noi, text="Current NOI : " +  current_noi_s, showarrow=True, arrowhead=1, ax=70, ay=-30, bgcolor="white", bordercolor="black", borderwidth=1,  yref='y3')
    #fig.add_annotation(x=current_yld_l, y=current_yld, text="Current 10Y : " +  current_yld_s, showarrow=True, arrowhead=1, ax=0, ay=-0, bgcolor="white", bordercolor="black", borderwidth=1,  yref='y3')
    fig.add_annotation(x=current_rate_l, y=current_rate, text="Current Rate + Spread: " +  current_rate_s, showarrow=True, arrowhead=1, ax=-0, ay=70, bgcolor="white", bordercolor="black", borderwidth=1,  yref='y3')
    fig.add_annotation(x=irr_real_f.dropna()['date'].iloc[-1], y= 0, text="Current IRR  ->  Forecast IRR ", showarrow=False, arrowhead=1, ax=0, ay=-40, bgcolor="white", bordercolor="black", borderwidth=1,  yref='paper', font=dict(size=11, color='black')  )
    fig.add_annotation(x=irr_real_f.dropna()['date'].iloc[-1] ,y= 0.03,  text = 'Last IRR 5Y: ' + format(irr_real_f.dropna()['irr'].iloc[-1], '.2%'), showarrow=False, arrowhead=1, ax=0, ay=-40, bgcolor="white", bordercolor="black", borderwidth=1,  yref='paper', font=dict(size=11, color='black')  ) 

    current_rent_less_interest_str = format((current_noi - current_rate), '.2%')
    # Assumpitons chart upper 
    fig.add_annotation(x= current_price_l, y = 0.955 , text= 'Current Assumed Debt Rate  SOFR 10Y + 200 b.p.:  ' + current_rate_s, ax = -150, ay=0, bgcolor="#eb6e74", bordercolor="black", borderwidth=1,  yref='paper')
    fig.add_annotation(x= current_price_l, y = 0.993 , text= 'Current Assumed NOI Margin:  ' + current_noi_s,  ax=-150, ay=0, bgcolor="#86e394", bordercolor="black", borderwidth=1,  yref='paper')
    fig.add_annotation(x= current_price_l, y = 0.915 , text= 'Current Assumed Profit from Holding: ' + current_rent_less_interest_str, ax=-150, ay=0, bgcolor="#d9b0eb", bordercolor="black", borderwidth=1,  yref='paper')
    fig.add_annotation(x= current_price_l, y = 0.875 , text= 'Current Leverage Limit: ' + leverage_f
                    , ax=-150, ay=0, bgcolor="#7299ed", bordercolor="black", borderwidth=1,  yref='paper')

    forecast_date_irr = expected_irr_f.index[-1] #+ pd.offsets.DateOffset(years=1)
    forecast_date_price = price_f.index[-1] #+ pd.offsets.DateOffset(years=1)

    price_forecasted = price_f.loc[forecast_date_price].sort_values(ascending = False).to_frame()
    price_forecasted.columns = ['price']
    price_forecasted['yoy'] = (price_forecasted / current_price)**(1/5)  -1 
    price_forecasted['yoy'] = price_forecasted['yoy'].apply(lambda x: format(x, '.2%'))
    price_forecasted['price'] = price_forecasted['price'].apply(lambda x: format(x, ',.0f'))

    price_forecasted.index = price_forecasted.index

    y_loc = 0.99
    for i in subcategories:
        fig.add_annotation(x= forecast_date_price+ pd.offsets.DateOffset(years=4), y = y_loc , text= i.replace('sd', 'severe_d').replace('rates', 'rate_s') +' Price : $'  +    price_forecasted['price'].loc[i] + ' | YoY: ' + price_forecasted['yoy'].loc[i] + '', ax = 0, ay=0, bordercolor="black", borderwidth=1,  yref='paper' , bgcolor=  'rgba(7, 18, 74,0.5)', font=dict(color='white'))
        y_loc = y_loc - 0.034


    noi_forecasted = noi_f.loc[forecast_date_price].sort_values(ascending = False).to_frame()
    noi_forecasted.columns = ['noi']
    noi_forecasted['noi'] = noi_forecasted['noi'].apply(lambda x: format(x, '.2%'))

    y_loc = 0.65 
    for i in subcategories:
        fig.add_annotation(x= forecast_date_price+ pd.offsets.DateOffset(years=3), y = y_loc , text= i.replace('sd', 'severe_d').replace('rates', 'rate_s') +' NOI : '  +    noi_forecasted['noi'].loc[i] + '', ax = 0, ay=0, bordercolor="black", borderwidth=1,  yref='paper',  bgcolor=  '#18ab61', font=dict(color='white'))
        y_loc = y_loc - 0.034

    irr_forecasted = expected_irr_f.loc[forecast_date_irr].sort_values(ascending = False).to_frame()
    irr_forecasted.columns = ['irr']
    irr_forecasted['irr'] = irr_forecasted['irr'].apply(lambda x: format(x, '.2%'))

    y_loc = 0.29 
    for i in subcategories:
        fig.add_annotation(x= forecast_date_irr+ pd.offsets.DateOffset(years=3), y =y_loc , text= i.replace('sd', 'severe_d').replace('rates', 'rate_s') +' IRR : '  +    irr_forecasted['irr'].loc[i] + '', ax = 0, ay=0, bordercolor="black", borderwidth=1,  yref='paper', bgcolor=  '#055f73', font=dict(color='white'))
        y_loc = y_loc - 0.034

    irr_real_f['date'] = pd.to_datetime(irr_real_f['date'])
    for x,y in irr_real_f.dropna()[['date', 'irr']].values[1::2]:
        fig.add_annotation(x=x, y=y, text= format(y, '.1%'), xanchor='center', yanchor='bottom', showarrow=False, yshift=20, font=dict(color='black', size=10), yref='y2', textangle=-65, bgcolor='rgba(255, 255, 255,1)', bordercolor='rgba(0, 0, 0,0.1)')



    return fig , categories_options, subcategories

if __name__ == '__main__':
    app.run_server(debug=True)
