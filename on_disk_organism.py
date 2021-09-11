import numpy as np
from rand_walk import deconv
from matplotlib import pyplot as plt
import json
import traceback

img_size = 128
num_cromosomes = 12

label_track = 0

class gene:
    def __init__(self,mode="blank",label="XD",fileobject=None):
        self.child_count = 0
        self.label = label
        if(mode=="progeneitor"):
            self.img_generator = np.random.randint(0,256,(img_size,img_size),dtype=np.uint8)
            self.mutation_rate = np.random.randint(0,5,self.img_generator.shape,dtype=np.uint8)
        if(mode == "blank"):
            self.img_generator = np.zeros((img_size,img_size),dtype=np.uint8)
            self.mutation_rate = np.zeros(self.img_generator.shape,dtype=np.uint8)
        if(mode == "file"):
            self.img_generator = np.array(list(fileobject.read(img_size**2)),dtype=np.uint8).reshape(img_size,img_size)
            self.mutation_rate = np.array(list(fileobject.read(img_size**2)),dtype=np.uint8).reshape(img_size,img_size)

    def reproduce(self):
        ret = gene(mode="blank",label=f"{self.label}-{self.child_count}")
        self.child_count += 1
        ret.img_generator = self.img_generator
        ret.img_generator += np.random.randint(1+np.int64(self.mutation_rate),dtype=np.uint8)
        ret.mutation_rate = self.mutation_rate
        ret.mutation_rate += np.uint8(np.abs(np.random.randint(-2,3,size=ret.mutation_rate.shape,dtype=np.int8)))
        return ret
    def __repr__(self):
        return f"{self.label}"

class organism:
    def __init__(self,mode="blank",filename=None):
        self.child_count = 0
        self.num_battles_fought = 0
        self.num_battles_lost = 0
        if(mode == "progeneitor"):
            global label_track
            self.genome = [[gene(mode="progeneitor",label=f"{label_track}.{j}.{i}") for i in range(2)] for j in range(num_cromosomes)]
            label_track += 1

        if(mode == "file"):
            f = open(filename+".organism","rb")
            self.genome = []
            for i in range(num_cromosomes):
                self.genome.append([])
                for j in range(2):
                    self.genome[-1].append(gene(mode="file",fileobject=f))
            remainder = f.read().decode()
            remainder = remainder[2:-2]
            ts = remainder.split("], [")
            for i,t in enumerate(self.genome):
                gs = ts[i].split(", ")
                for j,g in enumerate(t):
                    g.label = gs[j]
            f.close()
            trackdump = organism.read_trackdump(filename)
            self.child_count = trackdump["child_count"]
            self.num_battles_fought = trackdump["num_battles_fought"]
            self.num_battles_lost = trackdump["num_battles_lost"]
            c = 0
            for t in self.genome:
                for g in t:
                    g.child_count = trackdump["gene-childcounts"][c]
                    c += 1

    def get_mugshot(self):
        r,g,b = (0,0,0)
        r = deconv(np.mean([g.img_generator for g in sum(self.genome[0::3],[])],axis=0))
        g = deconv(np.mean([g.img_generator for g in sum(self.genome[1::3],[])],axis=0))
        b = deconv(np.mean([g.img_generator for g in sum(self.genome[2::3],[])],axis=0))
        ret = np.array([r,g,b],dtype=np.uint8).transpose(1,2,0)
        return ret
    def __repr__(self):
        return str(self.genome)
    def save_trackdump(self,filename):
        f = open(filename+".trackdump","w+")
        for t in self.genome:
            for g in t:
                f.write(f"{g.child_count}|")
        f.write(f"\n{self.child_count}")
        f.write(f"\n{self.num_battles_fought}")
        f.write(f"\n{self.num_battles_lost}")
        f.close()
    def save_img(self,filename):
        plt.imsave(filename+".png",self.get_mugshot())
    def save(self,filename):
        f = open(filename+".organism",'w+b')
        for t in self.genome:
            for g in t:
                f.write(bytes(g.img_generator.flatten().tolist()))
                f.write(bytes(g.mutation_rate.flatten().tolist()))
        f.write(bytes(str(self),'ascii'))
        f.close()
        self.save_trackdump(filename)
        self.save_img(filename)

    @staticmethod
    def read_trackdump(filename):
        f = open(filename+".trackdump","r")
        lines = f.readlines()
        f.close()
        ret = {}
        ret["gene-childcounts"] = list(map(int,lines[0].split("|")[:-1]))
        ret["child_count"] = int(lines[1].strip())
        ret["num_battles_fought"] = int(lines[2].strip())
        ret["num_battles_lost"] = int(lines[3].strip())
        return ret

    def redump_trackdump(filename,td):
        f = open(filename+".trackdump","w+")
        for z in td["gene-childcounts"]:
            f.write(str(z))
            f.write("|")
        f.write(f'\n{td["child_count"]}')
        f.write(f"\n{td['num_battles_fought']}")
        f.write(f"\n{td['num_battles_lost']}")
        f.close()

    def reproduce(organism1,organism2):
        ret = organism(mode="blank")
        ret.genome = []
        for i in range(len(organism1.genome)):
            choice1 = organism1.genome[i][np.random.randint(2)]
            choice2 = organism2.genome[i][np.random.randint(2)]
            ret.genome.append([choice1.reproduce(),choice2.reproduce()])
        organism1.child_count += 1
        organism2.child_count += 1
        return ret

    def ondiskbattle(filename1,filename2,winner,num_losses_to_death):
        td = [organism.read_trackdump(filename1),organism.read_trackdump(filename2)]
        if(td[0]["num_battles_lost"] >= num_losses_to_death or td[1]["num_battles_lost"] >= num_losses_to_death):
            return 4
        loser = 1-winner
        td[winner]["num_battles_fought"]+=1
        td[loser]["num_battles_fought"]+=1
        td[loser]["num_battles_lost"]+=1
        organism.redump_trackdump(filename1,td[0])
        organism.redump_trackdump(filename2,td[1])
        if(td[loser]["num_battles_lost"] == num_losses_to_death):
            return loser
        return 2

def testfunction1():
    o1 = organism('progeneitor')
    o2 = organism('progeneitor')
    o3 = organism.reproduce(o1,o2)
    o4 = organism.reproduce(o3,o1)
    plt.imshow(o1.get_mugshot())
    plt.figure()
    plt.imshow(o2.get_mugshot())
    plt.figure()
    plt.imshow(o3.get_mugshot())
    plt.figure()
    plt.imshow(o4.get_mugshot())
    print(o1,o2,o3,o4,sep="\n\n")
    o1.save('dump/o1')
    o2.save('dump/o2')
    o3.save('dump/o3')
    o4.save('dump/o4')
    #plt.show()

def readtestfunction():
    o2 = organism(mode="file",filename="dump/o2")
    plt.imshow(o2.get_mugshot())
    print(o2)
    o2.save_trackdump('dump/o22')
    plt.show()

def ondiskbattletest():
    o1 = organism('progeneitor')
    o2 = organism('progeneitor')
    o1.save('dump/o1')
    o2.save('dump/o2')
    print(organism.ondiskbattle('dump/o1','dump/o2',0,2))
    print(organism.ondiskbattle('dump/o1','dump/o2',1,2))
    print(organism.ondiskbattle('dump/o1','dump/o2',0,2))
    print(organism.ondiskbattle('dump/o1','dump/o2',0,2))

def main_step():
    inp = input()
    if(len(inp)>0):
        try:
            world_dump_filename = "public/dump/zhewarudo.json"
            f = open(world_dump_filename,'r')
            world_dump = json.load(f)
            f.close()
            fn1,fn2,w,nltd = inp.split(' ')
            w = int(w)
            nltd = int(nltd)
            ffn1 = world_dump["dumppath"] + fn1
            ffn2 = world_dump["dumppath"] + fn2
            ret = organism.ondiskbattle(ffn1,ffn2,w,nltd)
            printmsg = str(ret)

            dumpjson = False
            if(ret == 0 or ret == 1):
                world_dump["living_filenames"].pop(world_dump["living_filenames"].index([fn1,fn2][ret]))
                printmsg += f" killed {[fn1,fn2][ret]} |"
            if(len(world_dump["living_filenames"]) < 100):
                living_filenames = world_dump["living_filenames"]
                o1 = organism("file",world_dump["dumppath"]+np.random.choice(living_filenames))
                o2 = organism("file",world_dump["dumppath"]+np.random.choice(living_filenames))
                onew = organism.reproduce(o1,o2)
                new_filename = f'o{world_dump["nameprogression"]+1}'
                world_dump["nameprogression"] += 1
                living_filenames.append(new_filename)
                world_dump["living_filenames"] = living_filenames
                onew.save(world_dump["dumppath"]+new_filename)
                dumpjson = True
                printmsg += f" added {new_filename} |"
            if(ret == 4):
                ind1 = world_dump["living_filenames"].index(fn1)
                if(ind1 != -1):
                    world_dump["living_filenames"].pop(ind1)
                    printmsg += f" {fn1} was removed from list |"
                ind2 = world_dump["living_filenames"].index(fn2)
                if(ind2 != 2):
                    world_dump["living_filenames"].pop(ind2)
                    printmsg += f" {fn2} was removed from list |"
                dumpjson = True
            if(dumpjson):
                f = open(world_dump_filename,'w+')
                json.dump(world_dump,f)
                f.close()
            print(printmsg)
        except Exception as e:
            print(e)

def initialize(num_organisms=100,path="public/dump/"):
    world_dump = {
        "dumppath":path,
        "living_filenames":[],
        "nameprogression": 0,
        "num_organisms":num_organisms
    }
    for i in range(num_organisms):
        filename = f'o{i}'
        world_dump['living_filenames'].append(filename)
        o = organism('progeneitor')
        o.save(path+filename)
    world_dump['nameprogression'] = num_organisms-1
    f = open(path+'zhewarudo.json',"w+")
    json.dump(world_dump,f)
    f.close()

def main_step_test():
    while(True):
        main_step()

if(__name__ == "__main__"):
    import sys
    print("yep working anol")
    # testfunction1()
    # readtestfunction()
    #ondiskbattletest()
    if(len(sys.argv) > 1 and sys.argv[1] == "initiate"):
        initialize()
        exit(0)

    main_step_test()
