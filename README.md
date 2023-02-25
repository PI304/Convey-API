# Convey API

## 유의사항

1. [Test Server](##1.-Test-Server)
2. [Schemas](##2.-Schemas)
3. [Sector 와 문제 유형](##3.-Sector-와-문제-유형)
4. [협업 방법](##4.-협업-방법)
5. [코드 컨벤션](##5.-코드-컨벤션)

## 1. Test Server

[테스트 서버 API Doc 보기](http://13.125.243.32/api/swagger/)


## 2. Schemas

### 1. 시나리오별 Request Body Schemas 
body 에 들어갈 data 의 스키마는 API Document 에 정의되어 있습니다.

#### 1) survey package 응답 결과 보내기
헤더의 Authorization 를 이용하여 앱 이용자임을 식별합니다. 앱 이용자가 아니라면 요청을 거절됩니다.
피험자 id 는 request body 에 명시합니다. 피험자 응답은 Part 단위로 전송하며 sector 에 대한 응답들로 리스트가 구성됩니다.
자세한 스키마는 API Document 를 참고해주세요.


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
   "someOtherFields": "some other fields",
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

#### 2) survey package - 설문의 문항 정보 받기
업데이트 예정입니다.



## 3. Sector 와 문제 유형
업데이트 예정입니다.