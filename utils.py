import matplotlib.pyplot as plt 
import numpy as np 

def show2images(leftpic,rightpic):
    f = plt.figure()
    f.add_subplot(1,2, 1)
    plt.imshow(np.rot90(leftpic,2))
    f.add_subplot(1,2, 2)
    plt.imshow(np.rot90(rightpic,2))
    plt.show(block=True)