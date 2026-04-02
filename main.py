import pygame
import math
import random

# --- Configuración ---
ANCHO, ALTO = 1000, 700
ALTO_JUEGO = 600
COLOR_TERRENO = (34, 139, 34)
pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
reloj = pygame.time.Clock()

# --- Carga de Imágenes y Recortes ---
img_maestra = pygame.image.load("tanque1.png").convert_alpha()

# Aplicando tus medidas exactas
# Torreta/Cabina: (x=240, y=0, ancho=460, alto=330)
img_cabina = img_maestra.subsurface((240, 0, 460, 330))
# Base/Cuerpo: (x=0, y=330, ancho=940, alto=290)
img_base = img_maestra.subsurface((0, 330, 940, 290))

# Escalamos para que quepan en el juego (manteniendo proporción)
img_base = pygame.transform.scale(img_base, (80, 25))
img_cabina = pygame.transform.scale(img_cabina, (40, 28))

class Tanque:
    def __init__(self, x, es_p1):
        self.x = x
        self.y = 0
        self.angulo = 45 if es_p1 else 135
        self.vida = 100
        self.potencia = 50
        self.es_p1 = es_p1

    def mover(self, dx, terreno_surf):
        nueva_x = self.x + dx
        # Lógica de Escalada 📈
        # Intentamos subir hasta 10 píxeles si hay tierra
        for dy in range(0, -11, -1):
            test_y = self.y + dy
            try:
                # Si el píxel en la base del tanque es transparente, puede estar ahí
                if terreno_surf.get_at((int(nueva_x), int(test_y + 25)))[3] == 0:
                    self.x = nueva_x
                    self.y = test_y
                    break
            except IndexError:
                pass

    def caer(self, terreno_surf):
        # Gravedad simple: cae si no hay tierra debajo
        try:
            if terreno_surf.get_at((int(self.x), int(self.y + 26)))[3] == 0:
                self.y += 2
        except IndexError:
            pass

    def dibujar(self, superficie):
        # 1. Dibujar Base
        superficie.blit(img_base, (self.x - 40, self.y))
        
        # 2. Dibujar Cabina (centrada sobre la base)
        # El pin central está a 230/460 (mitad) en la original
        superficie.blit(img_cabina, (self.x - 20, self.y - 20))
        
        # 3. Dibujar Cañón (Línea desde el Pin) 📌
        # Pin en la imagen escalada aprox: (self.x, self.y - 12)
        pin_x, pin_y = self.x, self.y - 8
        largo = 40
        rad = math.radians(self.angulo)
        final_x = pin_x + largo * math.cos(rad)
        final_y = pin_y - largo * math.sin(rad)
        
        pygame.draw.line(superficie, (50, 50, 50), (pin_x, pin_y), (final_x, final_y), 4)

# --- Generación de Terreno (Superficie con Alpha) ---
terreno = pygame.Surface((ANCHO, ALTO_JUEGO), pygame.SRCALPHA)
puntos = [(0, 500), (200, 450), (400, 520), (600, 400), (800, 480), (1000, 500), (1000, 600), (0, 600)]
pygame.draw.polygon(terreno, COLOR_TERRENO, puntos)

t1 = Tanque(200, True)
t2 = Tanque(800, False)

# --- Bucle Principal ---
ejecutando = True
while ejecutando:
    pantalla.fill((135, 206, 235)) # Cielo
    pantalla.blit(terreno, (0, 0))
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: ejecutando = False

    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_a]: t1.mover(-2, terreno)
    if teclas[pygame.K_d]: t1.mover(2, terreno)
    if teclas[pygame.K_w]: t1.angulo = min(180, t1.angulo + 1)
    if teclas[pygame.K_s]: t1.angulo = max(0, t1.angulo - 1)

    t1.caer(terreno)
    t1.dibujar(pantalla)
    t2.dibujar(pantalla)

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
