#!/usr/bin/env python
# coding: utf-8

# In[1]:


#by:WIKI CHOu
#04/11/2020

import folium
import folium.plugins as plugins
import os
import numpy as np


# In[2]:


"""df 每一行记录代表一个点  包含 lon lat  和picturepath 三个数据"""
def draw_on_map(df,sav_path):
    sav_path="t.html"
    
    
    World_map = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=15)
    marker_cluster = plugins.MarkerCluster().add_to(World_map)
    for index, row in df:
        
   
        popup = folium.Popup('<img src="'+row['picturepath']+'" alt="'+index+'">')
        folium.Marker([row['lat'], row['lon']], tiles='Stamen Toner',popup=popup).add_to(marker_cluster)     
    #folium.RegularPolygonMarker([row["lat"], row["lon"]], popup="{0}:{1}".format(row["cities"], row["GDP"]),number_of_sides=10,radius=5).add_to(marker_cluster)
    
    World_map.save(sav_path)
    display(World_map)
    return World_map


# In[9]:





# In[ ]:




