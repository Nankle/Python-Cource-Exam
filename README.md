# Python-Cource-Exam
## Exam of python space analysis-2020.10.15

 == Let's do it
 
 ![Data Vision](https://github.com/Nankle/Python-Cource-Exam/blob/main/%E6%95%B0%E6%8D%AE%E5%BF%AB%E8%A7%86%E5%9B%BE.png)
 
## Explanation of project folders: 
 
utils : Function Modules<br>
data  : Work Data<br>
config: configration of project<br>

## Introduction<br>

### Background<br>
· 北京市道路的转向信息并非固定不变，常会随着政策调整而进行一些变更，这对于一些道路的导航工作造成了较大的困扰。<br>
· 通常伴随转向信息的变更，交通部门也会将道路上的转向标线做相应的变更，例如：不允许左转的区域会把道路左转的标线抹除掉。我们通过行车记录仪采集回来的视频手机路面标线的信息便可以一次性更新道路的转向信息了。<br>
  
  `But`
  
· 虽然采集了道路出现所有出现转线标线的位置与所有的道路路口，但无法进行道路的路口和转向标线的对应，因此无法准确获得每一个路口的转向信息。<br>
  
### Plan A 

  1、	根据所有路口的位置，生成Vorinio三角形与泰森多边形。<br>
  2、	根据Vorionio三角形，获取每个路口邻接的其他路口。<br>
  3、	根据泰森多边形，获取在此范围内的转向信息点。<br>
  4、	将范围内所有信息点与道路中心点比较，获取各个方向所有指向道路中心点的信息点。<br>
  5、	查询我们没有覆盖到的点情况，直行情况不必理会，非直行的情况进行异常情况的处理，这一节具体事务视情况而定。<br>
  6、	将情况缩小路口的其中一个方向，只讨论每条道路可否进行相应转向，那么如实记录所有信息点，查看是否可以左转、右转、掉头与直行即可。<br>
  7、 将获取的结果写入路口属性表，对每个路口点添加若干属性，采用规定编码格式，编码格式可以讨论或自定.<br>
      提供一种思路,例如：该入口一共3个方向来车。使用数字编码，第一位为路口序号，第二位为来车方向，第三位为是否可左转，第四位为是否可右转，第五位为是否可直行，第六位为是否可掉头。编码：701110，意思第7个点0度方向，可以直行，左转、右转，不可转向。<br>
  8、	将获取的道路结果读入，进行制图输出，需要调整几个图标的方向。内容介绍提到：可用统计数字和地图显示。这个可以到时候查下怎么做。<br>

### 讨论
1.  能否通过建立不同路口的拓扑关系建立路口连通性关系表？<br> 
    类似图结构，因为生成多边形后出现如下问题：<br>
    **相邻的多边形可能不存在连通性，即两个路口在生成的多边形结果中具有邻接关系，但实际其中间没有道路联通**`ZTW`<br>

## Methods<br>
 `wait to be confirmed`<br>


## Task assignment：<br>
 **张天巍** :<br>
  1.获取邻接道路交叉口点<br>
  2.数据解析表格<br>

  | File Name | 文件描述 | 主要字段与含义 |
  | :----:| :----: | :----: |
  |20201006_carvideo_orig.shp | 行车记录仪采样数据，包含采集到的路边标线类型，观测点|GPSTime 、Type（11种）
  |road_zhongguancun.shp | 道路线目标矢量文件 | None |
  |tracking_points_heading.shp| 行车轨迹点数据，包含时间，位置，和行驶朝向 | Time、经纬度、Heading|
  |traffic_intersection_zhongguancun.shp|道路交叉口点数据| 道路交叉口位置点数据 | |
  |zhongguancun.jpg| 实验区卫星数据 |None|None|

  3.矢量数据可视化  `Done` **utils.SHAPE class** <br> 

 **陈德跃** :<br>

 **翟富祥** :<br>
  1.生成Vorionio三角形<br>

 **邹玮杰** :<br>

 **陶诗语** :<br>

 **罗佩弦** :<br>
 
 **请大家在utils中增添属于自己的.py文件，用于不同分支任务的完成和模块调用**
 
## Reference
Scikit-Learn : https://scikit-learn.org/stable/index.html<br>
[How to edit Readme.md](https://blog.csdn.net/Kaitiren/article/details/38513715)<br>
[How to pull requst to updata ur own code](https://www.jianshu.com/p/ebad936fac4d)<br>
[Frequently-used command in github](https://blog.csdn.net/wjh2622075127/article/details/87900006?utm_medium=distribute.pc_aggpage_search_result.none-task-blog-2~all~baidu_landing_v2~default-1-87900006.nonecase&utm_term=github%20pull%20%E5%91%BD%E4%BB%A4&spm=1000.2123.3001.4430)<br>
[bad mf](https://blog.csdn.net/qq_31796651/article/details/80803599?utm_medium=distribute.pc_aggpage_search_result.none-task-blog-2~all~first_rank_v2~rank_v25-3-80803599.nonecase&utm_term=github%E4%B8%AD%E7%9A%84readme%E6%B7%BB%E5%8A%A0%E8%A1%A8%E6%A0%BC&spm=1000.2123.3001.4430)<br>