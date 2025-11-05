import cv2

def draw_neon_corner_box(frame, x1, y1, x2, y2, color=(0, 255, 255), thickness=2, corner_len=15, glow_intensity=0.4):
    """
    Draws a glowing neon-style corner box around the object.
    Combines neon glow + corner-only minimalistic box.
    """

    # --- Neon glow overlay ---
    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
    cv2.addWeighted(overlay, glow_intensity, frame, 1 - glow_intensity, 0, frame)

    # --- Corner-style edges ---
    # top-left
    cv2.line(frame, (x1, y1), (x1 + corner_len, y1), color, thickness)
    cv2.line(frame, (x1, y1), (x1, y1 + corner_len), color, thickness)
    # top-right
    cv2.line(frame, (x2, y1), (x2 - corner_len, y1), color, thickness)
    cv2.line(frame, (x2, y1), (x2, y1 + corner_len), color, thickness)
    # bottom-left
    cv2.line(frame, (x1, y2), (x1 + corner_len, y2), color, thickness)
    cv2.line(frame, (x1, y2), (x1, y2 - corner_len), color, thickness)
    # bottom-right
    cv2.line(frame, (x2, y2), (x2 - corner_len, y2), color, thickness)
    cv2.line(frame, (x2, y2), (x2, y2 - corner_len), color, thickness)

    return frame
