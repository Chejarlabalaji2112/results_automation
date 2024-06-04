import openpyxl
from openpyxl import Workbook
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import pandas as pd

wb = Workbook()
ws = wb.active
ws.append(["Roll number", "Name", "Gpa"])

df = pd.read_excel(r"rolls.xlsx")
rolls = df['rolls']
def getter(roll_num):
    url = "http://siddharthgroup.ac.in/aut3btech1regr20may2024.php?title=&dbn=aut3btech1r20may2024.php&htno="+roll_num+"&submit=Get+Results"
    html = urlopen(url)
    soup = bs(html,'html.parser')
    block = soup.find("div", {"class": None})
    fonts = block.find_all("font")
    gpa = soup.find_all('span',{'class': None})
    for each in gpa:
        print(roll_num, fonts[1].text, each.text.strip())
        ws.append([roll_num, fonts[1].text,each.text.strip()])

for roll in rolls:  
    getter(str(roll))
    
wb.save("csm_gpa.xlsx")