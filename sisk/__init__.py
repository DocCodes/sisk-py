#!/usr/bin/env python3
"""Gets gradebook information
"""
import requests
from datetime import datetime
from re import search as regsearch

__author__ = 'Evan Young'
__copyright__ = 'Copyright 2017, Evan Young'
__credits__ = 'Evan Young'

__license__ = 'GNU GPLv3'
__version__ = '0.3.0'
__maintainer__ = 'Evan Young'
__status__ = 'Beta'


class account:
   def __init__(self, username, password, site):
      """Makes a new account object

      Arguments:
         username {str} -- The username
         password {str} -- The password
         site     {str} -- The home site
      """
      self.username = username
      self.password = password
      self.site = site

      self.auth = self.getAuth()
      self.head = self.getHead()
      self.user = self.getUser()
      self.enrollment = self.getEnrollment()
      self.courses = self.getCourses()
      self.prettyCourses = self.getprettyCourses()
      self.prettyTerms = self.getprettyTerms()
      self.grades = self.getGrades()

   def getAuth(self):
      """Gets the authorization token
      """
      data = {
         "grant_type": "password",
         "username": self.username,
         "password": self.password,
         "scope": 3
      }

      res = requests.post(f"{self.site}/token", data=data).json()
      if("error" in res):
         raise RuntimeError("invalid credentials")
      ret = {"token":res["access_token"],"type":res["token_type"]}
      return ret

   def getHead(self):
      """Gets the user headers for future connections
      """
      head = {
         "Accept": "application/json, text/plain, */*",
         "Accept-Encoding": "gzip, deflate, br",
         "Accept-Language": "en-GB,en;q=0.9",
         "Authorization": f"{self.auth['type'].title()} {self.auth['token']}",
         "Connection": "keep-alive",
         "Host": regsearch("(?<=https://).*(?=/)", self.site)[0],
         "Referer": f"{self.site}/apphost/TylerSis",
         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
      }
      return head

   def getUser(self):
      """Gets the basic user account information
      """
      res = requests.get(f"{self.site}/AppApi/TylerSis/Student/GetUser", headers=self.head).json()
      if("error" in res):
         raise RuntimeError("invalid token")
      return res

   def getEnrollment(self):
      """Gets the enrollment information
      """
      params = {
         "studentId": {self.user['StudentId']},
         "academicYearId": {self.user['LoginYearId']}
      }
      res = requests.get(f"{self.site}/AppApi/TylerSis/Student/GetStudentEnrollment", params=params, headers=self.head).json()
      if("error" in res):
         raise RuntimeError("invalid token")
      return res

   def getCourses(self):
      """Gets the courses object
      """
      params = {
         "studentId": self.user["StudentId"],
         "yearId": self.user["LoginYearId"],
         "viewOption": self.user["UserType"],
         "includeAttendance": "false",
         "includeReportCardGrades": "true",
         "IsProgressGrades": "false",
         "userid": self.user["Id"],
         "includeDropped": "undefined"
      }
      res = requests.get(f"{self.site}/AppApi/TylerSis/Student/GetStudentSchedule", params=params, headers=self.head).json()
      if("error" in res):
         raise RuntimeError("invalid token")
      return res

   def getprettyCourses(self):
      """Converts the courses object to a prettier format
      """
      ret = {}
      for c in self.courses:
         gr = {
            "course": c["Course"],
            "abbr": c["AbbreviatedTitle"],
            "teacher": {
               "name": c["TeacherName"],
               "title": c["Teacher"],
               "email": c["TeacherEmail"]
            },
            "school": c["SchoolName"].title(),
            "period": c["StartPeriod"],
            "tardies": c["Tardies"],
            "absences": c["Absences"],
            "grades": {},
         }

         for t in c["ReportCardGradesTerms"]:
            gr["grades"][t["GradingTerm"]] = {}
            try:
               gr["grades"][t["GradingTerm"]]["percent"] = int(t["DisplayGrade"])
            except:
               gr["grades"][t["GradingTerm"]]["percent"] = 0
            gr["grades"][t["GradingTerm"]]["letter"] = t["Grade"]

         ret[c["$id"]] = gr
      return ret

   def getprettyTerms(self):
      """Converts the courses object's terms' times to a prettier format
      """
      now = datetime.now()
      ret = {}
      for c in self.courses:
         for t in c["CourseTerms"]:
            if(t["ShortDescription"] not in ret):
               ret[t["ShortDescription"]] = {
                  "start": datetime.strptime(t["StartDate"], "%Y-%m-%dT%H:%M:%S"),
                  "end": datetime.strptime(t["EndDate"], "%Y-%m-%dT%H:%M:%S")
               }
               if(now >= ret[t["ShortDescription"]]["start"] and now <= ret[t["ShortDescription"]]["end"]):
                  if(t["ShortDescription"][0] == "T"):
                     self.curTerm = t["ShortDescription"]
                  else:
                     self.curSem = t["ShortDescription"]
      return ret

   def getGrades(self, period="curTerm"):
      """Gets the current grades

      Keyword Arguments:
         period {str} -- The period for grades (default: {"curTerm"})
      """
      ret = {}
      period = getattr(self, period)
      for c in self.prettyCourses:
         gr = {
            "course": self.prettyCourses[c]["course"],
            "abbr": self.prettyCourses[c]["abbr"]
         }
         if(period in self.prettyCourses[c]["grades"]):
            gr["grade"] = self.prettyCourses[c]["grades"][period]
         else:
            gr["grade"] = {"percent":0,"letter":""}
         ret[c] = gr

      return ret
