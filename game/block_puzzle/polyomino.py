import numpy as np
import matplotlib.pyplot as plt
import math

# -----------------------------
# 多连方生成（只去重旋转，相同旋转不重复，镜像保留）
# -----------------------------
def normalize(shape):
    """将形状移动到左上角"""
    xs = [x for x, y in shape]
    ys = [y for x, y in shape]
    return frozenset((x - min(xs), y - min(ys)) for x, y in shape)

def add_square(shape):
    """在现有形状周围添加一个方块"""
    new_shapes = set()
    directions = [(0,1),(0,-1),(1,0),(-1,0)]
    for x, y in shape:
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (nx, ny) not in shape:
                new_shape = set(shape)
                new_shape.add((nx, ny))
                new_shapes.add(normalize(new_shape))
    return new_shapes

def all_rotations(shape):
    """生成 shape 的所有旋转（不考虑镜像）"""
    result = set()
    s = list(shape)
    for _ in range(4):
        s = [(y, -x) for x, y in s]  # 旋转90°
        result.add(normalize(s))
    return result

def generate_polyomino(n, remove_rotation_duplicate=False):
    """
    n: 方块数
    remove_rotation_duplicate: 是否去重旋转相同形状（True -> 只保留一个旋转方向）
    """
    if n == 1:
        return {frozenset([(0,0)])}
    
    smaller = generate_polyomino(n-1, remove_rotation_duplicate)
    shapes = set()
    
    for s in smaller:
        for new_s in add_square(s):
            if remove_rotation_duplicate:
                # 去重旋转重复
                is_duplicate = False
                for rot in all_rotations(new_s):
                    if rot in shapes:
                        is_duplicate = True
                        break
                if not is_duplicate:
                    shapes.add(new_s)
            else:
                shapes.add(new_s)
    return shapes

# -----------------------------
# 可视化绘制
# -----------------------------
def draw_polyomino_imshow(shape, ax):
    xs = [x for x, y in shape]
    ys = [y for x, y in shape]
    width = max(xs)+1
    height = max(ys)+1
    grid = np.zeros((height, width))
    for x, y in shape:
        grid[y, x] = 1
    ax.imshow(grid[::-1, :], cmap='Blues', interpolation='none')
    ax.axis('off')

def visualize_polyominoes(shapes, per_row=5, per_page=500, save_prefix="polyominoes"):
    shapes = list(shapes)
    n_shapes = len(shapes)
    n_pages = math.ceil(n_shapes / per_page)
    
    for page in range(n_pages):
        start = page * per_page
        end = min((page+1) * per_page, n_shapes)
        shapes_page = shapes[start:end]
        n_page_shapes = len(shapes_page)
        n_rows = math.ceil(n_page_shapes / per_row)
        fig, axes = plt.subplots(n_rows, per_row, figsize=(per_row*2, n_rows*2))
        
        if n_rows == 1:
            axes = [axes] if per_row==1 else axes
        else:
            axes = axes.flatten()
        
        for ax in axes[n_page_shapes:]:
            ax.axis('off')
        
        for i, shape in enumerate(shapes_page):
            draw_polyomino_imshow(shape, axes[i])
        
        plt.tight_layout()
        save_path = f"{save_prefix}_page{page+1}.png"
        plt.savefig(save_path, dpi=300)
        plt.close(fig)
        print(f"已保存 {save_path} ({start+1}-{end}/{n_shapes})")

# -----------------------------
# 主程序
# -----------------------------
if __name__ == "__main__":
    N = int(input("请输入方块数 N (建议 N <= 8): "))
    remove_rotation = input("是否去重旋转重复形状? (y/n) : ").strip().lower() == 'y'
    
    shapes = generate_polyomino(N, remove_rotation_duplicate=remove_rotation)
    print(f"N={N} 的多连方数量 (去重旋转={remove_rotation}, 镜像保留): {len(shapes)}")
    
    visualize_polyominoes(shapes, per_row=5, per_page=500, save_prefix=f"polyomino_{N}_rot{remove_rotation}")
