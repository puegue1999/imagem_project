import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from skimage.color import rgb2gray
from skimage.filters import unsharp_mask, threshold_otsu
from skimage import exposure
from scipy.ndimage import binary_fill_holes, label
from scipy.ndimage import find_objects

def redimensionar_imagem(imagem, largura=1200, altura=1200):
    return imagem.resize((largura, altura), Image.Resampling.LANCZOS)

def processar_imagem(imagem_placa):
    imagem_cinza = rgb2gray(imagem_placa)
    imagem_contraste = exposure.equalize_hist(imagem_cinza)
    imagem_nitida = unsharp_mask(imagem_contraste, radius=1.5, amount=2.0)
    limiar = threshold_otsu(imagem_nitida)
    imagem_limiarizada = (imagem_nitida > limiar).astype(np.uint8) * 255

    return imagem_limiarizada

def processar_contornos(imagem_original, imagem_processada):
    labels, num_features = label(binary_fill_holes(imagem_processada))
    objetos = find_objects(labels)
    possiveis_placas = []
    imagem_array = np.array(imagem_original)
    
    for obj in objetos:
        if obj is None:
            continue
        
        y_slice, x_slice = obj
        h, w = y_slice.stop - y_slice.start, x_slice.stop - x_slice.start
        area = h * w

        if h > w or h < (w * 0.2) or area < 10000 or area > 70000:
            continue
        
        imagem_recortada = imagem_array[y_slice, x_slice]
        possiveis_placas.append(imagem_recortada)

    return possiveis_placas

def exibir_resultado(imagem, imagem_recortada):
    fig, axes = plt.subplots(1, 2, figsize=(10, 6))
    
    axes[0].imshow(imagem)
    axes[0].set_title("Imagem Original")
    axes[0].axis("off")
    
    axes[1].imshow(imagem_recortada, cmap='gray')
    axes[1].set_title("Imagem Recortada")
    axes[1].axis("off")
    
    plt.show()

def detectar_placa(imagem_path):
    imagem_original = Image.open(imagem_path).convert('RGB')
    imagem_original = redimensionar_imagem(imagem_original)
    
    imagem_processada = processar_imagem(imagem_original)

    possiveis_placas = processar_contornos(imagem_original, imagem_processada)
    
    if not possiveis_placas:
        print("Nenhuma placa detectada.")
        return
    
    placa_recortada = possiveis_placas[0]
    
    exibir_resultado(imagem_original, placa_recortada)

if __name__ == "__main__":
    detectar_placa("/home/rafael/Facul/Imagem/Prova 3/imagem_project/img/placa7.png")