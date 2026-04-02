import pygame
import math
import random

# --- Configuración ---
ANCHO, ALTO = 1000, 700
ALTO_JUEGO = 600
GRAVEDAD = 0.25 # 1g simulado para la escala del juego
FPS = 60

# Colores Paleta 2
AZUL_P1 = (20, 60, 120)
ROJO_P2 = (180, 40, 40)
COLOR_CIELO = (135, 206, 235)
COLOR_TERRENO = (34, 139, 34)

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Artillería Geométrica - Pro")
fuente = pygame.font.SysFont("Arial", 18, bold=True)
reloj = pygame.time.Clock()

class Proyectil:
    def __init__(self, x, y, angulo, potencia, viento):
        self.x, self.y = x, y
        rad = math.radians(angulo)
        # Convertimos potencia a velocidad inicial
        v0 = potencia * 0.15
        self.vx = v0 * math.cos(rad)
        self.vy = -v0 * math.sin(rad)
        self.viento = viento

    def actualizar(self):
        self.vx += self.viento * 0.005 # El viento afecta la horizontal
        self.vy += GRAVEDAD           # La gravedad constante afecta la vertical
        self.x += self.vx
        self.y += self.vy

    def dibujar(self, superficie):
        pygame.draw.circle(superficie, (0, 0, 0), (int(self.x), int(self.y)), 5)

class Tanque:
    def __init__(self, x, color, es_p1):
        self.x = x
        self.y = 500
        self.color = color
        self.es_p1 = es_p1
        self.vida = 100
        self.potencia = 50
        self.angulo = 45 if es_p1 else 135

    def dibujar(self, superficie):
        # 1. Dibujar Base (940x290 escalado a 100x30 para pantalla)
        rect_base = pygame.Rect(self.x - 50, self.y - 15, 100, 30)
        pygame.draw.rect(superficie, self.color, rect_base, border_radius=15)

        # 2. Dibujar Torreta (Cono Truncado)
        # Base 460->50, Tope 230->25, Alto 330->35
        puntos = [
            (self.x - 25, self.y - 15), # Base izq
            (self.x + 25, self.y - 15), # Base der
            (self.x + 12, self.y - 50), # Tope der
            (self.x - 12, self.y - 50)  # Tope izq
        ]
        pygame.draw.polygon(superficie, self.color, puntos)

        # 3. Dibujar Cañón (Desde el Pin Central 230,290 -> aprox centro torreta)
        pin_x, pin_y = self.x, self.y - 32
        largo = 50
        rad = math.radians(self.angulo)
        dest_x = pin_x + largo * math.cos(rad)
        dest_y = pin_y - largo * math.sin(rad)
        pygame.draw.line(superficie, (30, 30, 30), (pin_x, pin_y), (dest_x, dest_y), 6)

def dibujar_interfaz(t1, t2, viento, turno_p1):
    # Fondo panel
    pygame.draw.rect(pantalla, (50, 50, 50), (0, 600, ANCHO, 100))
    
    # Indicadores P1 (Izquierda)
    color_p1 = (0, 255, 0) if turno_p1 else (100, 100, 100)
    pantalla.blit(fuente.render(f"P1 - VIDA: {int(t1.vida)}%", True, color_p1), (20, 620))
    pantalla.blit(fuente.render(f"ANG: {t1.angulo}° POT: {t1.potencia}", True, (255, 255, 255)), (20, 650))
    
    # Indicadores P2 (Derecha)
    color_p2 = (0, 255, 0) if not turno_p1 else (100, 100, 100)
    pantalla.blit(fuente.render(f"P2 - VIDA: {int(t2.vida)}%", True, color_p2), (800, 620))
    pantalla.blit(fuente.render(f"ANG: {t2.angulo}° POT: {t2.potencia}", True, (255, 255, 255)), (800, 650))

    # Viento (Centro)
    dir_v = "-->" if viento > 0 else "<--"
    pantalla.blit(fuente.render(f"VIENTO: {dir_v} {abs(viento):.2f}", True, (0, 200, 255)), (420, 635))

# --- Instancias y Terreno ---
t1 = Tanque(150, AZUL_P1, True)
t2 = Tanque(850, ROJO_P2, False)
viento = random.uniform(-1, 1)
balas = []
turno_p1 = True
corriendo = True

while corriendo:
    pantalla.fill(COLOR_CIELO)
    pygame.draw.rect(pantalla, COLOR_TERRENO, (0, 500, ANCHO, 100)) # Suelo plano para prueba
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: corriendo = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                t = t1 if turno_p1 else t2
                balas.append(Proyectil(t.x, t.y - 32, t.angulo, t.potencia, viento))
                turno_p1 = not turno_p1
                viento = random.uniform(-1, 1)

    # Controles
    keys = pygame.key.get_pressed()
    curr = t1 if turno_p1 else t2
    if keys[pygame.K_LEFT]: curr.angulo += 1
    if keys[pygame.K_RIGHT]: curr.angulo -= 1
    if keys[pygame.K_UP]: curr.potencia = min(100, curr.potencia + 1)
    if keys[pygame.K_DOWN]: curr.potencia = max(10, curr.potencia - 1)

    # Actualizar Balas
    for b in balas[:]:
        b.actualizar()
        b.dibujar(pantalla)
        # Colisión suelo
        if b.y > 500:
            # Daño simple por cercanía
            for t in [t1, t2]:
                dist = abs(b.x - t.x)
                if dist < 50: t.vida -= 20
            balas.remove(b)
        elif b.x < 0 or b.x > ANCHO:
            balas.remove(b)

    t1.dibujar(pantalla)
    t2.dibujar(pantalla)
    dibujar_interfaz(t1, t2, viento, turno_p1)

    pygame.display.flip()
    reloj.tick(FPS)

pygame.quit()
