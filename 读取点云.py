import numpy as np
import trimesh
import open3d as o3d
import os

class ModelToPointCloud:
    def __init__(self, model_path):
        self.model_path = model_path
        self.mesh = None
        self.point_cloud = None
    
    def load_model(self):
        """
        加载 3D 模型文件
        """
        loaded = trimesh.load(self.model_path)
        
        if isinstance(loaded, trimesh.Scene):
            print(f"检测到 Scene 对象，包含 {len(loaded.geometry)} 个网格")
            self.mesh = trimesh.util.concatenate(list(loaded.geometry.values()))
        else:
            self.mesh = loaded
        
        print(f"模型顶点数：{len(self.mesh.vertices)}")
        print(f"模型面数：{len(self.mesh.faces)}")
        return self.mesh
    
    def load_point_cloud(self, file_path):
        """
        直接读取点云文件（支持多种格式）
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.npy':
            # NumPy 格式
            self.point_cloud = np.load(file_path)
            print(f"✓ 读取 .npy 点云：{self.point_cloud.shape}")
        
        elif file_ext == '.ply':
            # PLY 格式（使用 open3d）
            pcd = o3d.io.read_point_cloud(file_path)
            self.point_cloud = np.asarray(pcd.points)
            print(f"✓ 读取 .ply 点云：{self.point_cloud.shape}")
        
        elif file_ext == '.pcd':
            # PCD 格式（使用 open3d）
            pcd = o3d.io.read_point_cloud(file_path)
            self.point_cloud = np.asarray(pcd.points)
            print(f"✓ 读取 .pcd 点云：{self.point_cloud.shape}")
        
        elif file_ext in ['.xyz', '.txt', '.csv']:
            # 文本格式（假设每行是 x,y,z）
            self.point_cloud = np.loadtxt(file_path)
            print(f"✓ 读取 .txt/.xyz 点云：{self.point_cloud.shape}")
        
        elif file_ext in ['.las', '.laz']:
            # LAS 格式（需要 laspy）
            import laspy
            las = laspy.read(file_path)
            self.point_cloud = np.vstack((las.x, las.y, las.z)).transpose()
            print(f"✓ 读取 .las 点云：{self.point_cloud.shape}")
        
        else:
            raise ValueError(f"不支持的点云格式：{file_ext}")
        
        return self.point_cloud
    
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
        points, _ = trimesh.sample.sample_surface(self.mesh, num_points)
        self.point_cloud = points
        print(f"采样点数：{len(points)}")
        return points
    
    def voxel_downsample(self, voxel_size=0.1):
        """
        方法三：体素下采样
        """
        if self.point_cloud is None:
            self.surface_sample(num_points=10000)
        
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(self.point_cloud)
        downsampled = pcd.voxel_down_sample(voxel_size)
        self.point_cloud = np.asarray(downsampled.points)
        return self.point_cloud

    
    def visualize(self):
        """
        可视化点云
        """
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(self.point_cloud)
        o3d.visualization.draw_geometries([pcd])

if __name__ == "__main__":
    converter = ModelToPointCloud("")  # 不需要模型路径
    
    # 方式一：读取 .npy 点云（与 save_point_cloud 兼容）
    converter.load_point_cloud("object_point_cloud.npy")
    
    # 方式二：读取 .ply 点云
    # converter.load_point_cloud("object_point_cloud.ply")
    
    # 方式三：读取 .pcd 点云
    # converter.load_point_cloud("object_point_cloud.pcd")
    
    # 方式四：读取 .xyz/.txt 点云
    # converter.load_point_cloud("object_point_cloud.xyz")
    
    # 可视化验证
    converter.visualize()
    
    # 可选：下采样处理
    # converter.voxel_downsample(voxel_size=0.2)