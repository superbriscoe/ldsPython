from collections import OrderedDict

NAME = 'AndrewBriscoe'
PASSWORD = 'Lindsay121'
MINIMUM_AGE = 18
NAME_EXCEPTIONS = {'Betty Carroll': 'Betty Jo Carroll', 'Deborah Howard': 'Deb Howard', 'Tylen Kattenhorn': 'Ty Kattenhorn', 'Samuel Olsen': 'Sam Olsen', 'Elizabeth Bizardi': 'Liz Bizardi'}
ORGS_TO_COMBINE = ['Music', 'Other Callings', 'Employment and Welfare', 'Young Single Adult', 'Family History', 'Additional Callings']
ORGS_TO_IGNORE = ['Full-Time Missionaries']
CALLINGS_WITH_ASSIGNMENTS = ['Primary Teacher', 'Sunday School Teacher']
CALLING_NAME_REPLACEMENTS = {
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
CALLING_ORDER = OrderedDict([
    ('Bishopric', ['Bishop','1st Counselor','2nd Counselor','Executive Secretary','Clerk','Assistant Clerk--Finance','Assistant Clerk--Membership']),
    ('High Priests Group', ['Group Leader','1st Assistant', '2nd Assistant','Secretary','Instructor','4th Sunday Instructor']),
    ('Elders Quorum', ['President','1st Counselor','2nd Counselor','Secretary','Assistant Secretary','Instructor']),
    ('Relief Society', ['President','1st Counselor','2nd Counselor','Secretary','Compassionate Service Coordinator','Teacher','VT Coordinator','VT District Supervisor','ARM Coordinator','ARM Committee','Pianist','Music Leader']),
    ('Young Men', ['President','1st Counselor','2nd Counselor','Secretary','Priests Adviser','Teachers Adviser','Deacons Adviser','Scoutmaster','Assistant Scoutmaster','Scouting Committee Chairman','Scouting Committee Member']),
    ('Young Women', ['President','1st Counselor','2nd Counselor','Secretary','Laurel Adviser','Mia Maid Adviser','Beehive Adviser','Camp Director','Sports Specialist']),
    ('Sunday School', ['President','1st Counselor','2nd Counselor','Secretary','Teacher (Course 12)','Teacher (Course 13)','Teacher (Course 14, Course 15)','Teacher (Course 16, Course 17)','Teacher (Gospel Doctrine)','Teacher (Gospel Principles)','Librarian','Assistant Librarian']),
    ('Primary', ['President','1st Counselor','2nd Counselor','Secretary','Nursery Leader','Teacher (Sunbeam A)','Teacher (Sunbeam B)','Teacher (CTR 4)','Teacher (CTR 5)','Teacher (CTR 6A)','Teacher (CTR 6B)','Teacher (CTR 7)','Teacher (Valiant 8A)','Teacher (Valiant 8B)','Teacher (Valiant 9, Valiant 10)','Teacher (Valiant 11)','Teacher (Unassigned)','Activity Days','Music Leader','Pianist','Cubmaster','Cub Scout Committee Chairman','Cub Scout Committee Member','11-Year-Old Scout Leader','Webelos Leader','Webelos Assistant Leader','Wolf Den Leader','Wolf Den Assistant Leader', 'Bear Den Leader', 'Bear Den Assistant Leader']),
    ('Ward Missionaries', ['Ward Mission Leader','Assistant Ward Mission Leader','Ward Missionary']),
    ('Other Callings', ['Music Director','Choir Director','Choir Accompanist','Family History Consultant','Single Adult Representative','Young Single Adult Leader','Emergency Prep. Specialist','Employment Specialist','Humanitarian Specialist','Activities Specialist','Building Representative','Technology Specialist','Newsletter Coordinator','Bulletin Coordinator','Ward Greeter']),
    ('Stake', ['President','High Councilor','Assistant Clerk','Assistant Clerk--Membership','RS President','RS 2nd Counselor','Primary 2nd Counselor','YM 1st Counselor','YM 2nd Counselor','YWs Sports Director','YW Camp DIrector','YW Assistant Camp Director','Auditor','Cannery Coordinator','Director of Public Affairs','Emergency Radio Operator','Humanitarian Specialist','Seminary Teacher','Family History Center Director','Music Chairman','Scheduler--Building 3','Scheduler--Building 4'])
    ])
CALLINGS_TO_IGNORE = OrderedDict([
    ('Bishopric', []),
    ('High Priests Group', ['HT District Supervisor']),
    ('Elders Quorum', ['HT District Supervisor']),
    ('Ward Missionaries', []),
    ('Relief Society', []),
    ('Young Men', ['Priests President','Varsity Coach','Assistant Venturing Crew Adviser', 'Venturing Crew Adviser', 'Assistant Varsity Coach']),
    ('Young Women', []),
    ('Primary', []),
    ('Sunday School', []),
    ('Other Callings', []),
    ('Stake', ['Assistant Clerk--Finance'])
    ])
VACANT_CALLINGS_TO_IGNORE = ['Scheduler--Building 1','Scheduler--Building 2','Scheduler--Building 3','Scheduler--Building 4','Scheduler--Building 5']
VACANT_GROUPS_TO_IGNORE = ['Teachers Quorum Presidency', 'Laurel Presidency']
VACANT_NAME_REPLACEMENTS = {'Relief Society':'RS',
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
                   'Assistant': 'Asst.',
                   '  ': ' '}


MEMBERS_WITHOUT_CALLINGS_IGNORE = ['Ryan Alvord','Alissa Augustine','Tom Babeor','Mandy Baca','Aaron Bacoccini','Alisha Bacoccini','Cassie Bacoccini','Jeremy Bacoccini','Chynna Begay','Stephen Blaylock','Scott Bradley','Jeff Braithwaite','Karen Braithwaite','Christopher Cahoon','Julie Carr','Kelly Chicas','Mike Chisholm','Roberta Closner','Lourdes Davis','Tyrell Davis','Monique Delgarito','Raland Delgarito','Rydall Delgarito','Tamani Enciso','Amber Fitzgerald','Catherine Fitzgerald','Erin Fitzgerald','John Fitzgerald','Janice Foster','Jaynette Foutz','Chad Frank','Jan Frank','Hailey Frentheway','Kay Green','Kathleen Griffin','Shirley Habish','Amy Hayward','Michael Hayward','Emily Healy','Pamela Hechler','Robert Hechler','Paul Howard','Christopher Joens','Katerra Johnson','Kimberly Johnson','Tim Johnson','John Lahoff','Joseph Lahoff','Carl Leishman','Florence Leishman','Candace Lewis','Kaye Lewis','Donald Lloyd','Edith Logan','Al Manning','Elizabeth Manning','Colleen Martinez','Sophia Martinez','John Mercer','Loretta Mercer','Philip Nelson','Gail Page','Abigail Peterson','Benjamin Peterson','David Peterson','Melanie Peterson','Martin Reed','Bevan Rhodes','Daniel Rhodes','Rosalee Rife','Sandra Ross','Tabitha Ruple','Gary Skidmore','Ruth Stevens','Bryan Struve','Leslie Sumner','Matthew Swensen','Shannon Swenson','Alice Tollestrup','Barbara Tompkins','Keegan Udall','Brittany Wade','Carla Wade','Wade Weeks','Ashley Wilson','Matthew Wilson','Michael Wilson','Candice Yazzie','Brian Zufelt','Jeanette Zufelt']

