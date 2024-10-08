import urllib.request
import json

class GoogleSheet:
    def __init__(self, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id

    def get_column_data(self):
        url = f'https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}/gviz/tq?tqx=out:json&range=A1:A'
        response = urllib.request.urlopen(url)
        data = response.read().decode()
        
        # 解析JSONP格式的数据
        json_data = json.loads(data[data.find("(") + 1 : data.rfind(")")])
        rows = json_data['table']['rows']
        
        # 获取第一列的数据
        first_column = [row['c'][0]['v'] for row in rows if row['c'][0]]
        return first_column

# # 使用示例
# spreadsheet_id = '1PFX3AO4M4cYuO-5s8DjxfN8ty4Op7p27gQuMhANVPpU'

# google_sheet = GoogleSheet(spreadsheet_id)
# first_column_data = google_sheet.get_column_data()

# for data in first_column_data:
#     print(data)
