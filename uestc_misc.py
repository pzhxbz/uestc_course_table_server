# -*- coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import urllib


refer_url = 'http://eams.uestc.edu.cn/eams/courseTableForStd.action'
table_url = 'http://eams.uestc.edu.cn/eams/courseTableForStd!courseTable.action'

# 用来在源码中提取POST数据和课程信息的正则
ids_pattern = re.compile(b'"ids","(\d+)"')
course_pattern = re.compile(r'TaskActivity\((.*)\)([^T]*)')
info_pattern = re.compile(r'"(.*?)",?' * 7)
time_pattern = re.compile(r'index =(\d+)\*unitCount\+(\d+);')


def course_info(user, semesterid=None):
    page = user.visit(refer_url).encode('utf-8')
    #print(page.encode('utf-8'))
    ids_info = ids_pattern.search(page)
    post_form = {
        'ignoreHead': 1,
        'setting.kind': 'std',
        'startWeek': 1,
        'semester.id': semesterid,
        'ids': ids_info[1],
    }
    courses = []
    for match in course_pattern.finditer(user.visit(table_url, post_form)):
        course = {}
        info = info_pattern.search(match[1])
        course['teacher_id'] = info[1]
        course['teacher_name'] = info[2]
        course['course_id'] = info[3]
        course['course_name'] = info[4]
        course['room_id'] = info[5]
        course['room_name'] = info[6]
        course['weeks'] = tuple(i for i, v in enumerate(info[7]) if v == '1')
        course['time'] = []
        time = time_pattern.findall(match[2])
        for weekday, clss in time:
            course['time'].append((int(weekday) + 1, int(clss) + 1))
        courses.append(course)
    return courses


class LoginError(Exception):
    def __init__(self, message):
        super().__init__(message)


class uestc_user(object):
    authurl = 'http://idas.uestc.edu.cn/authserver/login'
    eamsurl = 'http://eams.uestc.edu.cn/eams/home.action'

    def __init__(self, username=None, password=None):
        self._id = username
        # get cookie
        self._session = requests.Session()
        idas = self._session.get(uestc_user.authurl).text
        idas = BeautifulSoup(idas, 'html.parser')
        idas = idas.select('#casLoginForm')[0].find_all('input')
        post_form = {}
        for input in idas:
            post_form[input['name']] = input['value']
        post_form['username'] = username
        post_form['password'] = password
        response = self._session.post(uestc_user.authurl, post_form).text
        response = BeautifulSoup(response, 'html.parser')
        login_error = response.select('#msg')
        if login_error:
            raise LoginError(login_error[0].string)
        self._session.get(uestc_user.eamsurl)
        # will be set if self.name was used
        self._name = ''

    @property
    def cookies(self):
        return dict(self._session.cookies)

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        if not self._name:
            info = self._session.get(uestc_user.eamsurl)
            self._name = re.search(r'>(.*)\(' + self.id + r'\)<', info.text)[1]
        return self._name

    def visit(self, url, data=None):
        if data == None:
            return self._session.get(url).text
        else:
            return self._session.post(url, data).text