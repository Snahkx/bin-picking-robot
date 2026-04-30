def detect_blue_chips(frame_bgr):
    annotated = frame_bgr.copy()

    blurred = cv2.GaussianBlur(frame_bgr, (BLUR_SIZE, BLUR_SIZE), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)

    kernel = np.ones((KERNEL_SIZE, KERNEL_SIZE), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.GaussianBlur(mask, (BLUR_SIZE, BLUR_SIZE), 0)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    candidates = []

    for contour in contours:
        area = cv2.contourArea(contour)

        if area < MIN_AREA or area > MAX_AREA:
            continue

        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue

        circularity = (4 * np.pi * area) / (perimeter * perimeter)

        x_rect, y_rect, w_rect, h_rect = cv2.boundingRect(contour)
        if h_rect == 0:
            continue

        aspect_ratio = w_rect / float(h_rect)

        (x, y), radius = cv2.minEnclosingCircle(contour)
        cx, cy = int(x), int(y)
        radius = int(radius)

        circle_area = np.pi * radius * radius
        fill_ratio = area / circle_area if circle_area > 0 else 0

        # Perfect chip target:
        # circularity near 1
        # aspect ratio near 1
        # fill ratio near 1
        circularity_score = circularity
        aspect_score = 1.0 - abs(1.0 - aspect_ratio)
        fill_score = 1.0 - abs(1.0 - fill_ratio)

        score = (
            0.50 * circularity_score +
            0.30 * aspect_score +
            0.20 * fill_score
        )

        candidates.append({
            "center": (cx, cy),
            "radius": radius,
            "area": area,
            "circularity": circularity,
            "aspect_ratio": aspect_ratio,
            "fill_ratio": fill_ratio,
            "score": score,
            "bbox": (x_rect, y_rect, w_rect, h_rect),
            "contour": contour
        })

    # No valid candidates
    if not candidates:
        return annotated, mask, []

    # Pick ONE chip closest to perfect circle
    best = max(candidates, key=lambda d: d["score"])

    cx, cy = best["center"]
    radius = best["radius"]
    contour = best["contour"]

    # Draw all candidates faintly
    for det in candidates:
        cv2.drawContours(annotated, [det["contour"]], -1, (80, 80, 80), 1)

    # Draw selected best chip strongly
    cv2.drawContours(annotated, [contour], -1, (0, 255, 0), 3)
    cv2.circle(annotated, (cx, cy), radius, (255, 0, 0), 2)
    cv2.circle(annotated, (cx, cy), 5, (0, 0, 255), -1)

    label = f"TARGET ({cx}, {cy})"
    cv2.putText(
        annotated,
        label,
        (cx + 10, cy - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 255),
        2,
        cv2.LINE_AA
    )

    score_label = f"score={best['score']:.2f} circ={best['circularity']:.2f}"
    cv2.putText(
        annotated,
        score_label,
        (cx + 10, cy + 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 255),
        1,
        cv2.LINE_AA
    )

    return annotated, mask, [best]