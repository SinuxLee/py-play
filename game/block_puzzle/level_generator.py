import json
import random
import math
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass, asdict

@dataclass
class BlockShape:
    """方块形状定义"""
    shape: List[List[int]]
    difficulty: float
    name: str

@dataclass
class Level:
    """关卡数据"""
    level_id: int
    difficulty: float
    grid: List[List[Dict[str, Any]]]
    initial_blocks: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class DifficultyCalculator:
    """难度计算器"""
    
    GRID_SIZE = 9
    
    # 预定义的方块形状库
    BLOCK_SHAPES = [
        # 超简单 (1-5分)
        [[1]],                          # 单格
        [[1, 1]],                       # 横2
        [[1], [1]],                     # 竖2
        
        # 简单 (6-15分)
        [[1, 1, 1]],                    # 横3
        [[1], [1], [1]],                # 竖3
        [[1, 1], [1, 1]],               # 方块2x2
        
        # 中等 (16-30分)
        [[1, 1, 1, 1]],                 # 横4
        [[1], [1], [1], [1]],           # 竖4
        [[1, 1, 1], [1, 0, 0]],         # L型
        [[1, 1, 1], [0, 0, 1]],         # 反L型
        [[1, 0], [1, 1]],               # 小L
        [[0, 1], [1, 1]],               # 小反L
        [[1, 1], [0, 1]],               # 小L变体
        
        # 困难 (31-50分)
        [[1, 1, 1], [0, 1, 0]],         # T型
        [[1, 1, 0], [0, 1, 1]],         # Z型
        [[0, 1, 1], [1, 1, 0]],         # 反Z型
        [[1, 1, 1], [1, 1, 1]],         # 大方块3x3
        
        # 极难 (51+分)
        [[1, 0, 1], [1, 1, 1]],         # U型
        [[0, 1, 0], [1, 1, 1], [0, 1, 0]],  # 十字
        [[1, 1, 1], [1, 0, 1]],         # 凹型
    ]
    
    COLORS = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A',
        '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2',
        '#F8B4D9', '#A8E6CF', '#FFD3B6', '#FFAAA5'
    ]
    
    @staticmethod
    def count_cells(shape: List[List[int]]) -> int:
        """计算方块占用格子数"""
        return sum(sum(row) for row in shape)
    
    @staticmethod
    def get_bounding_box(shape: List[List[int]]) -> Tuple[int, int]:
        """获取方块的边界框"""
        h = len(shape)
        w = len(shape[0]) if h > 0 else 0
        return h, w
    
    @staticmethod
    def count_concavities(shape: List[List[int]]) -> int:
        """计算凹陷数量（被包围的空格）"""
        h, w = DifficultyCalculator.get_bounding_box(shape)
        count = 0
        
        for i in range(h):
            for j in range(w):
                if shape[i][j] == 0:
                    # 检查四周被包围的情况
                    surrounded = 0
                    if i > 0 and shape[i-1][j] == 1: surrounded += 1
                    if i < h-1 and shape[i+1][j] == 1: surrounded += 1
                    if j > 0 and shape[i][j-1] == 1: surrounded += 1
                    if j < w-1 and shape[i][j+1] == 1: surrounded += 1
                    
                    if surrounded >= 3:
                        count += 1
        
        return count
    
    @staticmethod
    def is_symmetric(shape: List[List[int]]) -> bool:
        """检查是否对称"""
        h, w = DifficultyCalculator.get_bounding_box(shape)
        
        # 检查水平对称
        h_symmetric = all(
            shape[i][j] == shape[i][w-1-j]
            for i in range(h) for j in range(w//2)
        )
        
        # 检查垂直对称
        v_symmetric = all(
            shape[i][j] == shape[h-1-i][j]
            for i in range(h//2) for j in range(w)
        )
        
        return h_symmetric or v_symmetric
    
    @classmethod
    def calculate_block_difficulty(cls, shape: List[List[int]]) -> float:
        """计算单个方块的难度"""
        difficulty = 0.0
        
        # 1. 基础大小
        size = cls.count_cells(shape)
        difficulty += size * 2
        
        # 2. 不规则度
        h, w = cls.get_bounding_box(shape)
        box_area = h * w
        occupancy = size / box_area if box_area > 0 else 1
        irregularity = 1 - occupancy
        difficulty += irregularity * 30
        
        # 3. 宽高比
        if min(h, w) > 0:
            aspect_ratio = max(h, w) / min(h, w)
            ratio_score = min(1, (aspect_ratio - 1) / 3)
            difficulty += ratio_score * 15
        
        # 4. 凹陷数量
        concavities = cls.count_concavities(shape)
        difficulty += concavities * 5
        
        # 5. 对称性降低难度
        if cls.is_symmetric(shape):
            difficulty -= 5
        
        return max(0, difficulty)
    
    @classmethod
    def calculate_grid_difficulty(cls, grid: List[List[Dict]]) -> float:
        """计算网格难度"""
        difficulty = 0.0
        
        # 1. 填充率
        filled_cells = sum(
            1 for row in grid for cell in row if cell['color'] is not None
        )
        fill_rate = filled_cells / (cls.GRID_SIZE * cls.GRID_SIZE)
        difficulty += fill_rate * 40
        
        # 2. 碎片化程度
        fragmentation = cls.calculate_fragmentation(grid)
        difficulty += fragmentation * 30
        
        # 3. 孤立空洞
        isolated_holes = cls.count_isolated_holes(grid)
        difficulty += isolated_holes * 10
        
        # 4. 接近完成的行列（降低难度）
        almost_complete = cls.count_almost_complete_lines(grid)
        difficulty -= almost_complete * 5
        
        # 5. 边缘占用率
        edge_occupancy = cls.calculate_edge_occupancy(grid)
        difficulty += edge_occupancy * 20
        
        return max(0, min(100, difficulty))
    
    @classmethod
    def calculate_fragmentation(cls, grid: List[List[Dict]]) -> float:
        """计算碎片化程度"""
        regions = cls.find_empty_regions(grid)
        if not regions:
            return 1.0
        
        total_empty = sum(len(r) for r in regions)
        if total_empty == 0:
            return 1.0
        
        max_region = max(len(r) for r in regions)
        # 最大连续空间越小，碎片化越严重
        return 1 - (max_region / (cls.GRID_SIZE * cls.GRID_SIZE))
    
    @classmethod
    def find_empty_regions(cls, grid: List[List[Dict]]) -> List[List[Tuple[int, int]]]:
        """查找所有空白区域（连通分量）"""
        visited = [[False] * cls.GRID_SIZE for _ in range(cls.GRID_SIZE)]
        regions = []
        
        def dfs(i: int, j: int, region: List[Tuple[int, int]]):
            if (i < 0 or i >= cls.GRID_SIZE or j < 0 or j >= cls.GRID_SIZE or
                visited[i][j] or grid[i][j]['color'] is not None):
                return
            
            visited[i][j] = True
            region.append((i, j))
            
            # 四个方向
            dfs(i-1, j, region)
            dfs(i+1, j, region)
            dfs(i, j-1, region)
            dfs(i, j+1, region)
        
        for i in range(cls.GRID_SIZE):
            for j in range(cls.GRID_SIZE):
                if not visited[i][j] and grid[i][j]['color'] is None:
                    region = []
                    dfs(i, j, region)
                    if region:
                        regions.append(region)
        
        return regions
    
    @classmethod
    def count_isolated_holes(cls, grid: List[List[Dict]]) -> int:
        """计算孤立空洞（1x1或小的无法利用空间）"""
        regions = cls.find_empty_regions(grid)
        # 小于等于2格的区域视为孤立空洞
        return sum(1 for r in regions if len(r) <= 2)
    
    @classmethod
    def count_almost_complete_lines(cls, grid: List[List[Dict]]) -> int:
        """计算接近完成的行列（只差1-2格）"""
        count = 0
        
        # 检查行
        for row in grid:
            empty = sum(1 for cell in row if cell['color'] is None)
            if 1 <= empty <= 2:
                count += 1
        
        # 检查列
        for j in range(cls.GRID_SIZE):
            empty = sum(1 for i in range(cls.GRID_SIZE) if grid[i][j]['color'] is None)
            if 1 <= empty <= 2:
                count += 1
        
        return count
    
    @classmethod
    def calculate_edge_occupancy(cls, grid: List[List[Dict]]) -> float:
        """计算边缘占用率"""
        edge_cells = []
        
        # 四条边
        for j in range(cls.GRID_SIZE):
            edge_cells.append(grid[0][j])  # 上
            edge_cells.append(grid[cls.GRID_SIZE-1][j])  # 下
        
        for i in range(1, cls.GRID_SIZE-1):
            edge_cells.append(grid[i][0])  # 左
            edge_cells.append(grid[i][cls.GRID_SIZE-1])  # 右
        
        occupied = sum(1 for cell in edge_cells if cell['color'] is not None)
        return occupied / len(edge_cells) if edge_cells else 0


class LevelGenerator:
    """关卡生成器"""
    
    def __init__(self):
        self.calculator = DifficultyCalculator()
        self.level_counter = 1
    
    def create_empty_grid(self) -> List[List[Dict]]:
        """创建空网格"""
        return [[{'color': None, 'hasGem': False} 
                 for _ in range(self.calculator.GRID_SIZE)]
                for _ in range(self.calculator.GRID_SIZE)]
    
    def fill_grid_randomly(self, grid: List[List[Dict]], 
                          target_fill_rate: float,
                          allowed_shapes_indices: List[int]) -> None:
        """随机填充网格"""
        target_cells = int(self.calculator.GRID_SIZE ** 2 * target_fill_rate)
        filled = 0
        
        attempts = 0
        max_attempts = 1000
        
        while filled < target_cells and attempts < max_attempts:
            attempts += 1
            
            # 随机选择一个方块
            shape_idx = random.choice(allowed_shapes_indices)
            shape = self.calculator.BLOCK_SHAPES[shape_idx]
            color = random.choice(self.calculator.COLORS)
            
            # 随机位置
            max_row = self.calculator.GRID_SIZE - len(shape)
            max_col = self.calculator.GRID_SIZE - len(shape[0])
            
            if max_row < 0 or max_col < 0:
                continue
            
            row = random.randint(0, max_row)
            col = random.randint(0, max_col)
            
            # 检查是否可以放置
            can_place = True
            for i in range(len(shape)):
                for j in range(len(shape[0])):
                    if shape[i][j] == 1:
                        if grid[row + i][col + j]['color'] is not None:
                            can_place = False
                            break
                if not can_place:
                    break
            
            # 放置方块
            if can_place:
                for i in range(len(shape)):
                    for j in range(len(shape[0])):
                        if shape[i][j] == 1:
                            grid[row + i][col + j]['color'] = color
                            filled += 1
    
    def remove_isolated_holes(self, grid: List[List[Dict]]) -> None:
        """移除孤立空洞，使关卡更合理"""
        regions = self.calculator.find_empty_regions(grid)
        
        for region in regions:
            if len(region) <= 2:
                # 填充小的孤立区域
                color = random.choice(self.calculator.COLORS)
                for i, j in region:
                    grid[i][j]['color'] = color
    
    def generate_level(self, target_difficulty: float, 
                      remove_holes: bool = True) -> Level:
        """生成指定难度的关卡"""
        
        # 根据难度确定参数
        if target_difficulty <= 20:
            level_type = 'TUTORIAL'
            fill_rate = 0.1 + random.uniform(0, 0.05)
            allowed_shapes = list(range(6))  # 简单形状
        elif target_difficulty <= 40:
            level_type = 'EASY'
            fill_rate = 0.2 + random.uniform(0, 0.1)
            allowed_shapes = list(range(10))
        elif target_difficulty <= 60:
            level_type = 'MEDIUM'
            fill_rate = 0.35 + random.uniform(0, 0.1)
            allowed_shapes = list(range(15))
        elif target_difficulty <= 80:
            level_type = 'HARD'
            fill_rate = 0.5 + random.uniform(0, 0.1)
            allowed_shapes = list(range(len(self.calculator.BLOCK_SHAPES)))
        else:
            level_type = 'EXPERT'
            fill_rate = 0.65 + random.uniform(0, 0.1)
            allowed_shapes = list(range(len(self.calculator.BLOCK_SHAPES)))
        
        # 生成网格
        grid = self.create_empty_grid()
        self.fill_grid_randomly(grid, fill_rate, allowed_shapes)
        
        # 可选：移除孤立空洞
        if remove_holes and target_difficulty < 60:
            self.remove_isolated_holes(grid)
        
        # 生成初始方块
        initial_blocks = self.generate_block_set(grid, target_difficulty)
        
        # 计算实际难度
        actual_difficulty = self.calculator.calculate_grid_difficulty(grid)
        
        level = Level(
            level_id=self.level_counter,
            difficulty=actual_difficulty,
            grid=grid,
            initial_blocks=initial_blocks,
            metadata={
                'target_difficulty': target_difficulty,
                'level_type': level_type,
                'fill_rate': fill_rate,
                'block_count': len(initial_blocks)
            }
        )
        
        self.level_counter += 1
        return level
    
    def generate_block_set(self, grid: List[List[Dict]], 
                          target_difficulty: float) -> List[Dict]:
        """生成一组方块"""
        blocks = []
        
        # 分析网格状态
        grid_analysis = self.analyze_grid_needs(grid)
        
        # 生成3个方块，难度递增
        difficulties = [
            max(5, target_difficulty * 0.6),   # 简单
            target_difficulty,                  # 目标
            min(60, target_difficulty * 1.3)    # 困难
        ]
        
        for block_difficulty in difficulties:
            block = self.select_block_by_difficulty(
                block_difficulty, 
                grid_analysis
            )
            blocks.append(block)
        
        return blocks
    
    def analyze_grid_needs(self, grid: List[List[Dict]]) -> Dict:
        """分析网格需求"""
        regions = self.calculator.find_empty_regions(grid)
        
        return {
            'largest_region': max(len(r) for r in regions) if regions else 0,
            'has_isolated': any(len(r) <= 2 for r in regions),
            'almost_complete_lines': self.calculator.count_almost_complete_lines(grid),
            'region_count': len(regions)
        }
    
    def select_block_by_difficulty(self, target_difficulty: float,
                                   grid_needs: Dict) -> Dict:
        """根据难度选择方块"""
        # 计算所有方块的难度
        candidates = []
        for shape in self.calculator.BLOCK_SHAPES:
            difficulty = self.calculator.calculate_block_difficulty(shape)
            candidates.append({
                'shape': shape,
                'difficulty': difficulty
            })
        
        # 根据网格需求过滤
        if grid_needs['has_isolated']:
            # 需要小方块填补孤立空间
            candidates = [c for c in candidates 
                         if self.calculator.count_cells(c['shape']) <= 3]
        
        # 按难度排序，选择最接近目标的
        candidates.sort(key=lambda x: abs(x['difficulty'] - target_difficulty))
        
        # 从前30%随机选择
        top_n = max(1, len(candidates) // 3)
        selected = random.choice(candidates[:top_n])
        
        # 创建方块对象
        shape = selected['shape']
        color = random.choice(self.calculator.COLORS)
        
        # 添加宝石（15%概率）
        gems = [[cell == 1 and random.random() < 0.15 
                for cell in row] for row in shape]
        
        return {
            'shape': shape,
            'color': color,
            'gems': gems,
            'difficulty': selected['difficulty']
        }
    
    def save_level(self, level: Level, filename: str) -> None:
        """保存关卡到JSON文件"""
        level_dict = {
            'level_id': level.level_id,
            'difficulty': level.difficulty,
            'grid': level.grid,
            'initial_blocks': level.initial_blocks,
            'metadata': level.metadata
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(level_dict, f, indent=2, ensure_ascii=False)
    
    def generate_level_pack(self, count: int = 10) -> List[Level]:
        """生成一组关卡（难度递增）"""
        levels = []
        
        for i in range(count):
            # 难度从10到90递增
            target_difficulty = 10 + (80 * i / (count - 1))
            level = self.generate_level(target_difficulty)
            levels.append(level)
            
            print(f"生成关卡 {level.level_id}: "
                  f"目标难度={target_difficulty:.1f}, "
                  f"实际难度={level.difficulty:.1f}, "
                  f"类型={level.metadata['level_type']}")
        
        return levels


def main():
    """主函数：生成测试关卡"""
    generator = LevelGenerator()
    
    print("=" * 60)
    print("方块拼图关卡生成器")
    print("=" * 60)
    
    # 生成10个关卡
    levels = generator.generate_level_pack(10)
    
    # 保存所有关卡
    level_pack = {
        'version': '1.0',
        'total_levels': len(levels),
        'levels': []
    }
    
    for level in levels:
        level_data = {
            'level_id': level.level_id,
            'difficulty': level.difficulty,
            'grid': level.grid,
            'initial_blocks': level.initial_blocks,
            'metadata': level.metadata
        }
        level_pack['levels'].append(level_data)
    
    # 保存关卡包
    with open('level_pack.json', 'w', encoding='utf-8') as f:
        json.dump(level_pack, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print(f"✓ 成功生成 {len(levels)} 个关卡")
    print("✓ 已保存到 level_pack.json")
    print("=" * 60)
    
    # 显示难度分布
    print("\n难度分布:")
    for level in levels:
        bar_length = int(level.difficulty / 2)
        bar = "█" * bar_length
        print(f"关卡 {level.level_id:2d}: {bar} {level.difficulty:.1f}")


if __name__ == '__main__':
    main()