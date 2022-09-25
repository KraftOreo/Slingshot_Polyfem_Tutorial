from slingshot.src.slingshot import SlingShot
import numpy as np
import time

start=time.time()
env = SlingShot(output_dir="results/simulation")
print("Initialzied.")
# pull the rubber band
for i in range(2):
    action = np.array([0.1,0,0,0])
    env.step(action)
    print("step", i)

# release it
action = np.array([0,0,0,-0.1])
env.step(action)
print("released")
# let it fly
for i in range(40):
    action = np.array([0,0,0,0])
    env.step(action)
    print("flying", i)
end=time.time()
print(f"Takes {end-start}s.")