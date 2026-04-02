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
        pygame.draw.line(superficie, self.color, (pin_x, pin_y), (dest_x, dest_y), 6)

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
# Posicionar tanques en diferentes alturas del terreno
t1 = Tanque(200, AZUL_P1, True)
t2 = Tanque(800, ROJO_P2, False)
viento = random.uniform(-1.5, 1.5)
balas = []
turno_p1 = True
corriendo = True

while corriendo:
    pantalla.fill(COLOR_CIELO)
    # Dibujar Terreno sinoidal
    pygame.draw.polygon(pantalla, COLOR_TERRENO, puntos_terreno)
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: corriendo = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE and not balas:
                t = t1 if turno_p1 else t2
                # Ajuste de Y para el disparo (sale de la torreta)
                balas.append(Proyectil(t.x, t.y - 34, t.angulo, t.potencia, viento, t.color))
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
        
        # Colisión precisa con el terreno sinoidal
        if 0 <= b.x < ANCHO:
            altura_suelo_impacto = obtener_altura_suelo(b.x)
            if b.y > altura_suelo_impacto:
                for t in [t1, t2]:
                    distancia = math.sqrt((b.x - t.x)**2 + (b.y - t.y)**2)
                    if distancia < 50: t.vida -= 25 # Radio de daño ajustado
                balas.remove(b)
        elif b.y > ALTO_JUEGO or b.x < 0 or b.x > ANCHO:
            # Eliminar si sale por los lados o abajo
            if b in balas:
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
