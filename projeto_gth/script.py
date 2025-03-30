import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

def redimensionar_imagem(imagem, largura=1200, altura=1200):
    return cv2.resize(imagem, (largura, altura))

def dilatacao(imagem, kernel_size=3):
    pad = kernel_size // 2
    imagem_padded = np.pad(imagem, pad, mode='constant', constant_values=0)
    output = np.zeros_like(imagem)
    for i in range(imagem.shape[0]):
        for j in range(imagem.shape[1]):
            regiao = imagem_padded[i:i+kernel_size, j:j+kernel_size]
            if np.any(regiao == 255):
                output[i, j] = 255
    return output

def erosao(imagem, kernel_size=3):
    pad = kernel_size // 2
    imagem_padded = np.pad(imagem, pad, mode='constant', constant_values=0)
    output = np.zeros_like(imagem)
    for i in range(imagem.shape[0]):
        for j in range(imagem.shape[1]):
            regiao = imagem_padded[i:i+kernel_size, j:j+kernel_size]
            if np.all(regiao == 255):
                output[i, j] = 255
    return output

def fechamento(imagem, kernel_size=3):
    erodida = erosao(imagem, kernel_size)
    dilatada = dilatacao(erodida, kernel_size)
    return dilatada

def processar_imagem(imagem_placa):
    imagem_cinza = cv2.cvtColor(imagem_placa, cv2.COLOR_BGR2GRAY)
    imagem_cinza = cv2.bilateralFilter(imagem_cinza, 9, 75, 75)

    imagem_limiarizada = cv2.adaptiveThreshold(
        imagem_cinza, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    imagem_morfologica = fechamento(imagem_limiarizada, kernel_size=3)
    return imagem_morfologica

def processar_contornos(imagem_original, imagem_processada):
    contornos, _ = cv2.findContours(
        imagem_processada, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    possiveis_placas = []

    for contorno in contornos:
        perimetro = cv2.arcLength(contorno, True)
        aprox = cv2.approxPolyDP(contorno, 0.02 * perimetro, True)
        area = cv2.contourArea(contorno)
        x, y, w, h = cv2.boundingRect(contorno)
        
        if h > w:
            continue
        if h < (w * 0.2):
            continue
        if area < 10000 or area > 70000:
            continue

        if 4 <= len(aprox) < 10:
            cv2.drawContours(imagem_original, [aprox], -1, (0, 255, 0), 2)
            imagem_recortada = imagem_original[y:y + h, x:x + w]
            possiveis_placas.append(imagem_recortada)

    return possiveis_placas

def exibir_resultado(imagem, imagem_recortada):
    fig = plt.figure(figsize=(10, 6))
    
    ax1 = plt.subplot2grid((2, 2), (0, 0))
    ax1.imshow(cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB))
    ax1.set_title("Imagem Original")
    
    ax1_2 = plt.subplot2grid((2, 2), (1, 0))
    ax1_2.imshow(cv2.cvtColor(imagem_recortada, cv2.COLOR_BGR2RGB))
    ax1_2.set_title("Imagem Recortada")
    
    plt.tight_layout()
    plt.show()

def detectar_placa(imagem_path):
    imagem_original = cv2.imread(imagem_path)
    if imagem_original is None:
        print("Erro: imagem não encontrada: ", imagem_path)
        return

    imagem_original = redimensionar_imagem(imagem_original)
    imagem_processada = processar_imagem(imagem_original)
    possiveis_placas = processar_contornos(imagem_original, imagem_processada)

    if not possiveis_placas:
        print("Nenhuma placa detectada.")
        return

    placa_recortada = possiveis_placas[0]
    exibir_resultado(imagem_original, placa_recortada)

if __name__ == "__main__":
    detectar_placa("../img/varias.jpg")
