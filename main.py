from typing import Optional
from fastapi import FastAPI, Request, UploadFile, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from urllib.parse import urlencode
import urllib.parse
from camera import *
from barcode_crawling import *
from pydantic import BaseModel
from oracleDB import OracleDB
from nltk_token import *
import json
from expert_nono import *

db = OracleDB()

app = FastAPI()
templates = Jinja2Templates(directory="RomanPick")
app.mount("/RomanPick", StaticFiles(directory="RomanPick"), name="RomanPick")

# 메인 인트로 화면
@app.get("/")
def read_root(request:Request):
    return templates.TemplateResponse('01_intro.html',{"request" : request})

# 메인 클러스터 선택 화면
@app.get("/main")
def read_main(request:Request):
    return templates.TemplateResponse('02_main.html', {"request" : request})

@app.post("/search/print")
async def search_list(request:Request):
    data = await request.json()
    novel_list = db.search_novel(**data)
    return novel_list

# 검색 기능
@app.post("/search")
def search(request: Request, input_text: str = Form(...), category: str = Form(...)):
    return templates.TemplateResponse('06_search_list.html', {"request" : request, "input_text": input_text, "category":category})

@app.get("/search/detail/{novel_no}")
def detail(request:Request, novel_no:str):
    novel_no = urllib.parse.unquote(novel_no)
    data = db.select_novel(novel_no)
    
    go = "title"
    return templates.TemplateResponse('04_List_title.html', {"request" : request, "data":data, "go":go})
        
# ajax 랜덤 데이터 추출, canvas 출력
@app.get("/main/{item}")
def pick_cluster(request:Request, item:str):
    label = urllib.parse.unquote(item)
    title_List = db.random_title_list(label)
    keyword_list = db.random_keyword_list(label)
    text_list = title_List+keyword_list
    return {"textList" :text_list}

# DB에서 라벨에 맞는 제목이 word와 같은게 있으면 title로, 없으면 keyword로
@app.get("/main/{item}/{word}")
def item_title(request:Request, item:str, word:str):
    label = urllib.parse.unquote(item)
    word = urllib.parse.unquote(word)
    select = {
        "label":label,
        "novel_nm":word
    }
    result = db.novel_nm_select(**select)
    
    if result is None:
        go = "keyword"
        data = {
            "word":word,
            "novel_no":"",
            "novel_nm":"",
            "novel_writer":"",
            "novel_synopsis":"",
            "novel_cover": ""
            }
        return templates.TemplateResponse('04_List_title.html', {"request" : request, "data":data, "go": go, "label" :label})
    else:
        data = {
            "novel_no":result[0],
            "novel_nm":result[1],
            "novel_writer":result[2],
            "novel_synopsis":result[3],
            "novel_cover": result[4]
        }
        go = "title"
        return templates.TemplateResponse('04_List_title.html', {"request" : request, "data":data, "go":go})
    
@app.get('/label/keyword')
def label_keyword(label:str, keyword:str):
    novel_list = db.label_keyword(label, keyword)
    return novel_list

@app.post('/novel_cover_select')
async def novel_cover(request:Request):
    data = await request.json()
    synopsis = db.novel_cover_select(data.get('img'))
    return synopsis

# ajax 카메라 동영상 바코드 인식 
@app.get("/camera_start")
async def camera_start():
    data = await run_camera()
    return data

# ajax 이미지에서 바코드 인식
@app.post("/img_barcode")
async def img_barcode(imageFile: UploadFile):
    image = await imageFile.read()
    result = image_barcode(image)
    return result

# ajax 텍스트로 isbn 입력 
@app.get("/input_isbn")
async def input_isbn(isbn: str):
    result = crawling_isbn(isbn)
    if result['isData']:
        data = {
            "result":result['isData'],
            "title" :result['title'],
            "textData" : result['text'],
            "book_code": result['book_code'],
            "img" : result['img']
        }
    else:
        data = {"result":result['isData']}
    return data

# 바코드 결과 화면
@app.get("/barcode")
async def barcode_result(request: Request, img:str, textData:str, title:str):
    data = {
        'novel_nm' : title,
        'novel_synopsis' : textData,
        'novel_cover':img
    }
    go = "barcode"
    return templates.TemplateResponse('04_List_title.html', {"request" : request, "data":data, "go":go})

# 선택된 소설과 유사한 소설 6개 추출 ajax
@app.get("/cosine/{novel_no}")
async def select_novel(novel_no:str):
    novel_no = urllib.parse.unquote(novel_no)
    novel_no = int(novel_no)
    data = db.select_cosine(novel_no)
    # novel_no로 소설 정보를 다 가져오는 쿼리
    return data

@app.post("/select/novel_no_6")
async def select_novel_6(request:Request):
    data = await request.json()
    novel_list = []
    for val in data.values():
        novel_list.append(db.select_novel(val))
    return novel_list

@app.post("/expert_noun")
async def noun_expert(request:Request):
    data = await request.json()
    text_list = extract_nouns(data.get('synposis'))
    novel_list = db.isbn_select_novel(text_list)
    return novel_list

@app.get("/select/emotion/{emotion}")
async def select_emotion(request: Request, emotion:str):
    emotion = urllib.parse.unquote(emotion)
    go = "emotion"
    data = {
        "novel_no":"",
        "novel_nm":"",
        "novel_writer":"",
        "novel_synopsis":"",
        "novel_cover": ""
            }
    return templates.TemplateResponse('04_List_title.html', {"request" : request, "data":data, "go": go, "emotion" :emotion})

@app.post('/emotion/novel')
async def emotion_novel(request:Request):
    data = await request.json()
    novel_list = db.execute_emotion_query(data.get('emotion'))
    return novel_list

@app.get("/select/novel_no")
def select_novel(pic_numver:int):
    return db.select_novel(pic_numver)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)

