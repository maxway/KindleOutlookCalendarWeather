原版本[ReadMe](README_original.md)

# Fork项目的需求
  不太需要RSS和Outlook日历功能，需要一个可远程更新同步的Todo List，最开始使用Google Sheet API调通，但因为需要翻墙，所以改为国内可以正常访问的维格表Vika，语雀表应该也可以用，未作适配。
  
# 这个版本和原版有以下区别：
* 增加了Vika表的展示
* 移除了RSS和Outlook日历功能
* 移除了失效的Outlook权限获取工具
* 移除了无关的代码

# 界面展示
![微信图片_20241008121523](https://github.com/user-attachments/assets/b3bda8f5-e256-487b-b44a-a2bedaf3ddcc)

# Vika表配置流程
## 1. Vika表网站：https://vika.cn/
## 2. 默认会有一个空表：
![3416662669c21e2abf1a1f91a998de3](https://github.com/user-attachments/assets/87fcdfae-d6dd-40cd-a940-4b22be58e176)
## 3. 获取表id：
![微信图片_20241008121832](https://github.com/user-attachments/assets/fafc52b5-ea76-4467-810f-057a29a2fca3)
## 4. 获取Token：
### 打开个人设置：
![微信图片_20241008122350](https://github.com/user-attachments/assets/0a5c3d8d-6ac4-4497-8ce2-7f6dd411c8d6)
### 复制开发者Token：
![微信图片_20241008122358](https://github.com/user-attachments/assets/69a587c4-e6c0-4971-9226-73ae3d917b01)

## 5. 修改配置bin/config.ini

# 一些限制
* 最多只拉取Vika表的前15行，仅读取第一列数据
* 没有做换行处理，太多字数的将会覆盖界面上其它元素
* 因为Vika表API每月有调用次数限制，建议配置为至少15分钟以上拉取一次vika表（900秒），0-7点不会刷新
* 界面1分钟刷新一次，0-7点不刷新
* 耗电较高，建议连接充电线使用
