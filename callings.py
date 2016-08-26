from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import time
from lxml import html

from dateutil.relativedelta import relativedelta
from datetime import date, timedelta, datetime

from pprint import pprint
import re
import sys

import config

def login():
    os.environ["webdriver.chrome.driver"] = os.path.join(os.getcwd(),"chromedriver")

    driver = webdriver.Chrome("./chromedriver")
    driver.get("https://ident.lds.org/sso/UI/Login?service=credentials")
    assert "Sign in" in driver.title
    elem = driver.find_element_by_name("IDToken1")
    elem.clear()
    elem.send_keys(config.NAME)
    elem = driver.find_element_by_name("IDToken2")
    elem.clear()
    elem.send_keys(config.PASSWORD)
    elem.send_keys(Keys.RETURN)

    return driver

def getMembersWithCallingsFromSite(driver):
    driver.get("https://www.lds.org/mls/mbr/orgs/members-with-callings?lang=eng")
    while driver.title != "Members with Callings":
        time.sleep(0.5)
    time.sleep(2)
    members_with_callings_dom = html.fromstring(driver.page_source)
    return members_with_callings_dom

def getMembersWithoutCallingsFromSite(driver):
    driver.get("https://www.lds.org/mls/mbr/orgs/members-without-callings?lang=eng")
    while driver.title != "Members without Callings":
         time.sleep(0.5)
    time.sleep(2)
    members_without_callings_dom = html.fromstring(driver.page_source)
    return members_without_callings_dom

def getCallingsbyOrgFromSite(driver):
    driver.get("https://www.lds.org/mls/mbr/orgs/callings-by-organization?lang=eng")
    while driver.title != "Callings by Organization":
        time.sleep(0.5)
    all_orgs_link = driver.find_element_by_xpath('//*[@id="organization"]/div[4]/div[1]/sub-orgs/div[1]/div/ul/li[1]/a')
    all_orgs_link.click()
    time.sleep(2)
    
    callings_dom = html.fromstring(driver.page_source)
    return callings_dom

def closeDriver(driver):
    driver.close()

def reorderName(name):
    #  Takes a name in Last, First Middle format and converts it to First Last format
    name_parts = name.split(",")
    last_name = name_parts[0]
    try:
        first_name = name_parts[1].split(" ")[1]
    except:
        first_name = name_parts[1]
    name = "{} {}".format(first_name, last_name)
    if name in config.NAME_EXCEPTIONS:
        name = config.NAME_EXCEPTIONS[name]
    return name

def getTimeInCalling(sustained):
    today = date.today()

    delta = relativedelta(today, sustained)
    
    timeStr = "{}{}".format("%dy" % delta.years if delta.years !=0 else "",
                        "%dm" % delta.months if delta.months !=0 else "")
    if timeStr == "" :
        timeStr = "0m"
    return timeStr

def getShortenedName(member):
    position = member['position']
    org = member['organization']
    class_assignment = member.get('class', None)
    
    global_replacements = {'First':'1st', 'Second': '2nd'}
    if class_assignment is not None:
        position = "{} ({})".format(position, class_assignment)
    try:
        new_position = position
        replacement_for_org =  config.CALLING_NAME_REPLACEMENTS.get(org, {})
        for k in sorted(list(replacement_for_org.keys())):
            v = replacement_for_org[k]
            new_position = new_position.replace(k,v)
        for k,v in global_replacements.items():
            new_position = new_position.replace(k,v)
        new_position = new_position.replace('  ', ' ')
        new_position = new_position.strip()
        return new_position
    except Exception as e:
        print(str(e))
        return position
    
def findClassAssignment(dom, position, name):
    group = 'UNKNOWN'
    for result in dom.xpath("//*[contains(text(),'{}')]".format(position)):
        found_name = result.xpath('../../td[3]/span/a/text()')[0]
        found_name = reorderName(found_name)
        if name == found_name:
            group = result.xpath('../../../../../../../../div[1]/h3/span/text()')[0].strip()
            break
    return group

def parse_members_with_callings(dom, callings_dom):
    """ returns a list of members"""
    
    rows = dom.xpath('//*[@id="mainContent"]/table/tbody/tr')
    member_list = []

    print(len(rows))
    for row in rows:
        member = {}
        try:
            name = row.xpath("./td[1]/a/text()")[0].strip()
            member_info = row.xpath("./td/text()")
            
            # GET NAME
            name = reorderName(name)
            member['name'] = name
            
            #  GET GENDER
            gender = member_info[2]
            member['gender'] = gender

            #  GET AGE
            age = member_info[3]
            member['age'] = age
            if int(age) < config.MINIMUM_AGE:
                continue

            #  GET ORGANIZATION
            organization = member_info[5]
            if organization in config.ORGS_TO_IGNORE:
                continue
            if organization in config.ORGS_TO_COMBINE:
                organization = "Other Callings"
            member['organization'] = organization
                
            #  GET POSITION
            position = member_info[6]
            member['position'] = position
            
            #  GET SUSTAINED
            sustained = member_info[7]
            sustained = datetime.strptime(sustained, "%d %b %Y").date()
            time_in_calling = getTimeInCalling(sustained)
            member['time_in_calling'] = time_in_calling
            
            #  GET SET APART
            set_apart = row.xpath('./td[8]/img')
            member['set_apart'] = True if len(set_apart) != 0 else False
            
            member['class'] = None

            if position in config.CALLINGS_WITH_ASSIGNMENTS:
                member['class'] = findClassAssignment(callings_dom, position, name)
            
            member['short_position'] = getShortenedName(member)
            
            member_list.append(member)
        except Exception as error:
            print(error)
    return member_list

def printUnmatchedCallings(unmatched_callings_by_org):
    for org,unmatched_callings in unmatched_callings_by_org.items():
        if unmatched_callings:
            print("{}: {}".format(org, unmatched_callings))

def getTimeInCallingClass(time_in_calling):
    match = re.search("(?:(\d+)y)?(?:(\d+)m)?", time_in_calling)
    if match:
        y = match.group(1)
        m = match.group(2)
        if y is not None and int(y) >= 2:
            return 'long'
        elif y is not None and int(y) >= 1:
            return 'medium'
        
def findMembersWithCalling(member_list, calling, org):
    members = []
    for member in list(member_list):
        if member['short_position'] == calling and member['organization'] == org:
            members.append(member)
            member_list.remove(member)
    return members
    
def getHTML(member_list, vacancies, members_without_callings):

    with open("callings.html", "w") as file:
        file.write('<!doctype html>\n')
        file.write('<html">\n')
        file.write('\t<head>\n')
        file.write('\t\t<title>High Desert Ward positions</title>\n')
        file.write('\t\t<link rel="stylesheet" href="main.css">\n')
        file.write('\t</head>\n')
        file.write('\t<body>\n')
        file.write('\t\t<div id=title>High Desert Callings <span class=date>{}</span></div>\n'.format(datetime.strftime(datetime.today(), "%B %d %Y %-I:%M%p")))
        file.write('\t\t<div id=calling_table>\n')
        for org, callings in config.CALLING_ORDER.items():
            file.write('\t\t\t<div class=group-wrapper><div class=group name="{}">\n'.format(org))
            file.write('\t\t\t\t<h2>{}</h2>\n'.format(org))
            for calling in callings:
                members_with_calling = findMembersWithCalling(member_list, calling, org)
                if len(members_with_calling) == 0:
                     file.write('\t\t\t\t<div class=calling><div class=position>{}</div><div class="name vacant">{}</div></div>\n'.format(calling,'VACANT'))
                else:
                    for member in members_with_calling:
                        time_class = getTimeInCallingClass(member['time_in_calling'])
                        set_apart_class = 'set_apart' if member['set_apart'] else 'not_set_apart'
                        set_apart_symbol = "&#x2713;" if member['set_apart'] else ""
                        file.write('\t\t\t\t<div class=calling><div class=position>{}</div><div class="name {} {}">{} <span class=time>({})</span><span class=set-apart>{}</span></div></div>\n'\
                               .format(member['short_position'],
                                time_class, set_apart_class, member['name'],member['time_in_calling'],set_apart_symbol))
            file.write('\t\t\t</div></div>\n')
        file.write('\t\t</div>\n')
        file.write('\t\t<p style="page-break-after:always;"></p>\n')
        file.write('\t\t <div id=other_info>\n')
        file.write('\t\t\t<div class=unfilled>\n')
        file.write('\t\t\t\t<h1>Un-Filled Callings</h1>\n')
        for v in vacancies:
            file.write('\t\t\t\t{} ({})<br />\n'.format(v['position'], v['group']))
        file.write('\t\t\t</div>\n')
        file.write('\t\t\t<div class=no_callings>\n')
        file.write('\t\t\t\t<h1>Members Without Callings</h1>\n')
        file.write('\t\t\t\t<div id=col1>\n')
        for m in members_without_callings[0:len(vacancies)]:
            file.write('\t\t\t\t\t{}<br />\n'.format(m))
        file.write('\t\t\t\t</div>\n')
        if len(members_without_callings) > len(vacancies):
            file.write('\t\t\t\t<div id=col2>\n')
            for m in members_without_callings[len(vacancies):]:
                file.write('\t\t\t\t\t{}<br />\n'.format(m))
            file.write('\t\t\t\t</div>\n')
        file.write('\t\t\t</div>\n')
        file.write('\t\t</div>\n')
        file.write('\t</body>\n')
        file.write('</html>\n')
        
    print("callings.html created")

def parseMembersWithoutCallings(dom):
    rows = dom.xpath("//table/tbody/tr")

    members_without_callings = []
    for row in rows:
        name = row.xpath("./td[1]/a/text()")[0].strip()
        name = reorderName(name)
        if name not in config.MEMBERS_WITHOUT_CALLINGS_IGNORE:
            age = row.xpath("./td[3]/text()")[0].strip()

            if int(age) > config.MINIMUM_AGE:
                members_without_callings.append(name)
    return members_without_callings

def parseVacantCallings(dom):
    rows = dom.xpath('//table/tbody/tr')

    vacancies = []
    for row in rows:
        try:
            name = row.xpath('./td[3]/span/a/text()')
            group = row.xpath('../../../../../../div[1]/h3/span/text()')[0].strip()
            
            position = row.xpath('./td[2]/span[3]/text()')[0].strip()
            for k,v  in config.VACANT_NAME_REPLACEMENTS.items():
                position = position.replace(k,v)
                group = group.replace(k,v)
            position = position.strip()
            group = group.strip()

            if not name:
                if position in config.VACANT_CALLINGS_TO_IGNORE or \
                   group in config.VACANT_GROUPS_TO_IGNORE:
                   continue
                else:   
                    vacancy = {'position': position, 'group':group}
                    vacancies.append(vacancy)
        except:
            pass
    return vacancies

def find_unmatched_callings(member_list):
    for org, callings_to_ignore in config.CALLINGS_TO_IGNORE.items():
        for calling in callings_to_ignore:
            for member in list(member_list):
                if member['short_position'] == calling and member['organization'] == org:
                    member_list.remove(member)
    return member_list

def createPDF():
    options = {
        'page-size': 'letter',
        'orientation': 'landscape',
        'margin-top': '0.25in',
        'margin-right': '0.25in',
        'margin-bottom': '0.25in',
        'margin-left': '0.25in',
    }
    pdfkit.from_file('callings.html', 'callings.pdf', options=options)

def main():
    doms = {}
    driver = login()
    doms['with'] = getMembersWithCallingsFromSite(driver)
    doms['without'] = getMembersWithoutCallingsFromSite(driver)
    doms['by_org'] = getCallingsbyOrgFromSite(driver)
    closeDriver(driver)

    member_list = parse_members_with_callings(doms['with'], doms['by_org'])
    vacant_callings_list = parseVacantCallings(doms['by_org'])
    members_without_calling_list = parseMembersWithoutCallings(doms['without'])
    getHTML(member_list, vacant_callings_list, members_without_calling_list)
    unmatched_callings_list = find_unmatched_callings(member_list)

    if unmatched_callings_list:
        pprint(unmatched_callings_list)


if __name__ == '__main__':
    main()
    # createPDF()
