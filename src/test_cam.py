import cv2
import time

def result_callback(result, output_image, timestamp_ms):
    pass # Dummy

def main():
    print("Testing RAW Camera Performance...")
    cap = cv2.VideoCapture(0)
    
    # Same settings as engine
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    prev_time = 0
    
    while True:
        success, frame = cap.read()
        if not success:
            print("Failed to read frame")
            break
            
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if prev_time > 0 else 0
        prev_time = curr_time
        
        cv2.putText(frame, f"Raw FPS: {int(fps)}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("TEST RAW CAMERA (Press q to quit)", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
