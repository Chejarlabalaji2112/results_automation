from re import fullmatch
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import URLError
import sqlite3
import json
import telebot
import os


def pre_processor(roll_num):
    """This function extracts details of the student from the roll_number."""
    connect = sqlite3.connect("results_scraper.db")
    cursor = connect.cursor()
    if fullmatch("[0-9]{2}(f6|4e)(1|5)a[0-9]{4}", roll_num := roll_num.lower()):
        # Above block checks whether the roll_num entered is valid or not.
        p_course = table_name = time_table = None
        p_entry = "eamcet"
        p_join_year, college = int(roll_num[:2]), roll_num[2:4]
        if college == "f6":  # f6 is for sietk
            table_name = "sietk_links"
            time_table = "sietk_exams"
        elif college == "4e":  # for sistk
            table_name = "sistk_links"
            time_table = "sistk_exams"

        if roll_num[4] == "5":  # this if block differentiate ecet entry students and eamcet students.
            p_join_year -= 1  # To keep track the actual batch started courses year. 22 le are 21 batch students.
            p_entry = "ecet"

        if roll_num[5] == "a":  # To know which course the student is enrolled.
            p_course = "b.tech"
        elif roll_num[5] == "f":
            p_course = "mca"
        print(p_course, time_table, p_join_year)
        cursor.execute(f"select `{p_course}` from {time_table} where joined_year = {p_join_year}")
        values = json.loads(cursor.fetchone()[0])

        if p_join_year > 22:  # To know student regulation.
            reg = "r23"
        elif 19 < p_join_year < 23:
            reg = "r20"
        elif p_join_year == 19:
            reg = "r19"
        elif p_join_year == 18:
            reg = "r18"
        elif 15 < p_join_year < 18:
            reg = "r16"
        else:
            return " sorry the regulation is different."

        return values, p_course, table_name, p_join_year, p_entry, reg, college
    else:
        print("IT SEEMS LIKE GIVEN ROLL_NUM IS NOT CORRECT.")
        return


def results_extractor(batch, values, p_course, table_name, roll_num, p_need, reg, e_type):
    """This function return the results html file..."""
    global college, user_roll_num
    ac_year, sem, mon, year = values[p_need]
    if link := result_link_loader(ac_year, p_course, sem, reg, e_type, mon, year, table_name):
        link = link[0]
        index1 = link.find("&submit")
        html = urlopen(link[:index1 - 4] + roll_num + link[index1:]).read()
    else:
        details = [ac_year, sem, mon, year, e_type, reg]
        print(f"There is no link for  {batch} batch- {ac_year, sem} in our database. Wait let us check in website")
        if main_fun.college == "f6":
            url = "http://siddharthgroup.ac.in/resultpage.html"
            base = "http://siddharthgroup.ac.in/"
            table = "sietk_updates"
        elif main_fun.college == "4e":
            url = "http://siddharthgroup.ac.in/sistkresultpage.html"
            base = "http://siddharthgroup.ac.in/"
            table = "sistk_updates"
        found_link, text, href = checker(url, table, details)
        if not found_link:
            print(text,"so no links are added after that.")
            return False
        elif found_link:
            href_index = href.find(reg)
            html = urlopen(f"{base}{href[:href_index]}reg{href[href_index:]}?title=&dbn={href}&htno={user_roll_num}&submit=Get+Results")

    soup = BeautifulSoup(html, 'html.parser')
    return soup.prettify()


def result_link_loader(ac_year, p_course, sem, reg, e_type, month, year, table_name):
    """This function returns the link of the results."""
    connect = sqlite3.connect("results_scraper.db")
    cursor = connect.cursor()
    if e_type == "regular":
        cursor.execute(f"SELECT link from {table_name} where year = '{year}' and month like '%{month}%' \
        and academic_year = '{ac_year}' and semester = '{sem}' and course = '{p_course}' \
        and regulation = '{reg}'and regular = 'yes' ")
    elif e_type == "supply" or e_type == "supplementary":
        s_month, s_year = input("please enter the supply details in this format feb 2023: ").strip().split()
        print(ac_year, p_course, sem, reg, e_type, s_month, s_year, table_name)
        cursor.execute(f"SELECT link from {table_name} where year = '{s_year}' and month like '%{s_month}%' \
        and academic_year = '{ac_year}' and semester = '{sem}' and course = '{p_course}' \
        and regulation = '{reg}'and supply = 'yes' ")
    link = cursor.fetchone()
    cursor.close()
    connect.close()
    return link


def file_saver(folder_name, file_name, html_content):
    """Saves files with roll_num as folder_name in working directory."""
    if not html_content:
        file_saver.status = False
    from os import makedirs
    makedirs(folder_name, exist_ok=True)
    with open(f"{folder_name}/{folder_name}{file_name}.html", 'w') as file:
        file.write(str(html_content))
        print(f"successful!!!! Stored in {folder_name}/{file_name}.html")
        file_saver.status = True
      

def checker(url, table, details, admin=False):
    """This function checks the website for new links. if admin is true it  returns the new links else some text only."""
    connect = sqlite3.connect("results_scraper.db")
    cursor = connect.cursor()
    cursor.execute(f"select * from {table}")
    found_link = True
    val = cursor.fetchone()
    new_links_counter = 0
    new_links = []
    html = urlopen(url)
    soup = BeautifulSoup(html, "html.parser")
    anchor_tags = soup.find_all('a')
    for each in anchor_tags:
        each_text = each.text.lower()
        if "rec" not in each.text and  "rev" not in each.text:
            if each_text == val[0] or each['href'] == val[1]:
                return ("reached the link we already loaded.", new_links, new_links_counter) if admin else (False, "reached the link we already loaded", None)
            for every in details:
                if every not in each_text:
                    found_link = False
                    break
            if found_link:
                return found_link, each_text, each['href']
            new_links_counter += 1
            new_links.append([each_text, each['href']])
    cursor.close()
    connect.close()


def main_fun(user_roll_num, need, request, exam_type):
    """This is the function which it handles all the code."""
    all_values, course, t_name, join_year, entry, regulation, main_fun.college = pre_processor(user_roll_num)

    try:
        if need == "all":
            keys = list(all_values.keys())
            for key in keys:
                if (entry == "ecet") and (key != "1-1" and key != "1-2"):
                    file_saver(user_roll_num, key, results_extractor(join_year, all_values, course, t_name, user_roll_num, key, regulation,
                                                       e_type = 'regular'))
                elif entry == "eamcet":
                    file_saver(user_roll_num, key, results_extractor(join_year, all_values, course, t_name, user_roll_num, key, regulation,
                                                       e_type = 'regular'))
            if entry == "ecet":
                print("AS the roll_num entered is LE , NO 1st year results are available")

        else:
            file_saver(user_roll_num, need, results_extractor(join_year, all_values, course, t_name, user_roll_num, need, regulation,
                                                       e_type = 'regular'))
    except URLError:
        print("There is problem while contacting website, CHECK YOUR INTERNET CONNECTION.")
try:
    bot = telebot.TeleBot('')
    def get_results(roll_num, needed, req, type):
        main_fun(roll_num, needed, req,type)
    @bot.message_handler(func = lambda message : True)
    def send_files(message):
      mssg = message.text.strip().lower().split()
      if fullmatch("[0-9]{2}(f6|4e)(1|5)a[0-9]{4}", mssg[0]):
         chat_id = message.chat.id
         bot.send_message(chat_id, "Wait getting file...")
         folder, need = mssg
         get_results (folder, need,'file_saver', 'regular')
         if os.path.exists(folder) and os.path.isdir(folder):
             for filename in os.listdir(folder):
                 file_path = os.path.join(folder, filename)
                 if os.path.isfile(file_path):
                     with open(file_path, 'rb') as file:
                         bot.send_document(chat_id, file, caption=f"{filename}")
                     os.remove(file_path)
             os.rmdir(folder)
         else:
             bot.send_message(chat_id, "Folder not found")
      else:
        bot.reply_to(message,  "enter in the format '[22f61a0901 all or 2-1'] ")

    bot.polling()
except Exception as e:
    print("error is :", e)
    bot.polling()


    

