import requests
from bs4 import BeautifulSoup
import re
import sqlite3 as sqlite
from email_validator import validate_email, EmailNotValidError

def checkmail(email):
    try:
        valid = validate_email(email)
        return valid
    except EmailNotValidError as e:
        return False

db = input("isim gir: ")
conn = sqlite.connect("{}.db".format(db))
cs = conn.cursor()
cs.execute("create table if not exists data (id integer primary key autoincrement, url, email, phone)") 
url = input("site linki gir: ")
urls = set()
def AllLinks(url):   
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    for link in soup.find_all("a"):
        i = link.get("href")
        if str(i).startswith(url):
            urls.add(str(i))
        if str(i).startswith("https") == False and str(i).startswith("/"):
            urls.add(url+str(i))
            
    cs.execute("create table if not exists code_200 (id integer primary key autoincrement, url)")      
    cs.execute("create table if not exists code_404 (id integer primary key autoincrement, url)") 
    conn.commit() 
    for url in urls:        
        page2 = requests.get(url)
        soup = BeautifulSoup(page2.text, 'html.parser')
        if page2.status_code == 200:           
            cs.execute("insert into code_200 values (null,?)",[url])
            conn.commit()      
        else:           
            cs.execute("insert into code_404 values (null,?)",[url])
            conn.commit()
                  
        email = re.findall("((?:[\w\.\-\+\_]+)@(?:[a-zA-Z0-9\.\-]+))",str(soup)) 
        try:
            if checkmail(email[0]) == False:
                email = None
            else:
                email =[*set(email)]
        except IndexError:
            pass

        phone =re.findall("^(\d{4}\s?\(?\d{3}\)?[\s]\d{4})|(\d{1,2}\s?\(?\d{3}\)?[\s]\d{3}[\s]\d{2}[\s]\d{2})|(\d{3}\)?[\s]\d{1}[\s]\d{3})",str(soup))  
        phone = [*set(phone)]   
        cs.execute("insert into Data values (null,?,?,?)",(url,str(email),str(phone)))
        conn.commit()
             
AllLinks(url)

