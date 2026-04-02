import pygame

# --- Configuración Inicial ---
ANCHO, ALTO = 800, 600
pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Diagnóstico de Recortes de Tanque")

# --- Carga de Imagen ---
# Asegúrate de que 'tanque1.png' esté en la misma carpeta
try:
    img_maestra = pygame.image.load("tanque1.png").convert_alpha()
except:
    print("Error: No se encontró tanque1.png")
    pygame.quit()
    exit()

# --- Definición de Recortes (Según tus medidas) ---
# Torreta/Cabina: x=240, y=0, ancho=460, alto=330
recorte_cabina = (240, 0, 460, 330)
img_cabina = img_maestra.subsurface(recorte_cabina)

# Base/Cuerpo: x=0, y=330, ancho=940, alto=290
recorte_base = (0, 330, 940, 290)
img_base = img_maestra.subsurface(recorte_base)

# --- Colores de Diagnóstico (con transparencia) ---
# Usaremos superficies auxiliares para ver el área de recorte
debug_cabina = pygame.Surface((460, 330), pygame.SRCALPHA)
debug_cabina.fill((255, 0, 0, 80)) # Rojo transparente

debug_base = pygame.Surface((940, 290), pygame.SRCALPHA)
debug_base.fill((0, 0, 255, 80)) # Azul transparente

# --- Bucle de Visualización ---
corriendo = True
while corriendo:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False

    pantalla.fill((200, 200, 200)) # Fondo gris neutro

    # Dibujamos las piezas en el centro de la pantalla
    x_centro = 50
    y_centro = 50

    # Dibujamos la Base
    pantalla.blit(img_base, (x_centro, y_centro + 330))
    pantalla.blit(debug_base, (x_centro, y_centro + 330))

    # Dibujamos la Cabina centrada sobre la base
    pantalla.blit(img_cabina, (x_centro + 240, y_centro))
    pantalla.blit(debug_cabina, (x_centro + 240, y_centro))

    # Dibujamos el punto del Pin (570, 100 en la original)
    # En la pieza de la cabina es (230, 100)
    pygame.draw.circle(pantalla, (255, 255, 0), (x_centro + 240 + 230, y_centro + 100), 10)

    pygame.display.flip()

pygame.quit()
