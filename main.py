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

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Artillería Pro - Duelo Geométrico")
fuente = pygame.font.SysFont("Arial", 18, bold=True)
fuente_grande = pygame.font.SysFont("Arial", 36, bold=True)
reloj = pygame.time.Clock()

class Proyectil:
    def __init__(self, x, y, angulo, potencia, viento, color):
        self.x, self.y = x, y
        self.color = color
        rad = math.radians(angulo)
        v0 = potencia * 0.2 # Ajuste de fuerza
        self.vx = v0 * math.cos(rad)
        self.vy = -v0 * math.sin(rad)
        self.viento = viento

    def actualizar(self):
        self.vx += self.viento * 0.005 
        self.vy += GRAVEDAD           
        self.x += self.vx
        self.y += self.vy

    def dibujar(self, superficie):
        pygame.draw.circle(superficie, self.color, (int(self.x), int(self.y)), 6)
        pygame.draw.circle(superficie, (0, 0, 0), (int(self.x), int(self.y)), 6, 1)

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
        # 1. Base redondeada (940x290 escala)
        rect_base = pygame.Rect(self.x - 50, self.y - 15, 100, 30)
        pygame.draw.rect(superficie, self.color, rect_base, border_radius=15)

        # 2. Torreta (Cono Truncado: Base 460, Tope 230, Alto 330 escala)
        puntos_torreta = [
            (self.x - 25, self.y - 15), 
            (self.x + 25, self.y - 15), 
            (self.x + 12, self.y - 50), 
            (self.x - 12, self.y - 50)  
        ]
        pygame.draw.polygon(superficie, self.color, puntos_torreta)

        # 3. Cañón (Mismo color que el tanque)
        pin_x, pin_y = self.x, self.y - 32
        largo = 55
        rad = math.radians(self.angulo)
        dest_x = pin_x + largo * math.cos(rad)
        dest_y = pin_y - largo * math.sin(rad)
        pygame.draw.line(superficie, self.color, (pin_x, pin_y), (dest_x, dest_y), 8)

def dibujar_hud(t1, t2, viento, turno_p1):
    # Panel inferior
    pygame.draw.rect(pantalla, (30, 30, 30), (0, 600, ANCHO, 100))
    
    # Textos de estado
    col_t1 = (255, 255, 255) if turno_p1 else (100, 100, 100)
    col_t2 = (255, 255, 255) if not turno_p1 else (100, 100, 100)
    
    # Jugador 1
    pygame.draw.rect(pantalla, AZUL_P1, (20, 615, 200, 20))
    pygame.draw.rect(pantalla, (0, 255, 0), (20, 615, 2 * t1.vida, 20))
    pantalla.blit(fuente.render(f"P1 - POT: {t1.potencia}  ANG: {t1.angulo}°", True, col_t1), (20, 645))
    
    # Jugador 2
    pygame.draw.rect(pantalla, ROJO_P2, (780, 615, 200, 20))
    pygame.draw.rect(pantalla, (0, 255, 0), (780, 615, 2 * t2.vida, 20))
    pantalla.blit(fuente.render(f"P2 - POT: {t2.potencia}  ANG: {t2.angulo}°", True, col_t2), (780, 645))

    # Viento e Instrucciones
    dir_v = ">>" if viento > 0 else "<<"
    pantalla.blit(fuente.render(f"VIENTO: {dir_v} {abs(viento):.2f}", True, (0, 200, 255)), (440, 620))
    pantalla.blit(fuente.render("ESPACIO: Disparar | FLECHAS: Ajustar", True, (200, 200, 200)), (380, 660))

# --- Inicio del Juego ---
t1 = Tanque(150, AZUL_P1, True)
t2 = Tanque(850, ROJO_P2, False)
viento = random.uniform(-1.5, 1.5)
balas = []
turno_p1 = True
corriendo = True

while corriendo:
    pantalla.fill(COLOR_CIELO)
    # Dibujar Terreno plano
    pygame.draw.rect(pantalla, COLOR_TERRENO, (0, 500, ANCHO, 100))
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: corriendo = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE and not balas:
                t = t1 if turno_p1 else t2
                balas.append(Proyectil(t.x, t.y - 32, t.angulo, t.potencia, viento, t.color))
                turno_p1 = not turno_p1
                viento = random.uniform(-1.5, 1.5)

    # Controles de ángulo y potencia
    keys = pygame.key.get_pressed()
    actual = t1 if turno_p1 else t2
    if keys[pygame.K_LEFT]: actual.angulo += 1
    if keys[pygame.K_RIGHT]: actual.angulo -= 1
    if keys[pygame.K_UP]: actual.potencia = min(100, actual.potencia + 1)
    if keys[pygame.K_DOWN]: actual.potencia = max(10, actual.potencia - 1)

    # Lógica de Proyectiles
    for b in balas[:]:
        b.actualizar()
        b.dibujar(pantalla)
        if b.y > 500: # Impacto contra el suelo
            for t in [t1, t2]:
                distancia = abs(b.x - t.x)
                if distancia < 60: t.vida -= 25
            balas.remove(b)
        elif b.x < 0 or b.x > ANCHO:
            balas.remove(b)

    t1.dibujar(pantalla)
    t2.dibujar(pantalla)
    dibujar_hud(t1, t2, viento, turno_p1)

    # Fin del juego
    if t1.vida <= 0 or t2.vida <= 0:
        ganador = "JUGADOR 2" if t1.vida <= 0 else "JUGADOR 1"
        pantalla.blit(fuente_grande.render(f"¡GANÓ EL {ganador}!", True, (0,0,0)), (350, 250))
        pygame.display.flip()
        pygame.time.delay(3000)
        corriendo = False

    pygame.display.flip()
    reloj.tick(FPS)

pygame.quit()
