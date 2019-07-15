from datetime import time, datetime, timedelta
import textwrap
import re

running_total = 0 
with open('testfile.txt', 'w') as f:
    day_one = input('\n\nHow many days back would you like to calculate hours for? ')
    running_date = datetime.now() - timedelta(days=int(day_one)) 
    f.write('Hours Worked: Hunter Templeman\n\n')
    while(running_date < datetime.now()):
        fdt = running_date.strftime('%A, %d. %B')
        calc_q = '\n\nWould you like to tally hours for {0}? '.format(fdt)
        calc_a = input(calc_q)
        if(calc_a == 'yes' or calc_a == 'y'):
            text_output = '{0}: \n'.format(fdt)
            f.write(text_output)
            continue_questions = True
            daily_total=0
            while(continue_questions):
                currDate = datetime.now()
                firstq = '\nEnter a start time: '
                q1 = input(firstq)
                time1 = re.findall(r"\d{1,2}", q1) 
                t1 = time(int(time1[0]), int(time1[1]))
                secondq = 'Enter an end time: '
                q2 = input(secondq)
                time2 = re.findall(r"\d{1,2}", q2)
                t2 = time(int(time2[0]), int(time2[1]))
                dt1 = datetime.combine(currDate, t1)
                dt2 = datetime.combine(currDate, t2)
                delta = (dt2 - dt1).total_seconds() / 3600
                running_total += delta
                daily_total += delta
                punch= '{0} -- {1}\n'.format(t1, t2)
                punchout = textwrap.indent(punch, '    ')
                f.write(punchout)
                ask_another = input('\nWould you like to enter another time span? ')
                if(ask_another == 'yes' or ask_another=='y'):
                    pass;
                else:
                    fin_daily = 'DAILY TOTAL: ' + str(daily_total) + ' HOURS\n\n'
                    fin_out = textwrap.indent(fin_daily, '    ')    
                    f.write(fin_out)
                    continue_questions = False
                    running_date = running_date + timedelta(days=1)
        elif(calc_a == 'no' or calc_a == 'n'):
            running_date = running_date + timedelta(days=1)
        else:
            print("I don't understand that!")
        #f.write(t)

final_hours = '\n\nTOTAL HOURS: ' + str(running_total)
f.write(final_hours)
