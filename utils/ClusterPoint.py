
import numpy as np
import os
import glob
from osgeo import gdal
from osgeo import ogr,osr
from gdal import gdalconst
import time
from osgeo import ogr, osr
import os

import matplotlib.pyplot as plt

time_start = time.time()

# 根据时间自动分割成若干个点簇。生成点簇和孤立点。
# 点簇：
# DataSet：[[1601971472 1601971473],[1601971456 1601971457],....]
# SimplePoint: [[1601970890],[1601970888]]
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
    print("Array Max:",Array.max())
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

    for i,it in enumerate(DataSet):
        DataSet[i] = it + oringin

    return DataSet,SimplePoint+ oringin


# 读入点簇或者孤立点，输出成shp格式
def CreatSetPoint(ListDataset,inshp,outshp):
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

    print(time.time()-time_start)
    OutList = []
    Outgeomlist = []
    for i,it in enumerate(ListDataset):
        for j,item in enumerate(reclist):
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


# 读入点簇，根据label的分类，将每个点簇生成一个矩形
def CreatRect(inshp,outshp):
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
    geomtype = ogr.wkbPolygon  # 几何对象类型（wkbPoint, wkbLineString, wkbPolygon）
    # print(in_geomtype,type(in_geomtype))
    # exit()
    layer = ds.CreateLayer(outshp[:-4], srs=in_spatialref, geom_type=geomtype)
    # fields

    List = []
    for j, item in enumerate(reclist):
        List.append(item['label'])
        # print(item)

    Maxnumber = max(List)+1

    BigList = []
    for i in range(Maxnumber):
        BigList.append([])

    print(time.time() - time_start)
    OutList = []
    Outgeomlist = []

    for j, item in enumerate(reclist):
        label = item['label']
        BigList[label].append([item['Lon'],item['Lat']])


    for pointset in BigList:
        pointset = np.asarray(pointset)
        MaxX,MaxY = np.max(pointset,axis=0)
        MinX, MinY = np.min(pointset, axis=0)

        outFeature = ogr.Feature(layer.GetLayerDefn())

        ring = ogr.Geometry(ogr.wkbLinearRing)  # 构建几何类型:线
        ring.AddPoint(MinX, MinY)  # 添加点01
        ring.AddPoint(MaxX, MinY)  # 添加点02
        ring.AddPoint(MaxX,MaxY)  # 添加点03
        ring.AddPoint(MinX,MaxY)  # 添加点04
        ring.AddPoint(MinX, MinY)  # 添加点01
        yard = ogr.Geometry(ogr.wkbPolygon)
        yard.AddGeometry(ring)


        outFeature.SetGeometry(yard)

        layer.CreateFeature(outFeature)
    ds.Destroy()


if __name__ == '__main__':


    inshp = 'Data/20201006_carvideo_orig.shp'
    Dataset,simple = CreatSential(inshp)

    for item in Dataset:
        print(item)
    exit()

    if not os.path.exists('Output/'): os.makedirs('Output/')

    outshp1 = 'Output/ClusterPoint.shp'
    outshp2 = 'Output/SimplePoint.shp'

    # CreatSetPoint(Dataset,inshp,outshp1)
    # CreatSetPoint(simple,inshp,outshp2)

    outrectshp = 'Output/ClusterRect.shp'
    CreatRect(outshp1,outrectshp)
    pass
