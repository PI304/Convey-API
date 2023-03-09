# Convey API

## 1. Test Server

[테스트 서버 API Doc 보기](http://3.34.67.68/api/swagger/)


## 2. Schemas

### 1. 시나리오별 Request Body Schemas 
body 에 들어갈 data 의 스키마는 API Document 에 정의되어 있습니다.

#### 1) survey package 응답 결과 보내기
헤더의 Authorization 를 이용하여 앱 이용자임을 식별합니다. 앱 이용자가 아니라면 요청이 거절됩니다.
피험자 id 는 request body 에 명시합니다. 피험자 응답은 Part 단위로 전송하며 sector 에 대한 응답들로 리스트가 구성됩니다.
자세한 스키마는 아래 json 파일과 API Document 를 참고해주세요.

[survey_package_answer.json](apps/survey_packages/tests/sample_data/survey_package_answer.json)

---

#### 2) sector 생성 시 question type 별 선지 및 문항 구성 방법
sector 생성 시 선택할 수 있는 문제 유형은 아래와 같습니다. 아래 code 의 string 값을 question_type 으로 지정해주시면 됩니다.
```python
LIKERT = "likert", "리커트"
SHORT_ANSWER = "short_answer", "단답형"
SINGLE_SELECT = "single_select", "단일 선택"
MULTI_SELECT = "multi_select", "다중 선택"
EXTENT = "extent", "정도"
LONG_ANSWER = "long_answer", "서술형"
```

각 sector 는 하나의 문제 유형만으로 구성됩니다.

(ex: 리커트 척도를 문제유형으로 가지는 sector 의 경우, 
1번부터 5번으로 구성된 같은 선지가 전체 sector 에 걸쳐 적용되며
문제 내용만 달라집니다. 아래 사진 참고)


<img width="472" alt="스크린샷 2023-03-01 오후 7 38 40" src="https://user-images.githubusercontent.com/89679621/222115745-b51edcb8-d752-4d53-a051-6b3ee7a6e1b2.png">


각 sector 는 title, description, question_type 을 기본으로 가지며 common_choices 로 공통선지를 구성해줄 수도 있습니다.
```json
{
  "title": "some sector title",
  "description": "this sector uses common choices",
  "question_type": "likert",
  "common_choices": [
    ...
  ],
  "questions": []
}
```

**공통 선지 구성하기**

```json
{
    "number": "1",
    "content": "매우 그렇다",
    "isDescriptive": false,
    "descForm": null
}
```
- number: 선지 번호
- content: 선지 내용
- isDescriptive: 서술형 여부
- descForm: 서술 형태 (description format)


**문항 구성하기: 공통 선지를 사용하는 경우**

```json
{
  "number": 1, 
  "content": "질문1",
  "choices": null,
  "is_required": true,
  "linked_sector": null
}
```
- number: 문항 번호
- content: 문항 내용
- choices: 문항 개별 선지 (위 likert 의 경우 공통선지를 이용하므로 null)
- is_required: 필수 여부 (default: true)
- linked_sector: 연결된 섹터 id


**문항 구성하기: 개별 선지를 사용하는 경우**

```json
{
  "number": 1,
  "content": "오늘 아침, 연구참여 아동이 일어날 때",
  "is_required": true,
  "linked_sector": null,
  "choices": [
    {
      "number": 1,
      "content": "아동 스스로 일어났다",
      "isDescriptive": false,
      "descForm": null
    },
    {
      "number": 2,
      "content": "소음이나 소란스러움으로 인해 깼다",
      "isDescriptive": false,
      "descForm": null
    },
    {
      "number": 3,
      "content": "알람소리에 깼다",
      "isDescriptive": false,
      "descForm": null
    },
    {
      "number": 4,
      "content": "부모님이 깨워서 일어났다",
      "isDescriptive": false,
      "descForm": null
    }
  ]
}
```

이 경우 sector 생성 시 common_choices 를 null 로 설정

각기 다른 문제 유형의 sector 들도 구성된 survey 의 전체 샘플 데이터는
[sample_survey_sector_data.json](apps/surveys/tests/sample_data/sample_survey_sector_data.json) 을 참고해주세요.

> ```single_select``` 와 ```multi_select``` 의 경우, survey sector 의 구성이 동일합니다

---


#### 3) 기본 survey package 생성
survey package 는 여러 개의 survey 가 하나로 모여 있는 것을 칭합니다.
survey package 를 구성 (compose) 하기 위해서는 **우선 기본 정보로만 채워진 survey package 를 생성**한 뒤,
생성한 survey package 의 **id 를 이용하여 put method 를 통해 survey package 를 구성**합니다.

기본 정보로만 채워진 survey package 를 생성하는 request 의 body 예시는 아래 파일에서 확인할 수 있습니다.

[base_package.json](apps/survey_packages/tests/sample_data/base_package.json)


---

#### 4) survey package 구성
survey package 큰 단위 순서대로 Parts -> Subjects -> Survey 로 이루어져 있습니다.


**Parts** 는 설문지에서 디바이더 (divider) 에 해당하는 부분이며 단순한 text 입니다.
<img width="471" alt="스크린샷 2023-03-04 오전 11 18 59" src="https://user-images.githubusercontent.com/89679621/222870719-92ad11ad-5ef3-4771-8a0d-04acfd625741.png">

```json
{
  "title": "기초설문",
  "subjects": ["하위 subjects..."]
}
```


**Subjects** 는 설문지에서 대주제에 해당하는 부분이며 숫자와 텍스트로 구성되어 있습니다.
<img width="471" alt="스크린샷 2023-03-04 오전 11 22 12" src="https://user-images.githubusercontent.com/89679621/222870832-cee25d1f-fb2e-40c4-9196-91c30501d963.png">
```json
{
  "number": 1,
  "title": "사회 정서 발달",
  "surveys": ["하위 surveys"]
}
```

**Surveys** 는 설문지에서 소주제에 해당하는 부분이며 제목과 연결하고자 하는 survey 의 id 로 구성합니다.

<img width="471" alt="스크린샷 2023-03-04 오전 11 23 55" src="https://user-images.githubusercontent.com/89679621/222870914-28639bcd-cddc-4171-902f-fe78cdabc5e8.png">

```json
{
  "number": 1,
  "title": "기질/환경민감성",
  "survey": 999
}
```

title 에 null 값을 넘기면 제목을 사용하지 않겠다는 의미이며 그 예시는 아래 사진과 같습니다. Part 에 해당하는 디바이더 아래에
subject 인 '양육' 만이 포함되어 있으며 survey 의 직접적인 제목이 설정되어 있지 않습니다.


<img width="471" alt="스크린샷 2023-03-04 오전 11 25 28" src="https://user-images.githubusercontent.com/89679621/222870992-97847277-9648-4a13-a414-aa577c03f5e2.png">


전체적 데이터 샘플은 [survey_package_parts.json](apps/survey_packages/tests/sample_data/survey_package_parts.json) 을 참고해주세요.


---


#### 5) survey package 에 대한 피험자 응답 보내기
```json
{
  "key": "워크스페이스 uuid + 피험자 고유 번호",
  "answers": [...]
}
```
> 처음 kick-off survey package 를 가지고 올 때 피험자가 입력했던 key 를 저장해두고 
> 어떤 survey package 에 대한 응답을 보낼 때마다 함께 전송하도록 합니다.

**문제유형별 answer schema 1: likert, single_select, multi_select, extent**
```json
{
  "question_id": 1,
  "answer": "1"
}
```
> ⚠️ answer 필드는 항상 string 입니다. string 으로 보내나 유효한 숫자가 아니면 에러를 반환합니다.


**문제유형별 answer schema 2: short_answer**
```json
{
  "question_id": 1,
  "answer": "2$30" -> ex.2시간 30분
}
```
> ⚠️ 채워넣어야 하는 빈칸이 여러 개인 short_answer 유형의 경우 $ 로 구분하여 
> string 으로 보냅니다.
> 
```json
{
  "number": 6,
  "content": "복용하는 약은? (모두 적으세요)",
  "choices": [
    {
      "number": 1,
      "content": null,
      "is_descriptive": true,
      "desc_form": "약 이름 %s, %d회 복용"
    },
    {
      "number": 2,
      "content": null,
      "is_descriptive": true,
      "desc_form": "약 이름 %s, %d회 복용"
    },
    {
      "number": 3,
      "content": null,
      "is_descriptive": true,
      "desc_form": "약 이름 %s, %d회 복용"
    }
  ]
}
```
위와 같이 한 문제에 단답형 선지가 여러 개 존재하는 경우, 아래와 같이 응답을 작성합니다.

```json
{
  "question_id": "999",
  "answer": "타이레놀$2$타이레놀$2$타이레놀$2"
}
```

**문제유형별 answer schema 3: long_answer**
```json
{
  "question_id": 1,
  "answer": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas fermentum nisi ligula. Mauris metus nulla, cursus in ante non, sollicitudin ullamcorper est. Sed nec ante et velit malesuada ornare vitae at nunc. Maecenas dignissim sollicitudin mi quis pulvinar. Integer imperdiet odio sit amet lacinia suscipit. Fusce bibendum interdum risus, id lobortis ipsum rhoncus et. Nam ac tortor non lectus bibendum auctor eget in ex."
}
```

---


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
