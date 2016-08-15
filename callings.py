from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import re
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta, datetime
import time
from pprint import pprint

def login():
    os.environ["webdriver.chrome.driver"] = os.path.join(os.getcwd(),"chromedriver")

    driver = webdriver.Chrome("./chromedriver")
    driver.get("https://ident.lds.org/sso/UI/Login?service=credentials")
    assert "Sign in" in driver.title
    elem = driver.find_element_by_name("IDToken1")
    elem.clear()
    elem.send_keys("AndrewBriscoe")
    elem = driver.find_element_by_name("IDToken2")
    elem.clear()
    elem.send_keys("Lindsay121")
    elem.send_keys(Keys.RETURN)

    return driver

def getMembersWithoutCallingsFromSite(driver, minAge=18):

    driver.get("https://www.lds.org/mls/mbr/orgs/members-without-callings?lang=eng")
    while driver.title != "Members without Callings":
        time.sleep(2)

    time.sleep(2)

    rows = driver.find_elements_by_xpath("//*[@id='mainContent']/table/tbody/tr")

    members_without_callings = []

    for row in rows:
        name = row.find_element_by_xpath("td[1]").text
        if name != "":
            name = reorderName(name)
            age = row.find_element_by_xpath("td[3]").text
            if int(age) > minAge:
                members_without_callings.append(name)
    return members_without_callings

def getTimeInCalling(sustained):
    today = date.today()

    numDays = (today - sustained).days

    relative_length = relativedelta(today, sustained)
    y = relative_length.years
    if y == 0:
        yStr = None
    else:
        yStr = "{}y".format(y)
    m = relative_length.months
    if m == 0:
        mStr = None
    else:
        mStr = "{}m".format(m)
    d = relative_length.days
    if d == 0:
        dStr = None
    else:
        dStr = "{}d".format(d)
    strings = [x for x in (yStr, mStr, dStr) if x]
    timeStr = "".join(strings)
    if timeStr == "":
        timeStr = "0d"
    timeStr_noDays = "".join([x for x in (yStr, mStr) if x])
    if timeStr_noDays == "" :
        timeStr_noDays = "0m"
    return numDays, timeStr, timeStr_noDays


def getShortenedName(member):
    position = member['position']
    org = member['organization']
    class_assignment = member['class']
    positions_with_class_assignments = ['Primary Teacher', 'Sunday School Teacher']
    replacement = {
        'Relief Society': {'Relief Society':'', 'Meeting Committee Member':'ARM Committee', 'Meeting Coordinator':'ARM Coordinator','Visiting Teaching':'VT'},
        'Elders Quorum': {'Elders Quorum':'','Home Teaching':'HT'},
        'Bishopric': {'Bishopric':'', 'Ward':''},
        'Young Women': {'Young Women':''},
        'Young Men': {'Young Men':'', ' Quorum': ''},
        'High Priests Group': {'Group':'', 'High Priest':'','s ':'', 'Home Teaching':'HT', 'Leader':'Group Leader'},
        'Sunday School': {'Sunday School':'', 'Unassigned Teachers': 'Unassigned'},
        'Primary': {'Primary':'', 'Unassigned Teachers': 'Unassigned', 'Activity Days Leader': 'Activity Days', 'Eleven':'11'},
        'Stake': {'Stake': '', 'Young Women':'YW', 'Young Men':'YM', 'Relief Society':'RS'},
        'Other Callings': {'Emergency Preparedness': 'Emergency Prep.'}
    }
    global_replacements = {'First':'1st', 'Second': '2nd'}
    if position in positions_with_class_assignments:
        position = "{} ({})".format(position, class_assignment)
    try:


        new_position = position
        replacement_list = replacement.get(org, {})
        for k in sorted(list(replacement_list.keys())):
            v = replacement_list[k]
            new_position = new_position.replace(k,v)
        for k,v in global_replacements.items():
            new_position = new_position.replace(k,v)
        new_position = new_position.replace('  ', ' ')
        new_position = new_position.strip()
        return new_position
    except Exception as e:
        print(str(e))
        return position

def reorderName(name):
     #  GET NAME
    name_parts = name.split(",")
    last_name = name_parts[0]
    try:
        first_name = name_parts[1].split(" ")[1]
    except:
        first_name = name_parts[1]
    name = "{} {}".format(first_name, last_name)
    return name

def getMembersWithCallingsFromSite(driver, class_assignments, minAge=18):
    orgs_to_combine = ['Music', 'Other Callings', 'Employment and Welfare', 'Young Single Adult', 'Family History', 'Additional Callings']
    orgs_to_remove = ['Full-Time Missionaries']
    positions_with_class_assignments = ['Primary Teacher', 'Sunday School Teacher']

    driver.get("https://www.lds.org/mls/mbr/orgs/members-with-callings?lang=eng")
    while driver.title != "Members with Callings":
        time.sleep(2)

    time.sleep(2)

    rows = driver.find_elements_by_xpath('//*[@id="mainContent"]/table/tbody/tr')

    members_with_callings = []

    print(len(rows))
    for row in rows:
        try:
            name = row.find_element_by_xpath("./td[1]/a").text
            if name != "":
                member = {}

                name = reorderName(name)
                member['name'] = name

                gender = row.find_element_by_xpath("./td[2]").text
                member['gender'] = gender
                               #  GET AGE
                age = row.find_element_by_xpath("./td[3]").text
                member['age'] = age
                if int(age) < minAge:
                    continue

                #  GET ORGANIZATION
                organization = row.find_element_by_xpath("./td[5]").text
                if organization in orgs_to_remove:
                    continue
                if organization in orgs_to_combine:
                    organization = "Other Callings"
                member['organization'] = organization

                #  GET POSITION
                position = row.find_element_by_xpath("./td[6]").text
                member['position'] = position

                #  GET SUSTAINED
                sustained = row.find_element_by_xpath("./td[7]").text
                sustained = datetime.strptime(sustained, "%d %b %Y").date()
                days_in_calling, time_in_calling, time_in_calling_no_days = getTimeInCalling(sustained)

                #  GET SET APART
                try:
                    set_apart = row.find_element_by_xpath('./td[8]/img')
                    member['set_apart'] = True
                except Exception as e:
                    member['set_apart'] = False

                member['sustained'] = sustained
                member['days_in_calling'] = days_in_calling
                member['time_in_calling'] = time_in_calling
                member['time_in_calling_no_days'] = time_in_calling_no_days
                member['class'] = None

                if position in positions_with_class_assignments:
                    for calling in class_assignments:
                        if name == calling['name'] and position == calling['position']:
                            member['class'] = calling['group']
                            break

                member['short_position'] = getShortenedName(member)
                members_with_callings.append(member)
        except Exception as e:
            print(str(e))

    return members_with_callings


def getClassAssignmentsFromSite(driver):
    driver.get("https://www.lds.org/mls/mbr/orgs/callings-by-organization?lang=eng")
    while driver.title != "Callings by Organization":
        time.sleep(2)

    time.sleep(2)

    all_orgs_link = driver.find_element_by_xpath('//*[@id="organization"]/div[4]/div[1]/sub-orgs/div[1]/div/ul/li[1]/a')
    all_orgs_link.click()
    time.sleep(2)

    sunday_school_teachers = driver.find_elements_by_xpath("//*[contains(text(), 'Sunday School Teacher')]")
    primary_teachers = driver.find_elements_by_xpath("//*[contains(text(), 'Primary Teacher')]")

    class_assignments = []
    for row in sunday_school_teachers+primary_teachers:
        callingDict = {}
        try:
            group = row.find_element_by_xpath('../../../../../../../../div[1]/h3/span').text
            position = row.text

            try:
                name = row.find_element_by_xpath('../../td[3]/span/a').text
                name_parts = name.split(",")
                last_name = name_parts[0]
                try:
                    first_name = name_parts[1].split(" ")[1]
                except:
                    first_name = name_parts[1]
                name = "{} {}".format(first_name, last_name)

                callingDict['group'] = group
                callingDict['position'] = position
                callingDict['name'] = name
                class_assignments.append(callingDict)
            except Exception as e:
                pass

        except Exception as e:
            print("couldn't find calling: "+str(e))

    return class_assignments


def closeDriver(driver):
    driver.close()

def getCallingList(members_with_callings):
    calling_list_by_org={}
    for member in members_with_callings:
        position = member['short_position']
        calling_list = calling_list_by_org.get(member['organization'], {})
        members_with_that_calling = calling_list.get(position, [])
        members_with_that_calling.append(member)
        calling_list[position] = members_with_that_calling
        calling_list_by_org[member['organization']] = calling_list

    return calling_list_by_org

def putCallingsInOrder(members_with_callings):
    calling_list = getCallingList(members_with_callings)
    calling_order = {
        'Bishopric': ['Bishop','1st Counselor','2nd Counselor','Executive Secretary','Clerk','Assistant Clerk--Finance','Assistant Clerk--Membership'],
        'High Priests Group': ['Group Leader','1st Assistant', '2nd Assistant','Secretary','Instructor','4th Sunday Instructor'],
        'Elders Quorum': ['President','1st Counselor','2nd Counselor','Secretary','Assistant Secretary','Instructor'],
        'Ward Missionaries': ['Ward Mission Leader','Assistant Ward Mission Leader','Ward Missionary'],
        'Relief Society': ['President','1st Counselor','2nd Counselor','Secretary','Compassionate Service Coordinator','Teacher','VT Coordinator','VT District Supervisor','ARM Coordinator','ARM Committee','Pianist','Music Leader'],
        'Young Men': ['President','1st Counselor','2nd Counselor','Secretary','Priests Adviser','Teachers Adviser','Deacons Adviser','Scoutmaster','Assistant Scoutmaster','Scouting Committee Chairman','Scouting Committee Member'],
        'Young Women': ['President','1st Counselor','2nd Counselor','Secretary','Laurel Adviser','Mia Maid Adviser','Beehive Adviser','Camp Director','Sports Specialist'],
        'Primary': ['President','1st Counselor','2nd Counselor','Secretary','Nursery Leader','Teacher (Sunbeam A)','Teacher (Sunbeam B)','Teacher (CTR 4)','Teacher (CTR 5)','Teacher (CTR 6A)','Teacher (CTR 6B)','Teacher (CTR 7)','Teacher (Valiant 8A)','Teacher (Valiant 8B)','Teacher (Valiant 9, Valiant 10)','Teacher (Valiant 11)','Teacher (Unassigned)','Activity Days','Music Leader','Pianist','Cubmaster','Cub Scout Committee Chairman','Cub Scout Committee Member','11-Year-Old Scout Leader','Webelos Leader','Webelos Assistant Leader','Wolf Den Leader','Wolf Den Assistant Leader', 'Bear Den Leader', 'Bear Den Assistant Leader'],
        'Sunday School': ['President','1st Counselor','2nd Counselor','Secretary','Teacher (Course 12)','Teacher (Course 13)','Teacher (Course 14, Course 15)','Teacher (Course 16, Course 17)','Teacher (Gospel Doctrine)','Teacher (Gospel Principles)','Librarian','Assistant Librarian'],
        'Other Callings': ['Music Director','Choir Director','Choir Accompanist','Family History Consultant','Single Adult Representative','Young Single Adult Leader','Emergency Prep. Specialist','Employment Specialist','Humanitarian Specialist','Activities Specialist','Building Representative','Technology Specialist','Newsletter Coordinator','Bulletin Coordinator','Ward Greeter'],
        'Stake': ['President','High Councilor','Assistant Clerk','Assistant Clerk--Membership','RS President','RS 2nd Counselor','Primary 2nd Counselor','YM 1st Counselor','YM 2nd Counselor','YWs Sports Director','YW Camp DIrector','YW Assistant Camp Director','Auditor','Cannery Coordinator','Director of Public Affairs','Emergency Radio Operator','Humanitarian Specialist','Seminary Teacher','Family History Center Director','Music Chairman','Scheduler--Building 3','Scheduler--Building 4']
        }
    callings_to_ignore = {
        'Bishopric': [],
        'High Priests Group': ['HT District Supervisor'],
        'Elders Quorum': ['HT District Supervisor'],
        'Ward Missionaries': [],
        'Relief Society': [],
        'Young Men': ['Priests President','Varsity Coach','Assistant Venturing Crew Adviser', 'Venturing Crew Adviser', 'Assistant Varsity Coach'],
        'Young Women': [],
        'Primary': [],
        'Sunday School': [],
        'Other Callings': [],
        'Stake': ['Assistant Clerk--Finance']
        }
    ordered_callings_by_org = {}
    unmatched_callings_by_org = {}
    for org, ordered_callings in calling_order.items():
        org_list = []
        org_calling_list = dict(calling_list[org])
        for calling in ordered_callings:
            callings = org_calling_list.get(calling, [])
            org_list = org_list + callings
            if callings:
                del org_calling_list[calling]
            else:
                print("{} ({}) is vacant".format(calling, org))
                member = {'short_position':calling, 'name':'VACANT', 'time_in_calling_no_days':''}
                org_list = org_list + [member]

        unmatched = [calling for calling in org_calling_list.keys() if calling not in callings_to_ignore[org]]
        unmatched_callings_by_org[org] = unmatched
        ordered_callings_by_org[org] = org_list

    return ordered_callings_by_org, unmatched_callings_by_org

def getTimeInCallingClass(time_in_calling):
    match = re.search("(?:(\d+)y)?(?:(\d+)m)?", time_in_calling)
    if match:
        y = match.group(1)
        m = match.group(2)
        if y is not None and int(y) >= 2:
            return 'long'
        elif y is not None and int(y) >= 1:
            return 'medium'

def getShortenedPosition(position):
    replacement = {'Relief Society':'RS',
                   'Meeting Committee Member':'ARM Committee',
                   'Meeting Coordinator':'ARM Coordinator',
                   'Visiting Teaching':'VT',
                   'Elders Quorum':'EQ',
                   'Home Teaching':'HT',
                   'High Priests Group':'HP',
                   'High Priest':'HP',
                   'Sunday School':'SS',
                   'Unassigned Teachers': 'Unassigned',
                   'Activity Days Leader': 'Activity Days',
                   'Eleven':'11',
                   'Young Women':'YW',
                   'Young Men':'YM',
                   'Relief Society':'RS',
                   'Emergency Preparedness': 'Emergency Prep.',
                   'First':'1st',
                   'Second': '2nd',
                   'Assistant': 'Asst.'}
    try:
        new_position = position
        for k,v  in replacement.items():
            new_position = new_position.replace(k,v)
        new_position = new_position.replace('  ', ' ')
        new_position = new_position.strip()
        return new_position
    except Exception as e:
        print(str(e))
        return position

def getVacantCallingsFromSite(driver):
    driver.get("https://www.lds.org/mls/mbr/orgs/callings-by-organization?lang=eng")
    while driver.title != "Callings by Organization":
        time.sleep(2)

    time.sleep(2)

    all_orgs_link = driver.find_element_by_xpath('//*[@id="organization"]/div[4]/div[1]/sub-orgs/div[1]/div/ul/li[1]/a')
    all_orgs_link.click()
    time.sleep(2)

    rows = driver.find_elements_by_class_name("calling")

    vacancies = []
    for row in rows:
        try:
            position = row.find_element_by_xpath('./td[2]/span[3]').text
            group = row.find_element_by_xpath('../../../../../../div[1]/h3/span').text
            try:
                name = row.find_element_by_xpath('./td[3]/span/a').text
            except:
                name = row.find_element_by_xpath('./td[3]/em').text
                vacancy = {'position': position, 'group':group}
                vacancies.append(vacancy)
        except Exception as e:
            pass
    return vacancies

def filterVacancies(vacancies):
    callingsToNotList = ['Scheduler--Building 1','Scheduler--Building 2','Scheduler--Building 3','Scheduler--Building 4','Scheduler--Building 5']
    groupsToNotList = ['Teachers Quorum Presidency', 'Laurel Presidency', 'Priests Quorum Presidency', 'Deacons Quorum Presidency', 'MiaMaid Presidency', 'Beehive Presidency']

    vacanciesToList = []
    for vacancy in vacancies:
        vacancy['position'] = getShortenedPosition(vacancy['position'])
        vacancy['group'] = getShortenedPosition(vacancy['group'])
        if vacancy['position'] not in callingsToNotList and \
           vacancy['group'] not in groupsToNotList:
            vacanciesToList.append(vacancy)
    return vacanciesToList

def filterMembersWithoutCallings(members):
    filterList = ['Ryan Alvord','Alissa Augustine','Tom Babeor','Mandy Baca','Aaron Bacoccini','Alisha Bacoccini','Cassie Bacoccini','Jeremy Bacoccini','Chynna Begay','Stephen Blaylock','Scott Bradley','Jeff Braithwaite','Karen Braithwaite','Christopher Cahoon','Julie Carr','Kelly Chicas','Mike Chisholm','Roberta Closner','Lourdes Davis','Tyrell Davis','Monique Delgarito','Raland Delgarito','Rydall Delgarito','Tamani Enciso','Amber Fitzgerald','Catherine Fitzgerald','Erin Fitzgerald','John Fitzgerald','Janice Foster','Jaynette Foutz','Chad Frank','Jan Frank','Hailey Frentheway','Kay Green','Kathleen Griffin','Shirley Habish','Amy Hayward','Michael Hayward','Emily Healy','Pamela Hechler','Robert Hechler','Paul Howard','Christopher Joens','Katerra Johnson','Kimberly Johnson','Tim Johnson','John Lahoff','Joseph Lahoff','Carl Leishman','Florence Leishman','Candace Lewis','Kaye Lewis','Donald Lloyd','Edith Logan','Al Manning','Elizabeth Manning','Colleen Martinez','Sophia Martinez','John Mercer','Loretta Mercer','Philip Nelson','Gail Page','Abigail Peterson','Benjamin Peterson','David Peterson','Melanie Peterson','Martin Reed','Bevan Rhodes','Daniel Rhodes','Rosalee Rife','Sandra Ross','Tabitha Ruple','Gary Skidmore','Ruth Stevens','Bryan Struve','Leslie Sumner','Matthew Swensen','Shannon Swenson','Alice Tollestrup','Barbara Tompkins','Keegan Udall','Brittany Wade','Carla Wade','Wade Weeks','Ashley Wilson', 'Matthew Wilson', 'Michael Wilson','Candice Yazzie','Brian Zufelt','Jeanette Zufelt']
    filtered = [member for member in members if member not in filterList]
    filtered_out = [member for member in members if member in filterList]
    return filtered, filtered_out

def getHTML(ordered_callings_by_org, filtered_vacancies, filtered_members_without_callings):
    org_names_in_order = ['Bishopric','High Priests Group','Elders Quorum','Relief Society','Young Men','Young Women','Sunday School','Primary','Ward Missionaries','Other Callings','Stake']
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
        for org in org_names_in_order:
            file.write('\t\t\t<div class=group-wrapper><div class=group name="{}">\n'.format(org))
            file.write('\t\t\t\t<h2>{}</h2>\n'.format(org))
            org_list = ordered_callings_by_org[org]
            for member in org_list:
                if member['name'] != 'VACANT':
                    time_class = getTimeInCallingClass(member['time_in_calling_no_days'])
                    set_apart_class = 'set_apart' if member['set_apart'] else 'not_set_apart'
                    set_apart_symbol = "&#x2713;" if member['set_apart'] else ""
                    file.write('\t\t\t\t<div class=calling><div class=position>{}</div><div class="name {} {}">{} <span class=time>({})</span><span class=set-apart>{}</span></div></div>\n'\
                           .format(member['short_position'],
                            time_class, set_apart_class, member['name'],member['time_in_calling_no_days'],set_apart_symbol))
                else:
                    file.write('\t\t\t\t<div class=calling><div class=position>{}</div><div class="name vacant">{}</div></div>\n'\
                           .format(member['short_position'],member['name']))
            file.write('\t\t\t</div></div>\n')
        file.write('\t\t</div>\n')
        file.write('\t\t<p style="page-break-after:always;"></p>\n')
        file.write('\t\t <div id=other_info>\n')
        file.write('\t\t\t<div class=unfilled>\n')
        file.write('\t\t\t\t<h1>Un-Filled Callings</h1>\n')
        for v in filtered_vacancies:
            file.write('\t\t\t\t{} ({})<br />\n'.format(v['position'], v['group']))
        file.write('\t\t\t</div>\n')
        file.write('\t\t\t<div class=no_callings>\n')
        file.write('\t\t\t\t<h1>Members Without Callings</h1>\n')
        file.write('\t\t\t\t<div id=col1>\n')
        for m in filtered_members_without_callings[0:len(filtered_vacancies)]:
            file.write('\t\t\t\t\t{}<br />\n'.format(m))
        file.write('\t\t\t\t</div>\n')
        if len(filtered_members_without_callings) > len(filtered_vacancies):
            file.write('\t\t\t\t<div id=col2>\n')
            for m in filtered_members_without_callings[len(filtered_vacancies):]:
                file.write('\t\t\t\t\t{}<br />\n'.format(m))
            file.write('\t\t\t\t</div>\n')
        file.write('\t\t\t</div>\n')
        file.write('\t\t</div>\n')
        file.write('\t</body>\n')
        file.write('</html>\n')
    print("callings.html created")

def printUnmatchedCallings(unmatched_callings_by_org):
    for org,unmatched_callings in unmatched_callings_by_org.items():
        if unmatched_callings:
            print("{}: {}".format(org, unmatched_callings))

def main():
    driver = login()

    class_assignments = getClassAssignmentsFromSite(driver)
    members_with_callings = getMembersWithCallingsFromSite(driver, class_assignments)
    members_without_callings = getMembersWithoutCallingsFromSite(driver)
    vacancies = getVacantCallingsFromSite(driver)
    closeDriver(driver)

    ordered_callings_by_org, unmatched_callings_by_org = putCallingsInOrder(members_with_callings)
    filtered_members_without_callings, filtered_out = filterMembersWithoutCallings(members_without_callings)
    filtered_vacancies = filterVacancies(vacancies)

    printUnmatchedCallings(unmatched_callings_by_org)

    getHTML(ordered_callings_by_org, filtered_vacancies, filtered_members_without_callings)

if __name__ == "__main__":
    import cProfile

    pr = cProfile.Profile()
    pr.enable()
    main()
    pr.disable()
    pr.print_stats(sort='time')
