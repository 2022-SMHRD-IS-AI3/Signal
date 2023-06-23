import requests as req
from bs4 import BeautifulSoup as bs
import re

def crawling_isbn(isbn:str):
    isbn = isbn # 수집한 isbn
    url = 'https://dl.nanet.go.kr/search/searchInnerList.do'
    data = {
        "searchType" :  "INNER_SEARCH",
        "resultType" : "INNER_SEARCH_DETAIL",
        "queryText":f"{isbn}:ALL:AND", # isbn 검색
        "selZone":"ALL",
        "dpBranch":"ALL",
        "synonymYn" :"Y",
        "searchMethod" : "L",
        "searchClass":"S",
    }
    res = req.post(url,data=data)
    soup = bs(res.text,'lxml')
    div = soup.find('div', class_="searchList")
    aTag = div.select('ul.list>li>a')
    try:
        jsDetail = aTag[0]['href']
    except:
        return {"isData" : False}
    
    
    mono = jsDetail[30:-7] 
    
    urlDetail = f'https://dl.nanet.go.kr/search/searchInnerDetail.do?searchType=INNER_SEARCH&resultType=INNER_SEARCH_DETAIL&searchMehtod=L&searchClass=S&controlNo={mono}&queryText=&zone=&fieldText=&prevQueryText=&prevPubYearFieldText=&languageCode=&synonymYn=&refineSearchYn=&pageNum=&pageSize=&orderBy=&topMainMenuCode=&topSubMenuCode=&totalSize=1&totalSizeByMenu=1&seqNo=&hanjaYn=Y&knowPub=&isdb=&isdbsvc=&tt1=&down=&checkedDbIdList=&baseDbId=&selectedDbIndexIdList=&caller=&asideState=true&dpBranch=ALL&journalKind=&selZone=ALL&searchQuery='

    resDetail = req.get(urlDetail)
    soupDetail = bs(resDetail.text,'lxml')
    book_code = soupDetail.select_one('#DP_CALL_NO span').text[0]
    titleText = soupDetail.select_one('#DP_TITLE_FULL .iBold').text
    titleText = re.search(r"([^:\/]+)", titleText)
    title = titleText.group(1) if titleText else ""
    try:
        textData = soupDetail.select_one('.item.item1 div#tab1').text # 출판사소개 가져오기
    except:
        try:
            textData = soupDetail.select_one('.item.item2 div#tab2').text # 책속에서 가져오기
        except:
            try:
                textData = soupDetail.select_one('.scrollY.on p').text # 목차 가져오기
            except:
                textData = title
    
    try:        
        imgUrl = "https://dl.nanet.go.kr" + soupDetail.select_one('.imgBox .img img')['src']
    except:
        imgUrl = ""

    return {"isData": True, "title" : title, "text":textData, "img":imgUrl, "book_code":book_code}