# mypjt_fastapi
mypjt_fastapi todos + dashboard + face recognition

# fastapi mypjt 실습

## python 가상환경 만들기

```
# 파이썬 가상환경
python -m venv fa_venv

# 콘다 가상환경
conda create -n faenv_py310 python=3.10

```

## 가상환경 활성화

```
[windows]
fa_venv/scripts/activate

[mac/linux]
source fa_venv/bin/activate

[anaconda]
conda activate faenv_py310
```

## 설치 라이브러리

<pre>
pip install fastapi "uvicorn[standard]"
pip install jinja2 python-multipart

# sql ORM
pip install sqlalchemy

# mysql 연동시 필요
pip install pymysql cryptography


# face_recognition 라이브러리 설치를 위해 필요함
conda install -c conda-forge dlib
 
# 얼굴 인식 라이브러리
pip install face_recognition

# 이미지 처리 라이브러리  
pip install opencv-python
</pre>

## 서버 실행방법

```
uvicorn main:app --reload

또는

python app_start.py
```

## mypjt 클라이언트 확인

```
[앱 실행]
http://localhost:8000

[스웨거]
http://localhost:8000/docs
```
