import pygame
import json
import sys
import random
from typing import List, Dict, Tuple, Optional

# 初始化Pygame
pygame.init()

# 常量定义
GRID_SIZE = 9
CELL_SIZE = 50
CELL_GAP = 2
CANVAS_SIZE = GRID_SIZE * CELL_SIZE
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700

# 颜色定义
WHITE = (255, 255, 255)
GRAY = (209, 213, 219)
BG_GRAY = (243, 244, 246)
PURPLE = (102, 126, 234)
DARK_PURPLE = (85, 104, 211)
YELLOW = (251, 191, 36)
GOLD = (245, 158, 11)
BLACK = (0, 0, 0)
GREEN = (34, 197, 94)
RED = (239, 68, 68)

# 中文字体 - 尝试多个可能的中文字体
FONT_PATHS = [
    "C:/Windows/Fonts/msyh.ttc",  # Windows 微软雅黑
    "C:/Windows/Fonts/simhei.ttf",  # Windows 黑体
    "/System/Library/Fonts/PingFang.ttc",  # macOS
    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",  # Linux
    None  # 使用系统默认
]

def load_chinese_font(size):
    """加载中文字体"""
    for font_path in FONT_PATHS:
        try:
            if font_path:
                return pygame.font.Font(font_path, size)
            else:
                # 尝试使用系统字体
                font = pygame.font.SysFont('microsoftyahei,simhei,pingfang,notosanscjk', size)
                return font
        except:
            continue
    # 如果都失败，使用默认字体
    return pygame.font.Font(None, size)

FONT_LARGE = load_chinese_font(48)
FONT_MEDIUM = load_chinese_font(32)
FONT_SMALL = load_chinese_font(24)


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """将十六进制颜色转换为RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


class Block:
    """方块类"""
    def __init__(self, shape: List[List[int]], color: str, gems: List[List[bool]]):
        self.shape = shape
        self.color = hex_to_rgb(color)
        self.gems = gems
        self.selected = False
        self.rect = None  # 用于拖拽检测
        self.original_pos = (0, 0)  # 原始位置
        
    def get_size(self) -> Tuple[int, int]:
        """获取方块尺寸"""
        return len(self.shape), len(self.shape[0]) if self.shape else 0
    
    def draw(self, surface: pygame.Surface, x: int, y: int, 
             cell_size: int = 30, highlight: bool = False, alpha: int = 255):
        """绘制方块"""
        h, w = self.get_size()
        
        # 绘制背景（如果被选中）
        if highlight or self.selected:
            padding = 10
            bg_rect = pygame.Rect(
                x - padding, y - padding,
                w * cell_size + padding * 2,
                h * cell_size + padding * 2
            )
            pygame.draw.rect(surface, (221, 214, 254), bg_rect, border_radius=10)
            pygame.draw.rect(surface, (139, 92, 246), bg_rect, 3, border_radius=10)
        
        # 绘制方块
        for i in range(h):
            for j in range(w):
                if self.shape[i][j] == 1:
                    cell_x = x + j * cell_size
                    cell_y = y + i * cell_size
                    
                    # 绘制单元格
                    cell_rect = pygame.Rect(
                        cell_x + 2, cell_y + 2,
                        cell_size - 4, cell_size - 4
                    )
                    
                    if alpha < 255:
                        # 半透明绘制
                        s = pygame.Surface((cell_size - 4, cell_size - 4), pygame.SRCALPHA)
                        color_with_alpha = (*self.color, alpha)
                        pygame.draw.rect(s, color_with_alpha, s.get_rect(), border_radius=5)
                        surface.blit(s, (cell_x + 2, cell_y + 2))
                        pygame.draw.rect(surface, (*GRAY, alpha), cell_rect, 2, border_radius=5)
                    else:
                        pygame.draw.rect(surface, self.color, cell_rect, border_radius=5)
                        pygame.draw.rect(surface, GRAY, cell_rect, 2, border_radius=5)
                    
                    # 绘制宝石
                    if self.gems[i][j]:
                        self.draw_gem(surface, 
                                    cell_x + cell_size // 2,
                                    cell_y + cell_size // 2,
                                    alpha)
    
    @staticmethod
    def draw_gem(surface: pygame.Surface, x: int, y: int, alpha: int = 255):
        """绘制宝石"""
        size = 8
        points = []
        for i in range(6):
            angle = (3.14159 / 3) * i - 3.14159 / 6
            px = x + size * pygame.math.Vector2(1, 0).rotate_rad(angle).x
            py = y + size * pygame.math.Vector2(1, 0).rotate_rad(angle).y
            points.append((px, py))
        
        if alpha < 255:
            s = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
            offset_points = [(p[0] - x + size * 1.5, p[1] - y + size * 1.5) for p in points]
            pygame.draw.polygon(s, (*YELLOW, alpha), offset_points)
            pygame.draw.polygon(s, (*GOLD, alpha), offset_points, 2)
            surface.blit(s, (x - size * 1.5, y - size * 1.5))
        else:
            pygame.draw.polygon(surface, YELLOW, points)
            pygame.draw.polygon(surface, GOLD, points, 2)


class Game:
    """游戏主类"""
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("方块拼图游戏 - 关卡测试")
        self.clock = pygame.time.Clock()
        
        # 游戏状态
        self.grid = [[{'color': None, 'hasGem': False} 
                     for _ in range(GRID_SIZE)]
                    for _ in range(GRID_SIZE)]
        self.blocks = []
        self.selected_block = None
        self.dragging_block = None
        self.drag_offset = (0, 0)
        self.hover_pos = None
        
        # 动画状态
        self.clearing_animation = []  # 存储正在清除的单元格动画
        self.animation_frame = 0
        self.is_animating = False
        
        self.score = 0
        self.combo = 0
        self.level_id = 1
        self.level_difficulty = 0
        
        # 加载关卡
        self.levels = []
        self.current_level_index = 0
        self.available_shapes = []
        self.available_colors = []
        
        self.load_levels()
        
        # UI位置
        self.canvas_x = 50
        self.canvas_y = 80
        self.blocks_y = self.canvas_y + CANVAS_SIZE + 30
        
        self.game_over = False
        self.show_victory = False
        
    def load_levels(self):
        """加载关卡数据"""
        try:
            with open('level_pack.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.levels = data['levels']
                print(f"成功加载 {len(self.levels)} 个关卡")
                self.load_level(0)
        except FileNotFoundError:
            print("未找到 level_pack.json，请先运行关卡生成器")
            sys.exit(1)
    
    def load_level(self, index: int):
        """加载指定关卡"""
        if index >= len(self.levels):
            self.show_victory = True
            return
        
        level = self.levels[index]
        self.current_level_index = index
        
        # 深拷贝网格（避免修改原始数据）
        self.grid = [[cell.copy() for cell in row] for row in level['grid']]
        
        # 从关卡中提取可用的形状和颜色
        self.available_shapes = [b['shape'] for b in level['initial_blocks']]
        self.available_colors = [b['color'] for b in level['initial_blocks']]
        
        # 加载初始方块
        self.blocks = self.generate_new_blocks()
        
        # 更新关卡信息
        self.level_id = level['level_id']
        self.level_difficulty = level['difficulty']
        self.score = 0
        self.combo = 0
        self.game_over = False
        self.selected_block = None
        self.dragging_block = None
        self.hover_pos = None
        
        print(f"\n加载关卡 {self.level_id}: 难度 {self.level_difficulty:.1f}")
    
    def generate_new_blocks(self) -> List[Block]:
        """生成新的三个方块"""
        new_blocks = []
        for _ in range(3):
            shape = random.choice(self.available_shapes)
            color = random.choice(self.available_colors)
            
            # 生成宝石
            gems = [[cell == 1 and random.random() < 0.15 
                    for cell in row] for row in shape]
            
            block = Block(shape, color, gems)
            new_blocks.append(block)
        
        return new_blocks
    
    def can_place_block(self, block: Block, row: int, col: int) -> bool:
        """检查是否可以放置方块"""
        h, w = block.get_size()
        
        for i in range(h):
            for j in range(w):
                if block.shape[i][j] == 1:
                    r = row + i
                    c = col + j
                    if (r >= GRID_SIZE or c >= GRID_SIZE or 
                        self.grid[r][c]['color'] is not None):
                        return False
        return True
    
    def place_block(self, block: Block, row: int, col: int) -> bool:
        """放置方块"""
        if not self.can_place_block(block, row, col):
            return False
        
        h, w = block.get_size()
        gems_placed = 0
        
        # 放置方块
        for i in range(h):
            for j in range(w):
                if block.shape[i][j] == 1:
                    r, c = row + i, col + j
                    self.grid[r][c]['color'] = block.color
                    if block.gems[i][j]:
                        self.grid[r][c]['hasGem'] = True
                        gems_placed += 1
        
        # 移除使用的方块
        self.blocks.remove(block)
        
        # 检查并清除完整的行列
        pygame.time.set_timer(pygame.USEREVENT, 100, 1)  # 延迟清除
        
        return True
    
    def clear_lines(self):
        """清除完整的行和列"""
        rows_to_clear = []
        cols_to_clear = []
        gems_collected = 0
        
        # 检查行
        for i in range(GRID_SIZE):
            if all(self.grid[i][j]['color'] is not None for j in range(GRID_SIZE)):
                rows_to_clear.append(i)
                gems_collected += sum(1 for j in range(GRID_SIZE) 
                                    if self.grid[i][j]['hasGem'])
        
        # 检查列
        for j in range(GRID_SIZE):
            if all(self.grid[i][j]['color'] is not None for i in range(GRID_SIZE)):
                cols_to_clear.append(j)
                gems_collected += sum(1 for i in range(GRID_SIZE) 
                                    if self.grid[i][j]['hasGem'])
        
        lines_cleared = len(rows_to_clear) + len(cols_to_clear)
        
        if lines_cleared > 0:
            # 启动清除动画
            self.clearing_animation = []
            for i in rows_to_clear:
                for j in range(GRID_SIZE):
                    if self.grid[i][j]['color'] is not None:  # 确保颜色不为空
                        self.clearing_animation.append({
                            'row': i,
                            'col': j,
                            'color': self.grid[i][j]['color'],
                            'hasGem': self.grid[i][j]['hasGem'],
                            'frame': 0,
                            'max_frames': 15
                        })
            
            for j in cols_to_clear:
                for i in range(GRID_SIZE):
                    if self.grid[i][j]['color'] is not None:  # 确保颜色不为空
                        # 避免重复添加（行列交叉点）
                        if not any(cell['row'] == i and cell['col'] == j 
                                 for cell in self.clearing_animation):
                            self.clearing_animation.append({
                                'row': i,
                                'col': j,
                                'color': self.grid[i][j]['color'],
                                'hasGem': self.grid[i][j]['hasGem'],
                                'frame': 0,
                                'max_frames': 15
                            })
            
            self.is_animating = True
            self.animation_frame = 0
            
            # 计算分数
            base_score = lines_cleared * 10
            gem_bonus = gems_collected * 5
            
            # 连击加成
            if lines_cleared >= 2:
                self.combo += 1
                base_score += self.combo * 10
            else:
                self.combo = 0
            
            self.score += base_score + gem_bonus
            
            # 记录要清除的行列，动画结束后再清除
            self.rows_to_clear = rows_to_clear
            self.cols_to_clear = cols_to_clear
        else:
            self.combo = 0
            
            # 检查是否需要生成新方块
            if len(self.blocks) == 0:
                self.blocks = self.generate_new_blocks()
            
            # 检查游戏状态
            self.check_game_over()
    
    def update_animation(self):
        """更新清除动画"""
        if not self.is_animating:
            return
        
        self.animation_frame += 1
        
        # 更新所有动画单元格
        all_finished = True
        for cell in self.clearing_animation:
            if cell['frame'] < cell['max_frames']:
                cell['frame'] += 1
                all_finished = False
        
        # 动画结束
        if all_finished:
            self.is_animating = False
            self.clearing_animation = []
            
            # 清除行
            for i in self.rows_to_clear:
                for j in range(GRID_SIZE):
                    self.grid[i][j] = {'color': None, 'hasGem': False}
            
            # 清除列
            for j in self.cols_to_clear:
                for i in range(GRID_SIZE):
                    self.grid[i][j] = {'color': None, 'hasGem': False}
            
            # 检查是否需要生成新方块
            if len(self.blocks) == 0:
                self.blocks = self.generate_new_blocks()
            
            # 检查游戏状态
            self.check_game_over()
    
    def check_game_over(self) -> bool:
        """检查是否游戏结束"""
        # 检查是否有任何一个方块可以放置
        for block in self.blocks:
            for i in range(GRID_SIZE):
                for j in range(GRID_SIZE):
                    if self.can_place_block(block, i, j):
                        return False
        
        # 所有方块都无法放置，游戏结束
        self.game_over = True
        return True
    
    def next_level(self):
        """进入下一关"""
        if self.current_level_index + 1 < len(self.levels):
            self.load_level(self.current_level_index + 1)
        else:
            self.show_victory = True
    
    def restart_level(self):
        """重新开始当前关卡"""
        self.load_level(self.current_level_index)
    
    def get_grid_pos(self, mouse_pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """将鼠标位置转换为网格坐标"""
        x, y = mouse_pos
        x -= self.canvas_x
        y -= self.canvas_y
        
        if 0 <= x < CANVAS_SIZE and 0 <= y < CANVAS_SIZE:
            col = x // CELL_SIZE
            row = y // CELL_SIZE
            return row, col
        return None
    
    def draw_grid(self):
        """绘制游戏网格"""
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                x = self.canvas_x + j * CELL_SIZE
                y = self.canvas_y + i * CELL_SIZE
                
                cell = self.grid[i][j]
                color = cell['color'] if cell['color'] else WHITE
                
                # 检查是否在清除动画中
                animation_cell = None
                for anim_cell in self.clearing_animation:
                    if anim_cell['row'] == i and anim_cell['col'] == j:
                        animation_cell = anim_cell
                        break
                
                # 绘制单元格
                cell_rect = pygame.Rect(x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4)
                
                if animation_cell and animation_cell['color'] is not None:
                    # 动画效果：缩放 + 淡出
                    progress = animation_cell['frame'] / animation_cell['max_frames']
                    scale = 1 - progress  # 从1缩小到0
                    alpha = int(255 * (1 - progress))  # 从255淡出到0
                    
                    # 计算缩放后的尺寸和位置
                    scaled_size = int((CELL_SIZE - 4) * scale)
                    offset = (CELL_SIZE - 4 - scaled_size) // 2
                    
                    if scaled_size > 0 and alpha > 0:
                        scaled_rect = pygame.Rect(
                            x + 2 + offset, y + 2 + offset,
                            scaled_size, scaled_size
                        )
                        
                        # 绘制带透明度的单元格
                        s = pygame.Surface((scaled_size, scaled_size), pygame.SRCALPHA)
                        anim_color = animation_cell['color']
                        # 确保颜色是RGB元组
                        if isinstance(anim_color, (list, tuple)) and len(anim_color) >= 3:
                            color_with_alpha = (*anim_color[:3], alpha)
                            pygame.draw.rect(s, color_with_alpha, 
                                           s.get_rect(), border_radius=3)
                            self.screen.blit(s, (x + 2 + offset, y + 2 + offset))
                        
                        # 绘制宝石动画
                        if animation_cell['hasGem']:
                            gem_x = x + CELL_SIZE // 2
                            gem_y = y + CELL_SIZE // 2
                            Block.draw_gem(self.screen, gem_x, gem_y, alpha)
                    
                    # 绘制背景边框
                    pygame.draw.rect(self.screen, WHITE, cell_rect, border_radius=3)
                    pygame.draw.rect(self.screen, GRAY, cell_rect, 2, border_radius=3)
                else:
                    # 正常绘制
                    pygame.draw.rect(self.screen, color, cell_rect, border_radius=3)
                    pygame.draw.rect(self.screen, GRAY, cell_rect, 2, border_radius=3)
                    
                    # 绘制宝石
                    if cell['hasGem']:
                        Block.draw_gem(self.screen, x + CELL_SIZE // 2, y + CELL_SIZE // 2)
        
        # 绘制拖拽预览（虚线框）- 始终显示
        if self.hover_pos and self.dragging_block:
            block = self.dragging_block
            row, col = self.hover_pos
            
            can_place = self.can_place_block(block, row, col)
            h, w = block.get_size()
            
            for bi in range(h):
                for bj in range(w):
                    if block.shape[bi][bj] == 1:
                        grid_i = row + bi
                        grid_j = col + bj
                        
                        # 确保在网格范围内
                        if 0 <= grid_i < GRID_SIZE and 0 <= grid_j < GRID_SIZE:
                            x = self.canvas_x + grid_j * CELL_SIZE
                            y = self.canvas_y + grid_i * CELL_SIZE
                            
                            preview_rect = pygame.Rect(x + 2, y + 2, 
                                                      CELL_SIZE - 4, CELL_SIZE - 4)
                            
                            if can_place:
                                # 可放置：半透明填充 + 紫色虚线
                                s = pygame.Surface((CELL_SIZE - 4, CELL_SIZE - 4), 
                                                 pygame.SRCALPHA)
                                s.fill((*block.color, 80))
                                self.screen.blit(s, (x + 2, y + 2))
                                self.draw_dashed_rect(preview_rect, (139, 92, 246), 3)
                            else:
                                # 不可放置：红色虚线（不填充）
                                self.draw_dashed_rect(preview_rect, (239, 68, 68), 3)
    
    def draw_dashed_rect(self, rect: pygame.Rect, color: Tuple[int, int, int], 
                         width: int, dash_length: int = 5):
        """绘制虚线矩形"""
        x, y, w, h = rect
        
        # 上边
        for i in range(0, w, dash_length * 2):
            pygame.draw.line(self.screen, color, 
                           (x + i, y), 
                           (x + min(i + dash_length, w), y), width)
        
        # 下边
        for i in range(0, w, dash_length * 2):
            pygame.draw.line(self.screen, color, 
                           (x + i, y + h), 
                           (x + min(i + dash_length, w), y + h), width)
        
        # 左边
        for i in range(0, h, dash_length * 2):
            pygame.draw.line(self.screen, color, 
                           (x, y + i), 
                           (x, y + min(i + dash_length, h)), width)
        
        # 右边
        for i in range(0, h, dash_length * 2):
            pygame.draw.line(self.screen, color, 
                           (x + w, y + i), 
                           (x + w, y + min(i + dash_length, h)), width)
    
    def draw_blocks(self):
        """绘制可用方块"""
        start_x = (WINDOW_WIDTH - len(self.blocks) * 120) // 2
        
        for idx, block in enumerate(self.blocks):
            if block == self.dragging_block:
                continue  # 拖拽中的方块单独绘制
            
            x = start_x + idx * 120
            y = self.blocks_y
            
            # 保存原始位置
            block.original_pos = (x, y)
            
            # 绘制方块
            block.draw(self.screen, x, y, 30, block == self.selected_block)
            
            # 保存矩形区域用于点击检测
            h, w = block.get_size()
            block.rect = pygame.Rect(x - 10, y - 10, w * 30 + 20, h * 30 + 20)
        
        # 绘制拖拽中的方块（在鼠标位置）
        if self.dragging_block:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # 居中绘制
            h, w = self.dragging_block.get_size()
            draw_x = mouse_x - (w * 30) // 2
            draw_y = mouse_y - (h * 30) // 2
            self.dragging_block.draw(self.screen, draw_x, draw_y, 30, False, alpha=200)
    
    def draw_ui(self):
        """绘制UI"""
        # 标题和关卡信息
        title_text = FONT_LARGE.render("💎 方块拼图", True, BLACK)
        self.screen.blit(title_text, (20, 10))
        
        level_text = FONT_SMALL.render(
            f"关卡 {self.level_id} | 难度: {self.level_difficulty:.1f}", 
            True, GRAY
        )
        self.screen.blit(level_text, (20, 55))
        
        # 分数
        score_text = FONT_MEDIUM.render(f"分数: {self.score}", True, PURPLE)
        self.screen.blit(score_text, (WINDOW_WIDTH - 200, 20))
        
        # 连击
        if self.combo > 0:
            combo_text = FONT_SMALL.render(
                f"连击 x{self.combo} 🔥", True, (239, 68, 68)
            )
            self.screen.blit(combo_text, (WINDOW_WIDTH - 200, 60))
        
        # 提示文字
        if self.dragging_block:
            hint = "拖动到合适位置松开放置"
        elif self.selected_block:
            hint = "点击网格放置方块"
        else:
            hint = "拖拽方块到网格放置"
        hint_text = FONT_SMALL.render(hint, True, GRAY)
        hint_rect = hint_text.get_rect(center=(WINDOW_WIDTH // 2, self.blocks_y - 20))
        self.screen.blit(hint_text, hint_rect)
        
        # 按钮
        button_y = WINDOW_HEIGHT - 60
        
        # 重新开始按钮
        restart_btn = pygame.Rect(WINDOW_WIDTH // 2 - 170, button_y, 150, 40)
        pygame.draw.rect(self.screen, PURPLE, restart_btn, border_radius=10)
        restart_text = FONT_SMALL.render("重新开始", True, WHITE)
        restart_rect = restart_text.get_rect(center=restart_btn.center)
        self.screen.blit(restart_text, restart_rect)
        
        # 下一关按钮
        next_btn = pygame.Rect(WINDOW_WIDTH // 2 + 20, button_y, 150, 40)
        pygame.draw.rect(self.screen, GREEN, next_btn, border_radius=10)
        next_text = FONT_SMALL.render("下一关", True, WHITE)
        next_rect = next_text.get_rect(center=next_btn.center)
        self.screen.blit(next_text, next_rect)
        
        self.restart_btn = restart_btn
        self.next_btn = next_btn
    
    def draw_game_over(self):
        """绘制游戏结束界面"""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # 游戏结束框
        box = pygame.Rect(WINDOW_WIDTH // 2 - 200, WINDOW_HEIGHT // 2 - 150, 400, 300)
        pygame.draw.rect(self.screen, WHITE, box, border_radius=20)
        
        # 文字
        title = FONT_LARGE.render("🎮 游戏结束", True, BLACK)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 80))
        self.screen.blit(title, title_rect)
        
        score = FONT_MEDIUM.render(f"最终分数: {self.score}", True, PURPLE)
        score_rect = score.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
        self.screen.blit(score, score_rect)
        
        # 重试按钮
        retry_btn = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 40, 200, 50)
        pygame.draw.rect(self.screen, PURPLE, retry_btn, border_radius=10)
        retry_text = FONT_MEDIUM.render("重试", True, WHITE)
        retry_rect = retry_text.get_rect(center=retry_btn.center)
        self.screen.blit(retry_text, retry_rect)
        
        self.retry_btn = retry_btn
    
    def draw_victory(self):
        """绘制胜利界面"""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        box = pygame.Rect(WINDOW_WIDTH // 2 - 200, WINDOW_HEIGHT // 2 - 150, 400, 300)
        pygame.draw.rect(self.screen, WHITE, box, border_radius=20)
        
        title = FONT_LARGE.render("🎉 恭喜通关！", True, GREEN)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 80))
        self.screen.blit(title, title_rect)
        
        msg = FONT_SMALL.render("你已完成所有关卡！", True, BLACK)
        msg_rect = msg.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
        self.screen.blit(msg, msg_rect)
    
    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.QUIT:
            return False
        
        elif event.type == pygame.USEREVENT:
            # 延迟清除行列
            self.clear_lines()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # 检查UI按钮
            if hasattr(self, 'restart_btn') and self.restart_btn.collidepoint(mouse_pos):
                self.restart_level()
                return True
            
            if hasattr(self, 'next_btn') and self.next_btn and self.next_btn.collidepoint(mouse_pos):
                self.next_level()
                return True
            
            if self.game_over:
                if hasattr(self, 'retry_btn') and self.retry_btn.collidepoint(mouse_pos):
                    self.restart_level()
                return True
            
            # 开始拖拽方块
            for block in self.blocks:
                if block.rect and block.rect.collidepoint(mouse_pos):
                    self.dragging_block = block
                    h, w = block.get_size()
                    self.drag_offset = (
                        mouse_pos[0] - block.original_pos[0] - (w * 30) // 2,
                        mouse_pos[1] - block.original_pos[1] - (h * 30) // 2
                    )
                    return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            # 放下方块
            if self.dragging_block:
                grid_pos = self.get_grid_pos(pygame.mouse.get_pos())
                if grid_pos:
                    row, col = grid_pos
                    self.place_block(self.dragging_block, row, col)
                
                self.dragging_block = None
                self.hover_pos = None
        
        elif event.type == pygame.MOUSEMOTION:
            # 更新悬停位置
            if self.dragging_block:
                grid_pos = self.get_grid_pos(pygame.mouse.get_pos())
                self.hover_pos = grid_pos
        
        return True
    
    def run(self):
        """游戏主循环"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if not self.handle_event(event):
                    running = False
            
            # 更新动画
            if self.is_animating:
                self.update_animation()
            
            # 绘制
            self.screen.fill(BG_GRAY)
            
            self.draw_grid()
            self.draw_blocks()
            self.draw_ui()
            
            if self.game_over:
                self.draw_game_over()
            
            if self.show_victory:
                self.draw_victory()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()


def main():
    """主函数"""
    game = Game()
    game.run()


if __name__ == '__main__':
    main()