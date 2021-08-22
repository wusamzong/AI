import io
from PIL import Image
from requests.models import Response
import matplotlib.pyplot as plt  # type: ignore
import numpy as np  # type: ignore
import time
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

from thsr_ticket.remote.http_request import HTTPRequest
from thsr_ticket.model.web.booking_form.booking_form import BookingForm
from thsr_ticket.model.web.booking_form.ticket_num import AdultTicket
from thsr_ticket.model.web.confirm_train import ConfirmTrain
from thsr_ticket.model.web.confirm_ticket import ConfirmTicket
from thsr_ticket.view_model.avail_trains import AvailTrains
from thsr_ticket.view_model.error_feedback import ErrorFeedback
from thsr_ticket.view_model.booking_result import BookingResult
from thsr_ticket.view.web.booking_form_info import BookingFormInfo
from thsr_ticket.view.web.show_avail_trains import ShowAvailTrains
from thsr_ticket.view.web.show_error_msg import ShowErrorMsg
from thsr_ticket.view.web.confirm_ticket_info import ConfirmTicketInfo
from thsr_ticket.view.web.show_booking_result import ShowBookingResult
from thsr_ticket.view.common import history_info
from thsr_ticket.model.db import ParamDB, Record
from thsr_ticket.ml.captcha_solver import solve_captcha

class BookingFlow:
    def __init__(self) -> None:
        self.client = HTTPRequest()

        self.book_form = BookingForm()
        self.book_info = BookingFormInfo()

        self.confirm_train = ConfirmTrain()
        self.show_avail_trains = ShowAvailTrains()

        self.confirm_ticket = ConfirmTicket()
        self.confirm_ticket_info = ConfirmTicketInfo()

        self.error_feedback = ErrorFeedback()
        self.show_error_msg = ShowErrorMsg()

        self.db = ParamDB()
        self.record = Record()

        self.select_hist: int = 0
        self.countinue_choice: bool = True
        self.date: str = "2021/09/17"
        self.period:str = "12~16" # 預訂票的時間段

    def mode(self) ->None:
        if(self.countinue_choice):
            return self.countinue()
        else:
            return self.run_once()

        sel = input("要持續訂票嗎？(Y/N): ")
        if(sel == 'Y'):
            return self.countinue()
        else:
            return self.run_once()

    def run_once(self) -> Response:

        self.show_history() # 顯示歷史紀錄 -->> model.db去獲得歷史紀錄


        # First page. Booking options
        self.set_start_station() # 顯示&輸入 起始站資訊 ->> (view.web.booking_form_info || model.db) && model.web.booking_form.booking_form
        self.set_dest_station()  # 顯示&輸入 終點站資訊 ->> (view.web.booking_form_info || model.db) && model.web.booking_form.booking_form
        self.book_form.outbound_date = self.book_info.date_info("出發") # 顯示&輸入 搭乘日期 -->> view.web.booking_form_info && model.web.booking_form
        self.set_outbound_time() # 顯示&輸入 出發時間 ->> (view.web.booking_form_info || model.db) && model.web.booking_form.booking_form
        self.set_adult_ticket_num() # 顯示&輸入 成人票數 -->> (view.web.booking_form_info || model.db) && model.web.booking_form.booking_form
        self.book_form.security_code = self.input_security_code() # 叫出驗證碼 -->> remote.http_request #辨識驗證碼
        form_params = self.book_form.get_params() # 將所有剛剛輸入到book_form的資料儲存下來 -->> remote.http_request
        result = self.client.submit_booking_form(form_params) # 將資料傳給伺服器 -->> remote.http_request
        
        if self.show_error(result.content):
            return result

        # Second page. Train confirmation
        avail_trains = AvailTrains().parse(result.content) # 爬到並儲存有開的的班次的資料 ->> view.web.avail_trains
        sel = self.show_avail_trains.show(avail_trains) # 顯示爬到的班次 + 儲存使用者選擇的班次 ->> view.web.show_avail_trains
        value = avail_trains[sel-1].form_value  # 找到使用者選擇的班次在html中的value ->> view.web.avail_trains
        self.confirm_train.selection = value  # 將獲得的資料「偵錯後」儲存在comfirm_train 的 params中 ->> model.web.confirm_train
        confirm_params = self.confirm_train.get_params() # 將comfirm_train的params取出 ->> model.web.confirm_train
        result = self.client.submit_train(confirm_params) # 將資料傳給伺服器 ->> remote.http_request
        if self.show_error(result.content):
            return result
        
        # Third page. Ticket confirmation
        self.set_personal_id() # 顯示&輸入 身份證字號 ->> (view.web.confirm_ticket_info || model.db) && model.web.confirm_ticket
        self.set_phone() # 顯示&輸入 電話號碼 ->> (view.web.confirm_ticket_info || model.db) && model.web.confirm_ticket
        ticket_params = self.confirm_ticket.get_params() # 將資料取出 ->> model.web.confirm_ticket
        result = self.client.submit_ticket(ticket_params) # 將資料傳給伺服器 ->> remote.http_request
        if self.show_error(result.content):
            return result
        
        result_model = BookingResult().parse(result.content) #爬取訂票結果的資料 -->> view_model.booking_result
        book = ShowBookingResult() #叫出訂票結果的view model -->> view.web.show_booking_result
        book.show(result_model) # 連接 m && vm
        print("\n請使用官方提供的管道完成後續付款以及取票!!")

        self.db.save(self.book_form, self.confirm_ticket)
        return result

    def countinue(self) -> Response:
        self.show_history() # 顯示歷史紀錄 -->> model.db去獲得歷史紀錄
        self.time_between()

        result = self.page_first()
        self.page_second(result)
        
        # Third page. Ticket confirmation
        self.set_personal_id() # 顯示&輸入 身份證字號 ->> (view.web.confirm_ticket_info || model.db) && model.web.confirm_ticket
        self.set_phone() # 顯示&輸入 電話號碼 ->> (view.web.confirm_ticket_info || model.db) && model.web.confirm_ticket
        ticket_params = self.confirm_ticket.get_params() # 將資料取出 ->> model.web.confirm_ticket
        result = self.client.submit_ticket(ticket_params) # 將資料傳給伺服器 ->> remote.http_request
        if self.show_error(result.content):
            return result
        
        result_model = BookingResult().parse(result.content) #爬取訂票結果的資料 -->> view_model.booking_result
        book = ShowBookingResult() #叫出訂票結果的view model -->> view.web.show_booking_result
        book.show(result_model) # 連接 m && vm
        print("\n請使用官方提供的管道完成後續付款以及取票!!")

        self.db.save(self.book_form, self.confirm_ticket)
        return result

    def show_history(self) -> None: 
        hist = self.db.get_history()
        if self.select_hist is not None:
            self.record = hist[self.select_hist]
            return

        h_idx = history_info(hist)
        if h_idx is not None:
            self.record = hist[h_idx]
    
    def time_between(self) -> None:
        if(self.period is not None):
            return
        self.period = input("想要搭乘的時間段：(ex.12~15, enter則不限定時間)")
        return

    def page_first(self)->None:
        while True:
            # First page. Booking options
            self.set_start_station() # 顯示&輸入 起始站資訊 ->> (view.web.booking_form_info || model.db) && model.web.booking_form.booking_form
            self.set_dest_station()  # 顯示&輸入 終點站資訊 ->> (view.web.booking_form_info || model.db) && model.web.booking_form.booking_form
            self.set_outbound_date() # 顯示&輸入 搭乘日期 -->> view.web.booking_form_info && model.web.booking_form
            self.set_outbound_time() # 顯示&輸入 出發時間 ->> (view.web.booking_form_info || model.db) && model.web.booking_form.booking_form
            self.set_adult_ticket_num() # 顯示&輸入 成人票數 -->> (view.web.booking_form_info || model.db) && model.web.booking_form.booking_form
            self.book_form.security_code = self.input_security_code() # 叫出驗證碼 -->> remote.http_request #辨識驗證碼
            form_params = self.book_form.get_params() # 將所有剛剛輸入到book_form的資料儲存下來 -->> remote.http_request
            result = self.client.submit_booking_form(form_params) # 將資料傳給伺服器 -->> remote.http_request
            
            if self.show_error(result.content):
                sleep(30)
            else:
                return result
    
    def page_second(self, result)->None:
        # Second page. Train confirmation
        while True:
            avail_trains = AvailTrains().parse(result.content) # 爬到並儲存有開的的班次的資料 ->> view.web.avail_trains
            period = self.period
            sel = self.select_train(avail_trains ,period) # 顯示爬到的班次 或 儲存使用者選擇的班次 ->> view.web.show_avail_trains
            if(sel is None):
                sleep(30)
                result = self.page_first()
            else:
                value = avail_trains[sel-1].form_value  # 找到使用者選擇的班次在html中的value ->> view.web.avail_trains
                self.confirm_train.selection = value  # 將獲得的資料「偵錯後」儲存在comfirm_train 的 params中 ->> model.web.confirm_train
                confirm_params = self.confirm_train.get_params() # 將comfirm_train的params取出 ->> model.web.confirm_train
                result = self.client.submit_train(confirm_params) # 將資料傳給伺服器 ->> remote.http_request
                if self.show_error(result.content):
                    sleep(30)
                    result = self.page_first()
                else:
                    break
                    


    def set_start_station(self) -> None:
        if self.record.start_station is not None:
            self.book_form.start_station = self.record.start_station
        else:
            self.book_form.start_station = self.book_info.station_info("啟程")

    def set_dest_station(self) -> None:
        if self.record.dest_station is not None:
            self.book_form.dest_station = self.record.dest_station
        else:
            self.book_form.dest_station = self.book_info.station_info("到達")

    def set_outbound_date(self) -> None:
        if(self.date is not None):
            self.book_form.outbound_date = self.date
            return
        
        if self.book_form.outbound_date is not None:
            return
        else:
            self.book_form.outbound_date = self.book_info.date_info("出發")

    def set_outbound_time(self) -> None:
        if self.record.outbound_time is not None:
            self.book_form.outbound_time = self.record.outbound_time
        else:
            self.book_form.outbound_time = self.book_info.time_table_info()

    def set_adult_ticket_num(self) -> None:
        if self.record.adult_num is not None:
            self.book_form.adult_ticket_num = self.record.adult_num
        else:
            sel = self.book_info.ticket_num_info("大人", default_value=1)
            self.book_form.adult_ticket_num = AdultTicket().get_code(sel) #將數量和票種整理為網站指定的value ex.3張大人=>3F 5張大人=>5F

    def select_train(self, avail_trains, period:str) -> int:
        if period is not None:
            return self.show_avail_trains.choice_period(avail_trains, period)
        else:
            return self.show_avail_trains.show(avail_trains)

    def set_personal_id(self) -> None:
        if self.record.personal_id is not None:
            self.confirm_ticket.personal_id = self.record.personal_id
        else:
            self.confirm_ticket.personal_id = self.confirm_ticket_info.personal_id_info()

    def set_phone(self) -> None:
        if self.record.phone is not None:
            self.confirm_ticket.phone = self.record.phone
        else:
            self.confirm_ticket.phone = self.confirm_ticket_info.phone_info()

    def input_security_code(self) -> str:
        model_path = './thsr_ticket/ml/model.pth'
        print("等待驗證碼...")
        book_page = self.client.request_booking_page() #開啟頁面
        img_resp = self.client.request_security_code_img(book_page.content) #獲得照片網址
        image = Image.open(io.BytesIO(img_resp.content)) #透過PIL的Image來儲存驗證碼
        code = solve_captcha(image, model_path,False)
        
        print("辨識出的驗證碼:")
        print(code)
        # img_arr = np.array(image) #用numpy來將圖片轉為array
        # plt.imshow(img_arr)
        # plt.show() #透過plt來顯示圖面
        return code #回傳輸入的驗證碼



    def show_error(self, html: bytes) -> bool:
        errors = self.error_feedback.parse(html)
        if len(errors) == 0:
            return False

        self.show_error_msg.show(errors)
        return True
