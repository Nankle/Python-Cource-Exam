#!/usr/bin/env python
# coding: utf-8

# In[1]:


#by:WIKI CHOu
#04/11/2020

import folium
import folium.plugins as plugins
import os
import numpy as np
import pandas as pd
import webbrowser


# In[2]:


"""df 每一行记录代表一个点  包含 lon lat  和picturepath 三个数据"""
def draw_on_map(df,sav_path):
    
    
    
    World_map = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=15)#创建底图，location表示显示地图的中心位置，zoom_start为缩放尺度
    marker_cluster = plugins.MarkerCluster().add_to(World_map)#marker_cluster 代表一个图层 之后会将点簇添加到这个图层上   相当于在arcgis里面的图层
    for index,row in df.iterrows():#遍历数据
        
   
        popup = folium.Popup('<img src="'+row['picturepath']+'" alt="'+str(index)+'">')#用H5语句创建水滴点的对象
        folium.Marker([row['lat'], row['lon']], tiles='Stamen Toner',popup=popup).add_to(marker_cluster)#将水滴点添加到图层内     
    #folium.RegularPolygonMarker([row["lat"], row["lon"]], popup="{0}:{1}".format(row["cities"], row["GDP"]),number_of_sides=10,radius=5).add_to(marker_cluster)
    
    World_map.save(sav_path)#储存整个项目

    webbrowser.open(sav_path)#用默认浏览器打开路径
    #display(World_map)#展示这个H5
    return World_map

if __name__=='__main__':
    dic=[{'lat':39.9683939896909 ,'lon':116.288813699693,'picturepath':'1.jpg'},
    {'lat': 39.9683932702333,'lon':116.289392940432,'picturepath':'2.jpg'}
        ]
    for i in range(40):
        dic.append({'lat': 39.9683932702333+i*0.00001,'lon':116.289392940432,'picturepath':'2.jpg'})
    df=pd.DataFrame(dic)
    sav_path="t.html"
    for index,row in df.iterrows():
        print(index)
    draw_on_map(df,sav_path)


# In[ ]:




