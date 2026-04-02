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

# --- Superficie del Terreno (Para permitir destrucción) ---
terreno_surf = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)

def inicializar_terreno():
    terreno_surf.fill((0, 0, 0, 0)) # Transparente
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
        v0 = potencia * 0.14
        self.vx = v0 * math.cos(rad)
        self.vy = -v0 * math.sin(rad)
        self.viento = viento

    def actualizar(self):
        self.vx += self.viento * 0.005
        self.vy += GRAVEDAD
        self.x += self.vx
        self.y += self.vy

    def dibujar(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), 4)

class Tanque:
    def __init__(self, x, color):
        self.x = x
        self.color = color
        self.vida = 100
        self.potencia = 50
        self.angulo = 45 if x < 500 else 135
        # Ajustar Y al terreno inicial
        self.y = 500 + math.sin(x * 0.01) * 30

    def obtener_rects(self):
        # Hitbox de la base
        rect_base = pygame.Rect(self.x - 35, self.y - 21, 70, 21)
        # Hitbox de la torreta (área superior)
        rect_torreta = pygame.Rect(self.x - 15, self.y - 45, 30, 25)
        return rect_base, rect_torreta

    def dibujar(self, surf):
        # Base
        pygame.draw.rect(surf, self.color, (self.x - 35, self.y - 21, 70, 21), border_radius=10)
        # Torreta
        puntos = [(self.x-18, self.y-21), (self.x+18, self.y-21), (self.x+9, self.y-46), (self.x-9, self.y-46)]
        pygame.draw.polygon(surf, self.color, puntos)
        # Cañón
        rad = math.radians(self.angulo)
        px, py = self.x, self.y - 34
        pygame.draw.line(surf, self.color, (px, py), (px + 38*math.cos(rad), py - 38*math.sin(rad)), 6)

def verificar_impacto_terreno(bala):
    if 0 <= int(bala.x) < ANCHO and 0 <= int(bala.y) < ALTO:
        color = terreno_surf.get_at((int(bala.x), int(bala.y)))
        return color[3] > 0 # Si el alpha es > 0, hay tierra
    return False

# --- Lógica Principal ---
t1, t2 = Tanque(200, AZUL_P1), Tanque(800, ROJO_P2)
balas, viento, turno_p1 = [], random.uniform(-1.5, 1.5), True
reloj = pygame.time.Clock()

while True:
    pantalla.fill(COLOR_CIELO)
    pantalla.blit(terreno_surf, (0, 0))
    
    for e in pygame.event.get():
        if e.type == pygame.QUIT: pygame.quit(); exit()
        if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE and not balas:
            t = t1 if turno_p1 else t2
            balas.append(Proyectil(t.x, t.y - 34, t.angulo, t.potencia, viento, t.color))
            turno_p1 = not turno_p1
            viento = random.uniform(-1.5, 1.5)

    # Controles
    k = pygame.key.get_pressed()
    curr = t1 if turno_p1 else t2
    if k[pygame.K_LEFT]: curr.angulo += 1
    if k[k[pygame.K_RIGHT]]: curr.angulo -= 1
    if k[pygame.K_UP]: curr.potencia = min(100, curr.potencia + 1)
    if k[pygame.K_DOWN]: curr.potencia = max(10, curr.potencia - 1)

    for b in balas[:]:
        b.actualizar()
        b.dibujar(pantalla)
        
        # Colisión con Tanques (Base y Torreta)
        impacto_tanque = False
        for t in [t1, t2]:
            r_base, r_torreta = t.obtener_rects()
            if r_base.collidepoint(b.x, b.y) or r_torreta.collidepoint(b.x, b.y):
                t.vida -= 30
                impacto_tanque = True
        
        # Colisión con Terreno y Explosión
        if impacto_tanque or verificar_impacto_terreno(b):
            # Crear hueco en el terreno
            pygame.draw.circle(terreno_surf, (0,0,0,0), (int(b.x), int(b.y)), 25)
            # Daño por proximidad si cayó al suelo
            if not impacto_tanque:
                for t in [t1, t2]:
                    dist = math.sqrt((b.x - t.x)**2 + (b.y - t.y)**2)
                    if dist < 50: t.vida -= 15
            balas.remove(b)
        elif b.x < 0 or b.x > ANCHO or b.y > ALTO: balas.remove(b)

    t1.dibujar(pantalla); t2.dibujar(pantalla)
    pygame.display.flip(); reloj.tick(FPS)
