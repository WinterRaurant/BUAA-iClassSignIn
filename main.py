import requests
import json
import time
import datetime

student_id = ''

# 获取用户id和sessionId，为查询课表和根据课表打卡做准备
url = 'https://iclass.buaa.edu.cn:8346/app/user/login.action'
para = {
    'password': '',
    'phone': student_id,
    'userLevel': '1',
    'verificationType': '2',
    'verificationUrl': ''
}

res = requests.get(url=url, params=para)
userData = json.loads(res.text)
userId = userData['result']['id']
sessionId = userData['result']['sessionId']

cnt = 0 # 连续没课的天数，超过7天说明放假了
today = datetime.datetime.today()
for i in range(120): 
    if cnt == 7:
        break

    date = today + datetime.timedelta(days=i)
    dateStr = date.strftime('%Y%m%d')
    # 查询课表
    url = 'https://iclass.buaa.edu.cn:8346/app/course/get_stu_course_sched.action'
    para = {
        'dateStr': dateStr,
        'id': userId
    }
    headers = {
        'sessionId': sessionId,
    }
    res = requests.get(url=url, params=para, headers=headers)
    json_data = json.loads(res.text)
    if json_data['STATUS'] == '0':
        cnt = 0
        for item in json_data['result']:
            courseSchedId = item['id']
            params = {
                'id': userId
            }
            current_timestamp_seconds = time.time()
            current_timestamp_milliseconds = int(current_timestamp_seconds * 1000)
            str = f'http://iclass.buaa.edu.cn:8081/app/course/stu_scan_sign.action?courseSchedId={courseSchedId}&timestamp={current_timestamp_milliseconds}'
            r = requests.post(url=str, params=params)
            classBeginTime = item['classBeginTime']
            classEndTime = item['classEndTime']
            date = classBeginTime[:10] 
            begin = classBeginTime[11:16] 
            end = classEndTime[11:16]
            if r.ok:
                print(f"已打卡：{date}\t{item['courseName']}\t{begin}-{end}")
            else:
                print(f"不知道发生什么了但是打卡失败了喵：{date}\t{item['courseName']}\t{begin}-{end}")
    else:
        cnt += 1
