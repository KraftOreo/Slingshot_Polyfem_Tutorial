import polyfempy as pf
import json
import numpy as np

class SlingShot:
    def __init__(self) -> None:
        self.asset_file = 'slingshot/assets/json/sling_shots.json'
        with open(self.asset_file,'r') as f:
            self.config = json.load(f)
        self.dt = self.config["dt"]
        self.step_count = 1
        self.solver = pf.Solver()
        self.solver.set_log_level(3)
        self.solver.set_settings(json.dumps(self.config))
        self.solver.load_mesh_from_settings()
        self.dt = self.config["dt"]
        self.t0 = self.config["t0"]
        self.solver.init_timestepping(self.t0, self.dt)
        self.id_to_mesh = {}
        self.id_to_position = {}
        self.id_to_vf = {}
        for mesh in self.config["meshes"]:
            self.id_to_mesh[mesh["body_id"]] = mesh["mesh"]
            self.id_to_position[mesh["body_id"]] = mesh["position"]
            
        self.pre_steps = 4
        for i in range(self.pre_steps):
            self.run_simulation()
        self.cumulative_action = {"0":np.array([0, -0.02 * self.dt * self.step_count, 0, 0.02 * self.dt * self.step_count]), "1":np.array([0, 0.02 * self.dt, 0, 0.02 * self.dt])}
        
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
        self.solver.step_in_time(0, self.dt, self.step_count)
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