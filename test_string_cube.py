from slingshot.src.string_cube import StringCube 
import numpy as np
import time

start=time.time()
env = StringCube()
print("Initialzied.")
# pull the rubber band
for i in range(5):
    action = 0.01
    env.step(action)
    print("step", i)

for i in range(2):
    action = -1
    env.step(action)
    print("flying", i)

for i in range(100):
    action = 0    
    env.step(action)
    print("oscalating", i)

end=time.time()
print("Takes ",end-start,"s")