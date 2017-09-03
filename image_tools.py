import os
import shutil
from PIL import Image as ImgPIL, ImageStat, ImageChops
import multiprocessing
from multiprocessing import Pool
import cv2
import numpy as np
import time
import operator
import logging
from scipy import misc
from os.path import basename
import operator

#todo review this part
imglist = list()
color_folder = 'D:\\Img_base\\Classes\\Anime_blonde\\tmp_color'
gray_folder = 'D:\\Img_base\\Classes\\Anime_blonde\\Junk'
#end part

# Custom Image class for specific purposes
class ImageCustom:
    def __init__(self, path):
        self.path = path
    #compare by path
    def __eq__(self, other):
        return self.path == other.path
    def __hash__(self):
        return hash(self.path)
    #to be able sort by width
    def __lt__(self, other):
        return self.width < other.width
    def getHeight(self):
        return self.height
    def setWH(self, width, height):
        self.height = height
        self.width = width
    #set PIL pixels
    def setCalculatePixels(self, calcPixels):
        self.calcPixels = calcPixels
    def setGray(self, isGray):
        self.isGray = isGray
    def setIsSimilar(self, isSimilar):
        self.isSimilar = isSimilar
    def detect_color_image(self, thumb_size=100, MSE_cutoff=22, adjust_color_bias=True):
        pil_img = ImgPIL.open(self.path)
        bands = pil_img.getbands()
        if bands == ('R', 'G', 'B') or bands == ('R', 'G', 'B', 'A'):
            thumb = pil_img.resize((thumb_size, thumb_size))
            SSE, bias = 0, [0,0,0]
            if adjust_color_bias:
                bias = ImageStat.Stat(thumb).mean[:3]
                bias = [b - sum(bias)/3 for b in bias ]
            for pixel in thumb.getdata():
                mu = sum(pixel)/3
                SSE += sum((pixel[i] - mu - bias[i])*(pixel[i] - mu - bias[i]) for i in [0,1,2])
            MSE = float(SSE)/(thumb_size*thumb_size)
            if MSE <= MSE_cutoff:
                #set gray
                self.setGray(True)
            else:
                #set color
                self.setGray(False)
        elif len(bands) == 1:
            #set gray
            self.setGray(True)
        else:
            #idk, but set color
            self.setGray(False)

#get difference in 2 lists
def diff(first, second):
        second = set(second)
        return [item for item in first if item not in second]

#to do make good rename
#rename all images in dir
def MaskRename(target_path, mask):
    namesOfFiles = os.listdir(target_path)
    i = 1
    l = list()
    #removing extension
    for item in namesOfFiles:
        l.append(os.path.splitext(item)[0])
    
    futureNamesOfFiles = list()
    #applying new mask 
    for q in range(0, len(l),1):
        futureNamesOfFiles.append(mask + "_" + str(q))  

    listOfDiff = diff(l, futureNamesOfFiles)
    
    fileAfterRename = [ x for x in namesOfFiles if x.startswith(tuple(listOfDiff)) ]

    iterator = 0
    shift = 1
    for newItem in fileAfterRename:
        filename, file_extension = os.path.splitext(newItem)
        old_file = os.path.join(target_path, newItem)
        new_file = os.path.join(target_path, futureNamesOfFiles[iterator] + file_extension)
        try:
            os.rename(old_file, new_file)
            iterator = iterator + 1
        except Exception:
            new_file = os.path.join(target_path, futureNamesOfFiles[iterator + 1] + file_extension)
            os.rename(old_file, new_file)
            iterator = iterator + 2
            pass

# fixed, works good, move images by width and height, plus clear unreadable junk
def moveImagesToFolderByResolution(sourceFolder ,targetFolder, width, height):
    imglist = list()
    for file in os.listdir(sourceFolder):
        pathToFile = sourceFolder + "\\" + file
        imglist.append(pathToFile)
    for i in range(len(imglist)):
        try:
            pil_img = ImgPIL.open(imglist[i])
            imgWidth, imgHeight = pil_img.size
            pil_img.close()
            if(imgWidth < width or imgHeight < height):
                shutil.move( imglist[i], targetFolder)
        except Exception as ex: 
            print(ex.args)
            shutil.move( imglist[i], targetFolder)
        else:
            pass

#working correct. If image is gray then move to gray folder, else to color
def updateImage(path):
    pil_img = ImgPIL.open(path)
    imgWidth, imgHeight = pil_img.size
    pil_img.close()
    img = ImageCustom(path)
    img.setWH(imgWidth, imgHeight)
    img.setGray(False)
    img.detect_color_image()
    if img.isGray:
        shutil.move(img.path, gray_folder)
    else:
        shutil.move(img.path, color_folder) 

#init Images with path, width and height from list of paths
def RemoveSimilarImages(pathsList, target = None):
    insideImgList = list()
    for path in pathsList:
        pil_img = ImgPIL.open(path)
        imgWidth, imgHeight = pil_img.size
        img = ImageCustom(path)
        #img.setCalculatePixels(pil_img)
        pil_img.close()
        img.setWH(imgWidth, imgHeight)
        insideImgList.append(img)
    insideImgList.sort()
    letnOfList = len(insideImgList)
    batchesList = MakeSimilarBatches(insideImgList)
    
    tuplList = list()
    counter = 0
    for item in batchesList:
        if(len(item)!= 0):
            tmp = item, target
            for i in item:
                counter = counter + 1
            tuplList.append(tmp)
        else:
            pass

    #for item in tuplList:
    #    RemoveImagesInBatchesFaster(item)
    #if __name__ == '__main__':
    pool = Pool(processes = multiprocessing.cpu_count())
    pool.map(RemoveImagesInBatches, tuplList)
    
    #tesing new function
    #pool = Pool(processes = multiprocessing.cpu_count())
    #pool.map(RemoveImagesInBatchesFaster, tuplList)
    

#break list by sets of same heigth 
#does not affect distinct heigths (drops them)
def BreakListByHeight(listOfImages):
    prev = None
    l = list()
    s = set()
    for item in listOfImages:
        if(prev is None):
            prev = item
        else:
            if(prev.height == item.height):
                s.add(prev)
                s.add(item)
                prev = item
            else:
                prev = item
                l.append(s)
                s = set()
    l.append(s)
    return l

#check if images are equeal
def equal(im1, im2):
    return ImageChops.difference(im1, im2).getbbox() is None

#perform compare function on batches
def RemoveImagesInBatches(inputData):
    batch, target = inputData
    l = list(batch)
    l.sort(key=lambda x: x.height)
    listOfAllImages = list()
    if(len(l)!=0):
        listOfSetsByHeight = BreakListByHeight(l)
        for itm in listOfSetsByHeight:
            newList = list(itm)
            q = 0
            for z in range(0,  len(newList)):
                prev = None
                for x in range(q,len(newList)):
                    if(prev is None):
                        prev = newList[x]
                    else:
                        if(prev.height == newList[x].height):
                            pil_img1 = ImgPIL.open(prev.path)
                            pil_img2 = ImgPIL.open(newList[x].path)  
                            try:
                                eqTmp = equal(pil_img1.convert('RGB'),pil_img2.convert('RGB'))
                                if(eqTmp == True):
                                    pil_img1.close()
                                    pil_img2.close()
                                    newList[x].setIsSimilar(True)
                                else:
                                    pil_img1.close()
                                    pil_img2.close()
                            except Exception as ex:
                                pass 
                        else:
                            pass
                q = q + 1    
            for item in newList:
                listOfAllImages.append(item)
    #debuging
    if (len(l)!=0):
        for item in listOfAllImages:
            try:
                if(item.isSimilar):
                    print(item.path + " " + str(item.isSimilar))
            except Exception as ex:
                print(item.path +  " " + "FALSE") 
        if(target is None):
            for item in listOfAllImages:
                try:
                    if(item.isSimilar):
                        os.remove(item.path)
                except Exception as ex:
                    pass       
        else:
            for item in listOfAllImages:
                try:
                    if(item.isSimilar):
                        shutil.move(item.path, target)
                except Exception as ex:
                    pass

#get list of similar images from all images list
def GetSimilarList(imgListOfSimilarImages):
    l = list()
    for item in imgListOfSimilarImages:
        try:
            if(item.isSimilar == True):
                l.append(item)
            else:
                pass
        except Exception as ex:
            pass
    return l

#make batches of similar images
def MakeSimilarBatches(allImgList):
    batchesList = list()
    prev = None
    tmpList = set()
    unmatchCount = 0
    for item in allImgList:
        if(prev is not None):
            if(item.width == prev.width):
                tmpList.add(prev)
                tmpList.add(item)
                prev=item
                unmatchCount = 0
            else:
                batchesList.append(tmpList)
                tmpList = set()
                prev=item
        else:
            prev=item
            unmatchCount = 0
    if len(batchesList) == 0:
        batchesList.append(tmpList)
    batchesList.append(tmpList)
    return batchesList

#turn image to gray
def turnToGray(path):
    img = cv2.imread(path, 0)
    os.remove(path)
    cv2.imwrite(path, img)

#filter using bilateral filter
def applyBillateralFilter(path):
    img = cv2.imread(path)
    blur = cv2.bilateralFilter(img, 10, 100, 100)
    os.remove(path)
    cv2.imwrite(path, img)

def writeImageDataToFile(imgPath, filePath):
    img = ImgPIL.open(imgPath)
    imgmat = np.array(list(img.getdata(band=0)), float)
    size_1 = img.size[1]
    size_0 = img.size[0]
    imgmat.shape = (img.size[1], img.size[0])
    imgmat = np.matrix(imgmat)
    np.savetxt(filePath, imgmat, delimiter=',', fmt='%10.5f',)

def SVDImage(tupl):
    path, composition = tupl
    img = ImgPIL.open(path)
    #conevrt to numpy array
    imgmat = np.array(list(img.getdata(band=0)), float)
    size_1 = img.size[1]
    size_0 = img.size[0]
    imgmat.shape = (img.size[1], img.size[0])
    imgmat = np.matrix(imgmat)
    #compute SVD
    U, sigma, V = np.linalg.svd(imgmat)
    round_numb = int(round(((size_1/100) * composition), 0))
    try:
        reconstimg = np.matrix(U[:, :round_numb]) * np.diag(sigma[:round_numb]) * np.matrix(V[:round_numb, :])
    except ValueError:
        round_numb = int(round(((size_0/100) * composition),0))
        reconstimg = np.matrix(U[:, :round_numb]) * np.diag(sigma[:round_numb]) * np.matrix(V[:round_numb, :])
    im_new = ImgPIL.fromarray(reconstimg)
    os.remove(path)
    im_new = im_new.convert('RGB')
    im_new.save(path)

def writeToFile(targetPathToFile, infoToWrite):
    f = open(targetPathToFile, 'w')
    string =   str(infoToWrite)
    f.write(string)
    f.close()

'''
#using move by sizes
sourcePath = 'D:\\Img_base\\Classes\\Anime_blonde\\All'
targetPath = 'D:\\Img_base\\Classes\\Anime_blonde\\Junk'
moveImagesToFolderByResolution(sourcePath, targetPath, 150, 150)
'''

#sorting by color
#sourcePath = 'D:\\Img_base\\Classes\\Anime_blonde\\All'
#sourcePath = 'E:\\AXEGAO\\Images\\PIL_TEST\\All to gray without filter'
#sourcePath = 'E:\\AXEGAO\\Images\\PIL_TEST\\image_comp_test'


    
'''
start_time = time.time()

arglist = []
pathsList = list()
for file in os.listdir(sourcePath):
    pathToFile = sourcePath + "\\" + file
    #tupl = (pathToFile, 70)
    #arglist.append(tupl)
    #SVDImage(tupl)
    pathsList.append(pathToFile)

RemoveSimilarImages(pathsList, target = gray_folder)
string =   str(time.time() - start_time)
print(string)
'''


'''
##playing with processes
if __name__ == '__main__':
    pool = Pool(processes=4)
    #sort Gray and color images
    pool.map(updateImage, pathsList)
    #turn color images to gray with noise
    #pool.map(turnToGray, pathsList)
    #apply billateral filter
    ##pool.map(applyBillateralFilter, pathsList)
    #apply SVD to images
    ##pool.map(SVDImage, arglist)
'''

'''
string =   str(time.time() - start_time)
f.write(string)
f.close()
'''

