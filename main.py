import pygame
import math
import random

# --- Configuración ---
ANCHO, ALTO = 1000, 700
ALTO_JUEGO = 600
GRAVEDAD = 0.25
FPS = 60

# Colores
AZUL_P1 = (20, 60, 120)
ROJO_P2 = (180, 40, 40)
COLOR_CIELO = (135, 206, 235)
COLOR_TERRENO = (34, 139, 34)

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Artillería Pro - Destrucción Total")
fuente = pygame.font.SysFont("Arial", 18, bold=True)
reloj = pygame.time.Clock()

# --- Superficie del Terreno ---
terreno_surf = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)

def inicializar_terreno():
    terreno_surf.fill((0, 0, 0, 0))
    puntos = []
    for x in range(ANCHO + 1):
        y = 500 + math.sin(x * 0.01) * 30
        puntos.append((x, y))
    puntos.extend([(ANCHO, ALTO), (0, ALTO)])
    pygame.draw.polygon(terreno_surf, COLOR_TERRENO, puntos)

inicializar_terreno()

class Proyectil:
    def __init__(self, x, y, angulo, potencia, viento, color):
        self.x, self.y = x, y
        self.color = color
        rad = math.radians(angulo)
        v0 = potencia * 0.15
        self.vx = v0 * math.cos(rad)
        self.vy = -v0 * math.sin(rad)
        self.viento = viento

    def actualizar(self):
        self.vx += self.viento * 0.005
        self.vy += GRAVEDAD
        self.x += self.vx
        self.y += self.vy

    def dibujar(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), 5)
        pygame.draw.circle(surf, (0, 0, 0), (int(self.x), int(self.y)), 5, 1)

class Tanque:
    def __init__(self, x, color, es_p1):
        self.x = x
        self.color = color
        self.es_p1 = es_p1
        self.vida = 100
        self.potencia = 50
        self.angulo = 45 if es_p1 else 135
        self.y = 500 + math.sin(x * 0.01) * 30

    def obtener_hitboxes(self):
        # Hitbox base y torreta simplificadas para detección
        base = pygame.Rect(self.x - 35, self.y - 21, 70, 21)
        torreta = pygame.Rect(self.x - 15, self.y - 45, 30, 25)
        return base, torreta

    def dibujar(self, surf):
        # Base redondeada
        pygame.draw.rect(surf, self.color, (self.x - 35, self.y - 21, 70, 21), border_radius=10)
        # Torreta (Trapecio)
        pts = [(self.x-18, self.y-21), (self.x+18, self.y-21), (self.x+9, self.y-46), (self.x-9, self.y-46)]
        pygame.draw.polygon(surf, self.color, pts)
        # Cañón
        rad = math.radians(self.angulo)
        px, py = self.x, self.y - 34
        pygame.draw.line(surf, self.color, (px, py), (px + 40*math.cos(rad), py - 40*math.sin(rad)), 6)

def dibujar_hud(t1, t2, viento, turno_p1):
    pygame.draw.rect(pantalla, (30, 30, 30), (0, 600, ANCHO, 100))
    c1 = (255,255,255) if turno_p1 else (120,120,120)
    c2 = (255,255,255) if not turno_p1 else (120,120,120)
    
    # P1
    pygame.draw.rect(pantalla, (200,0,0), (20, 620, 200, 15))
    pygame.draw.rect(pantalla, (0,200,0), (20, 620, 2 * t1.vida, 15))
    pantalla.blit(fuente.render(f"P1: {t1.angulo}° | POT: {t1.potencia}", True, c1), (20, 645))
    
    # P2
    pygame.draw.rect(pantalla, (200,0,0), (780, 620, 200, 15))
    pygame.draw.rect(pantalla, (0,200,0), (780, 620, 2 * t2.vida, 15))
    pantalla.blit(fuente.render(f"P2: {t2.angulo}° | POT: {t2.potencia}", True, c2), (780, 645))
    
    txt_v = f"VIENTO: {'>>' if viento > 0 else '<<'} {abs(viento):.2f}"
    pantalla.blit(fuente.render(txt_v, True, (0, 200, 255)), (440, 630))

# --- Ejecución ---
t1, t2 = Tanque(200, AZUL_P1, True), Tanque(800, ROJO_P2, False)
balas, viento, turno_p1 = [], random.uniform(-1.5, 1.5), True

while True:
    pantalla.fill(COLOR_CIELO)
    pantalla.blit(terreno_surf, (0, 0))
    
    for e in pygame.event.get():
        if e.type == pygame.QUIT: pygame.quit(); exit()
        if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE and not balas:
            t = t1 if turno_p1 else t2
            balas.append(Proyectil(t.x, t.y-34, t.angulo, t.potencia, viento, t.color))
            turno_p1 = not turno_p1
            viento = random.uniform(-1.5, 1.5)

    keys = pygame.key.get_pressed()
    curr = t1 if turno_p1 else t2
    if keys[pygame.K_LEFT]: curr.angulo += 1
    if keys[pygame.K_RIGHT]: curr.angulo -= 1
    if keys[pygame.K_UP]: curr.potencia = min(100, curr.potencia + 1)
    if keys[pygame.K_DOWN]: curr.potencia = max(10, curr.potencia - 1)

    for b in balas[:]:
        b.actualizar()
        b.dibujar(pantalla)
        
        hit_terreno = False
        if 0 <= int(b.x) < ANCHO and 0 <= int(b.y) < ALTO:
            if terreno_surf.get_at((int(b.x), int(b.y)))[3] > 0: hit_terreno = True

        hit_tanque = False
        for t in [t1, t2]:
            b_hb, t_hb = t.obtener_hitboxes()
            if b_hb.collidepoint(b.x, b.y) or t_hb.collidepoint(b.x, b.y):
                t.vida -= 20
                hit_tanque = True

        if hit_terreno or hit_tanque:
            pygame.draw.circle(terreno_surf, (0,0,0,0), (int(b.x), int(b.y)), 30)
            if b in balas: balas.remove(b)
        elif b.x < 0 or b.x > ANCHO or b.y > ALTO:
            if b in balas: balas.remove(b)

    t1.dibujar(pantalla); t2.dibujar(pantalla)
    dibujar_hud(t1, t2, viento, turno_p1)
    pygame.display.flip(); reloj.tick(FPS)
