import cv2

image_path = input("Введите путь к кадру: ")
img = cv2.imread(image_path)

# Выделите опасную зону (место, где стоит камера)
print("Выделите область камеры (danger zone) и нажмите Enter")
danger_zone = cv2.selectROI("Danger zone", img, False)
cv2.destroyAllWindows()

# Выделите bounding box машинки (вплотную к камере)
print("Выделите машинку (когда она касается камеры) и нажмите Enter")
robot_box = cv2.selectROI("Robot", img, False)
cv2.destroyAllWindows()

width_px = robot_box[2]   # ширина в пикселях
height_px = robot_box[3]
print(f"Опасная зона (x1,y1,x2,y2): {danger_zone[0]}, {danger_zone[1]}, {danger_zone[0]+danger_zone[2]}, {danger_zone[1]+danger_zone[3]}")
print(f"Ширина машинки в момент касания: {width_px} px")
