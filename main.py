import pygame
import math
import random

# --- Configuración ---
ANCHO, ALTO = 1000, 700 # Aumentamos alto para el panel de controles
ALTO_JUEGO = 600
COLOR_CIELO = (135, 206, 235)
COLOR_TERRENO = (34, 139, 34)
GRAVEDAD = 0.25

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Guerra de Artillería - Versión Final")
fuente = pygame.font.SysFont("Arial", 18)
fuente_grande = pygame.font.SysFont("Arial", 40, bold=True)

# --- Carga de Recursos ---
try:
    img_base = pygame.image.load("tanque1.png").convert_alpha()
    img_tanque = pygame.transform.scale(img_base, (50, 40))
except:
    # Si no encuentra la imagen, crea un rectángulo verde temporal
    img_tanque = pygame.Surface((50, 40), pygame.SRCALPHA)
    pygame.draw.rect(img_tanque, (0, 100, 0), (0, 15, 50, 25))
    pygame.draw.rect(img_tanque, (0, 80, 0), (15, 0, 20, 15))

# --- Funciones de Terreno ---
def generar_terreno_pixel():
    terreno = pygame.Surface((ANCHO, ALTO_JUEGO), pygame.SRCALPHA)
    alturas = []
    off_set = random.randint(0, 1000)
    for x in range(ANCHO + 1):
        y = int(ALTO_JUEGO * 0.7 + math.sin(x * 0.01 + off_set) * 50 + math.sin(x * 0.005) * 30)
        alturas.append(y)
    puntos = [(x, y) for x, y in enumerate(alturas)]
    puntos.extend([(ANCHO, ALTO_JUEGO), (0, ALTO_JUEGO)])
    pygame.draw.polygon(terreno, COLOR_TERRENO, puntos)
    return terreno

# --- Clases ---
class Proyectil:
    def __init__(self, x, y, angulo, potencia, es_p1):
        self.x, self.y = x, y
        rad = math.radians(angulo) if es_p1 else math.radians(180 - angulo)
        self.vx = math.cos(rad) * (potencia / 5)
        self.vy = -math.sin(rad) * (potencia / 5)

    def mover(self):
        self.vy += GRAVEDAD
        self.x += self.vx
        self.y += self.vy

    def dibujar(self, superficie):
        pygame.draw.circle(superficie, (0,0,0), (int(self.x), int(self.y)), 4)

class Tanque:
    def __init__(self, x, img, es_p1):
        self.x = x
        self.img = img if es_p1 else pygame.transform.flip(img, True, False)
        self.mask = pygame.mask.from_surface(self.img)
        self.y = 0
        self.angulo = 45
        self.potencia = 50
        self.vida = 100
        self.victorias = 0
        self.es_p1 = es_p1

    def caer(self, superficie_terreno):
        # Caída suave: si no hay suelo debajo, baja 2 píxeles por frame
        if self.y + self.img.get_height() < ALTO_JUEGO:
            # Chequeamos el píxel central inferior del tanque
            try:
                pixel_debajo = superficie_terreno.get_at((int(self.x), int(self.y + self.img.get_height())))
                if pixel_debajo[3] == 0: # Transparente
                    self.y += 2
            except: pass

    def dibujar(self, superficie, turno):
        superficie.blit(self.img, (self.x - 25, self.y))
        if turno: # Indicador de turno
            pygame.draw.polygon(superficie, (255, 255, 0), [(self.x, self.y-20), (self.x-10, self.y-35), (self.x+10, self.y-35)])

# --- Inicialización ---
terreno = generar_terreno_pixel()
t1 = Tanque(int(ANCHO * 0.15), img_tanque, True)
t2 = Tanque(int(ANCHO * 0.85), img_tanque, False)
# Posición inicial al suelo
for _ in range(ALTO_JUEGO): t1.caer(terreno); t2.caer(terreno)

proyectiles = []
turno_p1 = True
reloj = pygame.time.Clock()

def calcular_dano(px, py, tanque):
    dist = math.sqrt((px - tanque.x)**2 + (py - (tanque.y + 20))**2)
    if dist < 30: return 50
    if dist < 60: return 25
    return 0

# --- Bucle ---
ejecutando = True
while ejecutando:
    pantalla.fill(COLOR_CIELO)
    pantalla.blit(terreno, (0, 0))
    
    # Dibujar Panel de Controles
    pygame.draw.rect(pantalla, (200, 200, 200), (0, ALTO_JUEGO, ANCHO, 100))
    ctrls_p1 = "P1: A-D Mover | W-S Ángulo | Q-E Potencia | X Disparar"
    ctrls_p2 = "P2: J-L Mover | O-K Ángulo | I-P Potencia | M Disparar"
    pantalla.blit(fuente.render(ctrls_p1, True, (50,50,50)), (20, ALTO_JUEGO + 20))
    pantalla.blit(fuente.render(ctrls_p2, True, (50,50,50)), (20, ALTO_JUEGO + 60))

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: ejecutando = False
        if evento.type == pygame.KEYDOWN:
            if turno_p1 and evento.key == pygame.K_x:
                proyectiles.append(Proyectil(t1.x, t1.y + 10, t1.angulo, t1.potencia, True))
                turno_p1 = False
            elif not turno_p1 and evento.key == pygame.K_m:
                proyectiles.append(Proyectil(t2.x, t2.y + 10, t2.angulo, t2.potencia, False))
                turno_p1 = True

    teclas = pygame.key.get_pressed()
    if turno_p1:
        if teclas[pygame.K_a]: t1.x = max(25, t1.x - 2)
        if teclas[pygame.K_d]: t1.x = min(ANCHO-25, t1.x + 2)
        if teclas[pygame.K_w]: t1.angulo = min(90, t1.angulo + 1)
        if teclas[pygame.K_s]: t1.angulo = max(0, t1.angulo - 1)
        if teclas[pygame.K_q]: t1.potencia = max(10, t1.potencia - 1)
        if teclas[pygame.K_e]: t1.potencia = min(100, t1.potencia + 1)
    else:
        if teclas[pygame.K_j]: t2.x = max(25, t2.x - 2)
        if teclas[pygame.K_l]: t2.x = min(ANCHO-25, t2.x + 2)
        if teclas[pygame.K_o]: t2.angulo = min(90, t2.angulo + 1)
        if teclas[pygame.K_k]: t2.angulo = max(0, t2.angulo - 1)
        if teclas[pygame.K_i]: t2.potencia = max(10, t2.potencia - 1)
        if teclas[pygame.K_p]: t2.potencia = min(100, t2.potencia + 1)

    t1.caer(terreno); t2.caer(terreno)

    for p in proyectiles[:]:
        p.mover()
        # Colisión exacta con tanques
        hit_t1 = (t1.x-25 <= p.x <= t1.x+25) and (t1.y <= p.y <= t1.y+40)
        hit_t2 = (t2.x-25 <= p.x <= t2.x+25) and (t2.y <= p.y <= t2.y+40)
        
        if hit_t1 or hit_t2:
            pygame.draw.circle(terreno, (0,0,0,0), (int(p.x), int(p.y)), 40)
            t1.vida -= calcular_dano(p.x, p.y, t1)
            t2.vida -= calcular_dano(p.x, p.y, t2)
            proyectiles.remove(p)
        elif 0 <= int(p.x) < ANCHO and 0 <= int(p.y) < ALTO_JUEGO:
            if terreno.get_at((int(p.x), int(p.y)))[3] > 0:
                pygame.draw.circle(terreno, (0,0,0,0), (int(p.x), int(p.y)), 40)
                t1.vida -= calcular_dano(p.x, p.y, t1)
                t2.vida -= calcular_dano(p.x, p.y, t2)
                proyectiles.remove(p)
        elif p.y > ALTO_JUEGO: proyectiles.remove(p)

    t1.dibujar(pantalla, turno_p1)
    t2.dibujar(pantalla, not turno_p1)
    for p in proyectiles: p.dibujar(pantalla)
    
    # UI
    pantalla.blit(fuente.render(f"P1 Vida: {t1.vida}% | Ang: {t1.angulo} | Pot: {t1.potencia}", True, (0,0,0)), (10, 10))
    pantalla.blit(fuente.render(f"P2 Vida: {t2.vida}% | Ang: {t2.angulo} | Pot: {t2.potencia}", True, (0,0,0)), (ANCHO-300, 10))

    if t1.vida <= 0 or t2.vida <= 0:
        terreno = generar_terreno_pixel()
        t1.vida, t2.vida = 100, 100
        # Alternar posición inicial
    
    pygame.display.flip()
    reloj.tick(60)
pygame.quit()
