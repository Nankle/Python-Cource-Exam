from osgeo import ogr, osr
import os
import time
from tqdm import tqdm
import sys, math
import numpy as np

Road_Intersection_Path = \
    '/Users/yunsheng666/Documents/GitHub/Python-Cource-Exam/data/traffic_intersection_zhongguancun.shp'


class SHAPE:

    #读ArcGIS Shape文件
    def read_shp(self, filename):
        ds = ogr.Open(filename, False)  #代开Shape文件（False - read only, True - read/write）
        layer = ds.GetLayer(0)   #获取图层
        # layer = ds.GetLayerByName(filename[-4:])

        spatialref = layer.GetSpatialRef() #投影信息
        lydefn = layer.GetLayerDefn() #图层定义信息

        geomtype = lydefn.GetGeomType() #几何对象类型（ogr.wkbPoint, ogr.wkbLineString, ogr.wkbPolygon）

        fieldlist = [] #字段列表 （字段类型，ogr.OFTInteger, ogr.OFTReal, ogr.OFTString, ogr.OFTDateTime）
        for i in range(lydefn.GetFieldCount()):
            fddefn = lydefn.GetFieldDefn(i)
            fddict = {'name':fddefn.GetName(),'type':fddefn.GetType(),
                      'width':fddefn.GetWidth(),'decimal':fddefn.GetPrecision()}
            fieldlist += [fddict]

        geomlist, reclist = [], [] #SF数据记录 – 几何对象及其对应属性
        feature = layer.GetNextFeature() #获得第一个SF，横着是一条feature
        while feature is not None:
            geom = feature.GetGeometryRef()
            geomlist += [geom.ExportToWkt()]
            rec = {}
            for fd in fieldlist:
                rec[fd['name']] = feature.GetField(fd['name'])
            reclist += [rec]
            feature = layer.GetNextFeature()

        ds.Destroy()  # 关闭数据源

        return spatialref,geomtype,geomlist,fieldlist,reclist


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

        if len(self.PC) != 0:
            for i in range(len(self.PC)):
                heading_sum = 0
                for j in self.PC[i]:
                    heading_sum = heading_sum + j['heading']
                heading_mean = heading_sum/(len(self.PC[i]))
                if heading_mean > 315 or heading_mean <= 45:
                    for j in self.PC[i]:
                        list1.append(j['type'])
                if heading_mean > 45 and heading_mean <= 135:
                    for j in self.PC[i]:
                        list2.append(j['type'])
                if heading_mean > 135 and heading_mean <= 225:
                    for j in self.PC[i]:
                        list3.append(j['type'])
                if heading_mean > 225 and heading_mean <= 315:
                    for j in self.PC[i]:
                        list4.append(j['type'])
            dict1, arr1 = typediv(list1)
            dict2, arr2 = typediv(list2)
            dict3, arr3 = typediv(list3)
            dict4, arr4 = typediv(list4)
            self.RI_intersection = np.concatenate((arr1, arr2, arr3, arr4), 0).reshape(-1, 4)

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
        '/Users/yunsheng666/Documents/GitHub/Python-Cource-Exam/OutPut/ClusterPoint.shp')

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
    final_intersection_arr = np.zeros((4, 4), dtype=np.int)
    for index, RI_Item in enumerate(RI):
        # print(f'Road_Intersection[{ii}]:')
        RI_Item.Generate_Drive_type()
        if RI_Item.RI_intersection.shape[0] == 0:
            tem = index * np.ones((4, 4), dtype=np.int)
            final_intersection_arr = np.concatenate((final_intersection_arr, tem), 0)
            continue
        final_intersection_arr = np.concatenate((final_intersection_arr, RI_Item.RI_intersection), 0)
        ii += 1
        if ii == 40:
            RI_Item.Generate_copywrite()
    # print(final_intersection_arr[4:, :])

    return final_intersection_arr[4:, :].reshape(46, 4, 4)


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


"""按时间点 合并道路类型   roll up on type"""
"""只有三类完全不相关 左转 右转 直行 掉头 最优可4个字节表达   先使用四个开关实现"""
# cardf
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


if __name__ == "__main__":
    test = SHAPE()
    spatialref, geomtype, geomlist, fieldlist, reclist = test.read_shp(
        '/Users/yunsheng666/Documents/GitHub/Python-Cource-Exam/OutPut/ClusterPoint.shp')

    RI, intersection = Read_Road_Intersection(Road_Intersection_Path)
    print('交叉口经纬度')     # 每个道路交叉口及其经纬度，共46个
    print(intersection)
    Point_Cluster = []
    Final_Result = Parse_Model(RI, Point_Cluster)
    print('交叉口对应的道路方向及其规则')
    print(Final_Result)     # 46*4*4的矩阵，46代表每个道路交叉口，4*4矩阵中每行代表一个方向(从正北开始顺时针转，四个方向)
                            # 每列代表是否能通行(依次是左转，右转，直行，拐弯；0代表不能通行，1代表可以通行）