# ==========================================
# PROYECTO: Artillería Pro - Destrucción Total
# VERSIÓN: 2.5 (Audio & FX)
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

# Colores
AZUL_P1, ROJO_P2 = (20, 60, 120), (180, 40, 40)
COLOR_CIELO, COLOR_TERRENO = (135, 206, 235), (34, 139, 34)
AMARILLO, NARANJA, BLANCO, NEGRO = (255, 255, 0), (255, 165, 0), (255, 255, 255), (0, 0, 0)

pygame.init()
pygame.mixer.init() # Inicializamos el mezclador de sonido 🔊
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption(f"Artillería Pro V 2.5 - Alfredo & Gemi")
fuente = pygame.font.SysFont("Arial", 20, bold=True)
fuente_grande = pygame.font.SysFont("Arial", 50, bold=True)
reloj = pygame.time.Clock()

# --- Carga de Sonidos ---
# Intentamos cargar los sonidos. Si no existen, el juego no se romperá.
try:
    snd_disparo = pygame.mixer.Sound("disparo.wav")
    snd_explosion = pygame.mixer.Sound("explosion.wav")
    snd_disparo.set_volume(0.5)
    snd_explosion.set_volume(0.8)
except:
    snd_disparo = None
    snd_explosion = None
    print("Aviso: No se encontraron archivos de audio. El juego continuará en silencio.")

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

class Explosion:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.radio = 3
        self.max_radio = 30
        self.activa = True
        if snd_explosion: snd_explosion.play() # ¡BUM! 💥

    def actualizar(self):
        self.radio += 2
        if self.radio >= self.max_radio: self.activa = False

    def dibujar(self, surf):
        radios = [self.radio, self.radio - 0.5, self.radio - 1.0]
        colores = [AMARILLO, NARANJA, AMARILLO]
        for r, col in zip(radios, colores):
            if r > 0: pygame.draw.circle(surf, col, (int(self.x), int(self.y)), int(r), 1)

def punto_en_torreta(px, py, vertices):
    n, dentro = len(vertices), False
    p1x, p1y = vertices[0]
    for i in range(n + 1):
        p2x, p2y = vertices[i % n]
        if py > min(p1y, p2y) and py <= max(p1y, p2y):
            if px <= max(p1x, p2x):
                if p1y != p2y:
                    xinters = (py - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                if p1x == p2x or px <= xinters: dentro = not dentro
        p1x, p1y = p2x, p2y
    return dentro

class Proyectil:
    def __init__(self, x, y, angulo, potencia, viento, color, dueno):
        self.x, self.y = x, y
        self.color, self.dueno = color, dueno
        rad = math.radians(angulo)
        v0 = potencia * 0.15
        self.vx, self.vy = v0 * math.cos(rad), -v0 * math.sin(rad)
        self.viento = viento
        if snd_disparo: snd_disparo.play() # ¡FUEGO! 🚀

    def actualizar(self):
        self.vx += self.viento * 0.005
        self.vy += GRAVEDAD
        self.x += self.vx
        self.y += self.vy

    def dibujar(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), 5)
        pygame.draw.circle(surf, NEGRO, (int(self.x), int(self.y)), 5, 1)

class Tanque:
    def __init__(self, x, color, es_p1):
        self.x, self.color, self.es_p1 = x, color, es_p1
        self.reiniciar()

    def reiniciar(self):
        self.vida, self.potencia = 100, 50
        self.angulo = 45 if self.es_p1 else 135
        self.y = 500 + math.sin(self.x * 0.01) * 30

    def obtener_poligono_torreta(self):
        return [(self.x - 18, self.y - 21), (self.x + 18, self.y - 21), (self.x + 9, self.y - 46), (self.x - 9, self.y - 46)]

    def obtener_rect_base(self): return pygame.Rect(self.x - 35, self.y - 21, 70, 21)

    def dibujar(self, surf):
        pygame.draw.rect(surf, self.color, (self.x - 35, self.y - 21, 70, 21), border_radius=10)
        pygame.draw.polygon(surf, self.color, self.obtener_poligono_torreta())
        rad = math.radians(self.angulo)
        px, py = self.x, self.y - 34
        pygame.draw.line(surf, self.color, (px, py), (px + 40*math.cos(rad), py - 40*math.sin(rad)), 6)

def dibujar_hud(t1, t2, viento, turno_p1):
    pygame.draw.rect(pantalla, (30, 30, 30), (0, 600, ANCHO, 100))
    c1, c2 = (BLANCO if turno_p1 else (120, 120, 120)), (BLANCO if not turno_p1 else (120, 120, 120))
    pygame.draw.rect(pantalla, (150, 0, 0), (20, 620, 200, 20))
    pygame.draw.rect(pantalla, (0, 200, 0), (20, 620, 2 * max(0, t1.vida), 20))
    pantalla.blit(fuente.render(f"P1: {t1.angulo}° | POT: {t1.potencia}", True, c1), (20, 650))
    pygame.draw.rect(pantalla, (150, 0, 0), (780, 620, 200, 20))
    pygame.draw.rect(pantalla, (0, 200, 0), (780, 620, 2 * max(0, t2.vida), 20))
    pantalla.blit(fuente.render(f"P2: {t2.angulo}° | POT: {t2.potencia}", True, c2), (780, 650))
    txt_v = f"VIENTO: {'>>' if viento > 0 else '<<'} {abs(viento):.2f}"
    pantalla.blit(fuente.render(txt_v, True, (0, 200, 255)), (440, 620))

t1, t2 = Tanque(200, AZUL_P1, True), Tanque(800, ROJO_P2, False)
inicializar_terreno()

def reset_game():
    global t1, t2, balas, explosiones, viento, turno_p1, game_over
    t1.reiniciar(); t2.reiniciar(); inicializar_terreno()
    balas, explosiones, viento, turno_p1, game_over = [], [], random.uniform(-1.5, 1.5), True, False

balas, explosiones, viento, turno_p1, game_over = [], [], random.uniform(-1.5, 1.5), True, False

while True:
    pantalla.fill(COLOR_CIELO)
    pantalla.blit(terreno_surf, (0, 0))
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: pygame.quit(); sys.exit()
        if game_over:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_s: reset_game()
                if evento.key == pygame.K_n: pygame.quit(); sys.exit()
        else:
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE and len(balas) == 0:
                t_act = t1 if turno_p1 else t2
                balas.append(Proyectil(t_act.x, t_act.y - 34, t_act.angulo, t_act.potencia, viento, t_act.color, t_act))
                turno_p1, viento = not turno_p1, random.uniform(-1.5, 1.5)

    if not game_over:
        keys = pygame.key.get_pressed()
        t_control = t1 if turno_p1 else t2
        if keys[pygame.K_LEFT]: t_control.angulo += 1
        if keys[pygame.K_RIGHT]: t_control.angulo -= 1
        if keys[pygame.K_UP]: t_control.potencia = min(100, t_control.potencia + 1)
        if keys[pygame.K_DOWN]: t_control.potencia = max(10, t_control.potencia - 1)
        for b in balas[:]:
            b.actualizar(); b.dibujar(pantalla)
            impacto = False
            for t_obj in [t1, t2]:
                if t_obj != b.dueno:
                    if t_obj.obtener_rect_base().collidepoint(b.x, b.y) or punto_en_torreta(b.x, b.y, t_obj.obtener_poligono_torreta()):
                        t_obj.vida -= 25; impacto = True
            if not impacto and 0 <= int(b.x) < ANCHO and 0 <= int(b.y) < ALTO:
                if terreno_surf.get_at((int(b.x), int(b.y)))[3] > 0: impacto = True
            if impacto:
                explosiones.append(Explosion(b.x, b.y))
                pygame.draw.circle(terreno_surf, (0, 0, 0, 0), (int(b.x), int(b.y)), 30)
                balas.remove(b)
            elif b.x < 0 or b.x > ANCHO or b.y > ALTO: balas.remove(b)
        if t1.vida <= 0 or t2.vida <= 0: game_over = True

    for exp in explosiones[:]:
        exp.actualizar(); exp.dibujar(pantalla)
        if not exp.activa: explosiones.remove(exp)

    t1.dibujar(pantalla); t2.dibujar(pantalla); dibujar_hud(t1, t2, viento, turno_p1)
    if game_over:
        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA); overlay.fill((0, 0, 0, 180)); pantalla.blit(overlay, (0,0))
        ganador = "AZUL" if t2.vida <= 0 else "ROJO"
        color_ganador = AZUL_P1 if t2.vida <= 0 else ROJO_P2
        pantalla.blit(fuente_grande.render("GAME OVER", True, BLANCO), (ANCHO//2 - 140, 250))
        pantalla.blit(fuente.render(f"GANADOR: TANQUE {ganador}", True, color_ganador), (ANCHO//2 - 110, 320))
        pantalla.blit(fuente.render("¿Otra partidita? (S/N)", True, BLANCO), (ANCHO//2 - 100, 380))

    pygame.display.flip(); reloj.tick(FPS)
