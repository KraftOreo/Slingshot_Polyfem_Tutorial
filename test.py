from slingshot.src.slingshot import SlingShot
import numpy as np
import time

start=time.time()
env = SlingShot(output_dir="results/simulation",force_reload=False)
print("Initialzied.")
# pull the rubber band
for i in range(20):
    action = np.array([0.01,0,0,0])
    env.step(action)
    print("step", i)

# release it
action = np.array([0,0,0,0])
env.step(action)
action = np.array([0,0,0,0])
env.step(action)
env.step(action)
action = np.array([0,0,0,-0.1])
env.step(action)
print("released")
# let it fly
for i in range(40):
    action = np.array([0,0,0,0])
    env.step(action)
    print("flying", i)

end=time.time()
print("Takes ",end-start,"s")