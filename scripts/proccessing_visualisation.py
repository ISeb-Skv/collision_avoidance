video_files = list(VIDEOS_DIR.glob("*.mp4")) + list(VIDEOS_DIR.glob("*.avi"))
print(f"Найдено видео: {len(video_files)}")
video_max_state = {}

for video_path in video_files:
    print(f"\nОбработка: {video_path.name}")
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    history = deque(maxlen=HISTORY_LEN)
    log_entries = []
    max_state = 'SAFE' 

    out_video = cv2.VideoWriter(
        str(RESULTS_DIR / "annotated_videos" / f"annotated_{video_path.name}"),
        cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height)
    )

    frame_num = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_num += 1

        results = model(frame)
        center, width_robot, orientation = get_robot_info_from_lights(results[0].boxes)

        state = 'SAFE'
        if center and width_robot:
            history.append((center[0], center[1], width_robot))
            state = predict_state(history)
            log_entries.append({
                'frame': frame_num, 'x': center[0], 'y': center[1],
                'width': width_robot, 'state': state
            })
            if state == 'CRITICAL':
                max_state = 'CRITICAL'
            elif state == 'WARNING' and max_state != 'CRITICAL':
                max_state = 'WARNING'
            
            if state != 'SAFE':
                print(f"  Кадр {frame_num}: {state} (center={center}, width={width_robot:.1f})")
            
            # Визуализация центра
            cv2.circle(frame, center, 5, (0,255,0), -1)
            if orientation:
                norm = np.hypot(orientation[0], orientation[1])
                if norm > 1e-6:
                    dx = orientation[0] / norm
                    dy = orientation[1] / norm
                    if ARROW_REVERSE:
                        dx, dy = -dx, -dy
                    end_x = int(center[0] + dx * 40)
                    end_y = int(center[1] + dy * 40)
                	cv2.arrowedLine(frame, center, (end_x, end_y), (0,255,255), 2, tipLength=0.3)
            		cv2.putText(frame, f"Width: {width_robot:.1f} px", (center[0]+10, center[1]-10),
                	cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
            		if len(history) >= 2:
                      speed = np.hypot(history[-1][0]-history[-2][0], history[-1][1]-history[-2][1])
                	cv2.putText(frame, f"Speed: {speed:.1f} px/f", (center[0]+10, center[1]+10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,0), 2)
        color_state = (0,255,0) if state == 'SAFE' else (255,255,0) if state == 'WARNING' else (0,0,255)
               cv2.putText(frame, f"State: {state}", (10, frame_height - 20),
                  cv2.FONT_HERSHEY_SIMPLEX, 1, color_state, 2)
        cv2.rectangle(frame, (DANGER_ZONE[0], DANGER_ZONE[1]), (DANGER_ZONE[2], DANGER_ZONE[3]), (0,0,255), 2)
        		   cv2.putText(frame, "DANGER ZONE", (DANGER_ZONE[0], DANGER_ZONE[1]-5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
        if len(history) >= 2:
            if len(history) >= 3:
                (x3,y3,w3), (x2,y2,w2), (x1,y1,w1) = history[-3], history[-2], history[-1]
                vx = (x1 - x3) / 2.0
                vy = (y1 - y3) / 2.0
            else:
                (x2,y2,w2), (x1,y1,w1) = history[-2], history[-1]
                vx = x1 - x2
                vy = y1 - y2
            for s in range(1, PREDICTION_HORIZON+1):
                px = int(history[-1][0] + s * vx)
                py = int(history[-1][1] + s * vy)
                cv2.circle(frame, (px, py), 3, (255,255,0), -1)
                if s > 1:
                    prev_px = int(history[-1][0] + (s-1)*vx)
                    prev_py = int(history[-1][1] + (s-1)*vy)
                    cv2.line(frame, (prev_px, prev_py), (px, py), (255,255,0), 1)

        out_video.write(frame)
        if frame_num % 300 == 0:
            print(f"  Кадр {frame_num}/{total_frames} ({100*frame_num/total_frames:.1f}%)")

    cap.release()
    out_video.release()
    print(f"Готово. Сохранено {len(log_entries)} записей. Максимальное состояние: {max_state}")
    if log_entries:
        pd.DataFrame(log_entries).to_csv(RESULTS_DIR / "logs" / f"log_{video_path.stem}.csv", index=False)
    
    video_max_state[video_path.stem] = max_state

print("\n Обработка всех видео завершена!")
