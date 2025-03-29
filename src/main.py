import json
import os
import sys
import time
import requests
os.makedirs("./src/json", exist_ok=True)

pokerFansIdResume = {"datas": []}

# 設定 API 參數
evenBeginTime = "2025-03-24"
evenEndTime = "2025-03-30"
rankingBountyUrl = "https://www.citypoker.vip/prod-api/system/data/rankingBounty"
rankingBountyParams = {
    "pageNum": 1,
    "pageSize": 100000, # 單次顯示數據數量
    "evenBeginTime": evenBeginTime,
    "evenEndTime": evenEndTime,
}

try:
    rankingBountyResponse = requests.get(rankingBountyUrl, params=rankingBountyParams)
    rankingBountyResponse.raise_for_status()
    rankingBountyData = rankingBountyResponse.json()

    if not rankingBountyData.get("data") or not rankingBountyData["data"].get("rows"):
        print("API 回應中沒有 'data' 或 'rows'，檢查 API 是否正確")
        sys.exit(1)

except requests.exceptions.RequestException as e:
    print(f"請求 rankingBounty 失敗: {e}")
    sys.exit(1)

resumeUrl = "https://www.citypoker.vip/prod-api/system/data/even/resume"

# 處理每一個玩家的資料
for row in rankingBountyData["data"]["rows"]:
    pokerFansId = row.get("pokerFansId")
    if not pokerFansId:
        print("警告: 跳過無效的 pokerFansId")
        continue

    resumeParams = {
        "pokerFansId": pokerFansId,
        "evenBeginTime": evenBeginTime,
        "evenEndTime": evenEndTime,
        "type": 1
    }

    try:
        # 請求 resume 資料
        resumeResponse = requests.get(resumeUrl, params=resumeParams)
        resumeResponse.raise_for_status()
        resumeData = resumeResponse.json()

        if not resumeData.get("data"):
            print(f"警告: 玩家 {pokerFansId} 沒有對應的 resume 資料，跳過")
            continue

        pokerFansIdResume["datas"].append({
            "pokerFansId": pokerFansId,
            "resume": [
                {
                    "tournamentName": data.get("tournamentName", "未知"),
                    "tournamentDate": data.get("tournamentDate", "未知"),
                    "KO integration": data.get("integration", 0)
                } for data in resumeData["data"] if data]
        })

        print(f"成功獲取玩家 {pokerFansId} 對應的 resume 資料")

    except requests.exceptions.RequestException as e:
        print(f"請求 resume 失敗 (pokerFansId: {pokerFansId}): {e}")
        continue  # 繼續處理下一個玩家，不會終止整個程式

    # 限制請求頻率，避免被封鎖
    time.sleep(0.1)

# 確保 pokerFansIdResume["data"] 不是空的才寫入 JSON
if pokerFansIdResume["datas"]:
    pokerFansIdResume["total"] = len(pokerFansIdResume["datas"])  # 資料筆數
    try:
        with open("./src/json/pokerFansIdResume.json", "w", encoding="utf-8") as file:
            json.dump(pokerFansIdResume, file, indent=4, ensure_ascii=False)
        print("pokerFansIdResume.json 檔案已成功儲存")
    except Exception as e:
        print(f"pokerFansIdResume.json 儲存失敗: {type(e).__name__}: {e}")
else:
    print("沒有可儲存的數據，pokerFansIdResume.json 檔案未建立")
    


bonus = {
    600: 50,
    1200: 50,
    1700: 50,
    2300: 50,
    3400: 50,
    6600: 100,
    11000: 150,
    22000: 250,
    33000: 400,
    54000: 500,
}

tournamentDatas = {"datas": []}

for data in pokerFansIdResume["datas"]:
    for resume in data["resume"]:
        try:
            fee = int(resume["tournamentName"].split("#")[0].split("-")[0].split(" ")[0].replace("TLT", "").replace("限時錦標賽", ""))
            found = next((item for item in tournamentDatas["datas"] if item["fee"] == fee), None)
            if found:
                found["times"] += 1
            else:
                tournamentDatas["datas"].append({"fee": fee, "times": 1})
        except ValueError:
            print(f"警告: 無法解析比賽名稱 '{resume['tournamentName']}'")

for item in tournamentDatas["datas"]:
    if item["fee"] in bonus:
        item["bonus"] = bonus[item["fee"]]* item["times"]
    else: 
        print(f"未擁有 {item["fee"]} 的獎金資料")

        
if tournamentDatas["datas"]:
    tournamentDatas["totalBonus"] = sum(item["bonus"] for item in tournamentDatas["datas"])
    try:
        with open("./src/json/tournamentDatas.json", "w", encoding="utf-8") as file:
            json.dump(tournamentDatas, file, indent=4, ensure_ascii=False)
        print("tournamentDatas.json 檔案已成功儲存")
    except Exception as e:
        print(f"tournamentDatas.json 儲存失敗: {type(e).__name__}: {e}")
else:
    print("沒有可儲存的數據，JSON 檔案未建立")