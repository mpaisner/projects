import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
import numpy as np

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

xs = (0.50902015, 0.134998404, 0.359977948, 0.130461968, 0.241641806, 0.110780615, 0.154571487, 0.041151526)
ys = (0.241836382, 0.484003732, 0.175700865, 0.35100951, 0.179261853, 0.207819914, 0.087780768, 0.047118033)
zs = (0.122699234, 0.145240808, 0.076568059, 0.094903964, 0.01883706, 0.073650025, 0.053971636, 0.046230187)

oneanomx = (0.0843468329401, 0.0772315392164, 0.0934379161447, 0.0801144075276, 0.038787564708)
oneanomy = (0.472076451622, 0.303390206817, 0.0896248812158, 0.0479269446555, 0.0442151697927)
oneanomz = (0.199940093355, 0.136637828511, 0.0947922330848, 0.0502050613446, 0.0347728248689)

oneanomcolors = ['orange', 'orange', 'g', 'g', 'g']

normx = (0.193766684339, 0.122452958334, 0.0538885233884)
normy = (0.117323313165, 0.0953252376977, 0.06268956964)
normz = (0.0915731756393, 0.0538657018896, 0.0784035803396)

colors = ['r', 'b', 'r', 'b', 'r', 'b', 'g', 'g']

ax.scatter(xs, ys, zs, s=180, c=colors)
#ax.scatter(oneanomx, oneanomy, oneanomz, s=180, c=oneanomcolors)
#ax.scatter(normx, normy, normz, s=180, c='black')

u = np.linspace(0, 2 * np.pi, 100)
v = np.linspace(0, 1 * np.pi, 100)

x = 0.23 * np.outer(np.cos(u), np.sin(v))
y = 0.23 * np.outer(np.sin(u), np.sin(v))
z = 0.23 * np.outer(np.ones(np.size(u)), np.cos(v))
		
ax.plot_surface(x, y, z,  rstride=20, cstride=20, color='black', alpha = 0.15, linewidth=1)


plt.ylim([0, 0.7])
plt.xlim([0, 0.7])

boundaryx = [0, 0, 0, 0, 0.7, 0.7, 0.7, 0.7]
boundaryy = [0, 0, 0.7, 0.7, 0, 0, 0.7, 0.7]
boundaryz = [0, 0.7, 0, 0.7, 0, 0.7, 0, 0.7]

ax.scatter(boundaryx, boundaryy, boundaryz, alpha=0)
ax.set_xlabel("Inside-Truck A-distance")
ax.set_ylabel("Inside-Airplane A-distance")
ax.set_zlabel("At-Object A-distance")

plt.show()