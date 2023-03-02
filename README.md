# Convey API

## 1. Test Server

[테스트 서버 API Doc 보기](http://3.34.67.68/api/swagger/)


## 2. Schemas

### 1. 시나리오별 Request Body Schemas 
body 에 들어갈 data 의 스키마는 API Document 에 정의되어 있습니다.

#### 1) survey package 응답 결과 보내기
헤더의 Authorization 를 이용하여 앱 이용자임을 식별합니다. 앱 이용자가 아니라면 요청을 거절됩니다.
피험자 id 는 request body 에 명시합니다. 피험자 응답은 Part 단위로 전송하며 sector 에 대한 응답들로 리스트가 구성됩니다.
자세한 스키마는 API Document 를 참고해주세요.

#### 2) sector 생성 시 question type 별 선지 구성 방법
sector 생성 시 선택할 수 있는 문제 유형은 아래와 같습니다. 아래 code 의 string 값을 question_type 으로 지정해주시면 됩니다.
```python
LIKERT = "likert", "리커트"
SHORT_ANSWER = "short_answer", "단답형"
SINGLE_SELECT = "single_select", "단일 선택"
MULTI_SELECT = "multi_select", "다중 선택"
EXTENT = "extent", "정도"
LONG_ANSWER = "long_answer", "서술형"
```

각 sector 는 하나의 문제 유형만으로 구성되며 하나의 sector 내에서는 선지 구성 역시 동일합니다.

(ex: 리커트 척도를 문제유형으로 가지는 sector 의 경우, 
1번부터 5번으로 구성된 같은 선지가 전체 sector 에 걸쳐 적용되며
문제 내용만 달라집니다. 아래 사진 참고)


<img width="472" alt="스크린샷 2023-03-01 오후 7 38 40" src="https://user-images.githubusercontent.com/89679621/222115745-b51edcb8-d752-4d53-a051-6b3ee7a6e1b2.png">

각기 다른 문제 유형의 sector 들도 구성된 survey 의 샘플 데이터는
[sample-survey-data.json](sample-survey-data.json) 을 참고해주세요.

> ```single_select``` 와 ```multi_select``` 의 경우, survey sector 의 구성이 동일합니다


### 2. 시나리오별 Response Schemas

#### 1) kick-off survey 응답 후 routine 정보 얻기
kick-off 서베이 응답 후에는 해당 workspace 의 정보가 반환됩니다. 
반환된 workspace_id 를 사용하여 /api/workspaces/{id}/routines/ 로 
요청을 보내 루틴에 대한 정보를 얻을 수 있습니다.

**kick-off suvey 이후의 응답**

**/api/survey-packages/{1}/answers/**
```json
{
   "id": 1,
   "name": "some workspace name",
   "someOtherFields": "some other fields"
}
```

**/api/workspaces/{1}/routines/**
```json
{
   "id": 1,
   "workspaceId": 1,
   "routines": [
      {
         "id": 1,
         "nthDay": 1,
         "time": "09:00",
         "surveyPackage": 3
      },
      {
         "id": 1,
         "nthDay": 1,
         "time": "12:00",
         "surveyPackage": 8
      }
   ]
}
```
