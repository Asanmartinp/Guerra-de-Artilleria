import pygame
import math
import random

# --- Configuración General ---
ANCHO, ALTO = 1000, 700
ALTO_JUEGO = 600
GRAVEDAD = 0.25 
FPS = 60

# Colores Paleta 2
AZUL_P1 = (20, 60, 120)
ROJO_P2 = (180, 40, 40)
COLOR_CIELO = (135, 206, 235)
COLOR_TERRENO = (34, 139, 34)

# --- Configuración de Terreno ---
ALTURA_SUELO_BASE = 500
AMPLITUD_COLINA = 30
FRECUENCIA_COLINA = 0.01

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Artillería Pro - Colinas Suaves")
fuente = pygame.font.SysFont("Arial", 18, bold=True)
fuente_grande = pygame.font.SysFont("Arial", 36, bold=True)
reloj = pygame.time.Clock()

# --- Funciones de Terreno ---
def generar_terreno():
    puntos = []
    for x in range(ANCHO + 1):
        # Fórmula sinoidal: y = base + sin(x * freq) * amp
        y = ALTURA_SUELO_BASE + math.sin(x * FRECUENCIA_COLINA) * AMPLITUD_COLINA
        puntos.append((x, y))
    # Cerrar el polígono por abajo para dibujarlo
    puntos.append((ANCHO, ALTO))
    puntos.append((0, ALTO))
    return puntos

def obtener_altura_suelo(x):
    # Devuelve la altura 'y' del terreno para una 'x' dada
    return ALTURA_SUELO_BASE + math.sin(x * FRECUENCIA_COLINA) * AMPLITUD_COLINA

# Generar puntos del terreno una vez
puntos_terreno = generar_terreno()

class Proyectil:
    def __init__(self, x, y, angulo, potencia, viento, color):
        self.x, self.y = x, y
        self.color = color
        rad = math.radians(angulo)
        # Fuerza ajustada para tanques más pequeños (30% menos que antes)
        v0 = potencia * 0.14
        self.vx = v0 * math.cos(rad)
        self.vy = -v0 * math.sin(rad)
        self.viento = viento

    def actualizar(self):
        self.vx += self.viento * 0.005 
        self.vy += GRAVEDAD           
        self.x += self.vx
        self.y += self.vy

    def dibujar(self, superficie):
        # Bala más pequeña proporcionalmente
        pygame.draw.circle(superficie, self.color, (int(self.x), int(self.y)), 4)
        pygame.draw.circle(superficie, (0, 0, 0), (int(self.x), int(self.y)), 4, 1)

class Tanque:
    def __init__(self, x, color, es_p1):
        self.x = x
        # Obtener altura real del suelo para posicionar
        self.y = obtener_altura_suelo(x)
        self.color = color
        self.es_p1 = es_p1
        self.vida = 100
        self.potencia = 50
        self.angulo = 45 if es_p1 else 135

    def dibujar(self, superficie):
        # --- NUEVA ESCALA: 30% MÁS PEQUEÑO ---
        
        # 1. Base redondeada (658x203 escala real, visualmente 70x21 px)
        anch_base = int(100 * 0.7)
        alt_base = int(30 * 0.7)
        rad_base = int(15 * 0.7)
        rect_base = pygame.Rect(self.x - anch_base//2, self.y - alt_base, anch_base, alt_base)
        pygame.draw.rect(superficie, self.color, rect_base, border_radius=rad_base)

        # 2. Torreta (Cono Truncado: visualmente 35x25 px de alto)
        # Base 322->35, Tope 161->18, Alto 231->25 (aprox)
        puntos_torreta = [
            (self.x - 18, self.y - alt_base), 
            (self.x + 18, self.y - alt_base), 
            (self.x + 9, self.y - alt_base - 25), 
            (self.x - 9, self.y - alt_base - 25)  
        ]
        pygame.draw.polygon(superficie, self.color, puntos_torreta)

        # 3. Cañón (Desde el Pin Central 161,203 -> aprox centro torreta)
        pin_x, pin_y = self.x, self.y - alt_base - 13
        largo = 38 # Largo ajustado
        rad = math.radians(self.angulo)
        dest_x = pin_x + largo * math.cos(rad)
        dest_y = pin_y - largo * math.sin(rad)
        pygame.draw.line(superficie, self.color
