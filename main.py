import pygame
import math
import random

# --- Configuración Inicial ---
ANCHO, ALTO = 1000, 600
COLOR_CIELO = (135, 206, 235)
COLOR_TERRENO = (34, 139, 34)

# Inicializar Pygame
pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Guerra de Artillería - Controles Activos")
fuente = pygame.font.SysFont("Arial", 20)

# --- Funciones y Clases ---

def generar_terreno_pixel():
    """Crea la superficie del terreno y devuelve las alturas para posicionar."""
    terreno = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    puntos = []
    off_set = random.randint(0, 1000)
    alturas_suelo = [] # Guardaremos la Y exacta para cada X

    for x in range(0, ANCHO + 1):
        # Fórmula matemática para colinas suaves
        y = int(ALTO * 0.7 + math.sin(x * 0.01 + off_set) * 50 + math.sin(x * 0.005) * 30)
        puntos.append((x, y))
        alturas_suelo.append(y) # Guardamos la altura
        
    # Dibujar el terreno sólido
    puntos.extend([(ANCHO, ALTO), (0, ALTO)])
    pygame.draw.polygon(terreno, COLOR_TERRENO, puntos)
    return terreno, alturas_suelo

class Tanque:
    def __init__(self, x, color, es_jugador1):
        self.x = x
        self.color = color
        self.es_jugador1 = es_jugador1
        self.vida = 100
        self.angulo = 45 # Ángulo inicial (grados)
        self.potencia = 50 # Potencia inicial
        self.velocidad_mov = 2
        self.y = 0 # Se calculará en el bucle principal

    def actualizar_posicion(self, alturas_suelo):
        """Asegura que el tanque esté sobre el suelo en su coordenada X."""
        if 0 <= self.x < len(alturas_suelo):
            self.y = alturas_suelo[self.x] - 15 # Ajuste para que se vea sobre el suelo

    def dibujar(self, superficie):
        # Cuerpo del tanque (rectángulo)
        pygame.draw.rect(superficie, self.color, (self.x - 15, self.y, 30, 15))
        
        # Calcular extremo del cañón basado en ángulo y potencia
        rad = math.radians(self.angulo)
        # Si es jugador 2, el cañón debe apuntar a la izquierda inicialmente
        if not self.es_jugador1:
            rad = math.radians(180 - self.angulo)
            
        largo_canon = self.potencia / 2 # El largo del cañón visualmente representa la potencia
        canon_x = self.x + math.cos(rad) * largo_canon
        canon_y = self.y - math.sin(rad) * largo_canon
        
        # Dibujar cañón (línea)
        pygame.draw.line(superficie, self.color, (self.x, self.y), (canon_x, canon_y), 5)

# --- Preparación del Juego ---
superficie_terreno, lista_alturas = generar_terreno_pixel()

# Crear Tanques con tus reglas de posición (10% y 85%)
tanque1 = Tanque(int(ANCHO * 0.1), (50, 50, 50), True) # Gris (Jugador 1)
tanque2 = Tanque(int(ANCHO * 0.85), (200, 0, 0), False) # Rojo (Jugador 2)

reloj = pygame.time.Clock()
ejecutando = True

# --- Bucle Principal ---
while ejecutando:
    # 1. Manejo de Eventos (Cerrar ventana y clics para destruir)
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        
        # Mantenemos la destrucción por clic para probar
        if evento.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            # Borrar un círculo del terreno
            pygame.draw.circle(superficie_terreno, (0, 0, 0, 0), pos, 25)
            # ¡IMPORTANTE! Al destruir terreno, debemos actualizar la lista de alturas
            # (Simplificado: solo en el punto X del clic)
            if 0 <= pos[0] < ANCHO:
                 lista_alturas[pos[0]] = pos[1] # Esto es aproximado, pero sirve para probar

    # 2. Manejo de Controles (Teclas mantenidas)
    teclas = pygame.key.get_pressed()

    # --- Controles Jugador 1 (Gris) ---
    if teclas[pygame.K_a]: tanque1.x -= tanque1.velocidad_mov # Mover Izq
    if teclas[pygame.K_d]: tanque1.x += tanque1.velocidad_mov # Mover Der
    if teclas[pygame.K_w]: tanque1.angulo = min(90, tanque1.angulo + 1) # Subir Ángulo
    if teclas[pygame.K_s]: tanque1.angulo = max(0, tanque1.angulo - 1)  # Bajar Ángulo
    if teclas[pygame.K_q]: tanque1.potencia = max(10, tanque1.potencia - 1) # Bajar Potencia
    if teclas[pygame.K_e]: tanque1.potencia = min(100, tanque1.potencia + 1) # Subir Potencia
    # (Falta programar el disparo con X)

    # --- Controles Jugador 2 (Rojo) ---
    if teclas[pygame.K_j]: tanque2.x -= tanque2.velocidad_mov # Mover Izq
    if teclas[pygame.K_l]: tanque2.x += tanque2.velocidad_mov # Mover Der
    if teclas[pygame.K_o]: tanque2.angulo = min(90, tanque2.angulo + 1) # Subir Ángulo
    if teclas[pygame.K_k]: tanque2.angulo = max(0, tanque2.angulo - 1)  # Bajar Ángulo
    if teclas[pygame.K_i]: tanque2.potencia = max(10, tanque2.potencia - 1) # Bajar Potencia
    if teclas[pygame.K_p]: tanque2.potencia = min(100, tanque2.potencia + 1) # Subir Potencia
    # (Falta programar el disparo con M)

    # 3. Actualizar Estados (Asegurar tanques sobre el suelo)
    tanque1.actualizar_posicion(lista_alturas)
    tanque2.actualizar_posicion(lista_alturas)

    # 4. Dibujo
    pantalla.fill(COLOR_CIELO) # Fondo
    pantalla.blit(superficie_terreno, (0, 0)) # Terreno
    
    tanque1.dibujar(pantalla) # Jugador 1
    tanque2.dibujar(pantalla) # Jugador 2

    # Mostrar Info de HUD (Ángulo y Potencia)
    texto_p1 = fuente.render(f"P1 (Gris): Áng:{tanque1.angulo} Pot:{tanque1.potencia}", True, (0,0,0))
    texto_p2 = fuente.render(f"P2 (Rojo): Áng:{tanque2.angulo} Pot:{tanque2.potencia}", True, (0,0,0))
    pantalla.blit(texto_p1, (10, 10))
    pantalla.blit(texto_p2, (ANCHO - 250, 10))
    
    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
