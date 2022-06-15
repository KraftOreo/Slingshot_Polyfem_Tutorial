from slingshot.src.slingshot import SlingShot
import numpy as np

env = SlingShot()
print("Initialzied.")
# pull the rubber band
for i in range(15):
    action = np.array([0.02,0,0,0])
    env.step(action)
    print("step", i)

# release it
action = np.array([0,0,0,0])
env.step(action)
action = np.array([0,0,0,-0.1])
env.step(action)
print("released")
# let it fly
for i in range(20):
    action = np.array([0,0,0,0])
    env.step(action)
    print("flying", i)