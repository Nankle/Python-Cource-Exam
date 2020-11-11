import numpy as np
import os
import glob
from osgeo import gdal
from osgeo import ogr, osr
from gdal import gdalconst
import time
from osgeo import ogr, osr
import os
from math import cos,sin,pi

import matplotlib.pyplot as plt

time_start = time.time()



"""
输入：
Seat:
rule: 5x4

输出: Polygon
"""

# 绕指定点旋转的旋转函数
def RotatePoint(corerate_point,point,angle):
    angle = angle/180*pi
    # print(angle)
    r_matrix = np.asarray([[cos(angle),-sin(angle)],
                           [sin(angle), cos(angle)]])
    corerate_point = np.asarray(corerate_point)
    point = np.asarray(point)

    new_point = np.dot(r_matrix,(point-corerate_point))+corerate_point
    return new_point
    # print(new_point)

def RotatePointList(corerate_point,pointlist,angle):
    newlist = []
    for point in pointlist:
        newlist.append(RotatePoint(corerate_point,point,angle))
    return np.asarray(newlist)

def DrawPoint_Direct(Seat, rule):
    Direct = rule[0]
    if Direct == -1:
        return None

    Direct_number = rule[1:].sum()
    New_Seat = []
    unit = np.asarray([0.00119714, 0.00097229])/ 25

    startpoint = Seat - np.asarray([0,unit[1]])*8 - np.asarray([unit[0],0])*Direct_number + np.asarray([unit[0],0])/2
    for i in range(Direct_number):
        New_Seat.append(startpoint+np.asarray([unit[0],0])*i*2)

    LineList = []
    seat = 0
    '''左转 右转 直行 掉头'''
    if rule[1]:
        Position = New_Seat[seat]

        # 直线
        point1 = Position + np.asarray([unit[0],0])*4/5
        point2 = Position
        point3 = Position - np.asarray([unit[0],0])*4/5

        # 折角
        point4 = Position - np.asarray([unit[0],0])*4/5+np.asarray([unit[0],unit[1]])/5
        point5 = Position - np.asarray([unit[0],0])*4/5+np.asarray([unit[0],-unit[1]])/5

        line1 = np.asarray([point1,point2,point3])
        line3 = np.asarray([point4, point3, point5])

        line1 = RotatePointList(Seat,line1,Direct)
        line3 = RotatePointList(Seat,line3,Direct)

        LineList.append(line1)
        LineList.append(line3)
        # plt.plot(line1[:,0],line1[:,1])
        # plt.plot(line3[:, 0], line3[:, 1])
        # plt.show()
        # exit()
        seat+=1

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
        point5 = Position - np.asarray([unit[0], 0]) * 4 / 5  + np.asarray([0, unit[1]]) * 4 / 5
        point6 = Position - np.asarray([unit[0], 0]) * 4 / 5

        point7 = Position - np.asarray([unit[0], 0]) * 4 / 5- np.asarray([0, unit[1]]) * 4 / 5

        # 折角
        point8 = point7 + np.asarray([unit[0], unit[1]]) / 5
        point9 = point7 + np.asarray([-unit[0], unit[1]])/ 5

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
            ring.AddPoint(point[0],point[1])  # 添加点01

        yard.AddGeometry(ring)
    yard.CloseRings()

    return yard

def DrawRoadSection(inshp_road, Bigrule, outshp):
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

    for i,point in enumerate(pointlist):
        four_rule = Bigrule[i]

        for rule in four_rule:
            # print(rule)
            # exit()
            outFeature = ogr.Feature(layer.GetLayerDefn())
            yard = DrawPoint_Direct(point,rule)
            if yard is None:
                continue
            outFeature.SetGeometry(yard)
            layer.CreateFeature(outFeature)

    ds.Destroy()



if __name__ == '__main__':
    Bigrule = np.ones((46, 4, 5)).astype(np.int)
    # Bigrule = np.zeros((4, 5))
    data = np.asarray([0, 90, 180, 270])
    Bigrule[:,:, 0] = data
    DrawRoadSection('../data/traffic_intersection_zhongguancun.shp', Bigrule, '../OutPut/Visual.shp')
    # polygon = DrawPoint_Direct()
    # DrawPoint_Direct(0,0)
    pass
