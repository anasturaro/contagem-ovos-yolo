from ultralytics import YOLO
import cv2

#Carrega o modelo treinado
model = YOLO('ovos/runs/detect/train4/weights/best.pt')

#Abre vídeo
cap = cv2.VideoCapture('20250524_215447(1).mp4')

#Obtém propriedades do vídeo original
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

#cria o vídeo de saída
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(
    'resultado_ovos_contados.mp4',
    fourcc,
    fps,
    (width, height)
)

#Define linha vertical
line_x = width // 2

#armazena o centro dos objetos
tracked_centers = {}

#Aarmazena IDs de ovos que já foram contados, para evitar repetir o mesmo objeto
already_counted = set()

#Próximo ID disponível
next_id = 0

#Conta total de ovos
total_count = 0

cv2.namedWindow('Detecção de Ovos', cv2.WINDOW_NORMAL)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, verbose=False)[0]
    boxes = results.boxes

    #Desenha a linha
    cv2.line(frame, (line_x, 0), (line_x, height), (0, 255, 255), 2)

    #Armazena os centros detectados no frame atual
    current_centers = []

    #Percorre todas as caixas detectadas
    for i, box in enumerate(boxes):
        cls = int(box.cls)  # classe detectada

        #Filtra apenas a classe "ovo"
        if cls != 0:
            continue

        #Extrai as coordenadas da caixa delimitadoaa
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

        #Calcula o centro da caixa delimitadora
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)
        center = (cx, cy)

        #Desenha o centro do objeto detectado
        cv2.circle(frame, center, 4, (0, 255, 0), -1)

        #Exibe a classe
        cv2.putText(
            frame,
            f'{cls}',
            (cx + 5, cy - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1
        )
        current_centers.append(center)

    #atualiza os objetos rastreados
    new_tracked = {}

    for center in current_centers:
        matched_id = None

        for tid, prev_center in tracked_centers.items():
            px, py = prev_center

            #Verifica se a distância é pequena
            if abs(center[0] - px) < 30 and abs(center[1] - py) < 30:
                matched_id = tid
                break

        #e não encontrou, cria um novo ID
        if matched_id is None:
            matched_id = next_id
            next_id += 1

        #Verifica se o objeto cruzou a linha de contagem
        prev = tracked_centers.get(matched_id)
        if (
            prev and
            prev[0] < line_x and
            center[0] >= line_x and
            matched_id not in already_counted
        ):
            total_count += 1
            already_counted.add(matched_id)

        #Atualiza a posição do objeto rastreado
        new_tracked[matched_id] = center

    #Atualiza os objetos rastreados para o próximo frame
    tracked_centers = new_tracked

    #Exibe o total de ovos contados no vídeo
    cv2.putText(
        frame,
        f'Ovos contados: {total_count}',
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 0, 0),
        2
    )

    out.write(frame)

    cv2.imshow('Detecção de Ovos', frame)

    #Sair
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
