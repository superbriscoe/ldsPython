abbreviations = {
    "HP": "High Priests",
    "EQ": "Elders Quorum",
    "RS": "Relief Society",
    "YM": "Young Men",
    "YW": "Young Women",
    "PR": "Primary",
    "SS": "Sunday School",
    "WM": "Ward Mission",
    "B": "Bishop Wheeler",
    "B1": "Brother Anderson",
    "1st": "Brother Anderson",
    "B2": "Brother Wilcox",
    "2nd": "Brother Wilcox",
    "ES": "Brother Briscoe",
    "BE": "Brother Briscoe",
    "BC": "Brother Beutler",
    "C": "Brother Beckett",
    "BA": "Bishopric",
    "WC":  "Ward Council",
    "PEC": "PEC",
    "SCC": "Scout Committee Chair"}

import gspread
from datetime import date, timedelta, datetime
import calendar
from pprint import pprint

from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds']

credentials = ServiceAccountCredentials.from_json_keyfile_name('ServiceKey.json', scope)

gc = gspread.authorize(credentials)
sheet = gc.open_by_key("1zbVPSP7gTzWARpx74MU47UEPwyrgasWI_aPy-JHB3WY").sheet1

def getSundayDate():
    today = date.today()

    if today.weekday() == calendar.SUNDAY:
        #Today is Sunday so pretend like its monday
        today = today + timedelta(days=1)

    sunday = today + timedelta((calendar.SUNDAY - today.weekday())%7)
    return sunday.strftime("%m/").lstrip("0")+sunday.strftime("%d").lstrip("0")+sunday.strftime("/%Y")

def findNextWeekColumn():
    column = sheet.row_values(1).index(getSundayDate())+1
    return column

def pullInfo():
    column = findNextWeekColumn()
    columnData = sheet.col_values(column)
    info={}
    info["date"] = columnData[0]
    info["bishopric_spiritual_thought"] = columnData[5]
    info["bishop_ppi"] = columnData[7]
    info["first_counselor_ppi"] = columnData[8]
    info["second_counselor_ppi"] = columnData[9]
    info["meeting"] = columnData[11]
    info["conducting"] = columnData[12]
    info["meeting_spiritual_thought"] = columnData[13]
    info["prayers"] = sheet.cell(19,column+1).value
#     info["BYD"]
#     info["BYC"]
#     info["primaryVisit"]
#     info["YWvisit"]
    return info

def getLetter(num):
    alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    if num > 702:
        raise Exception("NOT IMPLEMENTED FOR COLUMNS ABOVE 702 (ZZ)")

    if num <= 26:
        return alpha[num-1]
    else:
        count = int( (num-1)/26 ) - 1
        return alpha[count]+alpha[(num-1)%26]

def convertDate(dateStr, format1, format2):
    date = datetime.strptime(dateStr, format1)
    return date.strftime(format2)

def getNextWeeksInfo(numWeeks):
    col = findNextWeekColumn()
    data = [cell.value for cell in sheet.range("{}1:{}35".format(getLetter(col+1),getLetter(col+numWeeks)))]
    weeksInfo = list(zip(*[data[i:i+numWeeks] for i in range(0, len(data), numWeeks)]))

    output = ""
    missionaryMoments = ""

    #Check if we need to get a missionary moment for the current month
    if int(weeksInfo[0][2]) > 7:
        month = convertDate(weeksInfo[0][0], "%m/%d/%Y" ,"%B")
        org = abbreviations.get(weeksInfo[0][34], weeksInfo[0][30:35])
        missionaryMoments = "Missionary Letters/Moment ({}): {}\n".format(month, org)

    for week in weeksInfo:
        date = convertDate(week[0], "%m/%d/%Y" ,"%B %d")
        meeting = abbreviations.get(week[11], "No Meeting")
        if meeting != "No Meeting":
            thought = "Thought: " +abbreviations.get(week[13], "")
            note = ""
        else:
            thought = ""
            note = "(Time subject to change)"
        b_ppi = abbreviations.get(week[7].replace("*", ""), "")
        f_ppi = abbreviations.get(week[8], "")
        s_ppi = abbreviations.get(week[9], "")

        ppis = ", ".join([x for x in [b_ppi, f_ppi, s_ppi] if x != ""])
        if ppis != "":
            ppis = "8:30 PPIs: {} {}".format(ppis,note)
        output = output + "{:15}{:15}{:28}{}\n".format(date, meeting, thought, ppis)
        if int(week[2]) <= 7:  # This means the date is during the first week of a month
            month = convertDate(week[0], "%m/%d/%Y" ,"%B")
            org = abbreviations.get(week[34], "")
            missionaryMoments = missionaryMoments+"Missionary Letters/Moment ({}): {}\n".format(month, org)
    return output+missionaryMoments


def getMeetingThought():
    info = pullInfo()
    thought = abbreviations.get(info.get("meeting_spiritual_thought", ""), "ERROR")
    return info.get('date', "ERROR"), thought

def getWCAgendaHeader(numWeeks):
    nextSunday, thought = getMeetingThought()
    print(convertDate(nextSunday, "%m/%d/%Y", "%B %d, %Y\n"))
    print("Opening Prayer & Spiritual Thought - {}\n".format(thought))
    print(getNextWeeksInfo(numWeeks))


def getReminders():
    reminders = ""

    info = pullInfo()
    print(info['date'])
    print()

    try:
        s = abbreviations[info['bishopric_spiritual_thought']]
        print("Bishopric Spiritual Thought: {}".format(s))
    except Exception as e:
        pass

    try:
        s = abbreviations[info['bishop_ppi']]
        print("Bishop PPI: {}".format(s))
    except Exception as e:
        pass

    try:
        s = abbreviations.get("1st")
        t = abbreviations[info['first_counselor_ppi']]
        print("{} PPI: {}".format(s,t))
    except Exception as e:
        pass

    try:
        s = abbreviations.get("2nd")
        t = abbreviations[info['second_counselor_ppi']]
        print("{} PPI: {}".format(s, t))
    except Exception as e:
        pass

    try:
        s = abbreviations[info['meeting']]
        t = abbreviations[info['meeting_spiritual_thought']]
        print("{} Spiritual Thought: {}".format(s, t))
    except Exception as e:
        pass

    try:
        s = abbreviations[info['meeting']]
        t = abbreviations[info['conducting']]
        print("{} Conducting: {}".format(s, t))
    except Exception as e:
        pass

    try:
        s = abbreviations[info['prayers']]
        print("Next Week Sacrament Meeting Prayers: {}".format(s))
    except Exception as e:
        pass

def main():
    getWCAgendaHeader(4)
    print("\n")
    getReminders()
    print("\n")
    pprint(pullInfo())

if __name__ == "__main__":
    main()