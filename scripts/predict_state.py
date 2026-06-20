def predict_state(history):
    """
    history: список кортежей (x, y, width) длиной не менее 2.
    Возвращает: 'SAFE', 'WARNING' или 'CRITICAL'.
    """
    if len(history) < 2:
        return 'SAFE'
    if len(history) >= 3:
        (x3, y3, w3), (x2, y2, w2), (x1, y1, w1) = history[-3], history[-2], history[-1]
        vx = (x1 - x3) / 2.0
        vy = (y1 - y3) / 2.0
        vw = (w1 - w3) / 2.0
    else:
        (x2, y2, w2), (x1, y1, w1) = history[-2], history[-1]
        vx = x1 - x2
        vy = y1 - y2
        vw = w1 - w2

    # Экстраполяция на PREDICTION_HORIZON кадров
    for step in range(1, PREDICTION_HORIZON + 1):
        px = history[-1][0] + step * vx
        py = history[-1][1] + step * vy
        pw = history[-1][2] + step * vw
        in_zone = (DANGER_ZONE[0] <= px <= DANGER_ZONE[2] and
                   DANGER_ZONE[1] <= py <= DANGER_ZONE[3])
        over_width = (pw >= COLLISION_WIDTH_THRESHOLD_PX)

        if in_zone or over_width:
            if step <= 2:
                return 'CRITICAL'
            else:
                return 'WARNING'

    return 'SAFE'
