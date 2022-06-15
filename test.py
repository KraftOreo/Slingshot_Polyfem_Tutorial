from slingshot.src.slingshot import SlingShot
import numpy as np

env = SlingShot()

for i in range(5):
    action = np.array([0.1,0,0,0])
    env.step(action)
    