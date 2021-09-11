import numpy as np
from matplotlib import pyplot as plt
import time

from rand_walk import deconv

class organism:
    def __init__(self,blank=False):
        self.generation = 1
        self.rejection_count = 0
        self.age = 0
        self.num_cromosomes = 3
        self.size = (64,64,2)
        self.genome = [[],[]]
        self.mugshot_avg = None
        self.mugshot_std = None
        self.mutation_rate_avg = None
        self.mutation_rate_std = None

        self.mugshot_img = None
        for cr in self.genome:
            for i in range(self.num_cromosomes):
                if(not blank):
                    cr.append(np.random.randint(0,256,self.size))
                    cr[-1][:,:,1] %= 5
                else:
                    cr.append(np.zeros(self.size))
    def mugshot(self):
        if(self.mugshot_img is not None):
            return self.mugshot_img
        A = np.array(self.genome)[:,:,:,:,0]
        ret = np.zeros((self.size[0],self.size[1],3))
        ret[:,:,0] = A[:,0::3].mean((0,1))
        ret[:,:,1] = A[:,1::3].mean((0,1))
        ret[:,:,2] = A[:,2::3].mean((0,1))
        ret[:,:,0] = deconv(ret[:,:,0])
        ret[:,:,1] = deconv(ret[:,:,1])
        ret[:,:,2] = deconv(ret[:,:,2])
        if(self.mugshot_avg is None): self.mugshot_avg = ret.mean()
        if(self.mugshot_std is None): self.mugshot_std = ret.std()
        self.mugshot_img = np.uint8(ret)
        return self.mugshot_img
    def print_deets(self):
        if(self.mutation_rate_avg is None):
            A = np.array(self.genome)[:,:,:,:,1]
            self.mutation_rate_avg = A.mean()
            self.mutation_rate_std = A.std()
        print("___________")
        print(f"generation/age/rejection_count: {self.generation}/{self.age}/{self.rejection_count}")
        print(f"mugshot_stats: {self.mugshot_avg}/{self.mugshot_std}")
        print(f"mutation rate stats: {self.mutation_rate_avg}/{self.mutation_rate_std}")
        print("___________")

def reproduce(organism1,organism2):
    ret = organism()
    ret.generation = organism1.generation + organism2.generation
    for i in range(organism1.num_cromosomes):
        cr1 = organism1.genome[0][i] if np.random.randint(2) == 0 else organism1.genome[1][i]
        cr2 = organism2.genome[0][i] if np.random.randint(2) == 0 else organism2.genome[1][i]
        ret.genome[0][i][:,:,0] = np.uint8(cr1[:,:,0] + np.random.normal(0,cr1[:,:,1]))
        ret.genome[1][i][:,:,0] = np.uint8(cr2[:,:,0] + np.random.normal(0,cr2[:,:,1]))
        ret.genome[0][i][:,:,1] = np.int8(cr1[:,:,1] + np.random.normal(0,size=organism1.size[:2])).clip(0)
        ret.genome[1][i][:,:,1] = np.int8(cr2[:,:,1] + np.random.normal(0,size=organism2.size[:2])).clip(0)
    A = np.array(ret.genome)[:,:,:,:,1]
    ret.mutation_rate_avg = A.mean()
    ret.mutation_rate_std = A.std()
    return ret

plt.interactive(True)

pop_size = 20
rejection_limit = 2
O = []
for i in range(pop_size):
    O.append(organism())

fig, ((ax3,ax1),(ax4,ax2)) = plt.subplots(2,2)

axes = [ax4,ax2]

iteration_count = 0
kill_count = 0
starttime = time.time()
while(True):
    fig.suptitle(f"iteration no: {iteration_count}")
    displayed_organisms = []
    perm = np.random.permutation(pop_size)
    for i in range(2):
        displayed_organisms.append(perm[i])
        O[perm[i]].age += 1
        axes[i].imshow(O[perm[i]].mugshot())
        O[perm[i]].print_deets()
        axes[i].set_title(f"organism no.{perm[i]}")
    print("_______________________________________________________________________________")
    print(f"iterations: {iteration_count}. kills: {kill_count}. time elapsed: {time.time()-starttime:.2f}s indices displayed: {displayed_organisms}")
    inp = input(">>>>>>>>>input plz (put stop to stop): ")
    print("_______________________________________________________________________________")
    if(inp == "stop"):
        break
    if(inp == "organism"):
        inp = input(f"which organism? (0-{pop_size-1}) : ")
        try:
            inp = int(inp)
            if(inp >= pop_size or inp < 0):
                print("not in range")
                continue
            O[inp].print_deets()
            ax3.set_title(f"mugshot of organism no.{inp}")
            ax3.imshow(O[inp].mugshot())
            input("----press enter to continue----")
        except(ValueError):
            print("give valid index")
        continue
    if(inp == "cromosome"):
        inp = input(f"which organism? (0-{pop_size-1}): ")
        try:
            org = int(inp)
            if(org >= pop_size or org < 0):
                print("index not in range")
                continue
            inp = input(f"which cromosome?(0-{O[org].num_cromosomes-1}): ")
            try:
                cromosome = int(inp)
                if(cromosome >= O[org].num_cromosomes or cromosome < 0):
                    print("index not in range")
                    continue

                ax3.set_title(f"cromosome.{org}.{cromosome}.1 mugshot")
                ax3.imshow(O[org].genome[1][cromosome][:,:,0],cmap="gray")
                ax4.set_title(f"cromosome.{org}.{cromosome}.1 std")
                ax4.imshow(O[org].genome[1][cromosome][:,:,1],cmap="gray")

                ax1.set_title(f"cromosome.{org}.{cromosome}.0 mugshot")
                ax1.imshow(O[org].genome[0][cromosome][:,:,0],cmap="gray")
                ax2.set_title(f"cromosome.{org}.{cromosome}.0 std")
                ax2.imshow(O[org].genome[0][cromosome][:,:,1],cmap="gray")
                input("----press enter to contunue----")
            except(ValueError):
                print("give valid index")
        except(ValueError):
            print("give valid index")
        continue
    if(inp == "1"):
        rejected = 1
        iteration_count += 1
    elif(inp == "2"):
        rejected = 0
        iteration_count += 1
    else:
        rejected = None
    if(rejected is not None):
        O[displayed_organisms[rejected]].rejection_count += 1
        if(O[displayed_organisms[rejected]].rejection_count >= rejection_limit):
            print(f"killed no.{displayed_organisms[rejected]}")
            kill_count += 1
            O.pop(displayed_organisms[rejected])
            perm = np.random.permutation(pop_size-1)
            print(O)
            O.append(reproduce(O[perm[0]],O[perm[1]]))
