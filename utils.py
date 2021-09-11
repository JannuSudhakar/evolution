import numpy as np

def translate_x(arr,n):
    ret = arr*0
    if(n > 0):
        partition = min(n,arr.shape[1]-1)
    else:
        partition = max(arr.shape[1] + n,1)
    ret[:,:partition] = arr[:,-partition:]
    ret[:,partition:] = arr[:,:(-partition)]
    return ret

def translate_y(arr,n):
    ret = arr*0
    if(n > 0):
        partition = min(n,arr.shape[0]-1)
    else:
        partition = max(arr.shape[0] + n,1)
    ret[:partition] = arr[-partition:]
    ret[partition:] = arr[:(-partition)]
    return ret

if(__name__ == "__main__"):
    arr = np.arange(12).reshape(3,4)
    print(arr)
    print(translate_x(arr,2))
    print(translate_y(arr,2))
