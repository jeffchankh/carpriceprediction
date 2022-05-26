from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt2
import matplotlib.patches as patches
import cv2
import datetime
import os
import csv
import sys, getopt

#from google.colab import drive

#drive.mount('/content/drive')
#img = cv2.imread('/content/drive/MyDrive/20130824_205655.jpg')
#img = cv2.imread('webscrap/s1928270_high.jpg')


def color_from_pic(path):
    
    itms=[]
    print(path)
    img = cv2.imread(path)
    if img is None:
        return itms
    #cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    plt.imshow(img[:,:,::-1])
    #plt.show()
    height, width, dim = img.shape
    print(height/4, width/4, dim)
    img = img[int(height/4):int(3*height/4), int(width/4):int(3*width/4), :]
    height, width, dim = img.shape

    img_vec = np.reshape(img, [height * width, dim] )

    kmeans = KMeans(n_clusters=3)
    kmeans.fit( img_vec )

    unique_l, counts_l = np.unique(kmeans.labels_, return_counts=True)
    sort_ix = np.argsort(counts_l)
    sort_ix = sort_ix[::-1]

    fig = plt2.figure()
    ax = fig.add_subplot(111)
    x_from = 0.05

    for cluster_center in kmeans.cluster_centers_[sort_ix]:
        itms.append('#%02x%02x%02x' % (int(cluster_center[2]), int(cluster_center[1]), int(cluster_center[0])))
        ax.add_patch(patches.Rectangle((x_from, 0.05), 0.29, 0.9, alpha=None, facecolor='#%02x%02x%02x' % (int(cluster_center[2]), int(cluster_center[1]), int(cluster_center[0])) ) )
        x_from = x_from + 0.31

    plt2.savefig(path.replace('_low', '_colorcodes'))
    #plt2.show()
    return itms



def main(argv):
    
    options, remainder = getopt.getopt(sys.argv[1:], 'd:v', ['directory=', 
                                                         'verbose'
                                                         ])
    print('OPTIONS   :', options)
    
    for opt, arg in options:
        if opt in ('-d', '--dir'):
            directory = arg
        elif opt in ('-v', '--verbose'):
            verbose = True
            
    #directory='/Users/admin/DSBS/STAT5102/Project'

    #file='s1975996_high.jpg'
    #fullpath=os.path.join(str(directory), file)
    #color_from_pic(fullpath)
    #return
    now = datetime.datetime.now()
    ts=now.strftime("%Y%m%d%H%M%S")

    f=open(os.path.join(str(directory), 'colorcode'+ts+'.txt'), 'w')

    cnt=0
    for file in os.listdir(directory):
        #if cnt == 1:
        #    break
        #filename = os.fsdecode(file)
        #file='s2073562_low.jpg'
        if file.endswith("_low.jpg") and \
        not os.path.isfile(file.replace('_low', '_colorcodes')):
            fullpath=os.path.join(str(directory), file)
            print("Processing file # " + str(cnt) + ": " + fullpath)
            itms=color_from_pic(fullpath)
            f.write(file+',')
            f.write(','.join(itms))
            f.write('\n')
            f.flush()
            cnt+=1
            continue
        else:
            continue
    
    colorcode='colorcode.txt'

    f2=open(os.path.join(str(directory), 'colorcode.txt'), 'r')
    f3=open(os.path.join(str(directory), 'colorcode'+ts+'.csv'), 'w')
    writer = csv.writer(f3, delimiter=',', quotechar='"')
    writer.writerow(['EntryID','Color1','Color2','Color3','Color1_1','Color1_2','Color1_3','Color2_1','Color2_2','Color2_3','Color3_1','Color3_2','Color3_3'])
    f3.flush()
    
    line = f2.readline()
    cnt = 1
    while line:
        if (cnt % 100 == 0):
            print("Processed "+str(cnt)+" so far")
        tok=line.split(',')
        entryid=tok[0].split('_')[0]
        if len(tok) != 4:
            line = f2.readline()
            cnt += 1
            continue
        color1_1=int(tok[1][1:3], 16)
        color1_2=int(tok[1][3:5], 16)
        color1_3=int(tok[1][5:7], 16)
        color1=int(tok[1][1:7],16)
        color2_1=int(tok[2][1:3], 16)
        color2_2=int(tok[2][3:5], 16)
        color2_3=int(tok[2][5:7], 16)
        color2=int(tok[2][1:7],16)
        color3_1=int(tok[3][1:3], 16)
        color3_2=int(tok[3][3:5], 16)
        color3_3=int(tok[3][5:7], 16)
        color3=int(tok[3][1:7],16)
        #print(line)
        writer.writerow([entryid,str(color1),str(color2),str(color3),str(color1_1),str(color1_2),str(color1_3),str(color2_1),str(color2_2),str(color2_3),str(color3_1),str(color3_2),str(color3_3)])
        f3.flush()
        line = f2.readline()
        cnt += 1

    print("Processed "+str(cnt)+" files in total")    

if __name__ == "__main__":
   main(sys.argv[1:])
    
