# 高鐵訂票小幫手



![](https://github.com/BreezeWhite/THSR-Ticket/workflows/build/badge.svg)

**!!--純研究用途，請勿用於不當用途--!!**

此程式提供另一種輕便的方式訂購高鐵車票，操作介面為命令列介面。相較於使用網頁訂購，本程式因為省卻了渲染網頁介面的時間，只保留最核心的訂購功能，因此能省下大量等待的時間。

## 執行

本程式由python語言所寫成，因此必須先安裝python才能夠使用。官方下載網址[點這裡](https://www.python.org/downloads/release/python-381/)

首先先將程式碼下載到本機，執行以下指令或是直接按右上方的下載按鈕

```
git clone https://github.com/BreezeWhite/THSR-Ticket.git
```

再來進入到資料夾中

```
cd thsr_ticket
```

安裝必要的套件

```
python -m pip install -r requirements.txt
```

最後執行程式

```
python thsr_ticket/main.py
```
## test
2020/11/26
21:11 台北往台中 
default 1  booking_flow.py 60,61

##
訂高鐵票/.db/history.json 歷史紀錄
view/web/show_avail_trains 顯示可選擇的班次 #可以去輸入默認班次
view/web/booking_form_info 進入網站後的第一頁 
model/web/bookingform/station_mapping 有數字對應到車站的關係
要輸入的資訊有：


view_model/abstract_view_model 查看網站(用bs4)


## 注意事項!!!

本程式依舊有許多尚未完成的部分，僅具備基本訂購的功能，若是僅需要訂購成人票、且無特殊需求者，此程式對您而言是加速訂購流程的方便小工具。不符合以上描述者，目前仍建議使用官方網頁進行訂購。

#### 提供功能

- [x] 選擇啟程、到達站
- [x] 選擇出發日期、時間
- [x] 選擇班次
- [x] 選擇**"成人"**票數
- [x] 輸入驗證碼
- [x] 輸入身分證字號
- [x] 輸入手機號碼
- [x] 保留此次輸入紀錄，下次可快速選擇此次紀錄

#### 未提供功能

以下功能為未提供輸入的選項，但程式具備相關功能，可依照自身需求、對程式進行修改

- [ ] 選擇車廂種類(標準/商務)
- [ ] 座位喜好(靠窗/走道)
- [ ] 訂位方式(依時間搜尋車次/直接輸入車次號碼)
- [ ] 輸入孩童/愛心/敬老/學生優惠票數
- [ ] 僅顯示早鳥優惠票

#### 未完成功能

- [ ] 重新產生認證碼
- [ ] 語音播放認證碼
- [ ] 重新查詢車次
- [ ] 輸入護照號碼
- [ ] 輸入市話
- [ ] 輸入電子郵件
- [ ] 會員購票

