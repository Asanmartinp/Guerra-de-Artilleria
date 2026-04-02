import pygame
import math
import random

# --- Configuración ---
ANCHO, ALTO = 1000, 600
COLOR_CIELO = (135, 206, 235)
COLOR_TERRENO = (34, 139, 34)
GRAVEDAD = 0.25

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Guerra de Artillería - ¡Fuego!")
fuente = pygame.font.SysFont("Arial", 20)

# --- Funciones de Apoyo ---
def generar_terreno_pixel():
    terreno = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    puntos = []
    off_set = random.randint(0, 1000)
    alturas = []
    for x in range(0, ANCHO + 1):
        y = int(ALTO * 0.7 + math.sin(x * 0.01 + off_set) * 50 + math.sin(x * 0.005) * 30)
        puntos.append((x, y))
        alturas.append(y)
    puntos.extend([(ANCHO, ALTO), (0, ALTO)])
    pygame.draw.polygon(terreno, COLOR_TERRENO, puntos)
    return terreno, alturas

# --- Clases ---
class Proyectil:
    def __init__(self, x, y, angulo, potencia, color, es_p1):
        self.x, self.y = x, y
        self.color = color
        # Convertir ángulo a radianes y ajustar dirección
        rad = math.radians(angulo) if es_p1 else math.radians(180 - angulo)
        self.vx = math.cos(rad) * (potencia / 5)
        self.vy = -math.sin(rad) * (potencia / 5)
        self.radio = 4

    def mover(self):
        self.vy += GRAVEDAD # La gravedad tira hacia abajo
        self.x += self.vx
        self.y += self.vy

    def dibujar(self, superficie):
        pygame.draw.circle(superficie, self.color, (int(self.x), int(self.y)), self.radio)

class Tanque:
    def __init__(self, x, color, es_p1):
        self.x, self.color, self.es_p1 = x, color, es_p1
        self.angulo, self.potencia = 45, 50
        self.y = 0

    def actualizar_y(self, alturas):
        if 0 <= int(self.x) < len(alturas):
            self.y = alturas[int(self.x)] - 15

    def dibujar(self, superficie):
        pygame.draw.rect(superficie, self.color, (self.x - 15, self.y, 30, 15))
        rad = math.radians(self.angulo) if self.es_p1 else math.radians(180 - self.angulo)
        long = self.potencia / 2
        pygame.draw.line(superficie, self.color, (self.x, self.y), 
                         (self.x + math.cos(rad) * long, self.y - math.sin(rad) * long), 5)

# --- Inicialización ---
superficie_terreno, lista_alturas = generar_terreno_pixel()
tanque1 = Tanque(int(ANCHO * 0.1), (50, 50, 50), True)
tanque2 = Tanque(int(ANCHO * 0.85), (200, 0, 0), False)
proyectiles = []
reloj = pygame.time.Clock()

# --- Bucle ---
ejecutando = True
while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: ejecutando = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_x: # Disparar P1
                proyectiles.append(Proyectil(tanque1.x, tanque1.y, tanque1.angulo, tanque1.potencia, tanque1.color, True))
            if evento.key == pygame.K_m: # Disparar P2
                proyectiles.append(Proyectil(tanque2.x, tanque2.y, tanque2.angulo, tanque2.potencia, tanque2.color, False))

    teclas = pygame.key.get_pressed()
    # Controles P1
    if teclas[pygame.K_a]: tanque1.x -= 2
    if teclas[pygame.K_d]: tanque1.x += 2
    if teclas[pygame.K_w]: tanque1.angulo = min(90, tanque1.angulo + 1)
    if teclas[pygame.K_s]: tanque1.angulo = max(0, tanque1.angulo - 1)
    if teclas[pygame.K_q]: tanque1.potencia = max(10, tanque1.potencia - 1)
    if teclas[pygame.K_e]: tanque1.potencia = min(100, tanque1.potencia + 1)
    # Controles P2
    if teclas[pygame.K_j]: tanque2.x -= 2
    if teclas[pygame.K_l]: tanque2.x += 2
    if teclas[pygame.K_o]: tanque2.angulo = min(90, tanque2.angulo + 1)
    if teclas[pygame.K_k]: tanque2.angulo = max(0, tanque2.angulo - 1)
    if teclas[pygame.K_i]: tanque2.potencia = max(10, tanque2.potencia - 1)
    if teclas[pygame.K_p]: tanque2.potencia = min(100, tanque2.potencia + 1)

    tanque1.actualizar_y(lista_alturas)
    tanque2.actualizar_y(lista_alturas)

    # Actualizar Proyectiles
    for p in proyectiles[:]:
        p.mover()
        # Colisión con terreno (píxel no transparente)
        if 0 <= int(p.x) < ANCHO and 0 <= int(p.y) < ALTO:
            if superficie_terreno.get_at((int(p.x), int(p.y)))[3] > 0:
                pygame.draw.circle(superficie_terreno, (0,0,0,0), (int(p.x), int(p.y)), 30)
                proyectiles.remove(p)
        elif p.y > ALTO: proyectiles.remove(p)

    # Dibujo
    pantalla.fill(COLOR_CIELO)
    pantalla.blit(superficie_terreno, (0, 0))
    tanque1.dibujar(pantalla)
    tanque2.dibujar(pantalla)
    for p in proyectiles: p.dibujar(pantalla)
    
    pygame.display.flip()
    reloj.tick(60)
pygame.quit()
