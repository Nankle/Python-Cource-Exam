# Python-Cource-Exam
## Exam of python space analysis-2020.10.15

 == Let's do it
 
 ![Data Vision](https://github.com/Nankle/Python-Cource-Exam/blob/main/%E6%95%B0%E6%8D%AE%E5%BF%AB%E8%A7%86%E5%9B%BE.png)
 
## Explanation of project folders: 
 
utils : 支持该项目的功能函数包集合<br>
data  : 原始数据<br>

  | File Name                 | Description                                     | Meanings |
  | :----:                    | :----:                                      | :----: |
  |20201006_carvideo_orig.shp | 行车记录仪采样数据，包含采集到的路边标线类型，观测点 | GPSTime 、Type（11种)|
  |road_zhongguancun.shp      | 道路线目标矢量文件                             | None |
  |tracking_points_heading.shp| 行车轨迹点数据，包含时间，位置，和行驶朝向 | Time、经纬度、Heading|
  |traffic_intersection_zhongguancun.shp|道路交叉口点数据| 道路交叉口位置点数据 | |
  |zhongguancun.jpg| 实验区航空影像 |None|None|
说明：我们为

config: 配置文件，待更新<br>
OutPut: 中间与最终结果保存<br>
| File Name        |    Meanings     |
| :----:           |    :----:       |
|Visual1.shp       | 生成的矢量方向图   |
|RoadInsection.txt | 路口行驶规则      |


## 1 Introduction<br>

### 1.1 Background<br>
· 北京市道路的转向信息并非固定不变，常会随着政策调整而进行一些变更，这对于一些道路的导航工作造成了较大的困扰。<br>
· 通常伴随转向信息的变更，交通部门也会将道路上的转向标线做相应的变更，例如：不允许左转的区域会把道路左转的标线抹除掉。我们通过行车记录仪采集回来的视频手机路面标线的信息便可以一次性更新道路的转向信息了。<br>
  
  `难点：`
  
· 虽然采集了道路出现所有出现转线标线的位置与所有的道路路口，但无法进行道路的路口和转向标线的对应，因此无法准确获得每一个路口的转向信息。因此本次实验主要需要解决的问题有一下内容：<br>
1. 将提取的行车记录点的，对应到每个路口。
2. 将记录点归类到相应路口方向，提取路口规则。
3. 可视化提取的路口规则。


### 1.2 Installation<br>
**Download first**<br>
`git clone https://github.com/Nankle/Python-Cource-Exam` <br>

if you want to run your own data:
`cd PATH_TO_YOUR_ROOT/PYTHON-COURCE_EXAM/`<br>
`python main.py`<br>


**1.3 Requirements：**<br>
Python library:<br>
numpy<br>
OSGEO<br>
Matplotlib<br>
tqdm<br>
turtle<br>
PIL<br>
Software：Ghostscript<br>
folium<br>


## 2 Methods<br>
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

4. 编写函数**Parse_Model(RI, Point_Cluster)**，目标：解析出属于 **每一个道路交叉口对象** 的 点簇(PC，Point_Cluster)有哪些,对每一个道路交叉口对象调用<br>
`RI.Generate_Point_Cluster(Point_Cluster_Part)`<br>
成员函数，从而完成归类，即`RI.P_Cluster`属性，为一个List<br>
算法实现思路：通过判断每个点簇中点的GPSTime先后顺序，判断处于时间序列最后的那个点距离哪个道路交叉口最近，并判断是否为驶入该交叉口，通过截断Point_Cluster链表来对每个道路交叉口赋值.<br>

-------------------------------------------------------------------------------------------------------<br>

5. 类的成员函数编写：<br>
```python
·RI.Generate_Point_Cluster(Point_Cluster_Part) #点簇分离归并函数<br>
·RI.Generate_Drive_type() #提取并生成每个路口的行驶规则<br>
```
    每个道路交叉口对象的行驶规则保存在RI_intersection中：
    np.array: Grive_Principle(str):
    RI_intersection.shape: [4, 5]
    [
      [Heading ∈ [315˚, 360˚]or[0˚, 45˚], Turn_Left, Turn_Right, Go_Straight, Turn_Around],
      [Heading ∈ [45˚ , 135˚], Turn_Left, Turn_Right, Go_Straight, Turn_Around],
      [Heading ∈ [135˚, 225˚], Turn_Left, Turn_Right, Go_Straight, Turn_Around],
      [Heading ∈ [225˚, 315˚], Turn_Left, Turn_Right, Go_Straight, Turn_Around],
    ]
    即Heading表示路口该方向来车点簇的平均heading值，提取规则结果中如果能够通行则赋值1，不能则赋值0
    示例：
    [23, 1, 1, 1, 0]->路口方向为23˚，可左转、右转、直行，但不可掉头
    [-1, 0, 0, 0, 0]->如出现该形式的数组说明在某个方向不存在路口，也即不存在任何交通规则



6. 数据可视化
info：对生成的道路行驶规则与道路交叉口数据进行可视化展示<br>

**EXAMPLE:**<br>

```python
#将turtle绘图结果保存为当前文件夹下的.eps文件
#用postscript生成图片时，对于.jpg格式，即使生成图片，也因为JPEG标识符段长度太短，导致文件不完整无法打开，故保存为.eps格式，作为中间结果
EpsPic="p"+str(seq)+".eps" #文件名，例：p1.eps
ts=t.getscreen()
ts.getcanvas().postscript(file=EpsPic)
```

```python
#将.eps格式图片转换为.png格式图片
#由于JPEG是有损压缩，会导致生成的图片清晰度较低，因此不保存为.jpg格式，而是.png格式
JpgPic1 = "p"+str(seq)+".png" #文件名，例：p1.png
im = Image.open(EpsPic)
im.load(scale=5)
im.save(JpgPic1,"PNG",quality=95) #quality参数：保存图像的质量，范围从1-95，尽量避免设置高于95的值，若使用默认参数会导致结果图片被压缩
```

```python
#缩小图片到合适尺寸
JpgPic2=str(seq)+".png" #文件名，例：1.png
im=Image.open(JpgPic1)
out=im.resize((300,300),PIL.Image.ANTIALIAS) #缩小图片，设置重采样方法为ANTIALIAS，以保证缩小后的图片有较高的分辨率
out.save(JpgPic2, "PNG", quality=100)
```
<br>

7. 文档整理编写
整理结果，生成解释文档


## 3 Task assignment：<br>

 **张天巍** :<br>
  1. **STEP**2 3 4 5<br>
  2. Make Repository and 

 **陈德跃** :<br>

 **翟富祥** :<br>

 **邹玮杰** :<br>
 以H5的形式将路口通行结果用可交互的方式添加到地图上<br>

 **陶诗语 && 罗佩弦** :<br>
``数据结果可视化``<br>
罗佩弦: 路口绘制、画箭头函数的调用、图片保存、格式转换<br>


## 4 Results

### 4.1 结果展示

1. 按照时间序列生成点簇
将所有的点按照时间顺序排列如下图，GPS Time持续时间一共5596s，(一维展开不便显示，将数据折叠成70x80)，可以看到其中的数据都呈现段状的不连续分布，根据这一点将所有的点归类到点簇与孤立点两种。其中跨度5596s的时间内共有28295个点，其中28039个点被归类到不同的点簇中，生成了308个点簇，另有256个时间上孤立的点.
**生成后进行检核：**对每个点簇生成矩形对时间聚类的结果进行检验，经验证，归类结果没有跨越路口的情况发生，认定方案成立

2. 


 
## 5 Reference
Scikit-Learn : https://scikit-learn.org/stable/index.html<br>
[How to edit Readme.md](https://blog.csdn.net/Kaitiren/article/details/38513715)<br>
[How to pull requst to updata ur own code](https://www.jianshu.com/p/ebad936fac4d)<br>
[Frequently-used command in github](https://blog.csdn.net/wjh2622075127/article/details/87900006?utm_medium=distribute.pc_aggpage_search_result.none-task-blog-2~all~baidu_landing_v2~default-1-87900006.nonecase&utm_term=github%20pull%20%E5%91%BD%E4%BB%A4&spm=1000.2123.3001.4430)<br>

[visualization1](https://blog.csdn.net/qq_36808245/article/details/89085018)<br>
[visualization2](https://www.osgeo.cn/pillow/handbook/image-file-formats.html#eps)<br>
[visualization3](https://blog.csdn.net/weixin_41935140/article/details/83308359)<br>
[visualization4](https://blog.csdn.net/qingyuanluofeng/article/details/50483812?utm_medium=distribute.pc_relevant.)<br>
[visualization5](none-task-blog-title-7&spm=1001.2101.3001.4242)<br>
