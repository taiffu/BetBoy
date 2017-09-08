#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
import dateutil.parser

from csv import reader
from PySide import QtCore


class BetExploerer():
    """
    Scrape from betexploerer.com
    results+fixtures+odds
    """
    def __init__(self,dst, mode):
        

        self.html = os.path.join('tmp','page')
        self.dst = dst
        self.be_mode = mode
        self.run()
    def run(self):
        ''' Start thread'''
        if self.be_mode == 'results':
            self.scrape_results()
        else:
            self.scrape_fixtures(self.dst)
    def scrape_results(self):
        with open(self.html, 'r') as f:
            html_page = f.read()
        #print html_page
        re_pattern = '<td class="h-text-left">.*?</td></tr>'
        re_compiled = re.compile(re_pattern,re.DOTALL)
        html_page = re.sub(r' <span title="Awarded">.*?</span>','', html_page)
	html_page = re.sub(r' <span title="After Penalties">PEN.</span>','', html_page)
        re_pattern_a = 'class="in-match"><span><strong>(?P<home>.*?)</strong></span> - <span>(?P<away>.*?)</span></a></td><td .*?><a.*?>(?P<goals_home>.*?):(?P<goals_away>.*?)</a></td><td.*?><span><span><span>(?P<odd_1>.*?)</span></span></span></td><td.*?>(?P<odd_x>.*?)</td><td.*?>(?P<odd_2>.*?)</td><td.*?>(?P<date>.*?)</td></tr>'
        re_compiled_a = re.compile(re_pattern_a, re.DOTALL)
        search = re_compiled.search(html_page)
        print search
        try:
            html_text = search.group(0)
        except:
            print 'No results'
            html_text = ""
        with open(os.path.join('tmp','results.txt'),'w') as f:
            while search:
                search_a = re_compiled_a.search(html_text)
                if search_a:
                    #check if game not yet played => golas_home =NULL golas_away=NULL
                    group = search_a.group('date','home','away','goals_home','goals_away',
                                        'odd_1','odd_x','odd_2')
                    #date 01.34.6789
                    #convert all given datestime to same format

                    print "DATE:" + group[0]
                    date = dateutil.parser.parse(group[0])                    
                    day = str(date.day) #group[0][0:2]
                    month = str(date.month) #group[0][3:5]
                    year = str(date.year) #group[0][6:]
                    date = year +'.'+month +'.'+ day
                    print "CDATE:" + date
                    odd_1 = group[5]
                    odd_x = group[6]
                    odd_2 = group[7]
                    if odd_1=='&nbsp;' or odd_x=='&nbsp;' or odd_2=='&nbsp;':
                        odd_1 = '0'
                        odd_x = '0'
                        odd_2 = '0'
                    print group[:]
                    #if group[3] == Null
                    print "Game not played:", group[3]
                    f.write(date+',')
                    f.write(group[1]+',')
                    f.write(group[2]+',')
                    f.write(group[3].strip()+',')
                    f.write(group[4].strip()+',')
                    f.write(odd_1+',')
                    f.write(odd_x+',')
                    f.write(odd_2+'\n')
                html_page = re.sub(re_compiled, ' ', html_page, 1)
                search = re_compiled.search(html_page)
                if search:
                    html_text = search.group(0)

    def scrape_fixtures(self, dst):
        with open(self.html, 'r') as f:
            html_page = f.read()
        html_page = re.sub("\n","", html_page)
        re_pattern_main = '<td class="table-main__datetime">.*?</tr>'
	re_pattern_a ='.*td class="table-main__datetime">(?P<date>.*?)</td><td class="h-text-left"><a.*?><span>(?P<home>.*?)</span> - <span>(?P<away>.*?)</span></a></td>.*?<a href="/myselections.*?target="mySelections">(?P<odd_1>.*?)</a></td>.*?target="mySelections">(?P<odd_x>.*?)</a></td>.*?target="mySelections">(?P<odd_2>.*?)</a></td></tr>'
        re_pattern_b = '"first-cell date tl">(?P<date>.*?) .*?<a href.*?>(?P<home>.*?) - (?P<away>.*?)</a>(?P<odd_1>.)(?P<odd_x>.)(?P<odd_2>.)'
        re_compiled = re.compile(re_pattern_main, re.DOTALL)
        re_compiled_a = re.compile(re_pattern_a, re.DOTALL)
	re_compiled_b = re.compile(re_pattern_b, re.DOTALL)
        previous_date = ''
        with open(os.path.join('tmp','fixtures.txt'),'w') as f:
            search = re_compiled.search(html_page)
            try:
                html_text = search.group(0)
            except:
                print 'No results'
                html_text = ""
            while search:
                #print html_text
                search_a = re_compiled_a.search(html_text)
                if search_a:
                    print "A pattern"
                    group = search_a.group('date','home','away','odd_1','odd_x','odd_2')
                    group = list(group)
                    
                    if group[0][0]=="&":
                        group[0] = previous_date
                    else:
                        previous_date = group[0]
                    print group[:]
                    #date 01.34.6789
                    print "DATE:" + group[0]
                    date = dateutil.parser.parse(group[0])
                    day = str(date.day) #group[0][0:2]
                    month = str(date.month) #group[0][3:5]
                    year = str(date.year) #group[0][6:]
                    date = year +'.'+month +'.'+ day
                    print "CDATE:" + date
                    odd_1 = group[3]
                    odd_x = group[4]
                    odd_2 = group[5]
                    if odd_1=='&nbsp;' or odd_x=='&nbsp;' or odd_2=='&nbsp;':
                        odd_1 = '0'
                        odd_x = '0'
                        odd_2 = '0'
                    f.write(date+',')
                    f.write(group[1]+',')
                    f.write(group[2]+',')
                    f.write('NULL,') # home goals
                    f.write('NULL,') # away goals
                    f.write(odd_1+',')
                    f.write(odd_x+',')
                    f.write(odd_2+'\n')
                #else: 
                 #   print "ELSE B pattern"
                 #   search_b = re_compiled_b.search(html_text)
                 #   group = search_b.group('date','home','away','odd_1','odd_x','odd_2')
                 #   group = list(group)
                    
                 #   if group[0][0]=="&":
                 #       group[0] = previous_date
                 #   else:
                 #       previous_date = group[0]
                 #   if len(group[3])<2: #odds
                 #       group[3]='0'
                 #       group[4]='0'
                  #      group[5]='0'
                    #date 01.34.6789
                 #   print group[:]
                 #   day = group[0][0:2]
                 #   month = group[0][3:5]
                 #   year =group[0][6:]
                 #   date = year +'.'+month +'.'+ day
                 #   odd_1 = group[3]
                 #   odd_x = group[4]
                 #   odd_2 = group[5]
                 #   if odd_1=='&nbsp;' or odd_x=='&nbsp;' or odd_2=='&nbsp;':
                 #       odd_1 = '0'
                 #       odd_x = '0'
                 #       odd_2 = '0'
                 #   f.write(date+',')
                 #   f.write(group[1]+',')
                 #   f.write(group[2]+',')
                 #   f.write('NULL,') # home goals
                 #   f.write('NULL,') # away goals
                 #   f.write(odd_1+',')
                 #   f.write(odd_x+',')
                 #   f.write(odd_2+'\n')
                html_page = re.sub(re_compiled, ' ', html_page, 1)
                search = re_compiled.search(html_page)
                if search:
                    html_text = search.group(0)
        self.merge(dst)
    def merge(self, dst):
        path = os.path.join('tmp','')
        results = reader(open(path + 'results.txt', 'r'))
        fixtures = reader(open(path + 'fixtures.txt', 'r'))
        copy = []
        #reverse results
        for i in results:
            copy.append(i)
        
        copy.reverse() 
        with open(dst, 'w') as merged:
            for i in copy:
                for j in range(0,len(i)):
                    if (j+1) == len(i):
                        merged.write(i[j]+'\n')
                    else:
                        merged.write(i[j]+',')
            for i in fixtures:
                for j in range(0,len(i)):
                    if (j+1) == len(i):
                        merged.write(i[j]+'\n')
                    else:
                        merged.write(i[j]+',')
        
            
            

if __name__== '__main__':
    test = BetExploerer()
    test.scrape_results()
    test.scrape_fixtures()
    test.merge()









