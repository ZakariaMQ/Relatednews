from datetime import datetime as dt, timedelta
from googleapiclient.discovery import build
from googleapiclient import http
from dotenv import load_dotenv
import os

from style import style

load_dotenv(".env")

class News:

    def __init__(self) -> None:
        self._api_key = os.environ.get("API")
        self._api_keys = [os.environ.get("API1"), os.environ.get("API2"), os.environ.get("API3")]
        self._cx = os.environ.get("CX")
        self.queries = self.__queries()


    @staticmethod
    def __queries():
        with open("queries.txt", "r", encoding="utf-8") as f:
            return f.read().split("\n")
        
    def __search(self, query):
        service = build('customsearch', 'v1', developerKey=self._api_key)
        
        try:
            return service.cse().list(q=query, cx=self._cx).execute()
        except http.HttpError:
            for api in self._api_keys:
                service = build('customsearch', 'v1', developerKey=api)
                try:
                    return service.cse().list(q=query, cx=self._cx).execute()
                except http.HttpError:
                    continue
            raise Exception("No available key..")

    def __build_html(self, result:dict, start:int=1) -> str:

        html = []

        for i, item in enumerate(result['items'], start=start):
            element = f"""
                    <div class="search-result">
                        <p><b>News No. {i}<b></p>
                        <h3><a href="{item['link']}" target="_blank">{item['title']}</a></h3>
                        
                        <div class="result-details">
                            <p><b>{item.get('snippet', '')}</b></p>
                        </div>
                        
                        <div class="meta-info">
                            <span class="info-item">Published on: {item.get('formattedUrl', '')}</span>
                        </div>
                    </div>
                    """
            html.append(element)
        
        return "\n".join(html)
    
    
    def __body(self):
        whole_page = []
        start = 1

        for query in self.queries:
            result =  self.__search(query=query)
            whole_page.append(self.__build_html(result=result, start=start))
            start += 10

        return whole_page
    
    @staticmethod
    def __cache_logic():
        html_files = [f for f in os.listdir("./cache") if f.endswith(".html")]

        if len(html_files) == 0:
            return False
        
        elif len(html_files) == 1:
            name, _ = str(*html_files).split(".")
            _, date_stamp = name.split("-")
            
            if not date_stamp:
                os.remove(f"./cache/{str(*html_files)}")
                return False
            
            imestamp_datetime = dt.utcfromtimestamp(int(date_stamp))
            time_difference = dt.utcnow() - imestamp_datetime
            
            if time_difference >= timedelta(hours=24):
                os.remove(f"./cache/{str(*html_files)}")
                return False
            
            return str(*html_files)
            
        else:
            for f in html_files:
                os.remove(f)
            return False

    
    def get_news(self):
        esc = "\n"
        cached_file = __class__.__cache_logic()
        
        if cached_file:
            with open(f"./cache/{cached_file}", "r", encoding="utf-8") as f:
                return f.read()

        index = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Search Results</title>
                    <style>
                        {style}
                    </style>
                </head>
                <body>
                    {esc.join(self.__body())}
                </body>
                </html>
            """
        with open(f"./cache/index-{int(dt.utcnow().timestamp())}.html", "w", encoding="utf-8") as f:
            f.write(index)

        return index