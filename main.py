import pygame
import math
import random

# --- Configuración Inicial ---
ANCHO, ALTO = 1000, 600
COLOR_CIELO = (135, 206, 235)
COLOR_TERRENO = (34, 139, 34)
COLOR_TANQUE = (50, 50, 50)

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Guerra de Artillería - Prototipo")

def generar_terreno_pixel():
    """Crea una superficie con montañas aleatorias."""
    terreno = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    puntos = []
    
    # Generar alturas usando una onda simple para simular colinas
    off_set = random.randint(0, 1000)
    for x in range(0, ANCHO + 1):
        # Fórmula matemática para colinas suaves
        y = int(ALTO * 0.7 + math.sin(x * 0.01 + off_set) * 50 + math.sin(x * 0.005) * 30)
        puntos.append((x, y))
    
    # Dibujar el terreno
    puntos.extend([(ANCHO, ALTO), (0, ALTO)])
    pygame.draw.polygon(terreno, COLOR_TERRENO, puntos)
    return terreno

# --- Variables de Juego ---
superficie_terreno = generar_terreno_pixel()
reloj = pygame.time.Clock()
ejecutando = True

# --- Bucle Principal ---
while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
            
        # Simulación de disparo/explosión al hacer clic para probar el píxel a píxel
        if evento.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            # "Borramos" un círculo del terreno (el tamaño de un tanque aprox 25px)
            pygame.draw.circle(superficie_terreno, (0, 0, 0, 0), pos, 25)

    # Dibujo
    pantalla.fill(COLOR_CIELO)
    pantalla.blit(superficie_terreno, (0, 0))
    
    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
