#!/usr/bin/env python3
"""
Gets gradebook information
Takes 6 seconds (AVG/50)
"""

import requests
import datetime

class account:
   def __init__(self, username, password):
      """Makes a new account object

      Arguments:
         username  {str} -- The username
         password  {str} -- The password
      """
      self.username = username
      self.password = password

      self.auth = self.getAuth()
      self.head = self.getHead()
      self.user = self.getUser()
      self.enrollment = self.getEnrollment()
      self.courses = self.getCourses()
      self.prettycourses = self.getPrettyCourses()
      self.prettyterms = self.getPrettyTerms()

   def getAuth(self):
      """Gets the authorization token
      """
      data = {
         "grant_type": "password",
         "username": self.username,
         "password": self.password,
         "scope": 3
      }

      res = requests.post("https://sdm.sisk12.com/VP360/token", data=data).json()
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
         "Host": "sdm.sisk12.com",
         "Referer": "https://sdm.sisk12.com/VP360/apphost/TylerSis",
         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
      }
      return head

   def getUser(self):
      """Gets the basic user account information
      """
      res = requests.get("https://sdm.sisk12.com/VP360/AppApi/TylerSis/Student/GetUser", headers=self.head).json()
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
      res = requests.get(f"https://sdm.sisk12.com/VP360/AppApi/TylerSis/Student/GetStudentEnrollment", params=params, headers=self.head).json()
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
      res = requests.get("https://sdm.sisk12.com/VP360/AppApi/TylerSis/Student/GetStudentSchedule", params=params, headers=self.head).json()
      if("error" in res):
         raise RuntimeError("invalid token")
      return res

   def getPrettyCourses(self):
      """Converts the courses object to a prettier format
      """
      ret = []
      for c in self.courses:
         gr = {}
         gr["course"] = c["Course"]
         gr["abbr"] = c["AbbreviatedTitle"]
         gr["teacher"] = {
            "name": c["TeacherName"],
            "title": c["Teacher"],
            "email": c["TeacherEmail"]
         }
         gr["school"] = c["SchoolName"].title()
         gr["period"] = c["StartPeriod"]
         gr["tardies"] = c["Tardies"]
         gr["absences"] = c["Absences"]
         gr["grades"] = {}

         for t in c["ReportCardGradesTerms"]:
            gr["grades"][t["GradingTerm"]] = {}
            try:
               gr["grades"][t["GradingTerm"]]["percent"] = int(t["DisplayGrade"])
            except:
               gr["grades"][t["GradingTerm"]]["percent"] = 0
            gr["grades"][t["GradingTerm"]]["letter"] = t["Grade"]

         ret.append(gr)
      return ret

   def getPrettyTerms(self):
      """Converts the courses object's terms' times to a prettier format
      """
      now = datetime.datetime.now()
      ret = {}
      for c in self.courses:
         for t in c["CourseTerms"]:
            if(t["ShortDescription"] not in ret):
               ret[t["ShortDescription"]] = {
                  "start": datetime.datetime.strptime(t["StartDate"], "%Y-%m-%dT%H:%M:%S"),
                  "end": datetime.datetime.strptime(t["EndDate"], "%Y-%m-%dT%H:%M:%S")
               }
               if(now >= ret[t["ShortDescription"]]["start"] and now <= ret[t["ShortDescription"]]["end"]):
                  if(t["ShortDescription"][0] == "T"):
                     self.curTerm = t["ShortDescription"]
                  else:
                     self.curSem = t["ShortDescription"]
      return ret
