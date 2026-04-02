import pygame
import math
import random

# --- Configuración Constante ---
ANCHO, ALTO = 1000, 700
ALTO_JUEGO = 600
COLOR_TERRENO = (34, 139, 34)
pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
reloj = pygame.time.Clock()

# --- Carga de Imágenes y Recortes (Usando tus medidas exactas) ---
img_maestra = pygame.image.load("tanque1.png").convert_alpha()

# Recorte de la Cabina/Torreta (centrada sobre la base): (x=240, y=0, ancho=460, alto=330)
img_cabina = img_maestra.subsurface((240, 0, 460, 330))
# Recorte de la Base/Cuerpo: (x=0, y=330, ancho=940, alto=290)
img_base = img_maestra.subsurface((0, 330, 940, 290))

# Escalamos para que quepan en el juego (manteniendo proporción)
img_base = pygame.transform.scale(img_base, (100, 30))
img_cabina = pygame.transform.scale(img_cabina, (50, 35))

class Tanque:
    def __init__(self, x, es_p1):
        self.x = x
        self.y = 0 # Se ajustará con caer()
        self.angulo = 45 if es_p1 else 135
        self.vida = 100
        self.potencia = 50
        self.es_p1 = es_p1
        self.esta_en_suelo = False

    def mover(self, dx, terreno_surf):
        nueva_x = self.x + dx
        
        # 1. Comprobamos límites de pantalla horizontal
        if nueva_x < 50 or nueva_x > ANCHO - 50:
            return

        # 2. Lógica de Escalada (Avanzar y Subir pendientes) 📈
        # Sensor para el movimiento horizontal
        sensor_x = int(nueva_x)
        # Sensor para la base del tanque (donde tocan las orugas)
        base_y = int(self.y + 15) # Punto medio vertical de la base escalada

        # Intentamos subir hasta 10 píxeles si hay tierra en la nueva X
        max_escalada = 10
        for dy in range(0, -max_escalada - 1, -1):
            test_y = base_y + dy
            try:
                # Si el píxel en la nueva X y la test_y es transparente, hay aire y podemos subir
                if terreno_surf.get_at((sensor_x, test_y))[3] == 0:
                    self.x = nueva_x
                    self.y = self.y + dy # El tanque sube
                    break
            except IndexError:
                pass

    def caer(self, terreno_surf):
        # Sensor para la base del tanque
        sensor_x = int(self.x)
        base_y = int(self.y + 15) # Punto de contacto con el suelo

        try:
            # Si el píxel justo debajo es aire, el tanque cae
            if terreno_surf.get_at((sensor_x, base_y + 2))[3] == 0:
                self.y += 3
                self.esta_en_suelo = False
            else:
                self.esta_en_suelo = True
        except IndexError:
            self.esta_en_suelo = True

    def dibujar(self, superficie):
        # 1. Ajuste de posición: La 'y' es el centro de la base
        pos_base_y = self.y
        pos_cabina_y = self.y - 18 # La cabina va 18px arriba de la base

        # 2. Capa 1: Dibujar Cañón (Detrás de la cabina) 📌
        # Pin central en la imagen escalada aprox (self.x, pos_cabina_y + 12)
        pin_x, pin_y = self.x, pos_cabina_y + 12
        largo = 40
        rad = math.radians(self.angulo)
        final_x = pin_x + largo * math.cos(rad)
        final_y = pin_y - largo * math.sin(rad)
        
        # Color del cañón diferente para P1 y P2
        color_canon = (50, 50, 50) if self.es_p1 else (100, 50, 50)
        pygame.draw.line(superficie, color_canon, (pin_x, pin_y), (final_x, final_y), 6)

        # 3. Capa 2: Dibujar Cabina (centrada y sobre el cañón)
        # Pin rojo 🔴 (230, 100) en original -> escalado (25, 12) aprox.
        # Ajustamos el blit para que el pin central (25px) coincida con self.x
        superficie.blit(img_cabina, (self.x - 25, pos_cabina_y))

        # 4. Capa 3: Dibujar Base (sobre todo) 🚜
        superficie.blit(img_base, (self.x - 50, pos_base_y - 15))


# --- Generación de Terreno (Superficie con Alpha) ---
terreno = pygame.Surface((ANCHO, ALTO_JUEGO), pygame.SRCALPHA)
# Dibujamos un terreno más interesante
pygame.draw.polygon(terreno, COLOR_TERRENO, [(0, 550), (150, 480), (300, 530), (450, 380), (600, 500), (750, 420), (900, 540), (1000, 500), (1000, 600), (0, 600)])

t1 = Tanque(200, True)
t2 = Tanque(800, False) # Tanque 2 en una posición diferente

# --- Bucle Principal ---
ejecutando = True
while ejecutando:
    pantalla.fill((135, 206, 235)) # Cielo
    pantalla.blit(terreno, (0, 0))
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: ejecutando = False

    # Controles Tanque 1 (P1)
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_a]: t1.mover(-2, terreno)
    if teclas[pygame.K_d]: t1.mover(2, terreno)
    if teclas[pygame.K_w]: t1.angulo = min(180, t1.angulo + 1)
    if teclas[pygame.K_s]: t1.angulo = max(0, t1.angulo - 1)

    # Controles Tanque 2 (P2)
    if teclas[pygame.K_j]: t2.mover(-2, terreno)
    if teclas[pygame.K_l]: t2.mover(2, terreno)
    if teclas[pygame.K_i]: t2.angulo = min(180, t2.angulo + 1)
    if teclas[pygame.K_k]: t2.angulo = max(0, t2.angulo - 1)

    # Física de Gravedad para AMBOS tanques
    for t in [t1, t2]:
        t.caer(terreno)
        t.dibujar(pantalla)

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
