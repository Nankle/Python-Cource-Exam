import turtle as t
import shapefile as sf
import numpy as np
import PIL
from tkinter import *
from PIL import Image
from PIL import EpsImagePlugin
EpsImagePlugin.gs_windows_binary =  r'C:\Program Files\gs\gs9.53.3\bin\gswin64c'
#读取路口点坐标，生成数组coor
#coor:数组，41行2列，路口坐标
tpath="D:/data/traffic_intersection_zhongguancun.shp"
cross=sf.Reader(tpath)
shapes=cross.shapes()
coor=np.zeros((len(shapes),2))
for i in range(len(shapes)):
    coor[i][0]=shapes[i].points[0][0]
    coor[i][1]=shapes[i].points[0][1]

#生成测试数组n
#n:三维数组，41*4*5。第一维代表路口。第二维和第三维的含义：4行5列，每行依次对应右、上、左、下方向，任意一行的每列依次为(0/1)：道路是否存在/角度，是否调头，是否左转，是否直行，是否右转
basic=[[10,0,1,1,1],[100,0,1,1,1],[190,0,1,1,1],[280,0,1,1,1]]
test=[]
for i in range(len(shapes)):
    test.append(basic)

n=np.array(test)

#单个路口画图函数
def SinPicture(n,seq):
    #画布
    CanLen=800 #画布长度
    CanWid=800 #画布宽度
    t.setup(CanLen,CanWid)
    t.tracer(False)
    t.bgcolor("grey")

    #画背景矩形
    t.goto(-CanLen/2,-CanWid/2)
    t.fillcolor(t.Screen().bgcolor())
    t.begin_fill()
    t.setheading(0)
    t.forward(CanLen)
    t.setheading(90)
    t.forward(CanWid)
    t.setheading(180)
    t.forward(CanLen)
    t.setheading(270)
    t.forward(CanWid)
    t.end_fill()

    #画笔
    t.pensize(3)
    t.color("black")
    t.speed(0)

    #画路口
    width = 300
    length = 200
    def DrawRoad(angle):
        t.tracer(False)
        t.penup()
        t.goto(0, 0)
        t.seth(angle)
        t.fd(width/2)
        t.right(90)
        t.fd(width/2)
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
        t.fd(width/2)
        t.right(90)
        t.fd(width/2)
        t.left(180)
        t.pd()
        t.fd(width)
        t.penup()

    t.tracer(False)
    t.penup()
    ang=0
    m=0
    for i in range(4):
        if n[i][0]>=0:
            ang+=n[i][0]-90*i
            m+=1
    MeanAng=int(ang/m)
    CurAug=MeanAng
    for i in range(4):
        if n[i][0]>=0:
            DrawRoad(CurAug)
        else:
            Drawline(CurAug)
        CurAug+=90

    #右转
    def GoRight(a,b):
    #依据路口设置颜色
        if a == 0:
          t.color("black","red")
        elif a == 1:
          t.color("black","yellow")
        elif a == 2:
          t.color("black","blue")
        elif a == 3:
          t.color("black","green")
        t.pensize(2)
        # 设置起点为矩形边框左上角
        t.penup()
        t.forward(118)
        t.lt(90)
        t.fd(b/6)
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
        t.fd(b/5)
        t.rt(90)
        t.fd(118)
        t.rt(90)
        #t.exitonclick()
    #直行
    def GoStraight(a,b):
    #依据路口设置颜色
        if a == 0:
          t.color("black","red")
        elif a == 1:
          t.color("black","yellow")
        elif a == 2:
          t.color("black","blue")
        elif a == 3:
          t.color("black","green")
    # 设置起点为矩形边框左上角
        t.penup()
        t.forward(150)
        t.lt(90)
        t.fd(5*b/12)
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
        t.fd(5*b/12)
        t.rt(90)
        t.fd(150)
        t.rt(90)
    #左转
    def GoLeft(a,b):
    # 依据路口设置颜色
        if a == 0:
            t.color("black","red")
        elif a == 1:
            t.color("black","yellow")
        elif a == 2:
            t.color("black","blue")
        elif a == 3:
            t.color("black","green")
        t.pensize(2)
        # 设置起点为矩形边框左上角
        t.penup()
        t.forward(134)
        t.lt(90)
        t.fd(7*b/8)
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
        t.fd(7*b/8)
        t.rt(90)
        t.fd(134)
        t.rt(90)
        #t.exitonclick()
    #掉头
    def GoBack(a,b):
    # 依据路口设置颜色
        if a == 0:
            t.color("black","red")
        elif a == 1:
            t.color("black","yellow")
        elif a == 2:
            t.color("black","blue")
        elif a == 3:
            t.color("black","green")
        t.pensize(2)
    #设置起点为矩形边框左上角
        t.penup()
        t.forward(142)
        t.lt(90)
        t.fd(b/6)
    #绘制箭头
        t.pendown()
        t.begin_fill()
        t.fd(8)
        t.lt(90)
        t.fd(18)
        t.rt(180)
        t.circle(15, -180)
        t.rt(180)
        t.fd(18)
        t.rt(90)
        t.fd(8)
        t.rt(90)
        t.fd(18)
        t.circle(8, 180)
        t.fd(18)
        t.lt(90)
        t.fd(8)
        t.rt(135)
        t.fd(15)
        t.lt(270)
        t.fd(15)
        t.end_fill()
    #返回矩形左上角
        t.penup()
        t.lt(45)
        t.fd(b/3)
        t.rt(90)
        t.fd(142)
        t.rt(90)

    #绘制每条道路的转向标志
    t.penup()
    t.goto(0, 0)
    t.seth(MeanAng)
    for i in range(4):
        k=0
        if n[i][0]>=0:
            for j in range(1,5):
                if n[i][j]==1:
                    k+=1
            SignPosW=width/k
            t.penup()
            t.fd(width/2)
            t.right(90)
            t.fd(width/2)
            t.left(90)
            if n[i][1]==1:
                GoBack(i,SignPosW)
                t.penup()
                t.fd(SignPosW)
                t.right(90)
            if n[i][2]==1:
                GoLeft(i,SignPosW)
                t.penup()
                t.fd(SignPosW)
                t.right(90)
            if n[i][3]==1:
                GoStraight(i,SignPosW)
                t.penup()
                t.fd(SignPosW)
                t.right(90)
            if n[i][4]==1:
                GoRight(i,SignPosW)
                t.penup()
                t.fd(SignPosW)
                t.right(90)
        t.penup()
        t.goto(0, 0)
        t.seth(MeanAng+90*i+90)

    #保存图片为eps格式
    EpsPic="p"+str(seq)+".eps"
    ts=t.getscreen()
    ts.getcanvas().postscript(file=EpsPic)
    #将图片格式转换为png
    JpgPic1 = "p"+str(seq)+".png"
    im = Image.open(EpsPic)
    im.load(scale=5)
    im.save(JpgPic1,"PNG",quality=95)
    #重新打开图片，缩小图片
    JpgPic2=str(seq)+".png"
    im=Image.open(JpgPic1)
    out=im.resize((300,300),PIL.Image.ANTIALIAS)
    out.save(JpgPic2, "PNG", quality=100)

#所有路口画图
for i in range(len(n)):
    SinPicture(n[i],i)
