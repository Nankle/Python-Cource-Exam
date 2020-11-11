import numpy as np
import os
import glob
from osgeo import gdal
from osgeo import ogr, osr
from gdal import gdalconst
import time
from osgeo import ogr, osr
import os
from tqdm import tqdm
import sys
import matplotlib.pyplot as plt
import cv2
import pandas as pd

time_start = time.time()

'''
#############################################################################################################
###########################################========--获取规则点簇--========###################################
#############################################################################################################
输入：带有gpstim的地面规则点
输出：带有gpstim的地面规则点，在该数据集基础上排除了孤立时间点，增强了属性label，同一label表示属于一类
完成者：陈德跃
'''


def CreatSential(shp):
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(shp, 1)
    layer = dataSource.GetLayer()

    # set 集合对每个数值只会保留一次
    Array = set()
    for feature in layer:
        t = feature.GetField('gpstim')
        Array.add(t)

    Array = np.asarray(sorted(Array)).astype(int)
    oringin = Array.min()
    Array = Array - Array.min()

    # AgglomerativeClustering  层次聚类，每次合并两个距离最近的点。
    # print(Array.max())
    # exit()

    # TODO: 需要优化成动态的数字
    print("Array Max:", Array.max())
    Data = np.zeros((5600,))
    Data[Array] = 1

    DataSet = []
    SimplePoint = []

    templist = []
    for i, item in enumerate(Data):
        if item:
            templist.append(i)
        else:
            if len(templist) > 1:
                # print(len(templist))
                DataSet.append(templist)
                templist = []
            elif len(templist) > 0:
                SimplePoint.append(templist)
                templist = []
            else:
                templist = []

    for i, it in enumerate(DataSet):
        DataSet[i] = it + oringin

    return DataSet, SimplePoint + oringin


# 读入点簇或者孤立点，输出成shp格式
def CreatSetPoint(ListDataset, inshp, outshp):
    in_ds = ogr.Open(inshp, False)  # False - read only, True - read/write
    in_layer = in_ds.GetLayer(0)
    in_lydefn = in_layer.GetLayerDefn()
    in_spatialref = in_layer.GetSpatialRef()
    in_geomtype = in_lydefn.GetGeomType()
    fieldlist = []
    for i in range(in_lydefn.GetFieldCount()):
        fddefn = in_lydefn.GetFieldDefn(i)
        fddict = {'name': fddefn.GetName(), 'type': fddefn.GetType(),
                  'width': fddefn.GetWidth(), 'decimal': fddefn.GetPrecision()}
        fieldlist += [fddict]

    geomlist = []
    reclist = []
    feature = in_layer.GetNextFeature()
    while feature is not None:
        geom = feature.GetGeometryRef()
        geomlist += [geom.ExportToWkt()]
        rec = {}
        for fd in fieldlist:
            rec[fd['name']] = feature.GetField(fd['name'])
        reclist += [rec]
        feature = in_layer.GetNextFeature()
    # close
    in_ds.Destroy()

    '''
      #  ------------------------------打开读取属性完毕，开始写出--------------------------
    '''

    driver = ogr.GetDriverByName("ESRI Shapefile")
    if os.access(outshp, os.F_OK):
        driver.DeleteDataSource(outshp)

    ds = driver.CreateDataSource(outshp)
    layer = ds.CreateLayer(outshp[:-4], srs=in_spatialref, geom_type=in_geomtype)
    # fields

    fddict = {'name': 'label', 'type': ogr.OFTInteger,
              'width': 13, 'decimal': 11}
    fieldlist += [fddict]

    for fd in fieldlist:
        field = ogr.FieldDefn(fd['name'], fd['type'])
        if 'width' in fd:
            field.SetWidth(fd['width'])
        if 'decimal' in fd:
            field.SetPrecision(fd['decimal'])

        # print(fd['name'],fd['width'],fd['decimal'])
        layer.CreateField(field)

    print(time.time() - time_start)
    OutList = []
    Outgeomlist = []
    for i, it in enumerate(ListDataset):
        for j, item in enumerate(reclist):
            if int(item['gpstim']) in it:
                item["label"] = i
                OutList.append(item)
                Outgeomlist.append(geomlist[j])
                # reclist[j] = item
    # print(time.time()-time_start)
    # print(fieldlist,len(OutList),len(Outgeomlist))
    # exit()
    for i in range(len(OutList)):
        geom = ogr.CreateGeometryFromWkt(Outgeomlist[i])
        feat = ogr.Feature(layer.GetLayerDefn())
        feat.SetGeometry(geom)
        for fd in fieldlist:
            feat.SetField(fd['name'], OutList[i][fd['name']])
        layer.CreateFeature(feat)
    # close
    ds.Destroy()


def Getheading(inshp, outshp):
    in_ds = ogr.Open(inshp, False)  # False - read only, True - read/write
    in_layer = in_ds.GetLayer(0)
    in_lydefn = in_layer.GetLayerDefn()
    fieldlist = []
    for i in range(in_lydefn.GetFieldCount()):
        fddefn = in_lydefn.GetFieldDefn(i)
        fddict = {'name': fddefn.GetName(), 'type': fddefn.GetType(),
                  'width': fddefn.GetWidth(), 'decimal': fddefn.GetPrecision()}
        fieldlist += [fddict]

    reclist = {}
    feature = in_layer.GetNextFeature()
    while feature is not None:
        gpstim = feature.GetField('tim')
        heading = feature.GetField('heading')
        reclist[gpstim] = heading
        feature = in_layer.GetNextFeature()
    in_ds.Destroy()

    out_ds = ogr.Open(outshp, True)  # False - read only, True - read/write
    out_layer = out_ds.GetLayer(0)
    out_lydefn = out_layer.GetLayerDefn()
    field = ogr.FieldDefn('heading', ogr.OFTReal)
    field.SetWidth(18)
    field.SetPrecision(11)

    print(out_lydefn.GetFieldIndex('heading'))
    if out_lydefn.GetFieldIndex('heading') == -1:
        out_layer.CreateField(field)

    feature = out_layer.GetNextFeature()
    while feature is not None:
        gpstim = feature.GetField('gpstim')
        heading = reclist[gpstim]
        print(heading)
        feature.SetField('heading', heading)
        out_layer.SetFeature(feature)

        feature = out_layer.GetNextFeature()

    out_ds.Destroy()


# 读入点簇，根据label的分类，将每个点簇生成一个矩形
def CreatRect(inshp, outshp):
    in_ds = ogr.Open(inshp, False)  # False - read only, True - read/write
    in_layer = in_ds.GetLayer(0)
    in_lydefn = in_layer.GetLayerDefn()
    in_spatialref = in_layer.GetSpatialRef()
    in_geomtype = in_lydefn.GetGeomType()
    fieldlist = []
    for i in range(in_lydefn.GetFieldCount()):
        fddefn = in_lydefn.GetFieldDefn(i)
        fddict = {'name': fddefn.GetName(), 'type': fddefn.GetType(),
                  'width': fddefn.GetWidth(), 'decimal': fddefn.GetPrecision()}
        fieldlist += [fddict]

    geomlist = []
    reclist = []
    feature = in_layer.GetNextFeature()
    while feature is not None:
        geom = feature.GetGeometryRef()
        geomlist += [geom.ExportToWkt()]
        rec = {}
        for fd in fieldlist:
            rec[fd['name']] = feature.GetField(fd['name'])
        reclist += [rec]
        feature = in_layer.GetNextFeature()
    # close
    in_ds.Destroy()

    driver = ogr.GetDriverByName("ESRI Shapefile")
    if os.access(outshp, os.F_OK):
        driver.DeleteDataSource(outshp)

    ds = driver.CreateDataSource(outshp)
    geomtype = ogr.wkbPolygon  # 几何对象类型（wkbPoint, wkbLineString, wkbPolygon）
    # print(in_geomtype,type(in_geomtype))
    # exit()
    layer = ds.CreateLayer(outshp[:-4], srs=in_spatialref, geom_type=geomtype)
    # fields

    List = []
    for j, item in enumerate(reclist):
        List.append(item['label'])
        # print(item)

    Maxnumber = max(List) + 1

    BigList = []
    for i in range(Maxnumber):
        BigList.append([])

    print(time.time() - time_start)
    OutList = []
    Outgeomlist = []

    for j, item in enumerate(reclist):
        label = item['label']
        BigList[label].append([item['Lon'], item['Lat']])

    for pointset in BigList:
        pointset = np.asarray(pointset)
        MaxX, MaxY = np.max(pointset, axis=0)
        MinX, MinY = np.min(pointset, axis=0)

        outFeature = ogr.Feature(layer.GetLayerDefn())

        ring = ogr.Geometry(ogr.wkbLinearRing)  # 构建几何类型:线
        ring.AddPoint(MinX, MinY)  # 添加点01
        ring.AddPoint(MaxX, MinY)  # 添加点02
        ring.AddPoint(MaxX, MaxY)  # 添加点03
        ring.AddPoint(MinX, MaxY)  # 添加点04
        ring.AddPoint(MinX, MinY)  # 添加点01
        yard = ogr.Geometry(ogr.wkbPolygon)
        yard.AddGeometry(ring)

        outFeature.SetGeometry(yard)

        layer.CreateFeature(outFeature)
    ds.Destroy()


'''
#############################################################################################################
###########################################========--点簇对应路口点--========################################
#############################################################################################################
输入：点簇的shp
输出：规则矩阵
完成者：张天巍、翟富祥
'''

"""按时间点 合并道路类型   roll up on type"""
"""只有三类完全不相关 左转 右转 直行 掉头 最优可4个字节表达   先使用四个开关实现"""


def typediv(typelist):  # 根据type 将数据整合
    div = {"l": 0, "r": 0, "s": 0, "t": 0}
    dir_arr = np.array([0, 0, 0, 0])
    for tp in typelist:
        if tp == 0:
            div['l'] = 1
            dir_arr[0] = 1
        elif tp == 1:
            div['r'] = 1
            dir_arr[1] = 1
        elif tp == 2:
            div['s'] = 1
            dir_arr[2] = 1
        elif tp == 3:
            div['t'] = 1
            dir_arr[3] = 1
        elif tp == 4:
            div['l'] = 1
            div['r'] = 1
            dir_arr[0] = 1
            dir_arr[1] = 1
        elif tp == 5:
            div['l'] = 1
            div['r'] = 1
            div['s'] = 1
            dir_arr[0] = 1
            dir_arr[1] = 1
            dir_arr[2] = 1
        elif tp == 6:
            div['r'] = 1
            div['s'] = 1
            dir_arr[1] = 1
            dir_arr[2] = 1
        elif tp == 7:
            div['l'] = 1
            div['s'] = 1
            dir_arr[0] = 1
            dir_arr[2] = 1
        elif tp == 8:
            div['l'] = 1
            div['s'] = 1
            div['t'] = 1
            dir_arr[0] = 1
            dir_arr[2] = 1
            dir_arr[3] = 1
        elif tp == 9:
            div['l'] = 1
            div['t'] = 1
            dir_arr[0] = 1
            dir_arr[3] = 1
        elif tp == 10:
            div['s'] = 1
            div['t'] = 1
            dir_arr[2] = 1
            dir_arr[3] = 1
        else:
            print("erro")

    return div, dir_arr


class SHAPE:
    # 读ArcGIS Shape文件
    def read_shp(self, filename):
        ds = ogr.Open(filename, False)  # 代开Shape文件（False - read only, True - read/write）
        layer = ds.GetLayer(0)  # 获取图层
        # layer = ds.GetLayerByName(filename[-4:])

        spatialref = layer.GetSpatialRef()  # 投影信息
        lydefn = layer.GetLayerDefn()  # 图层定义信息

        geomtype = lydefn.GetGeomType()  # 几何对象类型（ogr.wkbPoint, ogr.wkbLineString, ogr.wkbPolygon）

        fieldlist = []  # 字段列表 （字段类型，ogr.OFTInteger, ogr.OFTReal, ogr.OFTString, ogr.OFTDateTime）
        for i in range(lydefn.GetFieldCount()):
            fddefn = lydefn.GetFieldDefn(i)
            fddict = {'name': fddefn.GetName(), 'type': fddefn.GetType(),
                      'width': fddefn.GetWidth(), 'decimal': fddefn.GetPrecision()}
            fieldlist += [fddict]

        geomlist, reclist = [], []  # SF数据记录 – 几何对象及其对应属性
        feature = layer.GetNextFeature()  # 获得第一个SF，横着是一条feature
        while feature is not None:
            geom = feature.GetGeometryRef()
            geomlist += [geom.ExportToWkt()]
            rec = {}
            for fd in fieldlist:
                rec[fd['name']] = feature.GetField(fd['name'])
            reclist += [rec]
            feature = layer.GetNextFeature()

        ds.Destroy()  # 关闭数据源

        return spatialref, geomtype, geomlist, fieldlist, reclist

    # 写ArcGIS Shape文件
    def write_shp(self, filename, spatialref, geomtype, geomlist, fieldlist, reclist):

        driver = ogr.GetDriverByName("ESRI Shapefile")
        if os.access(filename, os.F_OK):  # 如文件已存在，则删除
            driver.DeleteDataSource(filename)

        ds = driver.CreateDataSource(filename)  # 创建Shape文件

        # spatialref = osr.SpatialReference( 'LOCAL_CS["arbitrary"]' )
        layer = ds.CreateLayer(filename[:-4], srs=spatialref, geom_type=geomtype)  # 创建图层

        for fd in fieldlist:  # 将字段列表写入图层
            field = ogr.FieldDefn(fd['name'], fd['type'])
            if fd.has_key('width'):
                field.SetWidth(fd['width'])
            if fd.has_key('decimal'):
                field.SetPrecision(fd['decimal'])
            layer.CreateField(field)

        for i in range(len(reclist)):  # 将SF数据记录（几何对象及其属性写入图层）
            geom = ogr.CreateGeometryFromWkt(geomlist[i])
            feat = ogr.Feature(layer.GetLayerDefn())  # 创建SF
            feat.SetGeometry(geom)
            for fd in fieldlist:
                feat.SetField(fd['name'], reclist[i][fd['name']])
            layer.CreateFeature(feat)  # 将SF写入图层

        ds.Destroy()  # 关闭文件


# 道路交叉口类，用于进行整体的数据处理封装
class Road_Intersection:

    def __init__(self, Lon, Lat):
        self.lon = Lon  # 道路交叉口经度
        self.lat = Lat  # 道路交叉口纬度
        self.PC = []
        self.RI_intersection = np.array([])
        self.tag = [[24352, 22825, 24013], \
                    [32735, 23500, 31077]]  # 属性表shape

    def Generate_Point_Cluster(self, Point_Cluster_Part):  # 点簇分离归并函数
        self.PC.append(Point_Cluster_Part)

    def Generate_Drive_type(self):  # 提取并生成每个路口的行驶规则
        # print(f'Cluster Number in this RI:{len(self.PC)}')
        # print(f'Lon:{self.lon}', f'Lat:{self.lat}')
        list1 = []
        list2 = []
        list3 = []
        list4 = []
        list1_head = []
        list2_head = []
        list3_head = []
        list4_head = []

        if len(self.PC) != 0:
            for i in range(len(self.PC)):
                heading_sum = 0
                for j in self.PC[i]:
                    heading_sum = heading_sum + j['heading']
                heading_mean = heading_sum/(len(self.PC[i]))
                if heading_mean > 315 or heading_mean <= 45:
                    for j in self.PC[i]:
                        list1.append(j['type'])
                        list1_head.append(j['heading'])
                if heading_mean > 45 and heading_mean <= 135:
                    for j in self.PC[i]:
                        list2.append(j['type'])
                        list2_head.append(j['heading'])
                if heading_mean > 135 and heading_mean <= 225:
                    for j in self.PC[i]:
                        list3.append(j['type'])
                        list3_head.append(j['heading'])
                if heading_mean > 225 and heading_mean <= 315:
                    for j in self.PC[i]:
                        list4.append(j['type'])
                        list4_head.append(j['heading'])
            heading1 = np.asarray(list1_head).mean()
            heading2 = np.asarray(list2_head).mean()
            heading3 = np.asarray(list3_head).mean()
            heading4 = np.asarray(list4_head).mean()
            dict1, arr1 = typediv(list1)
            dict2, arr2 = typediv(list2)
            dict3, arr3 = typediv(list3)
            dict4, arr4 = typediv(list4)
            tem = np.array([0, 0, 0, 0])
            if np.array_equal(arr1, tem):
                heading1 = -1
            if np.array_equal(arr2, tem):
                heading2 = -1
            if np.array_equal(arr3, tem):
                heading3 = -1
            if np.array_equal(arr4, tem):
                heading4 = -1

            heading = np.asarray([heading1, heading2, heading3, heading4])
            temp = np.concatenate((arr1, arr2, arr3, arr4), 0).reshape(-1, 4)

            other = np.zeros((4, 5))
            other[:, 1:] = temp
            other[:, 0] = heading

            self.RI_intersection = other
            # print(dict1, arr1)
            # print(dict2, arr2)
            # print(dict3, arr3)
            # print(dict4, arr4)
            # print('-------')
        else:
            pass
            # print('no intersection')




    def Generate_copywrite(self):
        for t in self.tag:
            print(f'copyright:{chr(t[0])}{chr(t[1])}{chr(t[2])}-->{time.asctime(time.localtime(time.time()))}')
            # print(f'copyright:{time.time()}')


def Parse_Model(RI, Point_Cluster):
    # 读取点簇数据，生成RoadIntersection对象
    PC = SHAPE()
    spatialref, geomtype, geomlist, fieldlist, reclist = PC.read_shp(
        Point_Cluster)

    Label = []
    for i in reclist:
        Label.append(float(i['label']))  # int

    # print(type(Label[0]))
    classes = len(set(Label))
    # print(f'Items Count:{len(reclist)}\nLabels Count:{classes}')

    # DataArray = np.vstack((np.array(Label), np.array(drive_type), np.array(gpstime), \
    #     np.array(Lat), np.array(Lon))).T
    # print(DataArray.shape)
    # print(reclist[0])
    # print(DataArray[])

    classification = []
    # 每个 i 为一类
    for i in tqdm(range(classes), desc='判断每个点簇的归属'):
        # this_class_Point_Class = np.where(DataArray[:, 0]==i)
        this_class_Point_Class = [field for field in reclist if field['label'] == i]   # 同属于第i簇的点拿出来组成this_class
                                                                                       # 包含的信息是 gpstim, lon, lat
        gpstime = []
        Lat = []
        Lon = []

        for item in this_class_Point_Class:
            Lat.append(item['Lat'])  # float
            Lon.append(item['Lon'])  # float
            gpstime.append(item['gpstim'])  # float

        mintime_index = gpstime.index(min(gpstime))
        maxtime_index = gpstime.index(max(gpstime))
        PC_Min_Lat = Lat[mintime_index]
        PC_Min_Lon = Lon[mintime_index]
        PC_Max_Lat = Lat[maxtime_index]
        PC_Max_Lon = Lon[maxtime_index]

        Which_RI = -1
        dis_mintime = 0  # 最小gpstime对应的到各个路口的距离
        dis_maxtime = sys.maxsize  # 最大gpstime对应的到各个路口的距离
        for index, RI_Item in enumerate(RI):
            RI_Lat = RI_Item.lat
            RI_Lon = RI_Item.lon

            maxtime_distance = (PC_Max_Lat - RI_Lat) ** 2 + (PC_Max_Lon - RI_Lon) ** 2
            if maxtime_distance < dis_maxtime:
                dis_maxtime = maxtime_distance
                Which_RI = index
                dis_mintime = (PC_Min_Lat - RI_Lat) ** 2 + (PC_Min_Lon - RI_Lon) ** 2

        if dis_maxtime < dis_mintime:
            # 表示为驶入车辆簇
            classification.append((this_class_Point_Class, Which_RI))
            RI[Which_RI].Generate_Point_Cluster(this_class_Point_Class)

    # print(len(classification))
    # print(type(classification[100]))
    # print(classification[:][1] == 2)

    '''

    找到每一个点簇对应的道路交叉口应该是哪个
    判断条件为：
    1. GPSTime 最后（也就是最大）的那个点，距离最近的那个道路交叉口
    2. GPSTime 最大的那个点，距离道路交叉口的距离应该比Time最小值的点到其的距离小，这样才为驶入路口
    print( ch + " 的ASCII 码为", ord(ch))
    print( uch , " 对应的字符为", chr(uch))
    '''
    ii = 0
    final_intersection_arr = np.zeros((4, 5), dtype=np.int)
    for index, RI_Item in enumerate(RI):
        # print(f'Road_Intersection[{ii}]:')
        RI_Item.Generate_Drive_type()
        if RI_Item.RI_intersection.shape[0] == 0:
            # tem = index * np.ones((4, 5), dtype=np.int)
            tem = np.zeros((4, 5))
            tem[:, 0] = -1
            final_intersection_arr = np.concatenate((final_intersection_arr, tem), 0)
            continue
        final_intersection_arr = np.concatenate((final_intersection_arr, RI_Item.RI_intersection), 0)
        ii += 1
        if ii == 40:
            RI_Item.Generate_copywrite()
    # print(final_intersection_arr[4:, :])

    return final_intersection_arr[4:, :].reshape(46, 4, 5)


def Read_Road_Intersection(path_RI):
    Road_I = SHAPE()
    spatialref, geomtype, geomlist, fieldlist, reclist = Road_I.read_shp(path_RI)
    # print(f'fieldList:\n{fieldlist}')
    # print(f'Road_Intersection_Number:{len(reclist)},type:{type(reclist)}')
    list_RI = []
    intersec_arr = np.zeros((len(reclist), 2))
    for index, RI in enumerate(reclist):
        RI_Lon = float(RI['Lon'])
        RI_Lat = float(RI['Lat'])
        intersec_arr[index, 0] = float(RI['Lon'])
        intersec_arr[index, 1] = float(RI['Lat'])

        list_RI.append(Road_Intersection(RI_Lon, RI_Lat))

    return list_RI, intersec_arr



'''
#############################################################################################################
###########################################========--可视化--========################################
#############################################################################################################
输入：规则矩阵
输出：路口图片
完成者：陶诗语、罗佩弦

输入：路口图片
输出：界面AI
完成者：邹玮杰


'''

import turtle as t
import numpy as np
from PIL import Image


# input:数组，4行5列，每行依次对应右、上、左、下方向，任意一行的每列依次为(0/1)：
# 道路是否存在/角度，是否调头，是否左转，是否直行，是否右转

def DrawRoadSection(Dataarray, outdir, name):
    width = 300

    def DrawRoad(angle):
        t.tracer(False)
        t.penup()
        t.goto(0, 0)
        t.seth(angle)
        t.fd(width / 2)
        t.right(90)
        t.fd(width / 2)
        t.left(90)
        t.pd()
        t.fd(length)
        t.left(90)
        t.penup()
        t.fd(width)
        t.left(90)
        t.pd()
        t.fd(length)
        t.penup()

    def Drawline(angle):
        t.tracer(False)
        t.penup()
        t.goto(0, 0)
        t.seth(angle)
        t.fd(width / 2)
        t.right(90)
        t.fd(width / 2)
        t.left(180)
        t.pd()
        t.fd(width)
        t.penup()

    # 右转
    def GoRight(a, b):
        # 依据路口设置颜色
        if a == 0:
            t.color("white", "red")
        elif a == 1:
            t.color("white", "yellow")
        elif a == 2:
            t.color("white", "blue")
        elif a == 3:
            t.color("white", "green")
        t.pensize(2)
        # 设置起点为矩形边框左上角
        t.penup()
        t.forward(118)
        t.lt(90)
        t.fd(b / 6)
        # 绘制箭头
        t.pendown()
        t.begin_fill()
        t.rt(90)
        t.forward(15)
        t.lt(90)
        t.forward(30)
        t.rt(90)
        t.forward(15)
        t.rt(225)
        t.forward(33)
        t.rt(270)
        t.forward(33)
        t.rt(225)
        t.forward(18)
        t.rt(90)
        t.forward(30)
        t.end_fill()
        # 返回矩形左上角
        t.penup()
        t.fd(b / 5)
        t.rt(90)
        t.fd(120)
        t.rt(90)

    # t.exitonclick()

    # 直行
    def GoStraight(a, b):
        # 依据路口设置颜色
        if a == 0:
            t.color("white", "red")
        elif a == 1:
            t.color("white", "yellow")
        elif a == 2:
            t.color("white", "blue")
        elif a == 3:
            t.color("white", "green")
        # 设置起点为矩形边框左上角
        t.penup()
        t.forward(140)
        t.lt(90)
        t.fd(b / 3)
        # 绘制箭头
        t.pendown()
        t.begin_fill()
        t.lt(90)
        t.pensize(2)
        t.rt(90)
        t.forward(15)
        t.lt(90)
        t.forward(30)
        t.rt(90)
        t.forward(15)
        t.rt(225)
        t.forward(33)
        t.rt(270)
        t.forward(33)
        t.rt(225)
        t.forward(18)
        t.rt(90)
        t.forward(30)
        t.end_fill()
        # 返回矩形左上角
        t.penup()
        t.rt(90)
        t.fd(b / 3)
        t.rt(90)
        t.fd(150)
        t.rt(90)

    # 左转
    def GoLeft(a, b):
        # 依据路口设置颜色
        if a == 0:
            t.color("white", "red")
        elif a == 1:
            t.color("white", "yellow")
        elif a == 2:
            t.color("white", "blue")
        elif a == 3:
            t.color("white", "green")
        t.pensize(2)
        # 设置起点为矩形边框左上角
        t.penup()
        t.forward(134)
        t.lt(90)
        t.fd(4 * b / 5)
        # 绘制箭头
        t.pendown()
        t.begin_fill()
        t.lt(90)
        t.forward(15)
        t.lt(90)
        t.forward(30)
        t.rt(90)
        t.forward(15)
        t.rt(225)
        t.forward(33)
        t.rt(270)
        t.forward(33)
        t.rt(225)
        t.forward(18)
        t.rt(90)
        t.forward(30)
        t.end_fill()
        # 返回矩形左上角
        t.penup()
        t.lt(180)
        t.fd(4 * b / 5)
        t.rt(90)
        t.fd(120)
        t.rt(90)

    # t.exitonclick()

    # 掉头
    def GoBack(a, b):
        # 依据路口设置颜色
        if a == 0:
            t.color("white", "red")
        elif a == 1:
            t.color("white", "yellow")
        elif a == 2:
            t.color("white", "blue")
        elif a == 3:
            t.color("white", "green")
        t.pensize(2)
        # 设置起点为矩形边框左上角
        t.penup()
        t.forward(142)
        t.lt(90)
        t.fd(b / 6)
        # 绘制箭头
        t.pendown()
        t.begin_fill()
        t.lt(90)
        t.fd(18)
        t.rt(180)
        t.circle(15, -180)
        t.rt(180)
        t.fd(18)
        t.lt(90)
        t.fd(6)
        t.rt(135)
        t.fd(15)
        t.rt(90)
        t.fd(15)
        t.rt(135)
        t.fd(8)
        t.lt(90)
        t.fd(18)
        t.circle(8, 180)
        t.fd(18)
        t.rt(90)
        t.fd(7)
        t.end_fill()
        # 返回矩形左上角
        t.penup()
        t.fd(b / 3)
        t.rt(90)
        t.fd(142)
        t.rt(90)

    # test = [[0, 1, 1, 1, 1], [90, 1, 1, 1, 1], [180, 1, 1, 1, 1], [270, 1, 1, 1, 1]]
    n = np.array(Dataarray)
    print(n)
    window = t.Screen()  # 获得一个窗口句柄
    window.bgcolor("darkorange")  # 把背景设为蓝色
    # 画布
    t.setup(1000, 1000)
    t.tracer(False)
    # 画笔
    t.pensize(5)
    t.color("black")
    # 画路口
    width = 300
    length = 500

    t.tracer(False)
    t.penup()
    ang = 0
    m = 0
    for i in range(4):
        if n[i][0] >= 0:
            ang += n[i][0] - 90 * i
            m += 1
    MeanAng = int(ang / m)
    # MeanAng = 60
    CurAug = MeanAng
    for i in range(4):
        if n[i][0] >= 0:
            DrawRoad(CurAug)
        else:
            Drawline(CurAug)
        CurAug += 90
    # 绘制每条道路的转向标志
    t.penup()
    t.goto(0, 0)
    t.seth(MeanAng)
    for i in range(4):
        k = 0
        if n[i][0] >= 0:
            for j in range(1, 5):
                if n[i][j] == 1:
                    k += 1
            SignPosW = width / k
            t.penup()
            t.fd(width / 2)
            t.right(90)
            t.fd(width / 2)
            t.left(90)
            if n[i][1] == 1:
                GoBack(i, SignPosW)
                t.penup()
                t.fd(SignPosW)
                t.right(90)
            if n[i][2] == 1:
                GoLeft(i, SignPosW)
                t.penup()
                t.fd(SignPosW)
                t.right(90)
            if n[i][3] == 1:
                GoStraight(i, SignPosW)
                t.penup()
                t.fd(SignPosW)
                t.right(90)
            if n[i][4] == 1:
                GoRight(i, SignPosW)
                t.penup()
                t.fd(SignPosW)
                t.right(90)
        t.penup()
        t.goto(0, 0)
        t.seth(MeanAng + 90 * i + 90)

    # t.exitonclick()
    ts = t.getscreen()

    if not os.path.exists(outdir): os.makedirs(outdir)
    ts.getcanvas().postscript(file=os.path.join(outdir, name + ".eps"))
    im = Image.open(os.path.join(outdir, name + ".eps"))
    im.save(os.path.join(outdir, name + ".png"))
    t.clear()


import folium
import folium.plugins as plugins


def draw_on_map(df, sav_path):
    # sav_path = "t.html"

    World_map = folium.Map(location=[df['lat'].mean(), df['lon'].mean()],
                           zoom_start=15)  # 创建底图，location表示显示地图的中心位置，zoom_start为缩放尺度
    marker_cluster = plugins.MarkerCluster().add_to(World_map)  # marker_cluster 代表一个图层 之后会将点簇添加到这个图层上   相当于在arcgis里面的图层
    for index, row in df.iterrows():  # 遍历数据

        popup = folium.Popup('<img src="' + row['picturepath'] + '" alt="' + str(index) + '">')  # 用H5语句创建水滴点的对象
        folium.Marker([row['lat'], row['lon']], tiles='Stamen Toner', popup=popup).add_to(
            marker_cluster)  # 将水滴点添加到图层内
    # folium.RegularPolygonMarker([row["lat"], row["lon"]], popup="{0}:{1}".format(row["cities"], row["GDP"]),number_of_sides=10,radius=5).add_to(marker_cluster)

    World_map.save(sav_path)  # 储存整个项目

    # webbrowser.open(sav_path)  # 用默认浏览器打开路径
    # display(World_map)#展示这个H5
    return World_map


'''
#############################################################################################################
###########################################========--可视化2--========################################
#############################################################################################################
输入：规则矩阵
输出：路口规则矢量

完成者：陈德跃
'''
from math import cos,sin,pi

# 绕指定点旋转的旋转函数,瞬时针旋转。
def RotatePoint(corerate_point, point, angle):
    angle = -angle / 180 * pi
    # print(angle)
    r_matrix = np.asarray([[cos(angle), -sin(angle)],
                           [sin(angle), cos(angle)]])
    corerate_point = np.asarray(corerate_point)
    point = np.asarray(point)

    new_point = np.dot(r_matrix, (point - corerate_point)) + corerate_point
    return new_point
    # print(new_point)

# corerate_point = [0,0]
# point = [0,-10]
# angle = 90
# newpoint = RotatePoint(corerate_point,point,angle)
# print(newpoint)
# exit()

# 旋转一个点列表
def RotatePointList(corerate_point, pointlist, angle):
    newlist = []
    for point in pointlist:
        newlist.append(RotatePoint(corerate_point, point, angle))
    return np.asarray(newlist)

# 绘制一个方向上的规则
def DrawPoint_Direct(Seat, rule):
    Direct = rule[0]
    if Direct == -1:
        return None

    Direct_number = rule[1:].sum()
    New_Seat = []
    unit = np.asarray([0.00119714, 0.00097229]) / 25

    startpoint = Seat - np.asarray([0, unit[1]]) * 8 - np.asarray([unit[0], 0]) * Direct_number + np.asarray(
        [unit[0], 0]) / 2
    for i in range(Direct_number):
        New_Seat.append(startpoint + np.asarray([unit[0], 0]) * i * 2)

    LineList = []
    seat = 0
    '''左转 右转 直行 掉头'''
    if rule[1]:
        Position = New_Seat[seat]

        # 直线
        point1 = Position + np.asarray([unit[0], 0]) * 4 / 5
        point2 = Position
        point3 = Position - np.asarray([unit[0], 0]) * 4 / 5

        # 折角
        point4 = Position - np.asarray([unit[0], 0]) * 4 / 5 + np.asarray([unit[0], unit[1]]) / 5
        point5 = Position - np.asarray([unit[0], 0]) * 4 / 5 + np.asarray([unit[0], -unit[1]]) / 5

        line1 = np.asarray([point1, point2, point3])
        line3 = np.asarray([point4, point3, point5])

        line1 = RotatePointList(Seat, line1, Direct)
        line3 = RotatePointList(Seat, line3, Direct)

        LineList.append(line1)
        LineList.append(line3)
        # plt.plot(line1[:,0],line1[:,1])
        # plt.plot(line3[:, 0], line3[:, 1])
        # plt.show()
        # exit()
        seat += 1

    if rule[2]:
        Position = New_Seat[seat]

        # 直线
        point1 = Position + np.asarray([unit[0], 0]) * 4 / 5
        point2 = Position
        point3 = Position - np.asarray([unit[0], 0]) * 4 / 5

        # 折角
        point4 = Position + np.asarray([unit[0], 0]) * 4 / 5 - np.asarray([unit[0], unit[1]]) / 5
        point5 = Position + np.asarray([unit[0], 0]) * 4 / 5 - np.asarray([unit[0], -unit[1]]) / 5

        line1 = np.asarray([point1, point2, point3])
        line3 = np.asarray([point4, point1, point5])

        line1 = RotatePointList(Seat, line1, Direct)
        line3 = RotatePointList(Seat, line3, Direct)

        LineList.append(line1)
        LineList.append(line3)
        # plt.plot(line1[:,0],line1[:,1])
        # plt.plot(line3[:, 0], line3[:, 1])
        # plt.show()
        # exit()
        seat += 1

    if rule[3]:
        Position = New_Seat[seat]

        # 直线
        point1 = Position + np.asarray([0, unit[1]]) * 4 / 5
        point2 = Position
        point3 = Position - np.asarray([0, unit[1]]) * 4 / 5

        # 折角
        point4 = Position + np.asarray([0, unit[1]]) * 4 / 5 - np.asarray([unit[0], unit[1]]) / 5
        point5 = Position + np.asarray([0, unit[1]]) * 4 / 5 - np.asarray([-unit[0], unit[1]]) / 5

        line1 = np.asarray([point1, point2, point3])
        line3 = np.asarray([point4, point1, point5])

        line1 = RotatePointList(Seat, line1, Direct)
        line3 = RotatePointList(Seat, line3, Direct)

        LineList.append(line1)
        LineList.append(line3)

        seat += 1

    if rule[4]:
        Position = New_Seat[seat]

        # 直线
        point1 = Position + np.asarray([unit[0], 0]) * 4 / 5 - np.asarray([0, unit[1]]) * 4 / 5
        point2 = Position + np.asarray([unit[0], 0]) * 4 / 5
        point3 = Position + np.asarray([unit[0], 0]) * 4 / 5 + np.asarray([0, unit[1]]) * 4 / 5

        point4 = Position + np.asarray([0, unit[1]]) * 4 / 5
        point5 = Position - np.asarray([unit[0], 0]) * 4 / 5 + np.asarray([0, unit[1]]) * 4 / 5
        point6 = Position - np.asarray([unit[0], 0]) * 4 / 5

        point7 = Position - np.asarray([unit[0], 0]) * 4 / 5 - np.asarray([0, unit[1]]) * 4 / 5

        # 折角
        point8 = point7 + np.asarray([unit[0], unit[1]]) / 5
        point9 = point7 + np.asarray([-unit[0], unit[1]]) / 5

        line1 = np.asarray([point1, point2, point3, point4, point5, point6, point7])
        line3 = np.asarray([point8, point7, point9])

        line1 = RotatePointList(Seat, line1, Direct)
        line3 = RotatePointList(Seat, line3, Direct)

        LineList.append(line1)
        LineList.append(line3)
        # plt.plot(line1[:,0],line1[:,1])
        # plt.plot(line3[:, 0], line3[:, 1])
        # plt.show()
        # exit()
        seat += 1

    yard = ogr.Geometry(ogr.wkbMultiLineString)
    for line in LineList:
        ring = ogr.Geometry(ogr.wkbLinearRing)  # 构建几何类型:线
        for point in line:
            ring.AddPoint(point[0], point[1])  # 添加点01

        yard.AddGeometry(ring)
    yard.CloseRings()

    return yard


def DrawRoadSection2(inshp_road, Bigrule, outshp):
    in_ds = ogr.Open(inshp_road, False)  # False - read only, True - read/write
    in_layer = in_ds.GetLayer(0)

    in_spatialref = in_layer.GetSpatialRef()

    pointlist = []
    feature = in_layer.GetNextFeature()
    while feature is not None:
        geom = feature.GetGeometryRef()
        lon = geom.GetPoints()[0][0]
        lat = geom.GetPoints()[0][1]
        pointlist.append([lon, lat])

        feature = in_layer.GetNextFeature()

    in_ds.Destroy()

    if len(pointlist) != Bigrule.shape[0]:
        print('规则数组和路口要素长度不同,规则数组：{},路口要素：{}'.format(Bigrule.shape[0], len(pointlist)))
        exit()

    '''---------------------------== 接下来创建路口图像 ==------------------------------------'''
    driver = ogr.GetDriverByName("ESRI Shapefile")
    if os.access(outshp, os.F_OK):
        driver.DeleteDataSource(outshp)

    ds = driver.CreateDataSource(outshp)

    in_geomtype = ogr.wkbMultiLineString
    layer = ds.CreateLayer(outshp[:-4], srs=in_spatialref, geom_type=in_geomtype)
    # fields
    fieldlist = []
    fddict = {'name': 'label', 'type': ogr.OFTInteger,
              'width': 13, 'decimal': 11}
    fieldlist += [fddict]

    for fd in fieldlist:
        field = ogr.FieldDefn(fd['name'], fd['type'])
        if 'width' in fd:
            field.SetWidth(fd['width'])
        if 'decimal' in fd:
            field.SetPrecision(fd['decimal'])

        # print(fd['name'],fd['width'],fd['decimal'])
        layer.CreateField(field)

    print(time.time() - time_start)

    # pp = np.asarray(pointlist)
    # a = (pp.max(axis=0)-pp.min(axis=0))/10
    # print(a)
    # exit()

    for i, point in enumerate(pointlist):
        four_rule = Bigrule[i]

        for rule in four_rule:
            # print(rule)
            # exit()
            outFeature = ogr.Feature(layer.GetLayerDefn())
            yard = DrawPoint_Direct(point, rule)
            if yard is None:
                continue
            outFeature.SetGeometry(yard)
            layer.CreateFeature(outFeature)

    ds.Destroy()

