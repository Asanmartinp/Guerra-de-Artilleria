import pygame
import math
import random

# --- Configuración Constante ---
ANCHO, ALTO = 1000, 600
COLOR_CIELO = (135, 206, 235)
COLOR_TERRENO = (34, 139, 34)
GRAVEDAD = 0.25

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Guerra de Artillería - Versión Final")
fuente = pygame.font.SysFont("Arial", 20)
fuente_grande = pygame.font.SysFont("Arial", 50, bold=True)

# --- Funciones de Terreno ---
def generar_terreno_pixel():
    terreno = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    alturas = []
    off_set = random.randint(0, 1000)
    for x in range(ANCHO + 1):
        y = int(ALTO * 0.7 + math.sin(x * 0.01 + off_set) * 50 + math.sin(x * 0.005) * 30)
        alturas.append(y)
    puntos = [(x, y) for x, y in enumerate(alturas)]
    puntos.extend([(ANCHO, ALTO), (0, ALTO)])
    pygame.draw.polygon(terreno, COLOR_TERRENO, puntos)
    return terreno, alturas

# --- Clases del Juego ---
class Proyectil:
    def __init__(self, x, y, angulo, potencia, color, es_p1):
        self.x, self.y = x, y
        self.color = color
        rad = math.radians(angulo) if es_p1 else math.radians(180 - angulo)
        self.vx = math.cos(rad) * (potencia / 5)
        self.vy = -math.sin(rad) * (potencia / 5)

    def mover(self):
        self.vy += GRAVEDAD
        self.x += self.vx
        self.y += self.vy

    def dibujar(self, superficie):
        pygame.draw.circle(superficie, self.color, (int(self.x), int(self.y)), 4)

class Tanque:
    def __init__(self, x, color, es_p1):
        self.x, self.color, self.es_p1 = x, color, es_p1
        self.angulo, self.potencia = 45, 50
        self.vida = 100
        self.victorias = 0
        self.y = 0

    def actualizar_y(self, alturas):
        if 0 <= int(self.x) < len(alturas):
            self.y = alturas[int(self.x)] - 15

    def dibujar(self, superficie, es_su_turno):
        pygame.draw.rect(superficie, self.color, (self.x - 15, self.y, 30, 15))
        rad = math.radians(self.angulo) if self.es_p1 else math.radians(180 - self.angulo)
        lx = self.x + math.cos(rad) * (self.potencia / 2)
        ly = self.y - math.sin(rad) * (self.potencia / 2)
        pygame.draw.line(superficie, self.color, (self.x, self.y), (lx, ly), 5)
        if es_su_turno:
            pygame.draw.polygon(superficie, (255, 255, 0), [(self.x, self.y - 40), (self.x-5, self.y-50), (self.x+5, self.y-50)])

# --- Lógica de Control ---
terreno, lista_alturas = generar_terreno_pixel()
t1 = Tanque(int(ANCHO * 0.1), (50, 50, 50), True)
t2 = Tanque(int(ANCHO * 0.85), (200, 0, 0), False)
proyectiles = []
turno_p1 = True
reloj = pygame.time.Clock()

def calcular_dano(px, py, tanque):
    dist = math.sqrt((px - tanque.x)**2 + (py - tanque.y)**2)
    if dist < 20: return 50 # Impacto directo
    if dist < 50: return 25 # Impacto cercano
    return 0

ejecutando = True
while ejecutando:
    pantalla.fill(COLOR_CIELO)
    pantalla.blit(terreno, (0, 0))
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: ejecutando = False
        if evento.type == pygame.KEYDOWN:
            if turno_p1 and evento.key == pygame.K_x:
                proyectiles.append(Proyectil(t1.x, t1.y, t1.angulo, t1.potencia, t1.color, True))
                turno_p1 = False
            elif not turno_p1 and evento.key == pygame.K_m:
                proyectiles.append(Proyectil(t2.x, t2.y, t2.angulo, t2.potencia, t2.color, False))
                turno_p1 = True

    teclas = pygame.key.get_pressed()
    if turno_p1:
        if teclas[pygame.K_a]: t1.x -= 2
        if teclas[pygame.K_d]: t1.x += 2
        if teclas[pygame.K_w]: t1.angulo = min(90, t1.angulo + 1)
        if teclas[pygame.K_s]: t1.angulo = max(0, t1.angulo - 1)
        if teclas[pygame.K_q]: t1.potencia = max(10, t1.potencia - 1)
        if teclas[pygame.K_e]: t1.potencia = min(100, t1.potencia + 1)
    else:
        if teclas[pygame.K_j]: t2.x -= 2
        if teclas[pygame.K_l]: t2.x += 2
        if teclas[pygame.K_o]: t2.angulo = min(90, t2.angulo + 1)
        if teclas[pygame.K_k]: t2.angulo = max(0, t2.angulo - 1)
        if teclas[pygame.K_i]: t2.potencia = max(10, t2.potencia - 1)
        if teclas[pygame.K_p]: t2.potencia = min(100, t2.potencia + 1)

    t1.actualizar_y(lista_alturas)
    t2.actualizar_y(lista_alturas)

    for p in proyectiles[:]:
        p.mover()
        if 0 <= int(p.x) < ANCHO and 0 <= int(p.y) < ALTO:
            if terreno.get_at((int(p.x), int(p.y)))[3] > 0:
                pygame.draw.circle(terreno, (0,0,0,0), (int(p.x), int(p.y)), 30)
                t1.vida -= calcular_dano(p.x, p.y, t1)
                t2.vida -= calcular_dano(p.x, p.y, t2)
                proyectiles.remove(p)
        elif p.y > ALTO: proyectiles.remove(p)

    t1.dibujar(pantalla, turno_p1)
    t2.dibujar(pantalla, not turno_p1)
    for p in proyectiles: p.dibujar(pantalla)
    
    pantalla.blit(fuente.render(f"P1 Vida: {t1.vida}% | Wins: {t1.victorias}", True, (0,0,0)), (10, 10))
    pantalla.blit(fuente.render(f"P2 Vida: {t2.vida}% | Wins: {t2.victorias}", True, (0,0,0)), (ANCHO-220, 10))

    if t1.vida <= 0 or t2.vida <= 0:
        vencedor = "P2" if t1.vida <= 0 else "P1"
        if t1.vida <= 0: t2.victorias += 1
        else: t1.victorias += 1
        t1.vida, t2.vida = 100, 100
        terreno, lista_alturas = generar_terreno_pixel()

    pygame.display.flip()
    reloj.tick(60)
pygame.quit()
