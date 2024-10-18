import face_recognition
import cv2
import camera
import os
import numpy as np

class FaceRecog():
    def __init__(self):
        # OpenCV를 사용하여 장치 0(기본 카메라)에서 영상 캡처
        # 웹캠에서 캡처하는데 문제가 있으면, 아래 줄을 주석 처리하고 동영상 파일을 사용 가능
        self.camera = camera.VideoCamera()

        self.known_face_encodings = []  # 알려진 얼굴 인코딩 저장
        self.known_face_names = []  # 알려진 얼굴 이름 저장

        # 샘플 이미지를 불러오고 얼굴 인식을 학습
        dirname = 'knowns'  # 얼굴 이미지가 저장된 디렉토리
        files = os.listdir(dirname)  # 디렉토리 내 파일 목록 가져오기
        for filename in files:
            name, ext = os.path.splitext(filename)  # 파일 이름과 확장자를 분리
            if ext == '.jpg':  # 확장자가 .jpg인 파일만 처리
                self.known_face_names.append(name)  # 파일 이름(얼굴 이름) 추가
                pathname = os.path.join(dirname, filename)  # 파일 경로 생성
                img = face_recognition.load_image_file(pathname)  # 이미지 파일 로드
                face_encoding = face_recognition.face_encodings(img)[0]  # 얼굴 인코딩 생성
                self.known_face_encodings.append(face_encoding)  # 인코딩된 얼굴 데이터 추가

        # 얼굴 인식 관련 변수를 초기화
        self.face_locations = []  # 얼굴 위치를 저장하는 리스트
        self.face_encodings = []  # 얼굴 인코딩을 저장하는 리스트
        self.face_names = []  # 인식된 얼굴 이름을 저장하는 리스트
        self.process_this_frame = True  # 매 프레임마다 처리를 스킵하는 플래그

    def __del__(self):
        # 객체가 소멸될 때 카메라 리소스를 해제
        del self.camera

    def get_frame(self):
        # 단일 프레임을 가져옴
        frame = self.camera.get_frame()

        # 프레임이 비어 있는지 확인
        if frame is None or frame.size == 0:
            print("Error: Frame is empty")
            return None

        # 얼굴 인식 속도를 높이기 위해 프레임 크기를 1/4로 축소
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # OpenCV는 BGR 형식의 이미지를 사용하지만 face_recognition은 RGB 형식을 사용하므로 변환
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # 처리 시간을 절약하기 위해 매 프레임마다 처리를 스킵 (매번 처리하지 않음)
        if self.process_this_frame:
            # 현재 프레임에서 모든 얼굴과 얼굴 인코딩을 찾음
            self.face_locations = face_recognition.face_locations(rgb_small_frame)
            self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

            self.face_names = []  # 인식된 얼굴 이름을 저장할 리스트 초기화
            for face_encoding in self.face_encodings:
                if not self.known_face_encodings:
                    # 알려진 얼굴 인코딩이 없으면 "Unknown" 반환
                    self.face_names.append("Unknown")
                    continue

                # 인식된 얼굴과 알려진 얼굴 간의 거리를 계산
                distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)

                # distances가 비어 있음
                if len(distances) == 0:
                    name = "Unknown"
                else:
                    min_value = min(distances)  # 가장 짧은 거리를 찾음
                    # tolerance: 얼굴을 매칭할 때의 거리 기준. 값이 낮을수록 더 엄격함
                    # 0.6이 일반적으로 좋은 성능을 냄
                    if min_value < 0.6:
                        index = np.argmin(distances)  # 가장 유사한 얼굴 인덱스 찾기
                        name = self.known_face_names[index]  # 해당 이름 할당

                self.face_names.append(name)  # 이름 추가

        # 매 프레임 처리 여부를 토글
        self.process_this_frame = not self.process_this_frame

        # 인식된 결과를 표시
        for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
            # 프레임을 1/4 크기로 줄였기 때문에 얼굴 위치를 다시 4배로 확장
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # 얼굴 주위에 사각형 그리기
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # 얼굴 아래에 이름을 표시할 박스를 그림
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        return frame  # 처리된 프레임 반환

    def get_jpg_bytes(self):
        frame = self.get_frame()
        # OpenCV는 기본적으로 raw 이미지를 캡처하지만, Motion JPEG를 사용하므로 JPG로 인코딩 필요
        ret, jpg = cv2.imencode('.jpg', frame)

        return jpg.tobytes()  # JPG 바이너리 데이터를 반환

# html에서 비디오 스트리밍 처리 기능
def video_process(fr):
    while True:
        # 프레임을 읽음
        frame = fr.get_frame()

        if frame is None:
            print("Error: 비어 있는 프레임을 받았습니다.")
            continue
        
        # JPG로 변환
        ret, jpg = cv2.imencode('.jpg', frame)
        if not ret:
            print("Error: 프레임을 JPG로 인코딩하는데 실패했습니다.")
            continue

        # 스트리밍으로 클라이언트에 프레임을 전송
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpg.tobytes() + b'\r\n\r\n')



if __name__ == '__main__':
    face_recog = FaceRecog()
    print(face_recog.known_face_names)  # 알려진 얼굴 이름 출력
    while True:
        frame = face_recog.get_frame()

        # 프레임을 화면에 표시
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # `q` 키가 눌리면 루프를 종료
        if key == ord("q"):
            break

    # 리소스 정리
    cv2.destroyAllWindows()
    print('finish')
