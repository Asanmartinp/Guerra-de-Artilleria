import pygame
import math
import random

# --- Configuración Constante ---
ANCHO, ALTO = 1000, 700
ALTO_JUEGO = 600
COLOR_CIELO = (135, 206, 235)
COLOR_TERRENO = (34, 139, 34)
GRAVEDAD = 0.25

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Guerra de Artillería Pro - Versión Final")
fuente = pygame.font.SysFont("Arial", 16, bold=True)

# --- Carga y Procesamiento de Imágenes ---
try:
    img_maestra = pygame.image.load("tanque1.png").convert_alpha()
    # Recortes basados en tus medidas (940x620 total)
    # Cañón: parte superior (0 a 330px)
    img_canon_base = img_maestra.subsurface((0, 0, 940, 330))
    # Cuerpo: parte inferior (330 a 620px)
    img_cuerpo_base = img_maestra.subsurface((0, 330, 940, 290))
    
    # Escalado para que quepan bien en el juego (aprox 60px de ancho)
    img_cuerpo = pygame.transform.scale(img_cuerpo_base, (60, 20))
    img_canon = pygame.transform.scale(img_canon_base, (60, 25))
except:
    # Fail-safe por si la imagen no carga
    img_cuerpo = pygame.Surface((60, 20), pygame.SRCALPHA)
    pygame.draw.rect(img_cuerpo, (34, 139, 34), (0, 0, 60, 20))
    img_canon = pygame.Surface((60, 25), pygame.SRCALPHA)
    pygame.draw.rect(img_canon, (0, 100, 0), (10, 10, 40, 10))

# --- Funciones Auxiliares ---
def generar_terreno():
    terreno = pygame.Surface((ANCHO, ALTO_JUEGO), pygame.SRCALPHA)
    alturas = []
    offset = random.randint(0, 1000)
    for x in range(ANCHO + 1):
        y = int(ALTO_JUEGO * 0.7 + math.sin(x * 0.01 + offset) * 50 + math.sin(x * 0.005) * 30)
        alturas.append(y)
    puntos = [(x, y) for x, y in enumerate(alturas)]
    puntos.extend([(ANCHO, ALTO_JUEGO), (0, ALTO_JUEGO)])
    pygame.draw.polygon(terreno, COLOR_TERRENO, puntos)
    return terreno

def rotar_pivote(superficie, angulo, pivote, posicion_en_pantalla):
    # Función Pro para rotar sobre el "alfiler"
    imagen_rotada = pygame.transform.rotate(superficie, angulo)
    centro_rect = superficie.get_rect(topleft=(posicion_en_pantalla[0] - pivote[0], posicion_en_pantalla[1] - pivote[1]))
    nuevo_rect = imagen_rotada.get_rect(center=centro_rect.center)
    return imagen_rotada, nuevo_rect

# --- Clases ---
class Proyectil:
    def __init__(self, x, y, angulo, potencia, viento, es_p1):
        self.x, self.y = x, y
        rad = math.radians(angulo) if es_p1 else math.radians(180 - angulo)
        self.vx = math.cos(rad) * (potencia / 4)
        self.vy = -math.sin(rad) * (potencia / 4)
        self.viento = viento

    def mover(self):
        self.vx += self.viento * 0.01 # Efecto del viento
        self.vy += GRAVEDAD
        self.x += self.vx
        self.y += self.vy

    def dibujar(self, superficie):
        pygame.draw.circle(superficie, (0, 0, 0), (int(self.x), int(self.y)), 4)

class Tanque:
    def __init__(self, x, cuerpo, canon, es_p1):
        self.x = x
        self.y = 0
        self.es_p1 = es_p1
        self.vida = 100
        self.potencia = 50
        self.angulo = 45 if es_p1 else 35
        
        # Preparar imágenes con tinte para P2
        self.img_cuerpo = cuerpo.copy()
        self.img_canon = canon.copy()
        if not es_p1:
            self.img_cuerpo.fill((255, 50, 50), special_flags=pygame.BLEND_RGB_MULT)
            self.img_canon.fill((255, 50, 50), special_flags=pygame.BLEND_RGB_MULT)
            self.img_cuerpo = pygame.transform.flip(self.img_cuerpo, True, False)
            self.img_canon = pygame.transform.flip(self.img_canon, True, False)

    def caer(self, terreno_surf):
        if self.y + 20 < ALTO_JUEGO:
            try:
                if terreno_surf.get_at((int(self.x), int(self.y + 20)))[3] == 0:
                    self.y += 2
            except: pass

    def dibujar(self, superficie):
        # Dibujar cuerpo
        superficie.blit(self.img_cuerpo, (self.x - 30, self.y))
        
        # Rotar y dibujar cañón (pivote en el centro de la pieza)
        pivote = (30, 12) 
        pos_pivote = (self.x, self.y + 5)
        
        # Ajuste de ángulo para P2 (espejado)
        ang_final = self.angulo if self.es_p1 else -self.angulo
        img_rot, rect_rot = rotar_pivote(self.img_canon, ang_final, pivote, pos_pivote)
        superficie.blit(img_rot, rect_rot)

# --- Juego ---
terreno = generar_terreno()
viento = random.uniform(-2, 2)
t1 = Tanque(150, img_cuerpo, img_canon, True)
t2 = Tanque(850, img_cuerpo, img_canon, False)
proyectiles = []
turno_p1 = True

ejecutando = True
reloj = pygame.time.Clock()

while ejecutando:
    pantalla.fill(COLOR_CIELO)
    pantalla.blit(terreno, (0, 0))
    
    # --- Interfaz de Usuario (Panel Inferior) ---
    pygame.draw.rect(pantalla, (50, 50, 50), (0, ALTO_JUEGO, ANCHO, 100))
    
    # Función para dibujar barras
    def dibujar_barras(x, y, vida, potencia, nombre):
        # Vida (Verde)
        pygame.draw.rect(pantalla, (100, 0, 0), (x, y, 150, 15))
        pygame.draw.rect(pantalla, (0, 255, 0), (x, y, 1.5 * vida, 15))
        # Potencia (Azul)
        pygame.draw.rect(pantalla, (0, 0, 100), (x, y + 20, 150, 15))
        pygame.draw.rect(pantalla, (0, 200, 255), (x, y + 20, 1.5 * potencia, 15))
        pantalla.blit(fuente.render(f"{nombre} - Vida: {int(vida)}% Pot: {int(potencia)}%", True, (255,255,255)), (x, y - 20))

    dibujar_barras(50, 640, t1.vida, t1.potencia, "P1 (VERDE)")
    dibujar_barras(750, 640, t2.vida, t2.potencia, "P2 (ROJO)")
    
    # Indicador de Viento (Flecha)
    centro_x = ANCHO // 2
    pygame.draw.line(pantalla, (0,0,0), (centro_x - 50, 30), (centro_x + 50, 30), 2)
    punta = centro_x + (50 if viento > 0 else -50)
    pygame.draw.polygon(pantalla, (0,0,0), [(punta, 25), (punta, 35), (punta + (10 if viento > 0 else -10), 30)])
    pantalla.blit(fuente.render(f"VIENTO: {abs(viento):.1f}", True, (0,0,0)), (centro_x - 40, 45))

    # --- Controles y Lógica ---
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: ejecutando = False
        if evento.type == pygame.KEYDOWN:
            if turno_p1 and evento.key == pygame.K_x:
                proyectiles.append(Proyectil(t1.x, t1.y, t1.angulo, t1.potencia, viento, True))
                turno_p1 = False
            elif not turno_p1 and evento.key == pygame.K_m:
                proyectiles.append(Proyectil(t2.x, t2.y, t2.angulo, t2.potencia, viento, False))
                turno_p1 = True
                viento = random.uniform(-2, 2) # Cambia el viento tras cada turno completo

    teclas = pygame.key.get_pressed()
    if turno_p1:
        if teclas[pygame.K_a]: t1.x -= 2
        if teclas[pygame.K_d]: t1.x += 2
        if teclas[pygame.K_w]: t1.angulo = min(90, t1.angulo + 1)
        if teclas[pygame.K_s]: t1.angulo = max(0, t1.angulo - 1)
        if teclas[pygame.K_q]: t1.potencia = max(10, t1.potencia - 1)
        if teclas[pygame.K_e]: t1.potencia = min(100, t1.potencia + 1)
    else:
        if teclas[pygame.K_j]: t2.x -= 2
        if teclas[pygame.K_l]: t2.x += 2
        if teclas[pygame.K_o]: t2.angulo = min(90, t2.angulo + 1)
        if teclas[pygame.K_k]: t2.angulo = max(0, t2.angulo - 1)
        if teclas[pygame.K_i]: t2.potencia = max(10, t2.potencia - 1)
        if teclas[pygame.K_p]: t2.potencia = min(100, t2.potencia + 1)

    t1.caer(terreno); t2.caer(terreno)
    
    for p in proyectiles[:]:
        p.mover()
        p.dibujar(pantalla)
        if 0 <= int(p.x) < ANCHO and 0 <= int(p.y) < ALTO_JUEGO:
            if terreno.get_at((int(p.x), int(p.y)))[3] > 0:
                pygame.draw.circle(terreno, (0,0,0,0), (int(p.x), int(p.y)), 35)
                # Dano por cercanía
                for t in [t1, t2]:
                    dist = math.sqrt((p.x - t.x)**2 + (p.y - t.y)**2)
                    if dist < 40: t.vida -= 40
                    elif dist < 70: t.vida -= 15
                proyectiles.remove(p)
        elif p.y > ALTO_JUEGO or p.x < 0 or p.x > ANCHO:
            proyectiles.remove(p)

    t1.dibujar(pantalla)
    t2.dibujar(pantalla)

    if t1.vida <= 0 or t2.vida <= 0:
        terreno = generar_terreno()
        t1.vida, t2.vida = 100, 100
        t1.x, t2.x = 150, 850

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
