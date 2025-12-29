import pygame
import sys
import numpy as np
import math

# ==========================================
# 1. SETUP DATA & MATRIKS
# ==========================================

def load_vertices(filename):
    vertices = []
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
            n = int(lines[0].strip())
            for i in range(1, n + 1):
                parts = lines[i].strip().split()
                if len(parts) >= 3:
                    x = float(parts[0])
                    y = float(parts[1])
                    z = float(parts[2])
                    vertices.append(np.array([x, y, z, 1])) 
        return vertices
    except FileNotFoundError:
        print(f"Error: File {filename} tidak ditemukan.")
        return []

def load_edges(filename):
    edges = []
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
            n = int(lines[0].strip())
            for i in range(1, n + 1):
                parts = lines[i].strip().split()
                if len(parts) >= 2:
                    start = int(parts[0]) - 1 
                    end = int(parts[1]) - 1
                    edges.append([start, end])
        return edges
    except FileNotFoundError:
        print(f"Error: File {filename} tidak ditemukan.")
        return []

# --- MATRIKS TRANSFORMASI ---
def get_translation_matrix(tx, ty, tz):
    return np.array([
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1]
    ])

def get_scale_matrix(sx, sy, sz):
    return np.array([
        [sx, 0, 0, 0],
        [0, sy, 0, 0],
        [0, 0, sz, 0],
        [0, 0, 0, 1]
    ])

def get_rotation_x(angle):
    rad = math.radians(angle)
    c, s = math.cos(rad), math.sin(rad)
    return np.array([
        [1, 0, 0, 0],
        [0, c, -s, 0],
        [0, s, c, 0],
        [0, 0, 0, 1]
    ])

def get_rotation_y(angle):
    rad = math.radians(angle)
    c, s = math.cos(rad), math.sin(rad)
    return np.array([
        [c, 0, s, 0],
        [0, 1, 0, 0],
        [-s, 0, c, 0],
        [0, 0, 0, 1]
    ])

def get_rotation_z(angle):
    rad = math.radians(angle)
    c, s = math.cos(rad), math.sin(rad)
    return np.array([
        [c, -s, 0, 0],
        [s, c, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

# ==========================================
# 2. ALGORITMA DDA (MANUAL LINE)
# ==========================================
def gambar_garis_dda(screen, x1, y1, x2, y2, color, thickness=2):
    dx = x2 - x1
    dy = y2 - y1
    steps = int(max(abs(dx), abs(dy)))
    
    if steps == 0: return

    x_inc = dx / steps
    y_inc = dy / steps
    x, y = x1, y1
    
    for _ in range(steps + 1):
        # Menggambar lingkaran kecil agar garis terlihat halus (anti-aliasing manual)
        pygame.draw.circle(screen, color, (int(x), int(y)), thickness)
        x += x_inc
        y += y_inc

# ==========================================
# 3. UI & VISUAL (Eye-Pleasing Theme)
# ==========================================
def draw_ui(screen, scale, angle_x, angle_y, tx, ty):
    # Panel Info Minimalis di Pojok Kiri
    # Warna panel semi-transparan (Dark Blue Glass)
    overlay = pygame.Surface((280, 180))
    overlay.set_alpha(150) 
    overlay.fill((10, 20, 40)) 
    screen.blit(overlay, (20, 20))
    
    # Border tipis elegan
    pygame.draw.rect(screen, (100, 149, 237), (20, 20, 280, 180), 1)

    font_header = pygame.font.SysFont("Verdana", 18, bold=True)
    font_text = pygame.font.SysFont("Consolas", 14)

    # Judul
    text_title = font_header.render("3D VIEWER SYSTEM", True, (255, 255, 255))
    screen.blit(text_title, (35, 30))

    # Info Status
    infos = [
        f"Position : {tx}, {ty}",
        f"Scale    : {scale:.1f}x",
        f"Rotation : X {int(angle_x)}° | Y {int(angle_y)}°",
        "",
        "CONTROLS:",
        "[ARROWS] Move Position",
        "[W/A/S/D] Rotate Object",
        "[Q / E] Zoom In/Out"
    ]
    
    y_offset = 60
    for line in infos:
        color = (200, 220, 255) # Soft White-Blue
        if "CONTROLS" in line: color = (255, 215, 0) # Soft Gold
        
        txt = font_text.render(line, True, color)
        screen.blit(txt, (35, y_offset))
        y_offset += 18

# ==========================================
# 4. MAIN PROGRAM
# ==========================================
def main():
    vertices = load_vertices('vertex.txt')
    edges = load_edges('edge.txt')
    if not vertices: return

    pygame.init()
    WIDTH, HEIGHT = 1280, 720
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tugas Grafika: Interaktif 3D")
    clock = pygame.time.Clock()

    # --- PALET WARNA "MODERN BLUEPRINT" (Enak di mata) ---
    BG_COLOR = (25, 35, 50)       # Midnight Blue (Gelap tapi tidak hitam pekat)
    GRID_COLOR = (40, 50, 70)     # Abu-abu kebiruan (Grid tipis)
    LINE_COLOR = (137, 207, 240)  # Baby Blue (Garis Objek)
    NODE_COLOR = (255, 223, 186)  # Soft Peach/Gold (Titik Sudut)
    
    # Variabel Posisi Awal (Ditaruh DI LUAR loop supaya tidak kereset)
    scale_val = 100.0
    angle_x, angle_y, angle_z = 0, 0, 0
    trans_x, trans_y = WIDTH // 2, HEIGHT // 2  # Posisi tengah

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
        
        # --- INPUT KEYBOARD ---
        keys = pygame.key.get_pressed()
        
        # 1. TRANSLASI (PINDAH POSISI) - Pakai PANAH
        if keys[pygame.K_LEFT]: trans_x -= 5
        if keys[pygame.K_RIGHT]: trans_x += 5
        if keys[pygame.K_UP]: trans_y -= 5
        if keys[pygame.K_DOWN]: trans_y += 5
        
        # 2. ROTASI (PUTAR) - Pakai WASD
        if keys[pygame.K_a]: angle_y -= 2
        if keys[pygame.K_d]: angle_y += 2
        if keys[pygame.K_w]: angle_x -= 2
        if keys[pygame.K_s]: angle_x += 2
        
        # 3. SKALA (ZOOM) - Pakai Q dan E
        if keys[pygame.K_e]: scale_val += 2
        if keys[pygame.K_q]: scale_val -= 2
        if scale_val < 10: scale_val = 10 # Batas minimum zoom

        # --- RENDER ---
        screen.fill(BG_COLOR)
        
        # Gambar Grid Background (Supaya berasa 3D space)
        for x in range(0, WIDTH, 50):
            pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 50):
            pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y), 1)

        # Hitung Matriks
        m_scale = get_scale_matrix(scale_val, scale_val, scale_val)
        m_rot_x = get_rotation_x(angle_x)
        m_rot_y = get_rotation_y(angle_y)
        m_rot_z = get_rotation_z(angle_z)
        m_trans = get_translation_matrix(trans_x, trans_y, 0)

        # Urutan Penting: Scale -> Rotate -> Translate
        matrix_final = m_trans @ m_rot_x @ m_rot_y @ m_rot_z @ m_scale

        # Proyeksi Titik
        projected = []
        for v in vertices:
            res = matrix_final @ v
            projected.append([res[0], res[1]])

        # Gambar Garis (DDA)
        for edge in edges:
            p1 = projected[edge[0]]
            p2 = projected[edge[1]]
            gambar_garis_dda(screen, p1[0], p1[1], p2[0], p2[1], LINE_COLOR, 2)

        # Gambar Titik Sudut (Biar cantik)
        for p in projected:
            pygame.draw.circle(screen, NODE_COLOR, (int(p[0]), int(p[1])), 4)

        # UI
        draw_ui(screen, scale_val, angle_x, angle_y, trans_x, trans_y)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()