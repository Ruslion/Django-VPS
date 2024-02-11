import plotly.graph_objects as go


def chart_with_markers(df_result, close_col, action_col):
    df_sell = df_result.loc[df_result[action_col] == 'S' ]
    df_sell[close_col] = df_sell[close_col].apply(lambda x: x*1.05)

    df_buy = df_result.loc[df_result[action_col] == 'B' ]
    df_buy[close_col] = df_buy[close_col].apply(lambda x: x*0.95)
    
    fig2 = go.Figure(data=[go.Scatter(x=df_result['timestamp'],
                
                y=df_result[close_col])])
    
    for date, price in zip(df_buy['timestamp'], df_buy[close_col] ):
        fig2.add_annotation(x=date, y=price,
                    text="B",
                    showarrow=False,
                    arrowhead=1,
                    bordercolor="#00ff00",
                    borderwidth=2,
                    borderpad=4,
                    bgcolor="#00ff00",)
        
    for date, price in zip(df_sell['timestamp'], df_sell[close_col]):
        fig2.add_annotation(x=date, y=price,
                    text="S",
                    showarrow=False,
                    arrowhead=1,
                    bordercolor="#ff0000",
                    borderwidth=2,
                    borderpad=4,
                    bgcolor="#ff0000",)
    return fig2