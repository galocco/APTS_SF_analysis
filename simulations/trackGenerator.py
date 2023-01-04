import numpy as np
import math as m
from random import random, gauss
import math
import ROOT
import ctypes

class Plane:
    def __init__(self, id, position, resolution = [5,5], npixels = [1024,512],pitch = [29.24,26.88], angle_range = 0.02, tras_range = 300):
        self.id = id
        self.position = position
        self.angle_range = angle_range
        self.tras_range = tras_range
        self.npixels = npixels
        self.pitch = pitch
        self.resolution = resolution
        if id != 0:
            self.displacement = np.array([[random()*self.tras_range*2-self.tras_range],
                             [random()*self.tras_range*2-self.tras_range],
                             [random()*self.tras_range*2-self.tras_range]])
            self.rotation = [random()*self.angle_range*2-self.angle_range,
                            random()*self.angle_range*2-self.angle_range,
                            random()*self.angle_range*2-self.angle_range]
        else:
            self.displacement = np.array([[0],[0],[0]])
            self.rotation = [0,0,0]

        self.p0 = np.array([[position[0]],[position[1]],[position[2]]])
        self.p1 = np.array([[position[0]],[position[1]+self.pitch[1]*self.npixels[1]],[position[2]]])
        self.p2 = np.array([[position[0]+self.pitch[0]*self.npixels[0]],[position[1]],[position[2]]])

        R = self.get_rotation_matrix()
        y0 = (R*self.p0+self.displacement)[1][0]
        y1 = (R*self.p1+self.displacement)[1][0]
        y2 = (R*self.p2+self.displacement)[1][0]
        z0 = (R*self.p0+self.displacement)[2][0]
        z1 = (R*self.p1+self.displacement)[2][0]
        z2 = (R*self.p2+self.displacement)[2][0]
        x0 = (R*self.p0+self.displacement)[0][0]
        x1 = (R*self.p1+self.displacement)[0][0]
        x2 = (R*self.p2+self.displacement)[0][0]

        self.a = (y1-y0)*(z2-z0)-(y2-y0)*(z1-z0)
        self.b = -((x1-x0)*(z2-z0)-(x2-x0)*(z1-z0))
        self.c = (x1-x0)*(y2-y0)-(x2-x0)*(y1-y0)
        self.d = -self.a*x0-self.b*y0-self.c*z0

    def get_plane_parameters(self):
        return [self.a, self.b, self.c, self.d]

    def __str__(self):
        return f"plane_{self.id}"

    def set_position(self, position):
        self.position = position

    def set_displacement(self, displacement):
        self.displacement = displacement

    def set_rotation(self, rotation):
        self.rotation = rotation

    def get_position(self):
        return self.position

    def get_displacement(self):
        return self.displacement

    def get_rotation(self):
        return self.rotation

    def get_rotation_x(self):
        return np.matrix([[ 1, 0           , 0           ],
                        [ 0, m.cos(self.rotation[0]),-m.sin(self.rotation[0])],
                        [ 0, m.sin(self.rotation[0]), m.cos(self.rotation[0])]])
    
    def get_rotation_y(self):
        return np.matrix([[ m.cos(self.rotation[1]), 0, m.sin(self.rotation[1])],
                        [ 0           , 1, 0           ],
                        [-m.sin(self.rotation[1]), 0, m.cos(self.rotation[1])]])
    
    def get_rotation_z(self):
        return np.matrix([[ m.cos(self.rotation[2]), -m.sin(self.rotation[2]), 0 ],
                        [ m.sin(self.rotation[2]), m.cos(self.rotation[2]) , 0 ],
                        [ 0           , 0            , 1 ]])

    def get_rotation_matrix(self):
        return self.get_rotation_z()*self.get_rotation_y()*self.get_rotation_x()

    def intersect_to_pixel(self, intersect):
        #ncolumns = self.npixels[0]*2
        #nrows = self.npixels[1]*2
        R = self.get_rotation_matrix()
        d = self.get_displacement()
        i = R*(self.p1 - self.p0)+d
        j = R*(self.p2 - self.p0)+d

        mod_i = math.sqrt(i[0][0]**2+i[1][0]**2+i[2][0]**2)
        mod_j = math.sqrt(j[0][0]**2+j[1][0]**2+j[2][0]**2)

        i = i*self.pitch[1]/mod_i/2
        j = j*self.pitch[0]/mod_j/2
        #print(mod_i)
        #print(mod_j)
        if i[0][0]==0 and j[0][0]!=0:
            row = intersect[0]/j[0][0]
            column = (intersect[1][0]-j[1][0]*row)/i[1][0]
        elif i[0][0]!=0 and j[0][0]==0:
            column = intersect[0]/i[0][0]
            row = (intersect[1][0]-i[1][0]*column)/j[1][0]
        else:
            column = (intersect[1]*j[0][0]-j[1][0]*intersect[0])/(i[1][0]*j[0][0]-i[0][0]*j[1][0])
            row = (intersect[0]-column*i[0][0])/j[0][0]
            
        return [float(row[0][0]/2), float(column[0][0]/2)]

ROOT.gRandom.SetSeed(0)
class Track:
    def __init__(self, hist_angle_x, hist_angle_y, f2t):
        anglex = 0#hist_angle_x.GetRandom()
        angley = 0#hist_angle_y.GetRandom()

        px = ctypes.c_double()
        py = ctypes.c_double()
        f2t.GetRandom2(px,py)
        self.vector = [math.tan(anglex),math.tan(angley)]
        self.point = [px.value*1000+512*29.24,py.value*1000+26.88*256]
        #self.point = [px.value*100,py.value*100]
    def set_vector(self, vector):
        self.vector = vector

    def set_point(self, point):
        self.point = point

    def get_position(self, z):
        return [self.vector[0]*z+self.point[0],
                self.vector[1]*z+self.point[1]]

    def get_intersect(self, plane):
        plane_params = plane.get_plane_parameters()
        a = plane_params[0]
        b = plane_params[1]
        c = plane_params[2]
        d = plane_params[3]

        vx = self.vector[0]
        vy = self.vector[1]
        x0 = self.point[0]
        y0 = self.point[1]
        
        zint = -(a*x0+b*y0+d)/(a*vx+b*vy+c)
        xint = x0+vx*zint
        yint = y0+vy*zint
        #TODO: put limits if tracks goes outside the plane
        return [xint, yint, zint]

    def get_intersect_and_smear(self, plane):
        hit = self.get_intersect(plane)
        #print("hit: ",hit)
        #TODO: put limits if tracks goes outside the plane
        return [hit[0]+gauss(0,plane.resolution[0]),hit[1]+gauss(0,plane.resolution[1]),hit[2]]

class Telescope:
  def __init__(self, planes = []):
    self.planes = planes

  def add_plane(self, plane):
    self.planes.append(plane)

  def get_plane(self, id):
    return self.planes[id]

  def get_planes(self):
    return self.planes

###############################################################
def main(n_tracks = 100):
    B2 = Telescope()
    Z_list = [0,25000,50000,150000,175000,200000]
    counter = 0
    for z in Z_list:
        ALPIDE = Plane(counter, [0,0,z])
        B2.add_plane(ALPIDE)
        counter += 1

    input_file = ROOT.TFile("/home/giacomo/its-corryvreckan-tools/output/PSAugust/B2/AF20P_W22B6/alignment_345211441220826211447_check.root","read")
    trackAngleXMC = input_file.Get("Tracking4D/trackAngleX")
    trackAngleYMC = input_file.Get("Tracking4D/trackAngleY")
    hitmap = input_file.Get("ClusteringSpatial/ALPIDE_0/clusterPositionGlobal")

    myHitmap = ROOT.TH2D("myhitmap",";x;y",1024,0.5,1024.5,512,0.5,512.5)
        
    suffix = int(ROOT.gRandom.Rndm()*100000000)
    output = ROOT.TFile("simQA_{}.root".format(suffix),"recreate")
    hitmap.Write()

    xmin = hitmap.GetXaxis().GetBinLowEdge(1)*1.1
    xmax = hitmap.GetXaxis().GetBinUpEdge(hitmap.GetNbinsX())*1.1 
    ymin = hitmap.GetYaxis().GetBinLowEdge(1)*1.1
    ymax = hitmap.GetYaxis().GetBinUpEdge(hitmap.GetNbinsY())*1.1

    xmean  = hitmap.GetMean(0)
    xsigma = hitmap.GetStdDev(0) 
    ymean  = hitmap.GetMean(1)
    ysigma = hitmap.GetStdDev(1)
    print("xmean: ",xmean)
    print("xsigma: ",xsigma)
    print("ymean: ",ymean)
    print("ysigma: ",ysigma)
    f2t = ROOT.TF2("f2t","xygaus",xmin,xmax,ymin,ymax)
    f2t.SetParameters(1000,xmean,xsigma,ymean,ysigma)
    hitmap.Fit(f2t,"QMIL+")

    f =  open("simulationHits_{}.txt".format(suffix), 'w')
    print("generating: ","simulationHits_{}.txt".format(suffix))
    for plane in B2.get_planes():
        position = plane.get_position()
        displacement = plane.get_displacement()
        rotations = plane.get_rotation()
        f.write("{} {} {} {} {} {} {} {} {}\n".format(position[0], position[1], position[2], displacement[0][0], displacement[1][0], displacement[2][0], rotations[0], rotations[1], rotations[2]))

    for _ in range(n_tracks):
        track = Track(trackAngleXMC, trackAngleYMC, f2t)
        hits = ''
        for plane in B2.get_planes():
            intersect = track.get_intersect_and_smear(plane)
            pixel = plane.intersect_to_pixel(intersect)
            myHitmap.Fill(pixel[0],pixel[1]) 
            hits += "{} {} ".format(pixel[0], pixel[1])
        f.write(hits+"\n")
    f2t.Write()
    myHitmap.Write()
    output.Close()

if __name__ == '__main__':
    main(10000)