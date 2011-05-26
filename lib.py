import cv
import os

##############################################################################
# Variables
##############################################################################
imagesize =(800,600)

tempimage =cv.CreateImage(imagesize,8,3)

grayimage =cv.CreateImage(imagesize,8,1)
edge = cv.CreateImage(imagesize,8,1)

color_tab = [
    cv.CV_RGB(0, 0,0),
    cv.CV_RGB(255, 255, 255),
    cv.CV_RGB(255, 0,255)]


##############################################################################
# Useful functions
##############################################################################

# Checks if the given 2 images are both landscape, portrait or mixed, counts ratio value of ratios.
def checkPosition(image, ratio, template, tempratio):
    if (image.width > image.height) and (template.width > template.height):
        val = tempratio/ratio
        pos = 'landscape'
    elif(image.width < image.height) and (template.width < template.height):
        val = tempratio/ratio
        pos='portrait'
    elif(image.width > image.height) and (template.width < template.height):
        val = tempratio*ratio
        pos='landpor'
    elif(image.width < image.height) and (template.width > template.height):
        val = tempratio*ratio
        pos='porland'
    return val, pos

#Takes the contour found on the image and crop the image accroding to the contour
def cropRoi(image, nc):
    box = cv.MinAreaRect2(nc)
    center = (box[0][0], box[0][1])  
    output =rotateImage(image, box, 1)

    size = cv.GetSize(output)
    ratio = size[0]/float(size[1])

    return output, ratio, box

# Rotates and scales the image
def rotateImage(image, box, scale):

    print 'Start rotation of the image'
    center = (box[0][0], box[0][1])
    angle =int(90-box[2])
    
    if image.width> image.height:
        side = int(image.width*2)        
    else:
        side = int(image.height*2)

    output = cv.CreateImage((side, side), image.depth, image.nChannels)
    output1 = cv.CreateImage((side, side), image.depth, image.nChannels)
    output2 = cv.CreateImage((int(box[1][0]),int(box[1][1])), image.depth, image.nChannels)

    cv.Set(output, [0,0,0])
    rect =(int((float(side)/2- center[0])), int(float(side)/2- center[1]),int(image.width),(int(image.height))) 
    cv.SetImageROI(output, rect)
    output.origin = image.origin
    cv.Copy(image, output)
    cv.ResetImageROI(output)
    
    centerOutput =(int(float(side)/2),int(float(side)/2))
    mat = cv.CreateMat(2,3,cv.CV_32FC1)      
    cv.GetRotationMatrix2D(centerOutput, angle, scale, mat)
    cv.WarpAffine(output,output1, mat,cv.CV_INTER_LINEAR + cv.CV_WARP_FILL_OUTLIERS,cv.ScalarAll(255))

    rect1 =(int((float(side)/2- float(box[1][0])/2)), int(float(side)/2- float(box[1][1])/2),int(box[1][0]),int(box[1][1]))
    cv.SetImageROI(output1,rect1)
    cv.Copy(output1, output2)

    print 'Finish rotation'
    return output2

#Prints image information
def printImageInfo(image):
    print '########Image###########'
    print 'Origin' + str(image.origin)
    print 'Size ' + str(cv.GetSize(image))
    print 'Depth '+ str(image.depth)
    print 'Channels '+ str(image.nChannels)

# Saves the resulting images into the specified folder
def saveImage(im, name, savepath, returnpath):
    os.chdir( savepath )
    spath = savepath + "\\" + name
    print spath
    cv.SaveImage(spath, im)
    os.chdir(returnpath)
    
##############################################################################
# Contour finding algorithms 
##############################################################################


def test_1(original, gray, mat):
# Main features:
# Splitting the image into the channels and using the blue channel
# Thresholind the image - 128, THRESH_BINARY
# Findcontours CHAIN_APPROX_NONE
# Contours length > 50

    cv.Split(original, r, g, b, None)

    # THRESH_BINARY, THRESH_BINARY_INV, THRESH_TRUNK, THRESH_TOZERO, THRESH_TOZERO_INV
    cv.Threshold(g, edge, 128 ,255, cv.CV_THRESH_BINARY)
    show(edge)
    nc = cv.FindContours(edge, cv.CreateMemStorage(), cv.CV_RETR_LIST, cv.CV_CHAIN_APPROX_NONE,(0,0))
    
    return nc

def test_2(original, gray, mat):
# Main features:
# Usage of grayscale image
# Addapritve thresholding by ADAPTIVE_THRESH_MEAN_C method
# Findcontours CHAIN_APPROX_NONE
# Contours length > 50
            
    cv.AdaptiveThreshold(gray, edge, 255, cv.CV_ADAPTIVE_THRESH_MEAN_C, cv.CV_THRESH_BINARY,61,0)

    nc = cv.FindContours(edge, cv.CreateMemStorage(), cv.CV_RETR_LIST, cv.CV_CHAIN_APPROX_NONE,(0,0))

    return nc

def test_3(original, gray, mat):
# Main features:
# Usage of grayscale image
# Addapritve thresholding by ADAPTIVE_THRESH_GAUSSIAN_C method
# Findcontours CHAIN_APPROX_NONE
# Contours length > 50
            
    cv.AdaptiveThreshold(gray, edge, 255, cv.CV_ADAPTIVE_THRESH_GAUSSIAN_C, cv.CV_THRESH_BINARY,51,0)

    nc = cv.FindContours(edge, cv.CreateMemStorage(), cv.CV_RETR_LIST, cv.CV_CHAIN_APPROX_NONE,(0,0))

    return nc

#### The best result is shown by test1.

def test_4(original, gray, mat):
# Main features:
# Morphological change of the image before thresholding.
# Splitting the image into the channels and using the blue channel
# Thresholind the image - 128, THRESH_BINARY
# Findcontours CHAIN_APPROX_NONE
# Contours length > 50

    cv.Split(original, r, g, b, None)

    # Morphological operation
    temp = cv.CreateImage((800,600), 8, 1)
    core = cv.CreateStructuringElementEx(10, 10, 5, 5, cv.CV_SHAPE_ELLIPSE)
    cv.MorphologyEx(b, b, temp, core, cv.CV_MOP_CLOSE, 2)
    show(b)
    

    # THRESH_BINARY, THRESH_BINARY_INV, THRESH_TRUNK, THRESH_TOZEOR, THRESH_TOZERO_INV
    cv.Threshold(b, edge, 128 ,255, cv.CV_THRESH_BINARY)

    nc = cv.FindContours(edge, cv.CreateMemStorage(), cv.CV_RETR_LIST, cv.CV_CHAIN_APPROX_NONE,(0,0))

    return nc

def test_5(original, gray, mat):
# Main features:
# Canny algorithm
# Findcontours CHAIN_APPROX_NONE
# Contours length > 50

    #Ration should be 1:2 or 1:3
    cv.Canny(gray, edge, 20, 40, 3)
    cv.SaveImage("test.jpg", edge)
    nc = cv.FindContours(edge, cv.CreateMemStorage(), cv.CV_RETR_LIST, cv.CV_CHAIN_APPROX_NONE,(0,0))

    return nc

def test_6(original, gray, imagematmat):
    print "K-mean clustering starts"

# Main features:
# K-mean clustering of the image

    clustersnum = 2
    
    # Changing from 8 bit to 32 bits
    clusterim =cv.CreateImage (imagesize,32,3)
    cv.ConvertScale(original, clusterim)

    # Defines the length of the 1 col array and creates it.  
    arrlength =clusterim.height*clusterim.width
    imagemat = cv.CreateMat(arrlength,1,cv.CV_32FC3)
    
    # Transfers all the data from image to one col imagemat
    for i in range(arrlength):
        x = abs(i- (i/clusterim.height)* clusterim.height)
        y = i/clusterim.height
        cv.Set2D(imagemat,i,0, cv.Get2D(imagematmat,x,y)[2])

    # Creates array to save the clusters.       
    clusters = cv.CreateMat(clusterim.height*clusterim.width,1,cv.CV_32SC1)

    cv.KMeans2(imagemat, clustersnum, clusters, (cv.CV_TERMCRIT_EPS+cv.CV_TERMCRIT_ITER,10,1.0))

    # Redraws all the pixels of the image depending on the cluster they belong to.
    for i in range(arrlength):
        cluster_idx = int(clusters[i, 0])

        x = abs(i- (i/clusterim.height)* clusterim.height)
        y = i/clusterim.height

        pt = (x,y)
        cv.Set2D(tempimage, x, y, color_tab[cluster_idx])

    #Grayscales the image
    cv.CvtColor(tempimage, grayimage, cv.CV_RGB2GRAY )
    cv.Threshold(grayimage, edge, 128 ,255, cv.CV_THRESH_BINARY)
    
    nc = cv.FindContours(edge, cv.CreateMemStorage(), cv.CV_RETR_LIST, cv.CV_CHAIN_APPROX_NONE,(0,0))

    print "K-mean clustering finished"
    return nc, grayimage

##############################################################################
# Not in use but helpful somehow 
##############################################################################

### Compares moments of the contours and thus reason about shape similarity.
##def compareContourMoments(cloudnc, animalcon):
##    
##    animalcon = getContour(animalcon,1)        
##    
##    while cloudnc.h_next():
##        if len(cloudnc)>minconlength:
##            result = cv.MatchShapes(cloudnc,animalcon, cv.CV_CONTOURS_MATCH_I1,0)
##            print "Result " + str(result1)
##        cloudnc = cloudnc.h_next()
##    return result1

### Creates contour trees and reasons about contour similarity
##def compareContourTrees(cloudnc, animalcon):
##    storage     = cv.CreateMemStorage()   
##    animalcon   = getContour(animalcon,1)
##    animaltree  = cv.CreateContourTree(animalcon, storage, 0)
##
##    print cloudnc.h_next()
##    while cloudnc.h_next():
##        if len(cloudnc)>minconlength:
##            cloudtree = cv.CreateContourTree(cloudnc, storage, 0)
##            result1 = cv.MatchContourTrees(cloudtree,animaltree, cv.CV_CONTOUR_TREES_MATCH_I1,0)
##            print str(result1)
##            return result1
##        cloudnc = cloudnc.h_next()

# Takes rectangle, rotates it and return new coordinates
##def findRotCoord(rect, angle):
##
##    xtl = int(rect[0]- rect[2]/2)
##    ytl = int(rect[1]- rect[3]/2)
##    
##    xtr = int(rect[0]+ rect[2]/2)
##    ytr = int(rect[1]- rect[3]/2)
##
##    xdl = int(rect[0]- rect[2]/2)    
##    ydl = int(rect[1]+ rect[3]/2)
##
##    xdr = int(rect[0]+ rect[2]/2)    
##    ydr = int(rect[1]+ rect[3]/2)
##
##    array = ((xtr,ytr),(xtl,ytl),(xdl,ydl),(xdr,ydr))
##    output=[]
##    print array
##    centerx = int(rect[0])
##    centery = int(rect[1])
##
##    for i in range(len(array)):
##        print i
##        dx = float(array[i][0] - centerx)
##        dy = float(centery - array[i][1])
##        
##        if (dx>0 and dy>0) or (dx>0 and dy<0):
##            alpha = math.atan(dy/dx) + 2*math.pi
##        if (dx<0 and dy>0) or (dx<0 and dy<0):
##            alpha = math.atan(dy/dx)+ math.pi
##
##        radius = math.sqrt(math.pow(dx,2)+ math.pow(dy,2))
##        corner = (float(angle)/180)*math.pi + alpha
##        x= centerx + int(radius*math.cos(corner))
##        y= centery - int(radius*math.sin(corner))
##        output.append((x,y))
##
##    return output
