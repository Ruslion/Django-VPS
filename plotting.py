import plotly.graph_objects as go


def chart_with_markers(df_result, column_name):
    df_sell = df_result.loc[df_result['action'] == 'S' ]
    df_sell[column_name] = df_sell[column_name].apply(lambda x: x*1.1)

    df_buy = df_result.loc[df_result['action'] == 'B' ]
    df_buy[column_name] = df_buy[column_name].apply(lambda x: x*0.9)
    
    fig2 = go.Figure(data=[go.Scatter(x=df_result['timestamp'],
                
                y=df_result[column_name])])
    
    for date, price in zip(df_buy['timestamp'], df_buy[column_name] ):
        fig2.add_annotation(x=date, y=price,
                    text="B",
                    showarrow=False,
                    arrowhead=1,
                    bordercolor="#00ff00",
                    borderwidth=2,
                    borderpad=4,
                    bgcolor="#00ff00",)
        
    for date, price in zip(df_sell['timestamp'], df_sell[column_name]):
        fig2.add_annotation(x=date, y=price,
                    text="S",
                    showarrow=False,
                    arrowhead=1,
                    bordercolor="#ff0000",
                    borderwidth=2,
                    borderpad=4,
                    bgcolor="#ff0000",)
    return fig2