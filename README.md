# Django

<details>
<summary>📕 Django guide</summary>

- **templates** : HTML 템플릿 파일을 보관하는 폴더입니다. 이 프로젝트에서는 실행을 위한 최소한의 프론트를 작성하였습니다.

- **__init__.py** : 패키지로써 인식되기 위한 빈 파일입니다.

- **apps.py** : 앱의 설정을 하는 파일입니다.

- **forms.py** : 웹 양식, 데이터 처리를 위한 폼 클래스를 정의하는 파일입니다.

- **models.py** : 데이터베이스 모델 구조를 정의하는 파일입니다.

- **serializers.py** : Django REST Framework에서 사용되는 직렬화 클래스를 정의하는 파일입니다.

- **urls.py** : URL 패턴을 정의하는 파일입니다.

- **views.py** : 뷰 함수를 정의하는 파일입니다. 요청 처리 로직, 템플릿 렌더링, API 응답 생성 등의 작업을 수행합니다.
<br><br>
</details>

## 🌿 폴더 설명

- **.config** : 서버 배포를 위한 nginx와 uwsgi의 설정 파일이 위치합니다.
  
- **capstProject** : 프로젝트의 전반적인 설정(settings.py)과 각 앱의 큰 url 경로 설정(urls.py) 등의 역할을 합니다.

- **home** : 기본 url 진입 시 보여지는 메뉴 페이지 앱입니다.

- **market** : 지역별 대분류/소분류 기능을 수행하는 검색 기능 앱입니다.

- **post** : firebase와 연동된 게시글 등록 기능의 앱입니다.
  * 게시글 목록/읽기/게시/수정/삭제와 함께 viewset을 통해 REST API 기능을 제공합니다.
    - 게시물 필드 : ['id', 'firebase_id', 'title', 'content', 'author', 'attachments']
    - 첨부파일 필드 : ['id', 'file', 'post']
    - 목록/읽기 : 모든 사용자
    - 게시 : 로그인 된 사용자
    - 수정/삭제 : 해당 게시글을 게시한 사용자

- **users** : firebase와 연동된 사용자 기능의 앱입니다.
  * 사용자 회원가입/로그인/로그아웃/아이디 찾기/비밀번호 찾기/회원정보 수정 및 각각의 REST API 기능을 제공합니다.
    - 사용자 필드 = ['id', 'username', 'password', 'email']
    - 아이디/비밀번호 찾기 기능은 이메일 전송(SMTP)을 통해 진행됩니다.
<br><br>

## 🌿 서버 구동

- React에서의 호출을 위해 서버를 구동했습니다.

- 서버 구동에는 AWS EC2와 가비아 도메인 네임서버를 이용했습니다.

[🔗바로가기](https://tradi-market.site)


