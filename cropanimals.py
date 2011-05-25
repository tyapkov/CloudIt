import os
import cv
from lib import rotateImage,saveImage, printImageInfo, cropRoi

animalpath = r"d:\pictures\mobi\CloudIt\animals\raw"
savepath = r"d:\pictures\mobi\CloudIt\animals\formated"

imagesize =(800,600)
edge = cv.CreateImage(imagesize,8,1)


os.chdir(animalpath)

   
def main():
    
    cv.NamedWindow("Result", 1)
    
    for name in os.listdir(os.getcwd()):
        try:
            print 'Start processing ' + str(name)
            print '##############################'

            animal = cv.LoadImage(name, cv.CV_LOAD_IMAGE_GRAYSCALE)
            cv.Threshold(animal, edge, 128 ,255, cv.CV_THRESH_BINARY_INV) 
            ncas = cv.FindContours(edge, cv.CreateMemStorage(), cv.CV_RETR_LIST, cv.CV_CHAIN_APPROX_NONE,(0,0))
   
            croped, ratio, box = cropRoi(animal, ncas)         
            cv.Threshold(croped,croped,128,255, cv.CV_THRESH_BINARY)

            del ncas
            cv.ShowImage("Result", croped)
            cv.WaitKey(0)
            saveImage(croped, name, savepath, animalpath)
            
            print '##############################'
                                     
        except IOError, e:
            print "Problem opening: ", e

main()
