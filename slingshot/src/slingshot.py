import polyfempy as pf
import json
import numpy as np
import os

class SlingShot:
    def __init__(self,output_dir='',force_reload=False) -> None:
        self.asset_file = 'slingshot/assets/json/sling_shots.json'
        self.init_config()
        self.preloaded=False
        self.output_dir=output_dir
        if (not force_reload) and os.path.exists(self.config["input"]['data']['u_path']) and os.path.exists(self.config["input"]['data']['v_path']) and os.path.exists(self.config["input"]['data']['v_path']):
            self.preloaded=True
        else:
            self.config['output']['data']={}
            self.config['output']['data']['u_path']=os.path.abspath(self.config['input']['data']['u_path'])
            self.config['output']['data']['v_path']=os.path.abspath(self.config['input']['data']['v_path'])
            self.config['output']['data']['a_path']=os.path.abspath(self.config['input']['data']['a_path'])
            self.config['input']['data']['u_path']=''
            self.config['input']['data']['v_path']=''
            self.config['input']['data']['a_path']=''
            self.config['output']['paraview']['file_name']='simPreload.pvd'
        self.step_count = 1
        self.dt = self.config["time"]["dt"]
        self.t0 = self.config["time"]["t0"]
        self.init_solver(self.preloaded)
        self.id_to_mesh = {}
        self.id_to_position = {}
        self.id_to_vf = {}
        self.obstacle_ids=[]
        for mesh in self.config["geometry"]:
            if ("is_obstacle" in mesh.keys()) and (mesh["is_obstacle"]):
                self.obstacle_ids.append(mesh["surface_selection"])
            else:
                self.id_to_mesh[mesh["volume_selection"]] = mesh["mesh"]
                self.id_to_position[mesh["volume_selection"]] = mesh["transformation"]["translation"]
        if not self.preloaded: 
            self.pre_steps = 4
            # squeeze the ball
            for _ in range(self.pre_steps):
                self.run_simulation()
            # self.cumulative_action = {"0":np.array([0, -0.02 * self.dt * self.step_count, 0, 0.02 * self.dt * self.step_count]), "1":np.array([0, 0.02 * self.dt, 0, 0.02 * self.dt])}
            # pull the rubber band for some distance
            for _ in range(self.pre_steps):
                self.step(np.array([0.01,0,0,0]))
            self.solver.export_uva()
            self.preloaded=True
            self.init_config()
            self.init_solver(True)
            print("reinitialized")
        
    def init_config(self):
        with open(self.asset_file,'r') as f:
            self.config = json.load(f)
    def init_solver(self, with_gravity):
        self.solver = pf.Solver()
        self.solver.set_log_level(3)
        if not with_gravity:
            self.config['boundary_conditions']['rhs']=[0,0,0]
        self.solver.set_settings(json.dumps(self.config))
        self.solver.load_mesh_from_settings()
        if self.preloaded:
            self.solver.set_output_dir(self.output_dir)
        else:
            self.solver.set_output_dir("results/preload")
        self.solver.init_timestepping(self.t0, self.dt)
        self.cumulative_action = {"0":np.zeros(4), "1":np.zeros(4)}
        self.step_count=1

    def set_boundary_conditions(self, actions):
        t0 = self.t0
        t1 = t0 + self.dt
        for mesh_id, action in actions.items(): 
            self.solver.update_obstacle_displacement(
                int(mesh_id),
                [
                    f"{self.cumulative_action[mesh_id][0]} + ((t-{t0})*{action[0]})/({t1-t0})",
                    f"{self.cumulative_action[mesh_id][1] + self.cumulative_action[mesh_id][3]} + ((t-{t0})*{action[1] + action[3]})/({t1-t0})",
                    f"{self.cumulative_action[mesh_id][2]} + ((t-{t0})*{action[2]})/({t1-t0})"
                ]
            )
            self.cumulative_action[mesh_id] += action
        
    def get_object_positions(self):
        points, tets, _, body_ids, displacement = self.solver.get_sampled_solution()
        self.id_to_position = {}
        self.id_to_vertex = {}
        for mesh_id, _ in self.id_to_mesh.items():
            vertex_position = points + displacement
            self.id_to_vertex[mesh_id] = vertex_position[body_ids[:,0]==mesh_id]
            mean_cell_id = np.mean(body_ids[tets], axis=1).astype(np.int32).flat
            tet_barycenter = np.mean(vertex_position[tets], axis=1)
            self.id_to_position[mesh_id] = np.mean(tet_barycenter[mean_cell_id == mesh_id], axis=0)
        return self.id_to_position
    
    def run_simulation(self):
        self.solver.step_in_time(0, self.dt, self.step_count,False)
        self.step_count += 1
        self.t0 += self.dt
        
    def step(self, action):
        actions = {
                # x, y, z gripper_displacement
                "0": np.array([action[0],
                                action[1],
                                action[2],
                               -1 * action[3]/2]),
                "1": np.array([action[0],
                                action[1],
                                action[2],
                               action[3]/2]) 
            }
        self.set_boundary_conditions(actions)
        self.run_simulation()
        return self.get_object_positions()