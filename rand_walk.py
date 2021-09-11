import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import ArtistAnimation

def nthintegralrandwalk(length,n):
    ret = np.random.randn(length)
    for i in range(n):
        ret = np.cumsum(ret)
    return ret

def laplacian(shape):
    ret = np.zeros(shape)
    middle = (shape[0]//2,shape[1]//2)
    ret[middle[0],middle[1]] = -4
    ret[middle[0]-1,middle[1]] = 1
    ret[middle[0]+1,middle[1]] = 1
    ret[middle[0],middle[1]-1] = 1
    ret[middle[0],middle[1]+1] = 1
    return ret

def walk2d(dim,n):
    lap = laplacian(dim)
    fftlap = np.fft.fft2(lap)
    ret = np.random.normal(size=dim)
    fftret = np.fft.fft2(ret)
    for i in range(n):
        fftret /= fftlap
        ret = np.fft.ifft2(fftret)
        ret -= np.mean(ret)
    return ret

def deconv(img,mask="laplacian"):
    eps = 1e-6
    if(mask == "laplacian"):
        mask = laplacian(img.shape)
    fftlap = np.fft.fft2(mask)
    ret = np.abs(np.fft.ifft2(np.fft.fft2(img)/(fftlap + eps)))
    ret -= ret.min()
    ret /= ret.max()
    ret *= 255
    return ret

if(__name__ == "__main__"):
    import sys
    if(sys.argv[1] == "walks"):
        for i in range(1): plt.plot(nthintegralrandwalk(10000,1),color="green")
        for i in range(1): plt.plot(nthintegralrandwalk(10000,2),color="blue")
        for i in range(1): plt.plot(nthintegralrandwalk(10000,3),color="red")
        plt.show()
    if(sys.argv[1] == "deconvolve"):
        #print(laplacian([10,10]))
        lap = laplacian((101,101))
        fftlap = np.fft.fft2(lap)
        plt.imshow(np.abs(fftlap))
        plt.figure()
        g_qm = np.fft.ifft2(1/fftlap)
        plt.imshow(g_qm.real)
        plt.figure()
        plt.imshow(g_qm.imag)
        plt.figure()
        w2d = walk2d([499,499],1)
        plt.imshow(w2d.real,cmap="gray")
        plt.show()
    if(sys.argv[1] == "animate-deconvolve"):
        u = np.random.normal(size=[499,499])
        v = np.random.normal(size=[499,499])
        fig = plt.figure()
        ims = []
        for lmd in np.linspace(0,1,100):
            print(lmd)
            i = lmd*v + (1-lmd)*u
            lap = laplacian([499,499])
            fftlap = np.fft.fft2(lap)
            ffti = np.fft.fft2(i)/fftlap
            i = np.fft.ifft2(ffti).real
            i -= i.mean()
            im = plt.imshow(i,animated=True)
            ims.append([im])

        ani = ArtistAnimation(fig, ims, interval = 100,repeat_delay = 1000)
        ani.save('animate-deconvolve.mp4')
        plt.show()
