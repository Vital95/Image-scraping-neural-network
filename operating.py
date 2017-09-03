import os
from multiprocessing import Pool
import time
import image_tools

targetPath = 'D:\\Img_base\\TMP_rename_test\\train\\train_folder'

#strange but it shuffle images somehow
image_tools.MaskRename(targetPath,'Ahegao')

#region remove same images tests
'''
sourcePath = 'D:\\Img_base\\Scraping\\big part faces'
targetPath = 'D:\\Img_base\\Scraping\\Junk'

pathsList = list()
for file in os.listdir(sourcePath):
    pathToFile = sourcePath + "\\" + file
    #tupl = (pathToFile, 70)
    #arglist.append(tupl)
    #SVDImage(tupl)
    pathsList.append(pathToFile)

start_time = time.time()

if __name__ == '__main__':
    import image_tools
    image_tools.RemoveSimilarImages(pathsList, target = targetPath)

string =   str(time.time() - start_time)

print(string)

'''
