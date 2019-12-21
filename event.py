class event:
  def __init__(self,name,start_date,end_date):
    self.name = name
    self.start_date = start_date
    self.end_date = end_date

class pt_event:
  def __init__(self,name,event_pt,lastmap_pt,daily_mission_pt,black_pt,shop_total_pt,shop_total_pt_lazy):
    self.name = name
    self.event_pt = event_pt
    self.lastmap_pt = lastmap_pt
    self.daily_mission_pt = daily_mission_pt
    self.black_pt = black_pt
    self.shop_total_pt = shop_total_pt
    self.shop_total_pt_lazy = shop_total_pt_lazy