from typing import List

from thsr_ticket.view.web.abstract_show import AbstractShow
from thsr_ticket.view_model.avail_trains import Train


class ShowAvailTrains(AbstractShow):
    def show(self, trains: List[Train], select: bool = True) -> int:
        if len(trains) == 0:
            print("No available train!")
            return None
        
        for idx, train in enumerate(trains, 1):
            dis_str = ""
            if "Early" in train.discount:
                dis_str += "早鳥{} ".format(train.discount["Early"])
            if "College" in train.discount:
                dis_str += "大學生{}".format(train.discount["College"])
            print("{}. {:>4s} {:>3}~{} {:>3} {:4}".format(
                idx, train.id, train.depart, train.arrive, train.travel_time, dis_str
            ))


        
        if select:
            return int(input("輸入選擇(預設: 1): ") or 1)
        return None
    
    def choice_period(self, trains: List[Train], period:str) -> int:
        if len(trains) == 0:
            print("No available train!")
            return None

        period = period.split("~")
        period[0] = int(period[0])
        period[1] = int(period[1])

        for idx, train in enumerate(trains, 1):
            dis_str = ""
            if "Early" in train.discount:
                dis_str += "早鳥{} ".format(train.discount["Early"])
            if "College" in train.discount:
                dis_str += "大學生{}".format(train.discount["College"])
            
            time = int(train.depart.split(":")[0])
            if(time>=period[0] and time<=period[1]):
                return int(idx)


            # print("{}. {:>4s} {:>3}~{} {:>3} {:4}".format(
            #     idx, train.id, train.depart, train.arrive, train.travel_time, dis_str
            # ))

            # return int(input("輸入選擇(預設: 1): ") or 1)
        return None



