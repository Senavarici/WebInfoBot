import requests
from bs4 import BeautifulSoup
import re
import sqlite3 as sqlite
from email_validator import validate_email, EmailNotValidError

db = input("isim gir: ")
conn = sqlite.connect("{}.db".format(db))
cs = conn.cursor()
class Database:       
    def create_table(self, name, datas):
        self.name = name
        crt = "create table if not exists {} (id integer primary key autoincrement".format(self.name)
        for value in datas.values():
            crt += ("," + str(value))
        crt += ")"
        cs.execute(crt)
        conn.commit()      
        
    def insert_table(self,name, datas):
        self.name = name
        insrt = "insert into {} values (null".format(self.name)
        for value in datas.values():
            insrt += (","+ '"' + str(value) + '"') 
        insrt += ')'
        cs.execute(insrt)
        conn.commit()

def checkmail(email):
    try:
        valid = validate_email(email)
        return valid
    except EmailNotValidError as e:
        return False

table = Database()
table.create_table("data", {'column1':"url", 'column2':"email", 'column3':"phone"})
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
            
    table1 = Database()
    table1.create_table("code_200",{'column1':"url"})
    table2 = Database()
    table2.create_table("code_404",{'column1':"url"})
   
    for url in urls:        
        page2 = requests.get(url)
        soup = BeautifulSoup(page2.text, 'html.parser')
        if page2.status_code == 200:   
            table1 = Database()
            table1.insert_table("code_200",{'column1':url})             
        else:          
            table2 = Database()
            table2.insert_table("code_404",{'column1':url}) 
                  
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
        table = Database()
        table.insert_table("data", {'column1':url, 'column2':email, 'column3':phone}) 
        
AllLinks(url)

