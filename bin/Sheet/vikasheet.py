"""Module Vika API"""

import requests


class VikaSheet:
    """vika sheet simple API, fetch the data by sheet_id & token"""

    __version__ = "0.0.1"
    BASE_URL = "https://api.vika.cn/fusion/v1/datasheets"
    PARAMS = "records?maxRecords=15"

    def __init__(self, sheet_id, token):
        self.url = f"{self.BASE_URL}/{sheet_id}/{self.PARAMS}"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

    def get_records(self):
        """pull data from vika"""
        try:
            response = requests.get(
                self.url, headers=self.headers, timeout=10
            )  # 设置超时时间为10秒
            response.raise_for_status()  # 检查请求是否成功
            return response.json()
        except requests.exceptions.Timeout:
            print("The request timed out.")
            return None
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred: {err}")
            return None
        except requests.exceptions.RequestException as err:
            print(f"Error occurred: {err}")
            return None

    def get_titles(self):
        """filter title col"""
        records = self.get_records()
        if records is None:
            return None
        titles = []
        for record in records["data"]["records"]:
            fields = record.get("fields", {})
            title = fields.get("标题")
            if title:
                titles.append(title)
        return titles
