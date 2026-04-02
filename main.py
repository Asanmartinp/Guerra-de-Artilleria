import pygame
import math
import random

# --- Configuración Inicial ---
ANCHO, ALTO = 1000, 600
COLOR_CIELO = (135, 206, 235)
COLOR_TERRENO = (34, 139, 34)

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Guerra de Artillería")

# --- Funciones y Clases ---

def generar_terreno_pixel():
    """Crea la superficie del terreno con colinas."""
    terreno = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    puntos = []
    off_set = random.randint(0, 1000)
    for x in range(0, ANCHO + 1):
        y = int(ALTO * 0.7 + math.sin(x * 0.01 + off_set) * 50 + math.sin(x * 0.005) * 30)
        puntos.append((x, y))
    puntos.extend([(ANCHO, ALTO), (0, ALTO)])
    pygame.draw.polygon(terreno, COLOR_TERRENO, puntos)
    return terreno

class Tanque:
    def __init__(self, x, color, superficie_terreno):
        self.x = x
        self.color = color
        self.vida = 100
        # Buscamos la altura inicial para que no flote
        self.y = self.encontrar_suelo(superficie_terreno)

    def encontrar_suelo(self, superficie):
        """Escanea de arriba a abajo hasta tocar un píxel del terreno."""
        for y in range(ALTO):
            if superficie.get_at((self.x, y))[3] > 0: # Si el píxel no es transparente
                return y
        return ALTO

    def dibujar(self, superficie):
        # Cuerpo del tanque (un rectángulo pequeño)
        pygame.draw.rect(superficie, self.color, (self.x - 15, self.y - 15, 30, 15))
        # Torreta (un cuadrado pequeño encima)
        pygame.draw.rect(superficie, self.color, (self.x - 5, self.y - 25, 10, 10))

# --- Preparación del Juego ---
superficie_terreno = generar_terreno_pixel()

# Aplicamos tu regla: Jugador 1 al 10% y Jugador 2 al 85% (separación > 70%)
tanque1 = Tanque(int(ANCHO * 0.1), (50, 50, 50), superficie_terreno)
tanque2 = Tanque(int(ANCHO * 0.85), (80, 20, 20), superficie_terreno)

reloj = pygame.time.Clock()
ejecutando = True

# --- Bucle Principal ---
while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

    # 1. Dibujar el fondo
    pantalla.fill(COLOR_CIELO)
    
    # 2. Dibujar el terreno
    pantalla.blit(superficie_terreno, (0, 0))
    
    # 3. Dibujar los tanques
    tanque1.dibujar(pantalla)
    tanque2.dibujar(pantalla)
    
    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
