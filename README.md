# spark_practice

## 1. brew를 이용한 Java 설치

```python
$ brew update
$ brew tap adoptopenjdk/openjdk # adoptopenjdk/openjdk 레포지토리 추가
$ brew search jdk # 다운로드 가능한 jdk 버전 확인
$ brew install --cask adoptopenjdk11 # java 11 다운로드
$ java --version # 자바 버전 확인
```

## 2. Python 가상 환경 구성, pyspark 라이브러리 설치

### 2-1. PyCharm 설치

### 2-2. `pip install pyspark`


## "현재 브랜치와 'origin/main'이(가) 갈라졌습니다," 오류 해결방법
### 오류 내용

```현재 브랜치 main
현재 브랜치와 'origin/main'이(가) 갈라졌습니다,
다른 커밋이 각각 1개와 1개 있습니다.

커밋할 사항 없음, 작업 폴더 깨끗함
```

### 해결책

```git fetch origin main``` 
```git merge FETCH_HEAD```
