import requests

class VikaSheet:
    def __init__(self, sheet_id, token):
        self.url = f"https://api.vika.cn/fusion/v1/datasheets/{sheet_id}/records?maxRecords=10"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

    def get_records(self):
        print('vika:' + self.url)
        print(self.headers)
        response = requests.get(self.url, headers=self.headers)
        return response.json()

    def get_titles(self):
        records = self.get_records()
        titles = []
        for record in records['data']['records']:
            fields = record.get('fields', {})
            title = fields.get('标题')
            if title:
                titles.append(title)
        return titles