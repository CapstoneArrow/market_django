from django.shortcuts import render


"""
데이터 연동 시 사용

import firebase_admin
from firebase_admin import credentials, firestore


# Firebase 서비스 계정 키 필요
cred = credentials.Certificate("path/to/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

data_ref = db.collection("전통시장정보데이터")
query_snapshot = data_ref.get()

market_data = [doc.to_dict() for doc in query_snapshot]

"""


# 임시 데이터
class MarketData:
    def __init__(self, address):
        self.소재지도로명주소 = address

temp_data = [
    MarketData("서울특별시 강남구 역삼동"),
    MarketData("서울특별시 서초구 양재동"),
    MarketData("부산광역시 해운대구 우동"),
    MarketData("부산광역시 동래구 명륜동"),
    MarketData("대구광역시 수성구 범물동"),
    MarketData("대구광역시 중구 대봉동")
]



# 전통시장정보데이터의 소재지도로명주소를 이용하여 대분류, 소분류
def market_list_view(request):
    
    # 데이터 속 주소에 맞게 수정 예정 ex) 서울특별시 <-> 서울시
    first_categories = ["서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "대전광역시", "울산광역시",
                        "세종특별자치시", "경기도", "강원도", "충청북도", "충청남도", "전라북도", "전라남도", "경상북도",
                        "경상남도", "제주도"]

    second_categories = {
        "서울특별시": ["강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구", "노원구", "도봉구",
                  "동대문구", "동작구", "마포구", "서대문구", "서초구", "성동구", "성북구", "송파구", "양천구", "영등포구",
                  "용산구", "은평구", "종로구", "중구", "중랑구"],
        "부산광역시": ["강서구", "금정구", "기장군", "남구", "동구", "동래구", "부산진구", "북구", "사상구", "사하구", 
                  "서구", "수영구", "연제구", "영도구", "중구", "해운대구"],
        "대구광역시": ["남구", "달서구", "달성군", "동구", "북구", "서구", "수성구", "중구", "유성구"],
        "인천광역시": ["계양구", "남동구", "동구", "미추홀구", "부평구", "서구", "연수구", "옹진구", "중구"],
        "광주광역시": ["광산구", "남구", "동구", "북구", "서구"],
        "대전광역시": ["대덕구", "동구", "서구", "유성구", "중구"],
        "울산광역시": ["남구", "동구", "북구", "울주군", "중구"],
        "세종특별자치시": ["전체"],
        "경기도": ["가평군", "고양시", "과천시", "광명시", "광주시", "구리시", "군포시", "김포시", "남양주시", "동두천시",
                "부천시", "성남시", "수원시", "시흥시", "안산시", "안성시", "안양시", "양주시", "양평군", "여주시", "연천군",
                "오산시", "용인시", "의왕시", "의정부시", "이천시", "파주시", "평택시", "포천시", "하남시", "화성시"],
        "강원도": ["강릉시", "고성군", "동해시", "삼척시", "속초시", "양구군", "양양군", "영월군", "원주시", "인제군",
                "정선군", "철원군", "춘천시", "태백시", "평창군", "홍천군", "화천군", "횡성군"],
        "충청북도": ["괴산군", "단양군", "보은군", "영동군", "옥천군", "음성군", "제천시", "증평군", "진천군", "청원군",
                 "청주시", "충주시"],
        "충청남도": ["계룡시", "공주시", "금산군", "논산시", "당진시", "보령시", "부여군", "서산시", "서천군", "아산시",
                 "예산군", "천안시", "청양군", "태안군", "홍성군"],
        "전라북도": ["고창군", "군산시", "김제시", "남원시", "무주군", "부안군", "순창군", "완주군", "익산시", "임실군",
                 "장수군", "전주시", "정읍시", "진안군"],
        "전라남도": ["강진군", "고흥군", "곡성군", "광양시", "구례군", "나주시", "담양군", "목포시", "무안군", "보성군",
                 "순천시", "신안군", "여수시", "영광군", "영암군", "완도군", "장성군", "장흥군", "진도군", "함평군", "해남군",
                 "화순군"],
        "경상북도": ["경산시", "경주시", "고령군", "구미시", "군위군", "김천시", "문경시", "봉화군", "상주시", "성주군",
                 "안동시", "영덕군", "영양군", "영주시", "영천시", "예천군", "울릉군", "울진군", "의성군", "청도군",
                 "청송군", "칠곡군", "포항시"],
        "경상남도": ["거제시", "거창군", "고성군", "김해시", "남해군", "밀양시", "사천시", "산청군", "양산시", "의령군",
                 "진주시", "창녕군", "창원시", "통영시", "하동군", "함안군", "함양군", "합천군"],
        "제주도": ["서귀포시", "제주시"],
}

    categorized_data = {}

    for first_category in first_categories:
        categorized_data[first_category] = {}
        for second_category in second_categories.get(first_category, []):
            categorized_data[first_category][second_category] = []

    for data in temp_data: # 연동 시 market_data
        for first_category, second_category_list in second_categories.items():
            if data.소재지도로명주소.startswith(first_category):
                for second_category in second_category_list:
                    if second_category in data.소재지도로명주소:
                        categorized_data[first_category][second_category].append(data)
   
    return render(request, 'market/market_list.html', {'categorized_data': categorized_data})
