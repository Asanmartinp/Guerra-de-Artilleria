# ==========================================
# PROYECTO: Artillería Pro - Destrucción Total
# VERSIÓN: 2.1
# AUTORES: Alfredo & Gemi
# ==========================================

import pygame
import math
import random
import sys

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
BLANCO = (255, 255, 255)

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption(f"Artillería Pro V 2.1 - Alfredo & Gemi")
fuente = pygame.font.SysFont("Arial", 20, bold=True)
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
        base = pygame.Rect(self.x - 35, self.y - 21, 70, 21)
        torreta = pygame.Rect(self.x - 15, self.y - 45, 30, 25)
        return base, torreta

    def dibujar(self, surf):
        # Base
        pygame.draw.rect(surf, self.color, (self.x - 35, self.y - 21, 70, 21), border_radius=10)
        # Torreta
        pts = [(self.x-18, self.y-21), (self.x+18, self.y-21), (self.x+9, self.y-46), (self.x-9, self.y-46)]
        pygame.draw.polygon(surf, self.color, pts)
        # Cañón
        rad = math.radians(self.angulo)
        px, py = self.x, self.y - 34
        pygame.draw.line(surf, self.color, (px, py), (px + 40*math.cos(rad), py - 40*math.sin(rad)), 6)

def dibujar_hud(t1, t2, viento, turno_p1):
    # Fondo del panel
    pygame.draw.rect(pantalla, (30, 30, 30), (0, 600, ANCHO, 100))
    
    # Colores según turno
    c1 = BLANCO if turno_p1 else (120, 120, 120)
    c2 = BLANCO if not turno_p1 else (120, 120, 120)
    
    # HUD P1
    pygame.draw.rect(pantalla, (150, 0, 0), (20, 620, 200, 20))
    pygame.draw.rect(pantalla, (0, 200, 0), (20, 620, 2 * max(0, t1.vida), 20))
    pantalla.blit(fuente.render(f"P1: {t1.angulo}° | POT: {t1.potencia}", True, c1), (20, 650))
    
    # HUD P2
    pygame.draw.rect(pantalla, (150, 0, 0), (780, 620, 200, 20))
    pygame.draw.rect(pantalla, (0, 200, 0), (780, 620, 2 * max(0, t2.vida), 20))
    pantalla.blit(fuente.render(f"P2: {t2.angulo}° | POT: {t2.potencia}", True, c2), (780, 650))
    
    # Info central
    txt_v = f"VIENTO: {'>>' if viento > 0 else '<<'} {abs(viento):.2f}"
    pantalla.blit(fuente.render(txt_v, True, (0, 200, 255)), (420, 620))
    pantalla.blit(fuente.render("ESPACIO para disparar", True, BLANCO), (400, 660))

# --- Instancias ---
t1 = Tanque(200, AZUL_P1, True)
t2 = Tanque(800, ROJO_P2, False)
balas = []
viento = random.uniform(-1.5, 1.5)
turno_p1 = True

# --- Bucle Principal ---
while True:
    pantalla.fill(COLOR_CIELO)
    pantalla.blit(terreno_surf, (0, 0))
    
    # Captura de eventos para disparo
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE and len(balas) == 0:
                t_act = t1 if turno_p1 else t2
                nueva_bala = Proyectil(t_act.x, t_act.y - 34, t_act.angulo, t_act.potencia, viento, t_act.color)
                balas.append(nueva_bala)
                turno_p1 = not turno_p1
                viento = random.uniform(-1.5, 1.5)

    # Captura de teclas mantenidas para ángulo y potencia
    keys = pygame.key.get_pressed()
    t_control = t1 if turno_p1 else t2
    
    if keys[pygame.K_LEFT]:
        t_control.angulo += 1
    if keys[pygame.K_RIGHT]:
        t_control.angulo -= 1
    if keys[pygame.K_UP]:
        t_control.potencia = min(100, t_control.potencia + 1)
    if keys[pygame.K_DOWN]:
        t_control.potencia = max(10, t_control.potencia - 1)

    # Actualizar proyectiles
    for b in balas[:]:
        b.actualizar()
        b.dibujar(pantalla)
        
        # Colisión terreno
        hit_suelo = False
        if 0 <= int(b.x) < ANCHO and 0 <= int(b.y) < ALTO:
            if terreno_surf.get_at((int(b.x), int(b.y)))[3] > 0:
                hit_suelo = True

        # Colisión tanques
        hit_tanque = False
        for t_objetivo in [t1, t2]:
            base_hb, torreta_hb = t_objetivo.obtener_hitboxes()
            if base_hb.collidepoint(b.x, b.y) or torreta_hb.collidepoint(b.x, b.y):
                t_objetivo.vida -= 20
                hit_tanque = True

        if hit_suelo or hit_tanque:
            # Crear cráter
            pygame.draw.circle(terreno_surf, (0, 0, 0, 0), (int(b.x), int(b.y)), 30)
            balas.remove(b)
        elif b.x < 0 or b.x > ANCHO or b.y > ALTO:
            balas.remove(b)

    # Dibujar todo
    t1.dibujar(pantalla)
    t2.dibujar(pantalla)
    dibujar_hud(t1, t2, viento, turno_p1)
    
    pygame.display.flip()
    reloj.tick(FPS)
