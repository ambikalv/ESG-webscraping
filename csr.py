import requests
import re
import openpyxl
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime


def getWordsFromURL(url):
  return re.compile(r'[\:/?=\-&]+', re.UNICODE).split(url)

def closeish(word1, list):
  for word2 in list:
    if word1 == word2 or word1 in word2 or word2 in word1:
      return word1
  return "no"
  

def getyear(words):
  if '2022' in words:
    return '2022'
  if '2023' in words:
    return "2023"
  return ""

def get_firstword_companyname(companies):
  ret = []
  for company in companies:
    company = company.split()[0]
    ret.append(company.lower())
  return ret
  
def getcompanyname(words, keyword):
  companyname = ""
  for word in words:
    if word.isupper() and word.lower() != keyword.lower():
      companyname = companyname + " " + word
  return companyname


keywords = ['TCFD', 'CSR', 'esg', 'dei', 'sustainability']
companynames = []
urls = []
titles = []
reporttype = []
publishdate = []
publishtime = []

for keyword in keywords:
  url = "https://www.marketscreener.com/search/?q=" + keyword + "+report"
  req = requests.get(url)
  soup = BeautifulSoup(req.text, 'html.parser')
  links = soup.find_all(
    'a', class_="txt-s1 txt-overflow-2 link my-5 my-m-0 txt-m-inline")
  dates = soup.find_all("time", class_="js-date-relative txt-muted h-100")
  words = []

  for i in range(len(links)):
    link = links[i]
    date = dates[i].get('data-utc-date')[0:10]
    time = dates[i].get('data-utc-date')[11:19]
    reportlink = link.get('href')
    if 'sustainability' in reportlink.lower() and 'report' in reportlink.lower(
    ) or keyword in reportlink.lower(
    ) or "corporate-sustainability-report" in reportlink.lower():
      words = getWordsFromURL(reportlink)
      companyname = getcompanyname(words, keyword)
      year = getyear(words)
      if companyname != "" and companyname not in companynames:
        companynames.append(companyname.title())
      if keyword == "sustainability":
        title = companyname.title(
        ) + " releases " + year + " " + keyword.title() + " report"
      else:
        title = companyname.title(
        ) + " releases " + year + " " + keyword.upper() + " report"
      titles.append(title)
      urls.append("https://www.marketscreener.com/" + reportlink + " ")
      reporttype.append(keyword.upper())
      publishdate.append(date)
      publishtime.append(time)
df = pd.DataFrame(
  [companynames, titles, urls, reporttype, publishdate, publishtime],
  index=[
    "company", "report title", "url", "reporttype", "publishdate",
    'publishtime'
  ])
df = df.T

df1 = pd.read_csv('plugged.csv', delim_whitespace=True )



ms_companies = get_firstword_companyname(df["company"])
pibe_companies = get_firstword_companyname(df1["headline"])



ms_dict = {}
for i in range(len(ms_companies)):
  company = ms_companies[i]
  ms_dict[company] = df["company"][i]
 

written = []
unwritten = []

for company in ms_companies:
  if closeish(company,pibe_companies) != "no":
    written.append(ms_dict[company])
  else:
    unwritten.append(ms_dict[company])
unwritten = list(set(unwritten))
written = list(set(written))
print("already written are ") 
print(written)
print("")
print("The unwritten companies are ")
print(unwritten)

df = df.drop_duplicates(subset='company', keep="first")
merge = pd.concat([df,df1])


df.to_csv("out.csv", sep=',')
merge.to_csv("merge.csv", sep = ',')
    





  


    
  



