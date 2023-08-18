import cv2
import numpy as np

init = True

def resize_image(input_img, scale_percent):
    width = int(input_img.shape[1] * scale_percent / 100)
    height = int(input_img.shape[0] * scale_percent / 100)
    return cv2.resize(input_img, (width, height), interpolation=cv2.INTER_AREA)

def warp_image_using_four_points(img, points):
    height, width = img.shape[:2]
    
    dst_pts = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]
    ], dtype='float32')
    
    M = cv2.getPerspectiveTransform(np.array(points, dtype='float32'), dst_pts)
    warped = cv2.warpPerspective(img, M, (width, height))
    
    return warped

def find_red_dots_centers(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    lower_red_1 = np.array([0, 70, 50])
    upper_red_1 = np.array([10, 255, 255])
    lower_red_2 = np.array([170, 70, 50])
    upper_red_2 = np.array([180, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower_red_1, upper_red_1)
    mask2 = cv2.inRange(hsv, lower_red_2, upper_red_2)
    mask = cv2.bitwise_or(mask1, mask2)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    centers = []
    for contour in contours:
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            centers.append((cx, cy))
    
    return centers

def is_near_center(x, y, centers):
    for cx, cy in centers:
        distance = np.sqrt((cx - x)**2 + (cy - y)**2)
        if distance < 20:
            return (cx, cy)
    return None

def click_event(event, x, y, flags, param):
    global img, points, init, red_dot_centers
    
    if event == cv2.EVENT_LBUTTONDOWN:
        print("LB Clicked")
        if init:
            cv2.circle(img, (x, y), 5, (255, 0, 0), -1)
            points.append((x, y))

            if len(points) == 4:
                img = warp_image_using_four_points(img, points)
                points = []
                cv2.imshow('image', img)
                init = False
                print('init done')
                red_dot_centers = find_red_dots_centers(img)
        else:
            center = is_near_center(x, y, red_dot_centers)
            if center:
                cv2.circle(img, center, 5, (255, 0, 0), -1)
                points.append(center)

                if (len(points)%2) == 0:
                    distance_pixel = np.sqrt((points[-1][0] - points[-2][0])**2 + (points[-1][1] - points[-2][1])**2)
                    txt_x = int(0.5*(points[-1][0] + points[-2][0]) - 50)
                    txt_y = int(0.5*(points[-1][1] + points[-2][1]))
                    
                    scale = real_distance / distance_pixel
                    print(f"ratio: {scale:.6f}")
                    cv2.putText(img, f"{scale:.6f}", (txt_x, txt_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    cv2.imshow('image', img)


img = cv2.imread('RS_dots_Color.png')
scale_percent = 100

img = resize_image(img, scale_percent)

cv2.imshow('image', img)
points = []
real_distance = float(input("Enter the real-world distance between the dots (in your desired unit): "))

red_dot_centers = []
cv2.setMouseCallback('image', click_event)

cv2.waitKey(0)
cv2.destroyAllWindows()
