from ultralytics import YOLO

#Carrega o modelo salvo
model = YOLO('ovos/runs/detect/train4/weights/best.pt')

# Realiza teste em uma única imagem
results = model('ovo.jpeg')

#mostra a caixa delimitadora com o resultado da classe e porcentagem
results[0].show()
results[0].save(filename='resultado.jpg')

#Percorre os resultados da teste, retornando uma lista de resultados
for result in results:
    # coordenadas das caixas delimitadoras x1,y1,x2,y2
    boxes = result.boxes.xyxy
    # confiança das detecções, ou seja, a pontuação de que realmente é um ovo
    scores = result.boxes.conf
    ## classe detectada
    classes = result.boxes.cls

    print("Caixas:", boxes)
    print("Confiança:", scores)
    print("Classes:", classes)
