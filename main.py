# ==========================================
# PROYECTO: Artillería Pro - Destrucción Total
# VERSIÓN: 2.3 (No Friendly Fire)
# AUTORES: Alfredo & Gemi
# ==========================================

import pygame
import math
import random
import sys

# --- Configuración ---
ANCHO, ALTO = 1000, 700
GRAVEDAD = 0.25
FPS = 60

AZUL_P1 = (20, 60, 120)
ROJO_P2 = (180, 40, 40)
COLOR_CIELO = (135, 206, 235)
COLOR_TERRENO = (34, 139, 34)
BLANCO = (255, 255, 255)

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption(f"Artillería Pro V 2.3 - Alfredo & Gemi")
fuente = pygame.font.SysFont("Arial", 20, bold=True)
reloj = pygame.time.Clock()

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

def punto_en_torreta(px, py, vertices):
    n = len(vertices)
    dentro = False
    p1x, p1y = vertices[0]
    for i in range(n + 1):
        p2x, p2y = vertices[i % n]
        if py > min(p1y, p2y) and py <= max(p1y, p2y):
            if px <= max(p1x, p2x):
                if p1y != p2y:
                    xinters = (py - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                if p1x == p2x or px <= xinters:
                    dentro = not dentro
        p1x, p1y = p2x, p2y
    return dentro

class Proyectil:
    def __init__(self, x, y, angulo, potencia, viento, color, dueno):
        self.x, self.y = x, y
        self.color = color
        self.dueno = dueno  # Guardamos quién disparó (t1 o t2)
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
        self.vida = 100
        self.potencia = 50
        self.angulo = 45 if es_p1 else 135
        self.y = 500 + math.sin(x * 0.01) * 30

    def obtener_poligono_torreta(self):
        return [(self.x - 18, self.y - 21), (self.x + 18, self.y - 21), 
                (self.x + 9, self.y - 46), (self.x - 9, self.y - 46)]

    def obtener_rect_base(self):
        return pygame.Rect(self.x - 35, self.y - 21, 70, 21)

    def dibujar(self, surf):
        pygame.draw.rect(surf, self.color, (self.x - 35, self.y - 21, 70, 21), border_radius=10)
        pygame.draw.polygon(surf, self.color, self.obtener_poligono_torreta())
        rad = math.radians(self.angulo)
        px, py = self.x, self.y - 34
        pygame.draw.line(surf, self.color, (px, py), (px + 40*math.cos(rad), py - 40*math.sin(rad)), 6)

def dibujar_hud(t1, t2, viento, turno_p1):
    pygame.draw.rect(pantalla, (30, 30, 30), (0, 600, ANCHO, 100))
    c1 = BLANCO if turno_p1 else (120, 120, 120)
    c2 = BLANCO if not turno_p1 else (120, 120, 120)
    pygame.draw.rect(pantalla, (150, 0, 0), (20, 620, 200, 20))
    pygame.draw.rect(pantalla, (0, 200, 0), (20, 620, 2 * max(0, t1.vida), 20))
    pantalla.blit(fuente.render(f"P1: {t1.angulo}° | POT: {t1.potencia}", True, c1), (20, 650))
    pygame.draw.rect(pantalla, (150, 0, 0), (780, 620, 200, 20))
    pygame.draw.rect(pantalla, (0, 200, 0), (780, 620, 2 * max(0, t2.vida), 20))
    pantalla.blit(fuente.render(f"P2: {t2.angulo}° | POT: {t2.potencia}", True, c2), (780, 650))
    txt_v = f"VIENTO: {'>>' if viento > 0 else '<<'} {abs(viento):.2f}"
    pantalla.blit(fuente.render(txt_v, True, (0, 200, 255)), (420, 620))

t1, t2 = Tanque(200, AZUL_P1, True), Tanque(800, ROJO_P2, False)
balas, viento, turno_p1 = [], random.uniform(-1.5, 1.5), True

while True:
    pantalla.fill(COLOR_CIELO)
    pantalla.blit(terreno_surf, (0, 0))
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: pygame.quit(); sys.exit()
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE and len(balas) == 0:
                t_act = t1 if turno_p1 else t2
                # Pasamos el tanque actual como 'dueno'
                balas.append(Proyectil(t_act.x, t_act.y - 34, t_act.angulo, t_act.potencia, viento, t_act.color, t_act))
                turno_p1 = not turno_p1
                viento = random.uniform(-1.5, 1.5)

    keys = pygame.key.get_pressed()
    t_control = t1 if turno_p1 else t2
    if keys[pygame.K_LEFT]: t_control.angulo += 1
    if keys[pygame.K_RIGHT]: t_control.angulo -= 1
    if keys[pygame.K_UP]: t_control.potencia = min(100, t_control.potencia + 1)
    if keys[pygame.K_DOWN]: t_control.potencia = max(10, t_control.potencia - 1)

    for b in balas[:]:
        b.actualizar()
        b.dibujar(pantalla)
        
        impacto_tanque = False
        for t_objetivo in [t1, t2]:
            # REGLA CLAVE: Si el tanque es el dueño, ignoramos la colisión
            if t_objetivo == b.dueno:
                continue
                
            if t_objetivo.obtener_rect_base().collidepoint(b.x, b.y) or \
               punto_en_torreta(b.x, b.y, t_objetivo.obtener_poligono_torreta()):
                t_objetivo.vida -= 20
                impacto_tanque = True
                break

        impacto_terreno = False
        if not impacto_tanque and 0 <= int(b.x) < ANCHO and 0 <= int(b.y) < ALTO:
            if terreno_surf.get_at((int(b.x), int(b.y)))[3] > 0:
                impacto_terreno = True

        if impacto_tanque or impacto_terreno:
            pygame.draw.circle(terreno_surf, (0, 0, 0, 0), (int(b.x), int(b.y)), 30)
            balas.remove(b)
        elif b.x < 0 or b.x > ANCHO or b.y > ALTO:
            balas.remove(b)

    t1.dibujar(pantalla); t2.dibujar(pantalla)
    dibujar_hud(t1, t2, viento, turno_p1)
    pygame.display.flip(); reloj.tick(FPS)
