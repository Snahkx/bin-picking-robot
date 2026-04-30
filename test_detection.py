from picamera2 import Picamera2
import cv2
import numpy as np
import time

FRAME_SIZE = (1280, 720)

LOWER_BLUE = np.array([90, 80, 40], dtype=np.uint8)
UPPER_BLUE = np.array([140, 255, 255], dtype=np.uint8)

MIN_AREA = 800
MAX_AREA = 30000

KERNEL_SIZE = 5
BLUR_SIZE = 5



def detect_blue_chips(frame_bgr):
    annotated = frame_bgr.copy()

    blurred = cv2.GaussianBlur(frame_bgr, (BLUR_SIZE, BLUR_SIZE), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)

    kernel = np.ones((KERNEL_SIZE, KERNEL_SIZE), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # Smooth for circle detection
    circle_input = cv2.GaussianBlur(mask, (9, 9), 2)

    circles = cv2.HoughCircles(
        circle_input,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=55,        # minimum distance between chip centers
        param1=80,
        param2=18,         # lower = more detections, higher = stricter
        minRadius=35,
        maxRadius=90
    )

    detections = []

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")

        for x, y, r in circles:
            if x < 0 or y < 0 or x >= frame_bgr.shape[1] or y >= frame_bgr.shape[0]:
                continue

            # Check how much blue exists inside the circle
            circle_mask = np.zeros(mask.shape, dtype=np.uint8)
            cv2.circle(circle_mask, (x, y), r, 255, -1)

            blue_pixels = cv2.countNonZero(cv2.bitwise_and(mask, mask, mask=circle_mask))
            circle_area = np.pi * r * r
            fill_ratio = blue_pixels / circle_area if circle_area > 0 else 0

            if fill_ratio < 0.45:
                continue

            # Prefer cleaner, more filled circles
            score = fill_ratio

            detections.append({
                "center": (x, y),
                "radius": r,
                "score": score,
                "fill_ratio": fill_ratio
            })

    if not detections:
        cv2.putText(
            annotated,
            "NO TARGET",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 0, 255),
            2
        )
        return annotated, mask, []

    # Pick ONE best circle
    best = max(detections, key=lambda d: d["score"])

    # Draw all detected circles faintly
    for det in detections:
        x, y = det["center"]
        r = det["radius"]
        cv2.circle(annotated, (x, y), r, (80, 80, 80), 1)

    # Draw target strongly
    x, y = best["center"]
    r = best["radius"]

    cv2.circle(annotated, (x, y), r, (0, 255, 0), 3)
    cv2.circle(annotated, (x, y), 5, (0, 0, 255), -1)

    cv2.putText(
        annotated,
        f"TARGET ({x}, {y})",
        (x + 10, y - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 255),
        2
    )

    cv2.putText(
        annotated,
        f"fill={best['fill_ratio']:.2f}",
        (x + 10, y + 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 255),
        1
    )

    return annotated, mask, [best]


print("Starting camera...")

picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"size": FRAME_SIZE, "format": "RGB888"}
)
picam2.configure(config)
picam2.start()

time.sleep(1)

print("Camera started. Press q to quit.")

try:
    while True:
        raw_frame = picam2.capture_array()
        frame_bgr = raw_frame

        annotated_frame, mask, detections = detect_blue_chips(frame_bgr)

        if detections:
            target = detections[0]
            print(f"TARGET: {target['center']} score={target['score']:.2f}")
        else:
            print("No target")

        cv2.imshow("Best Blue Chip Target", annotated_frame)
        cv2.imshow("Mask", mask)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

finally:
    cv2.destroyAllWindows()
    picam2.stop()
    print("Stopped.")