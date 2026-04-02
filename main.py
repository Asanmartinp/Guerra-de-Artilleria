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

def generar_terreno_pixel():
    terreno = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    puntos = []
    off_set = random.randint(0, 1000)
    for x in range(0, ANCHO + 1):
        # Guardamos la altura en una variable para usarla después
        y = int(ALTO * 0.7 + math.sin(x * 0.01 + off_set) * 50 + math.sin(x * 0.005) * 30)
        puntos.append((x, y))
    puntos.extend([(ANCHO, ALTO), (0, ALTO)])
    pygame.draw.polygon(terreno, COLOR_TERRENO, puntos)
    return terreno, puntos # Devolvemos los puntos para saber la altura fácil

class Tanque:
    def __init__(self, x, color, puntos_terreno):
        self.x = x
        self.color = color
        self.vida = 100
        # Usamos los puntos generados para encontrar la Y exacta
        self.y = puntos_terreno[self.x][1]

    def dibujar(self, superficie):
        # Dibujamos el tanque un poco más grande para verlo bien
        # Cuerpo
        pygame.draw.rect(superficie, self.color, (self.x - 20, self.y - 20, 40, 20))
        # Cañón (mirando hacia arriba)
        pygame.draw.line(superficie, self.color, (self.x, self.y - 20), (self.x, self.y - 40), 5)

# --- Preparación del Juego ---
superficie_terreno, puntos_alturas = generar_terreno_pixel()

# Tanques en las posiciones que definiste (10% y 85%)
tanque1 = Tanque(int(ANCHO * 0.1), (50, 50, 50), puntos_alturas)
tanque2 = Tanque(int(ANCHO * 0.85), (200, 0, 0), puntos_alturas)

reloj = pygame.time.Clock()
ejecutando = True

while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

    pantalla.fill(COLOR_CIELO)
    pantalla.blit(superficie_terreno, (0, 0))
    
    # Dibujamos los tanques al final para que estén "encima" del suelo
    tanque1.dibujar(pantalla)
    tanque2.dibujar(pantalla)
    
    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
