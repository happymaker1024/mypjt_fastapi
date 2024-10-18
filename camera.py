# camera.py
# pip install opencv-python

import cv2

class VideoCamera():
    def __init__(self):
        
        # 웹캠을 사용할 때
        self.video = cv2.VideoCapture(0)
        # 영상 파일을 사용할 때
        # self.video = cv2.VideoCapture('video.mp4')

    def __del__(self):
        self.video.release()

    def get_frame(self):
        # Grab a single frame of video
        ret, frame = self.video.read()
        return frame


if __name__ == '__main__':
    cam = VideoCamera()
    while True:
        frame = cam.get_frame()

        # show the frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # 'q'키 누르면 삭제
        if key == ord("q"):
            break

    # 모두 종료
    cv2.destroyAllWindows()
    print('finish')
