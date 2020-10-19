import sys
import numpy as np
from osgeo import gdal, ogr, osr
from scipy.spatial import Voronoi

sys.path.append(r'/Users/yunsheng666/PycharmProjects')
from gwp_shape_new import SHAPE
input_filename = 'traffic_intersection_zhonggguancun.shp'
# output_filename = '/Users/yunsheng666/pythoncourse/chapter_02/stations_voronoi_clip.shp'
shp_driver = SHAPE()
spatialref, geomtype, geomlist, fieldlist, reclist = shp_driver.read_shp(input_filename)
points = np.zeros((len(geomlist), 2), dtype=np.float)
for i in range(len(geomlist)):
    geom = ogr.CreateGeometryFromWkt(geomlist[i])
    points[i, 0], points[i, 1] = geom.GetX(), geom.GetY()
# print(len(geomlist))
tx = np.min(points[:, 0]), np.max(points[:, 0])
ty = np.min(points[:, 1]), np.max(points[:, 1])
mx, my = np.meshgrid(tx, ty)
points_ = np.vstack([mx.reshape(-1), my.reshape(-1)]).T
points = np.vstack([points, points_])
# print('--------------------')
# print(points_)
# print('----------------')
# print(points.shape)

vor = Voronoi(points)
vertices = vor.vertices  # ndarray(nvertices, ndim)，组成 region 的顶点表(顶点坐标)
regions = vor.regions  # list(nregions, *)，每个 region 对应的顶点下标(每个顶点都有一个编号，统计每个region对应的顶点编号)
point_region = vor.point_region  # list (npoints)，每个输入点对应的 region 下标

geomtype_ = ogr.wkbPolygon
fieldlist_ = [{'width': 20, 'decimal': 0, 'type': ogr.OFTInteger, 'name': 'ID'}, \
              {'width': 20, 'decimal': 3, 'type': ogr.OFTReal, 'name': 'AREA'},
              {'width': 20, 'decimal': 3, 'type': ogr.OFTReal, 'name': 'ANN_PREC'}]

(x0, x1), (y0, y1) = tx, ty    # tx,ty为整个shp最小最大x，最小最大y
ul = ('%f %f') % (x0, y1)      # 左上角
ur = ('%f %f') % (x1, y1)      # 右上角
lr = ('%f %f') % (x1, y0)      # 右下角
ll = ('%f %f') % (x0, y0)      # 左下角
cs_ = ','.join([ul, ur, lr, ll, ul])  # 以','为分隔符，将所有元素合并成一个新的字符串
wkt = 'POLYGON((%s))' % (cs_)
mbr = ogr.CreateGeometryFromWkt(wkt)


