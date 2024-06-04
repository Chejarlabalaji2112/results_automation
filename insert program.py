'''####################
table
sietk_links
sietk_links
2
CREATE TABLE sietk_links (year,month,course,regulation,regular,supply,academic_year,semester,link)
####################
table
sistk_links
sistk_links
3
CREATE TABLE sistk_links (year,month,course,regulation,regular,supply,academic_year,semester,link)
####################
table
sietk_exams
sietk_exams
26
CREATE TABLE sietk_exams(joined_year,'b.tech','m.tech',mba,mca)
####################
table
sistk_exams
sistk_exams
25
CREATE TABLE sistk_exams(joined_year,'b.tech','m.tech')
####################
table
sietk_updates
sietk_updates
27
CREATE TABLE sietk_updates (text, href)
####################
table
sistk_updates
sistk_updates
28
CREATE TABLE sistk_updates (text, href)

[Program finished]'''
import sqlite3
con = sqlite3.connect("results_scraper.db")
cur = con.cursor()
def get_tables():
    """ This is the function to get the table name and details"""
    cur.execute("select * from sqlite_master where type = 'table' ")
    #cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
cur.execute(f"INSERT INTO  sietk_links VALUES ('2024', 'may', 'b.tech', 'r20', 'yes', 'no', 'iv','ii','http://siddharthgroup.ac.in/aut4btech2regr20may2024.php?title=&dbn=aut4btech2r20may2024.php&htno=balu&submit=Get+Results' )")
cur.execute("select * from sietk_links ")
def exams_add():
	import json
	cur.execute("select `b.tech` from sistk_exams where joined_year = 20  ")
	dict_ = json.loads(cur.fetchone()[0])
	#print(type(dict_))
	#print(type(json.loads(dict_)))
	dict_['4-2'] = ['iv','ii','apr','2024']
	json_dict = json.dumps(dict_)
	cur.execute(f"update sistk_exams set `b.tech` = '{json_dict}' where joined_year = 20")
	cur.execute("select `b.tech` from sistk_exams where joined_year = 20  ")
	print(cur.fetchone()[0])
#exams_add()
"""cur.execute("select * from sietk_exams")"""
for each in cur.fetchall():
	  print(each)


	    