import plotly.graph_objects as go


def chart_with_markers(df_result,  action_col):
    df_sell = df_result.loc[df_result[action_col] == 'S' ]
    df_sell['close'] = df_sell['close'].apply(lambda x: x*1.05)

    df_buy = df_result.loc[df_result[action_col] == 'B' ]
    df_buy['close'] = df_buy['close'].apply(lambda x: x*0.95)
    
    fig2 = go.Figure(data=[go.Candlestick  (x=df_result['timestamp'],
                open=df_result['open'],
                high=df_result['high'],
                low=df_result['low'],
                close=df_result['close'])])
    
    for date, price in zip(df_buy['timestamp'], df_buy['close'] ):
        fig2.add_annotation(x=date, y=price,
                    text="B",
                    showarrow=False,
                    arrowhead=1,
                    bordercolor="#00ff00",
                    borderwidth=2,
                    borderpad=4,
                    bgcolor="#00ff00",)
        
    for date, price in zip(df_sell['timestamp'], df_sell['close']):
        fig2.add_annotation(x=date, y=price,
                    text="S",
                    showarrow=False,
                    arrowhead=1,
                    bordercolor="#ff0000",
                    borderwidth=2,
                    borderpad=4,
                    bgcolor="#ff0000",)
    return fig2