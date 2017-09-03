import logger
import lxml.html
import re
import concurrent.futures
import urllib.request
import codecs
import threading
import os

#region good code

#for links
theList = list()

#parse html and get links or load from clear file
def ReadListOfLinksFromFile(filePath, isHtml = False):
    if(not isHtml):
        f = open(filePath, 'r')
        x = f.readlines()
        t = map(lambda s: s.strip(), x)
        f.close()
        return list(t)
    else:
        doc = ""
        f = codecs.open(filePath, encoding='utf-8')
        for line in f:
            doc +=line
        p = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        links = re.findall(p, doc)

        filtredJPG = filter(lambda k: '.jpg' in k, links)
        filtredPNG = filter(lambda k: '.png' in k, links)
        filtredGIF = filter(lambda k: '.gif' in k, links)
        filtredJPG = cleanJPG(filtredJPG)
        allImages = list(filtredJPG) + list(filtredPNG) + list(filtredGIF)
        return allImages

def cleanJPG( listOfJPGs ):
   "remove all data after .jpg"
   q = list()
   for i in listOfJPGs:
       sub = i.split('.jpg', 1)[0] + '.jpg'
       q.append(sub) 
   return q

def LoadToFolder(folderPath, shortname, max_workers = 50):
    with concurrent.futures.ThreadPoolExecutor(max_workers) as e:
        for i in range(len(theList)):
            try:
                tmp = i, shortname, folderPath
                e.submit(getimg, tmp)
            except Exception as ex:
                logger.LogFromTread(str(i) + " " + ex.args + "\n") 

def getimg(tmp):
    count, shortname, folderPath = tmp
    filename, file_extension = os.path.splitext(theList[count])
    localpath =  (folderPath +   '\\{0}{1}' + file_extension).format(shortname, count)
    try:
        localpath, headers = urllib.request.urlretrieve(theList[count], localpath)
        #urllib.request.urlretrieve(theList[count], localpath)
        item = theList[count] + "|" + localpath + "|" + str(headers) + "\n"
        logger.LogFromTread(item, file_name = 'downloadLog.log')
    except Exception as ex:
        item = theList[count] + "|" + localpath + "|" + str(ex.args) + "\n"
        logger.LogFromTread(item, file_name = 'downloadLog.log')
    #theList[count] = localpath

#end region

#start dowloading images from web

theList = ReadListOfLinksFromFile('D:\\Img_base\\Scraping\\Faces\\faces.txt')
LoadToFolder('D:\\Img_base\\Scraping\\Faces','Face',200)

'''
def getimg(tmp):
    count, shortname, folderPath = tmp
    localpath = 'D:\\Img_base\\Scraping\\{0}{1}.jpg'.format(catname, count)
    try:
        localpath, headers = urllib.request.urlretrieve(theList[count], localpath)
        #urllib.request.urlretrieve(theList[count], localpath)
        item = theList[count] + "|" + localpath + "|" + "Loaded" + "|" + str(headers) + "\n"
        logger.LogFromTread('D:\\Img_base\\Scraping\\log.txt' + item)

    except Exception as ex:
        item = theList[count] + "|" + localpath + "|" + "NotLoaded" + "|" + str(ex.args) + "\n"
        logger.LogFromTread('D:\\Img_base\\Scraping\\log.txt' + item)
    theList[count] = localpath

#start dowloading images from web
with concurrent.futures.ThreadPoolExecutor(max_workers=50) as e:
    for i in range(len(allImages)):
        try:
            e.submit(getimg, i)
        except Exception as ex:
            logger.LogFromTread(i + ex.args + "\n")
        
'''

