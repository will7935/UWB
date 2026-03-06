import numpy as np
import trimesh
import open3d as o3d

class ModelToPointCloud:
    def __init__(self, model_path):
        self.model_path = model_path
        self.mesh = None
        self.point_cloud = None
    
    def load_model(self):
        """
        加载 3D 模型文件，处理 Scene 和 Mesh 两种情况
        """
        loaded = trimesh.load(self.model_path)
        
        # 如果是 Scene 对象，合并所有网格为单个 Mesh
        if isinstance(loaded, trimesh.Scene):
            print(f"检测到 Scene 对象，包含 {len(loaded.geometry)} 个网格")
            # 合并所有网格
            self.mesh = trimesh.util.concatenate(list(loaded.geometry.values()))
        else:
            self.mesh = loaded
        
        print(f"模型顶点数：{len(self.mesh.vertices)}")
        print(f"模型面数：{len(self.mesh.faces)}")
        return self.mesh

    def extract_vertices(self):
        """
        方法一：直接提取顶点作为点云
        """
        vertex_points = np.array(self.mesh.vertices)
        self.point_cloud = vertex_points
        return vertex_points
    
    def surface_sample(self, num_points=1000):
        """
        方法二：表面均匀采样
        """
        # 使用 trimesh 在网格表面随机采样
        points, _ = trimesh.sample.sample_surface(self.mesh, num_points)
        self.point_cloud = points
        print(f"采样点数：{len(points)}")
        return points
    
    def voxel_downsample(self, voxel_size):
        """
        方法三：体素下采样（需先有密集点云）
        """
        if self.point_cloud is None:
            self.surface_sample(num_points=10000)
        
        # 使用 open3d 进行体素下采样
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(self.point_cloud)
        downsampled = pcd.voxel_down_sample(voxel_size)
        self.point_cloud = np.asarray(downsampled.points)
        return self.point_cloud
    
    def save_point_cloud(self, output_path):
        """
        保存点云到文件（与标定点云.py 格式兼容）
        """
        np.save(output_path, self.point_cloud)
        print(f"点云已保存：{output_path}")
        print(f"点云形状：{self.point_cloud.shape}")
    
    def visualize(self):
        """
        可视化点云
        """
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(self.point_cloud)
        o3d.visualization.draw_geometries([pcd])


if __name__ == "__main__":
    # 加载 3D 模型
    model_path = r"D:\QTproject\hr_rtls_pc-master\Logs\1.21交职UWB报警实验\python文件\hammer.glb"
    converter = ModelToPointCloud(model_path)
    converter.load_model()
    
    # 生成点云（选择一种方法）
    # converter.extract_vertices()  # 方法一
    # converter.surface_sample(num_points=5000)  # 方法二
    converter.voxel_downsample(voxel_size=5)  # 方法三
    
    # # 保存点云
    converter.save_point_cloud("object_point_cloud.npy")
    
    # 可视化验证
    converter.visualize()