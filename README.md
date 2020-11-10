# Python-Cource-Exam
## Exam of python space analysis-2020.10.15

 == Let's do it
 
 ![Data Vision](https://github.com/Nankle/Python-Cource-Exam/blob/main/%E6%95%B0%E6%8D%AE%E5%BF%AB%E8%A7%86%E5%9B%BE.png)
 
## Explanation of project folders: 
 
utils : Function Modules<br>
data  : Work Data<br>

  | File Name                 | 文件描述                                     | 主要字段与含义 |
  | :----:                    | :----:                                      | :----: |
  |20201006_carvideo_orig.shp | 行车记录仪采样数据，包含采集到的路边标线类型，观测点 | GPSTime 、Type（11种)|
  |road_zhongguancun.shp      | 道路线目标矢量文件                             | None |
  |tracking_points_heading.shp| 行车轨迹点数据，包含时间，位置，和行驶朝向 | Time、经纬度、Heading|
  |traffic_intersection_zhongguancun.shp|道路交叉口点数据| 道路交叉口位置点数据 | |
  |zhongguancun.jpg| 实验区航空影像 |None|None|

config: configration of project<br>

## Introduction<br>

### Background<br>
· 北京市道路的转向信息并非固定不变，常会随着政策调整而进行一些变更，这对于一些道路的导航工作造成了较大的困扰。<br>
· 通常伴随转向信息的变更，交通部门也会将道路上的转向标线做相应的变更，例如：不允许左转的区域会把道路左转的标线抹除掉。我们通过行车记录仪采集回来的视频手机路面标线的信息便可以一次性更新道路的转向信息了。<br>
  
  `But`
  
· 虽然采集了道路出现所有出现转线标线的位置与所有的道路路口，但无法进行道路的路口和转向标线的对应，因此无法准确获得每一个路口的转向信息。<br>

### Installation<br>
`git clone https://github.com/Nankle/Python-Cource-Exam` <br>
    completed by Nankle Ztw
**Requirements：**<br>
numpy、OSGEO、Matplotlib、tqdm<br>

## Methods<br>
 `Confirmed`<br>

> 整体思路：· 通过对采集点数据进行时序聚类，生成以连续采集时间段为划分的处理对象，即**点簇**;<br>
> · 创建路口类`Road_Intersection`，将每一个路口视为一个待处理对象;<br>
> · 通过`Parse_Model()`函数，按照规则将点簇归并其所属路口类;<br>
> · 使用路口类成员函数，提取路口的行驶规则，具体步骤如下：<br>


1. 生成以连续时间段为划分的点簇数据，由**20201006_carvideo_orig.shp**中获取，数据组织格式：<br>
`List->Point_Cluster: dtype : Str [PointID, CLuster_ID, Lon, Lat, Type, GPSTime]`<br>

2. 建立Road_Intersection类<br>
读取路口数据生成Object<br>

3. 读取**traffic_intersection_zhongguancun.shp**文件，将每一个道路交叉口生成为一个Road_Intersection类的对象，
构造参数为该交叉口的经纬度。将所有的交叉口对象保存到一个List:RI中。<br>

4. 编写函数**Parse_Model(RI, Point_Cluster)**，目标：解析出属于 每一个道路交叉口对象 的 点簇(PC，Point_Cluster)有哪些,对每一个道路交叉口对象调用<br>
`RI.Generate_Point_Cluster(Point_Cluster_Part)`<br>
成员函数，从而完成归类，即`RI.P_Cluster`属性，为一个List<br>
算法实现思路：通过判断每个点簇中点的GPSTime先后顺序，判断处于时间序列最后的那个点距离哪个道路交叉口最近，并判断是否为驶入该交叉口，通过截断Point_Cluster链表来对每个道路交叉口赋值.<br>

-------------------------------------------------------------------------------------------------------<br>

5. 类的成员函数编写：<br>
```python
·RI.Generate_Point_Cluster(Point_Cluster_Part) #点簇分离归并函数<br>
·RI.Generate_Drive_type() #提取并生成每个路口的行驶规则<br>
```
    每个道路交叉口对象该函数的返回值为：<br>
    List: Grive_Principle(str):<br>
    **[RIID Lon Lat CW1 CW2 CW3 CW4]CWn='0011' 左转 右转 直行 掉头， 0代表允许，1代表禁止**


6. 数据可视化
对生成的道路行驶规则与道路交叉口数据进行可视化展示，具体想怎么做可以自行发挥

7. 文档整理编写


## Task assignment：<br>
 **张天巍** :<br>
  1.获取邻接道路交叉口点<br>
  2.数据解析表格<br>
  3.矢量数据可视化  `Done` **utils.SHAPE class** <br> 
  4.编写md文档

 **陈德跃** :<br>

 **翟富祥** :<br>

 **邹玮杰** :<br>

 **陶诗语 && 罗佩弦** :<br>
``数据结果可视化``

 
 **请大家在utils中增添属于自己的.py文件，用于不同分支任务的完成和模块调用**
 
## Reference
Scikit-Learn : https://scikit-learn.org/stable/index.html<br>
[How to edit Readme.md](https://blog.csdn.net/Kaitiren/article/details/38513715)<br>
[How to pull requst to updata ur own code](https://www.jianshu.com/p/ebad936fac4d)<br>
[Frequently-used command in github](https://blog.csdn.net/wjh2622075127/article/details/87900006?utm_medium=distribute.pc_aggpage_search_result.none-task-blog-2~all~baidu_landing_v2~default-1-87900006.nonecase&utm_term=github%20pull%20%E5%91%BD%E4%BB%A4&spm=1000.2123.3001.4430)<br>
[bad mf](https://blog.csdn.net/qq_31796651/article/details/80803599?utm_medium=distribute.pc_aggpage_search_result.none-task-blog-2~all~first_rank_v2~rank_v25-3-80803599.nonecase&utm_term=github%E4%B8%AD%E7%9A%84readme%E6%B7%BB%E5%8A%A0%E8%A1%A8%E6%A0%BC&spm=1000.2123.3001.4430)<br>