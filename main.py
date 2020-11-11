

from util_tool import *


'''
1、处理地面标志点。将地面标志点划分点簇，获取连续的点簇片段。
2、对点簇片段进行判断，获取每个点簇归属的十字路口点。
3、判断十字路口的来车方向以及转向规则。
4、根据十字路口的转向规则、来车方向以及中心点位置绘制路口转向图

成果1：shp格式的每个路口的转向规则表格。
成果2：每个路口的转向示意图
'''
if __name__ == '__main__':
    '''为地面标志点添加方向，运行一次即可，会更改output.shp'''
    # inheading = 'Data/tracking_points_heading.shp'
    # outshp = 'Data/20201006_carvideo_orig.shp'
    # Getheading(inheading,outshp)


    inshp = 'Data/20201006_carvideo_orig.shp'
    Dataset, _ = CreatSential(inshp)

    if not os.path.exists('Output/'): os.makedirs('Output/')
    outshp1 = 'Output/ClusterPoint.shp'

    ''' 创建点簇shp '''
    CreatSetPoint(Dataset, inshp, outshp1)

    ''' 将点簇生成可视化矩形，仅用作检查 '''
    # outrectshp = 'Output/ClusterRect.shp'
    # CreatRect(outshp1, outrectshp)

    ''' 读取点簇shp，生成路口规则矩阵 '''
    test = SHAPE()
    Point_Cluster = outshp1
    spatialref, geomtype, geomlist, fieldlist, reclist = test.read_shp(
        Point_Cluster)

    Road_Intersection_Path = 'data/traffic_intersection_zhongguancun.shp'
    RI, intersection = Read_Road_Intersection(Road_Intersection_Path)
    print('交叉口经纬度')  # 每个道路交叉口及其经纬度，共46个
    print(intersection.shape)
    # print(intersection[0])
    Final_Result = Parse_Model(RI, Point_Cluster)
    # 46*4*5的矩阵，46代表每个道路交叉口，4*4矩阵中每行代表一个方向(从正北开始顺时针转，四个方向)
    # 每列代表是否能通行(依次是左转，右转，直行，拐弯；0代表不能通行，1代表可以通行）
    print(Final_Result.shape)

    print(time.time()-time_start)

    outdir = 'OutPhoto'




    #读取规则矩阵，生成路口转向图片
    for i,data in enumerate(Final_Result):
        # temp_data = np.zeros((4,5))
        # temp_data[:,0] = np.asarray([0,90,180,270])
        # temp_data[:,1:5] = data
        print(data.shape)

        Important = False
        for j,item in enumerate(data):
            if item[1:].sum()<=0:

                continue
            Important = True

        # print(np.nonzero(data))
        if not Important:
            d = np.zeros((747,633))
            cv2.imwrite(os.path.join(outdir, str(i) + ".png"),d)
            continue
        DrawRoadSection(data,outdir,str(i))

    sav_path = os.path.join(outdir,'index.html')
    df = [{'lon':item[0],'lat':item[1],'picturepath':os.path.join(outdir, str(i) + ".png")}for i,item in enumerate(intersection)]
    # df=[{'lat':39.9683939896909 ,'lon':116.288813699693,'picturepath':'1.jpg'},
    # {'lat': 39.9683932702333,'lon':116.289392940432,'picturepath':'2.jpg'}]
    df=pd.DataFrame(df)
    print(df)

    # import pandas as pd
    # df=pd.DataFrame([df])
    draw_on_map(df, sav_path)
    


    ''' 
    #读取规则矩阵，生成路口转向规则shape
    Bigrule = Final_Result.astype(np.int)
    DrawRoadSection(Road_Intersection_Path, Bigrule, 'OutPut/Visual1.shp')
    '''