# https://www.citypoker.vip/rankings?redirect=/
import json
import os
import requests

os.makedirs("./src/json", exist_ok=True)
with open(f"./src/json/rankingBounty.json", "w", encoding= "utf-8") as file:
    json.dump(requests.get(f"https://www.citypoker.vip/prod-api/system/data/rankingBounty", params={
    "pageNum": 1, # 顯示頁數
    "pageSize": 415, # 每頁顯示筆數
    "evenBeginTime": "2025-03-24", # 資料起始時間
    "evenEndTime": "2025-03-30" ,# 資料起始時間
    }).json(), file, indent=4)

