import numpy as np
from matplotlib import pyplot as plt
import time
import utils

class organism:
    def __init__(self,blank=False):
        self.size = (64,64)
        self.age = 0
        self.num_rejections = 0
        if(not blank):
            self.img = np.random.randint(0,256,self.size,dtype=np.int64)
            self.generation = 0
    def reproduce(self):
        ret = organism(blank = True)
        ret.img = (self.img + np.uint8(np.random.exponential(size=self.size)) - np.uint8(np.random.exponential(size=self.size))).clip(0,255)
        dx,dy = np.int8(np.round(1.5*np.random.randn(2)))
        #ret.img = utils.translate_y(utils.translate_x(ret.img,dx),dy)
        ret.generation = self.generation + 1
        return ret

def fitness_function(o1,o2):
    half = int(o1.size[0]/2)
    y = np.int64(o1.img)-np.int64(o2.img)+255
    y1 = np.linalg.norm(y[0:half])
    y2 = np.linalg.norm(y[half:])
    if(y1 > y2):
        return True
    else:
        return False

plt.interactive(True)
num_organisms = 6
rejection_limit = 1
organisms = [organism() for i in range(num_organisms)]

fig,((ax1,ax2,ax3),(ax4,ax5,ax6)) = plt.subplots(2,3)
ax = [ax1,ax2,ax3,ax4,ax5,ax6]
iteration_count = 0
kill_count = 0

while(True):
    perm = np.random.permutation(num_organisms)
    organisms[perm[0]].age += 1
    organisms[perm[1]].age += 1
    print(f"organism no.{perm[0]}, gen: {organisms[perm[0]].generation}, age: {organisms[perm[0]].age}/{organisms[perm[0]].num_rejections}")
    print(f"organism no.{perm[1]}, gen: {organisms[perm[1]].generation}, age: {organisms[perm[1]].age}/{organisms[perm[1]].num_rejections}")
    if((iteration_count+1)%1000 == 0):
        for i in range(6):
            ax[i].clear()
            ax[i].imshow(organisms[perm[i]].img,cmap="gray")
            ax[i].set_title(f"organism no.{perm[i]}")
        fig.suptitle(f"iteration no: {iteration_count}")
        print(f"done with {iteration_count} iterations. {kill_count} killed")
        inp = input("stop? ")
        if(inp == "stop"):
            break
    if(fitness_function(organisms[perm[0]],organisms[perm[1]])):
        rejected = perm[1]
    else:
        rejected = perm[0]
    if(rejected is not None):
        organisms[rejected].num_rejections += 1
        if(organisms[rejected].num_rejections >= rejection_limit):
            kill_count += 1
            print(f"no.{rejected} killed")
            organisms.pop(rejected)
            reproducer = organisms[np.random.randint(0,num_organisms-1)]
            organisms.append(reproducer.reproduce())
    iteration_count += 1
