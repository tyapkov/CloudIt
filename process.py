import os
import cv
import random
import math
from lib import printImageInfo, rotateImage, cropRoi, test_6, checkPosition

# Here is the folder with clouds
picpath = r"d:\pictures\mobi\CloudIt\clouds\resized"

# The folder to save the images to
savepath = r"d:\pictures\mobi\CloudIt\clouds\test1"

# The folder with animals pictures
animalpath = r"d:\pictures\mobi\CloudIt\animals\formated"

imagesize =(800,600)
minconlength=100

original =cv.CreateImage(imagesize,8,3)

r =cv.CreateImage(imagesize,8,1)
g =cv.CreateImage(imagesize,8,1)
b =cv.CreateImage(imagesize,8,1)


os.chdir(picpath)

#############################################################################
# Additional functions
#############################################################################

# Prints the contour points
def printContour(nc, image):
    i=1

    while nc.h_next():
        for (x,y) in nc:
            print (x,y)
            cv.Line(image, (x,y),(x,y),(126,126,126),5,8)
        i=i+1
        print ("--------------------")
        show(image)
        cv.WaitKey(0)
        nc =nc.h_next()  
    else:
        for (x,y) in nc:
            print (x,y)
            cv.Line(image, (x,y),(x,y),(126,126,126),5,8)
      
    print "Done! " + str(i) + " Contour\s" 
    show(image)        

    cv.WaitKey(0)

# Returns the number of contours
def countContours(nc):
    i=1
    while nc.h_next():
        i=i+1
        nc = nc.h_next()
    return i

# Returns the index sequence
def getContour(nc, index):
    for i in range(index-1):
        nc = nc.h_next()
    return nc
    

# Draws contours and returns the image back
def drawContours(original, nc):
    while nc.h_next():
        if len(nc)> minconlength:           
            cv.DrawContours(original, nc, (255, 0, 0), (0, 0, 255), 0, 2, 4) 
        nc = nc.h_next()
    return original

# Approximates the found contour
def approximate(nc):

    # No more than 5! Last parameter - 1= itteration over all the contours.
    nc = cv.ApproxPoly(nc,cv.CreateMemStorage(),cv.CV_POLY_APPROX_DP, 10,1)
    return nc

# Prints pixels values
def printImage(image):
    
    for x in range(image.width):
        for y in range(image.height):
            z = cv.Get2D(image, int(y),int(x))
            print z
            cv.WaitKey(0)   

# Saves the resulting images
def saveImage(im, name):
    os.chdir( savepath )
    spath = savepath + "\\" + name
    print spath
    cv.SaveImage(spath, im)
    os.chdir(picpath)

def show(original):
    cv.ShowImage("Result", original)
    cv.WaitKey(0)

def checkBlack(image, nc):
    print 'Check black'
    contour     = getContour(nc, 0)
    box         = cv.MinAreaRect2(contour)
    pixel       = cv.Get2D(image, int(box[0][1]), int(box[0][0]))  
    if pixel[0]==0:
        answer='blackonwhite'
    else:
        answer='whiteonblack'
    return answer

   

# Calculates black on image
def calculateDif(image):

    cv.Threshold(image,image,128,255, cv.CV_THRESH_BINARY)
    total = int(image.height*image.width)
    white = black =0
    for x in range(image.width):
        for y in range(image.height):
            z = cv.Get2D(image, int(y),int(x))
            if z[0]==255:
                white = white+1
            else:
                black = black+1
    percentwhite = float(white)/ total*100
    percentblack = float(black)/total*100

##    print 'total ' + str(total)
##    print 'white ' + str(white)
##    print 'black ' + str(black)    
##    print '% white ' + str(percentwhite)

    print '% black ' + str(percentblack)

    if percentblack < 20:
        print '#####################'
        print 'Animal found!!!!!!!!!'

    return percentblack

    
# Creates absdif image
def absDif(image, template):

    print 'Start absDif'
    answers = []
    
    # Adjusts the image to the template's size
    res = cv.CreateImage(cv.GetSize(template), template.depth, template.nChannels)
    final = cv.CreateImage(cv.GetSize(template), template.depth, template.nChannels)   
    cv.Resize(image, res)

    # Flips the image in all directions and compares it to the template
    for i in range(4):

        # k = 0 - without rotation, 1 - flip horozontally and vertically, 2 - vertical fliping, 3 - horisontal fliping.
        temp = template
        if i !=0:
            k = i - 2
            cv.Flip(temp, temp,k)
            cv.AbsDiff(res, temp, final)
            err =calculateDif(final)
            answers.append(err)
            show(final)
##            saveImage(final, str(i)+"image.jpg")
            cv.Flip(temp, temp,k)
        else:
            cv.AbsDiff(res, temp, final)
            err = calculateDif(final)
            answers.append(err)
            show(final)
##            saveImage(final, str(i)+"image.jpg")
                    
    print 'Finish absDif'
    return answers

# Takes the found contours and crops the images from original one, so that the min rectangule is parallel to x,
# Returns the array of images,ratios and boxes
def cropImages(nc, image):
    print 'Croping images starts'
    images  =[]
    ratios  =[]
    boxes=[]

    # Checks if the clusterization was performed correctly so that there is a white figure on black beckground
    # After this block the image in all the cases should be WHITE on the BLACK background.
    check = checkBlack(image, nc)
    if check == 'blackonwhite':
        cv.Threshold(image,image,128,255, cv.CV_THRESH_BINARY_INV)
    elif check == 'whiteonblack':
        cv.Threshold(image,image,128,255, cv.CV_THRESH_BINARY)

    for i in range(countContours(nc)):
        contour = getContour(nc, i)
        if len(contour)> minconlength:
            croped, ratio, box = cropRoi(image, contour)
            ratios.append(ratio)
            images.append(croped)
            boxes.append(box)

    print 'Croping images finished'
    return images, ratios, boxes


# Compares how similar are the given array of images to the template
def compareImages(images, ratios):
    os.chdir( animalpath )
    for name in os.listdir(os.getcwd()):
        try:
            print 'Animal image name is ' + str(animalpath)+ str(name)
            template = cv.LoadImage(name, cv.CV_LOAD_IMAGE_GRAYSCALE)
            size = cv.GetSize(template)
            tempratio = size[0]/float(size[1])
            
            print 'Start comparing images'
            mistake = 0.2
            upborder = 1 + mistake
            downborder = 1 - mistake
            
            for i in range(len(images)):
                croped = images[i] 
                val, pos = checkPosition(croped, ratios[i], template, tempratio)      
                print val
                print pos

                # Checks how different are the sizes of the images
                if (val < upborder) and (val > downborder):
                    print " Ratio of croped image is in range!"
                    if pos == 'landscape' or pos == 'portrait':               
                        answers = absDif(croped,template)
                    else:
                        if pos =='landpor':
                            boxtwidth =     croped.width
                            boxtheight =    croped.height
                        elif pos=='porland':
                            boxtwidth =     croped.height
                            boxtheight =    croped.width

                        boxt =((int(float(croped.width)/2), int(float(croped.height)/2)), (boxtwidth, boxtheight), 0)
                        croped = rotateImage(croped,boxt,1)
                        answers = absDif(croped, template)
                    print answers

        except IOError, e:
            print "Problem opening: ", e
    os.chdir(picpath)
    print 'Stop comparing images'
        
        
def main():
    
    cv.NamedWindow("Result", 1)
    
    for name in os.listdir(os.getcwd()):
        try:
            print 'Start processing image ' + str(name)
            print '##############################'
            
            original =      cv.LoadImage(name)
            gray =          cv.LoadImage(name, cv.CV_LOAD_IMAGE_GRAYSCALE)
            imagematmat =   cv.LoadImageM(name, cv.CV_LOAD_IMAGE_COLOR)
            
            # Kmean clusterization
            nc, grim =      test_6(original, gray, imagematmat)

            #Extract all the contours aand makes small pictures
            images, ratios, boxes = cropImages(nc, grim)
            
            # Compares the extracted pictures with template
            compareImages(images, ratios)

            print '##############################'
                         
        except IOError, e:
            print "Problem opening: ", e

main()
