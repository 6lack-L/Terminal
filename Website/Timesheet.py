#Timesheet 
# basic application written in Python
#BY: lodo loro
#Working Hours for a Week
#Run the program. Click an option A = Add :: S = Search :: D = Delete :: E = Edit :: R = Report :: Q = Quit
#To add time Type A, press enter, write In for Clock-in, and Out for Clock Out
#Search based on names, to see Total Hours worked
#Delete based on Date, only manager can delete records
#Edit data by selecting an Employee and a Date, Only manager can edit the record.
#Report of employee, only manager can see it
from datetime import datetime
import time
import fileinput
import pandas as pd
import xlwings as xw


xw.Book ('Timelog.xlsx')
#variable for location of csv(change accordingly!!)
Time_Card = '/Users/lodoloro/programs/RMSPOPEProjects/Rms_Terminal_APP/Terminal/Website/timelog.csv'

#read CSV file into dataframe
df = pd.read_csv(Time_Card)
#creating Data frame table
table = pd.DataFrame(df, columns = ['Employee', 'Date', 'Description', 'Vehicle', 'Runs', 'Location', 'Clock-IN', 'Vehicle-2', 'Clock-Out'])
#opens workbook TimeCard.xlsx 
wb = xw.books('Timelog.xlsx')
#adds to and updates Timecard sheet displays as TimeCard(2)
ws = wb.sheets['timelog']
my_date_handler = lambda year, month, day, **kwargs: "%04i/%02i/%02i" % (year, month, day)
#sets excel values and formats table
ws.range('A1').options(index=False, dates=my_date_handler,column=['Employee', 'Date', 'Description', 'Vehicle', 'Runs', 'Location', 'Clock-IN', 'Vehicle-2', 'Clock-Out']).value = table


#Using Add to add data in file first, We have to add clock in time 
def Add(EmpName='',EmpDes='',EmpVeh='',EmpRuns='',EmpArea=''):
    
    Time_emp = 'in'
    #Change it to upper to get rid of input error
    Time = Time_emp.upper()
    if Time == "OUT":
        Clock_out()
    elif Time == "IN":

        #Open the Timecard.txt file in append mode
        TimeCard_file = open(Time_Card, 'a')
       
        # Add clock in time in file with current time.
        EmpName_ = EmpName
        EmpDes_ = EmpDes
        EmpVeh_ = EmpVeh
        EmpRuns_ = EmpRuns
        EmpArea_ = EmpArea
        Emp_Name = EmpName_.upper()
        Emp_Des = EmpDes_.upper()
        Emp_Veh = EmpVeh_.upper()
        Emp_Runs = EmpRuns_.upper()
        Emp_Area = EmpArea_.upper()
        now = datetime.now()
        print(TimeCard_file)
        Current  = now.strftime("%Y/%m/%d")
        Clock_in = now.strftime("%H:%M")

        #Append data to the file
        TimeCard_file.write(Emp_Name + ', ')
        TimeCard_file.write(Current + ', ')
        TimeCard_file.write(Emp_Des + ', ')
        TimeCard_file.write(Emp_Veh + ', ')
        TimeCard_file.write(Emp_Runs + ', ')
        TimeCard_file.write(Emp_Area + ', ')
        TimeCard_file.write(Clock_in + ',')
#        print("Your Current Date is:",Current)
#        print("Your Clock in Time is :", Clock_in)
#        print("Work Type: ", Emp_Des)
#        print("Vehicle: ", Emp_Veh)
#        print("Runs: ", Emp_Runs)
#        print("Location: ", Emp_Area)
        TimeCard_file.write('\n')
        #Close the file
        TimeCard_file.close()

    #Check if user wants to add another record to the file
#    func = input("Enter Q to quit, Press M for main menu or Press E to Edit:")
#    if func == "Q" or func =="q":
#        quit()
#    elif func == "M" or func =="m":
#        return main()
#    elif func == "E" or func == "e":
#        return Edit()
#    else:
#        print("Incorrect input, Please Try Again \n")

#First Ask for employee name so can add clock out time for same person.

def Clock_out(EmpVeh_='',EmpName_=''):
    found = False
    val = 'x'
    #input the name what you want to search
    employee_name = EmpName_
    employee = employee_name
    EmpVeh = EmpVeh_
    Emp_Veh = EmpVeh.upper()
    
    #open the time card file and search name
    TimeCard_file = open(Time_Card, 'r')
    TimeCard = TimeCard_file.readline()
    #read the file if you have entered any name
    while TimeCard != '':
        found = TimeCard.startswith(employee)
        if found:
            val = TimeCard
        TimeCard = TimeCard_file.readline()
    TimeCard_file.close()

    if val != '':
       #Add clockout time in file with current time
        now = datetime.now()
        Current  = now.strftime("%Y-%m-%d")
        Clock_out = now.strftime("%H:%M")
        search = val
#        print(search.rstrip('\n') + ' ' + Clock_out + ', ' + Emp_Veh)
#        print("You are Clocked out successfully")
        TimeCard_file.close()
       
        #open the file
        fn = Time_Card
        f = open(fn)
        output = []
        #for loop i you find search record
        for line in f:
            if line.startswith(val):
                output.append(line.replace(line, line.rstrip('\n') + ' ' +Emp_Veh+ ', ' + Clock_out) + '\n')
            else:
                output.append(line)
        f.close()
        f = open(fn, 'w')
        f.writelines(output)
        f.close()

    try:
        with open(Time_Card, 'r') as TimeCard_file:
            for TimeCard in TimeCard_file:
                if TimeCard.startswith(employee):
                    words = TimeCard.strip().split(',')
                    start = words[-1] if words[-1] else words[6]
                    end = Clock_out if Clock_out else words[-1]
                    start_hour, start_minute = map(int, start.split(':'))
                    end_hour, end_minute = map(int, end.split(':'))
                    total_minutes = (end_hour - start_hour) * 60 + (end_minute - start_minute)
                    if total_minutes < 0:
                        total_minutes += 12 * 60
                    total_hours, minutes = divmod(total_minutes, 60)
                    print(f"Total Working Hours is: {total_hours} Hours and {minutes} Minutes\n")
    except FileNotFoundError:
        print(f"Error: {Time_Card} file not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


    #added function to make decision if you want to work on this file or exit
#    func = input("Enter Q to quit or Press M for main menu:")
#    if func == "Q" or func =="q":
#        quit()
#    elif func == "M" or func =="m":
#        return main()
#    else:
#        print("Incorrect input, Please Try Again \n")

#This function will display all working time for all employee

def TimeReport():
    #open time card
    TimeCard_file = open(Time_Card,'r')
    TimeCard = TimeCard_file.readline()
    
    #read the rest of the file
    while TimeCard != '':
        word = [line.split(',') for line in TimeCard.splitlines()]
        names = word[0][0]
        date = word[0][1]
        start = word[0][7]
        if len(word[0][6]) > 6 or len(word[0][6]) == '':
            start = word[0][6]
            end = '00:00 -Clocked IN'
        else:
            start = word[0][-3]
            end = word[0][-1]
        
        #Display the record
        print('Employee Hours:', names, date, start, end)
        #Read the next Description
        TimeCard = TimeCard_file.readline()
    #close the file
    TimeCard_file.close()

    #Added function to make decision if want to work or exit
#    func = input("Enter Q to quit or Press M for main menu:")
#    if func == "Q" or func =="q":
#        quit()
#    elif func == "M" or func =="m":
#        return main()
#    else:
#        print("Incorrect input, Please Try Again \n")

#fix this so it calls add function to append new data to file for clock in/clock out
def Edit():
    found =  False

    #input the name you want to search
    EmpName = input("Please Enter Employee Name:")
    employee = EmpName.upper()

    #open the time card file and search name
    TimeCard_file = open(Time_Card,'r')
    TimeCard = TimeCard_file.readline()

    #read the file if you have entered any name
    while TimeCard != '':
        found = TimeCard.startswith(employee)
        if found:
            print(TimeCard)

        TimeCard = TimeCard_file.readline()
    TimeCard_file.close()
    

    Date = input("Enter the Date you want to edit[yyyy/mm/dd]:")
    search = (employee + ", " + Date)

    #Open the file
    fn = Time_Card
    f = open(fn)
    output = []
    #for loop i you find search record
    for line in f:
        if not line.startswith(search):
            output.append(line)
    f.close()
    f = open(fn, 'w')
    f.writelines(output)
    f.close()


    #open the TimeCard.txt file in append mode
    TimeCard_file = open(Time_Card, 'a')
    print("enter Clock in and Clock out for",employee)

    Clock_in = input("Enter Clock In time:")
    #Clock_out = input("Enter Clock Out time:")
    EmpDes = input ('Enter Work Type:')
    EmpVeh = input ('Enter Vehicle:')
    EmpRuns = input ('Enter Runs:')
    EmpArea = input ('Enter Area:')
    #EmpVeh2 = input ('Enter Vehicle-2 if you Switched:')
    Emp_Des = EmpDes.upper()
    Emp_Veh = EmpVeh.upper()
    #Emp_Veh2 = EmpVeh2.upper()
    Emp_Runs = EmpRuns.upper()
    Emp_Area = EmpArea.upper()
    #writing to file
    TimeCard_file.write(employee + ", ")
    TimeCard_file.write(Date + ", ")
    TimeCard_file.write(Emp_Des + ', ')
    TimeCard_file.write(Emp_Veh + ", ")
    TimeCard_file.write(Emp_Runs + ", ")
    TimeCard_file.write(Emp_Area + ", ")
    TimeCard_file.write(str(Clock_in) + ", ")
    #TimeCard_file.write(Emp_Veh2 + ", ")
    #TimeCard_file.write(str(Clock_out) + ", ")
    TimeCard_file.write('\n')

    #Close the file
    TimeCard_file.close()
    
#Check if user wants to add another record to the file
#    func = input("Enter Q to quit or Press M for main menu:")
#    if func == "Q" or func =="q":
#        quit()
#    elif func == "M" or func =="m":
#        return main()
#    else:
#        print("Incorrect input, Please Try Again \n")


#This function will search employee and his working hours 
def Search(EmpName_=''):
    emp_id = str(EmpName_).upper()
    EmpName_=emp_id

    lst = []
    sum_h = 0
    sum_m = 0
    with open(Time_Card, 'r') as file:
        for line in file:
            if line.startswith(emp_id):
                word = line.split(',')
#                worktype = word[2]
#                vehicle = word[3]
#                runs = word[4]
#                area = word[5]
                start = datetime.strptime(word[6], ' %H:%M')
                end = datetime.strptime(word[-1].strip(), '%H:%M') if len(word[-1]) >= 5 else datetime.strptime('00:00', '%H:%M')
                hours = (end - start).seconds // 3600
                minutes = ((end - start).seconds // 60) % 60
                if hours < 0:
                    hours = 0
                    minutes = 0
                sum_h += hours
                sum_m += minutes
                lst.append(line)
#    total_mins = sum_h * 60 + sum_m
#    total_hrs, total_mins = divmod(total_mins, 60)
#    lst.append(('Total Working Hours:', f'{total_hrs} Hours and {total_mins} Minutes'))
    return lst
    #added function to make decision if you want to work on this file or exit
#    func = input("Enter S to Keep Searching or Press M for main menu:")
#    if func == "S" or func =="s":
#        Search()
#    elif func == "M" or func =="m":
#        return main()
#    else:
#        print("Incorrect input, Please Try Again \n")


#this function will remove unwanted data from report

def Delete():
    found = False
    #input the name you want to search
    EmpName = input("Please Enter Employee Name:")
    employee = EmpName.upper()

    #open the time card file and search name
    TimeCard_file = open(Time_Card,'r')
    TimeCard = TimeCard_file.readline()

    #read the file if you have entered any name
    while TimeCard != '':
        found = TimeCard.startswith(employee)
        if found:
            print(TimeCard)

        TimeCard = TimeCard_file.readline()
    TimeCard_file.close()
    TimeCard = filter(lambda x: not x.isspace(), TimeCard)
    #Find the blank space and delete it
    Date = input("Enter the date you want to delete[yyyy/mm/dd]:")
    search = (employee + ', ' + Date)

    #open the file
    fn = Time_Card
    f = open(fn)
    output = []
    #for loop i you find search record
    for line in f:
        if not line.startswith(search):
            output.append(line)
    f.close()
    f = open(fn, 'w')
    f.writelines(output)
    f.write("".join(TimeCard))
    f.close()
    print("You successfully deleted " + search + "'s Record")
   

#    func = input("Enter D to Delete more or Press M for main menu:")
#    if func == "D" or func =="d":
#        Delete()
#    elif func == "M" or func =="m":
#        return main()
#    else:
#        print("Incorrect input, Please Try Again \n")



#Password function for manager access:
def getPassword():
   return input("Enter password: ")

def CountDigitsFor(password):
   return sum(character.isdigit() for character in password)

def validPassword(password):
   if len(password) >= 8 and password.isalnum() and CountDigitsFor(password) >= 2 and password == 'Rmspope2022':
      return True
   return False


def main():
    #Select the option what you like to do in you time card
    print("What would you like to do in Time Card System?")
    print("IN = Clock-IN :: OUT = Clock-OUT :: S = Search :: D = Delete :: E = Edit :: R = Report :: Q = Quit")
    func = input("Please select a function from the list above:")

    #Use while loop to enter in time card as selected option
    while func == '' or func != 'in'  or func != 'IN' or func != 'out'  or func != 'OUT' or func != 'S' or func != 's' or func != 'D' or func != 'd' or func != 'E' or func != 'e' or func != 'R' or func != 'r':
        if func == 'in' or func == 'IN':
            Add(EmpName='',EmpDes='',EmpVeh='',EmpRuns='',EmpArea='')
        elif func == 'out' or func == 'OUT':
            Clock_out()
        elif func == 'S' or func == 's':
            Search()
        
        # only manager can use Report, Delete and Edit Options
        elif func == 'D' or func == 'd':
            print('Are you Manager?:')
            Mrg_emp = input("Y=Yes, Anything Else = No:")
            Mgr= Mrg_emp.upper()
            if (Mgr == 'YES' or Mgr == 'Y'):
                password = getPassword()
                if validPassword(password) == True:
                    print(password + " is valid")
                    Delete()
                elif validPassword(password) == False:
                    print(password + " is invalid")
                    print('\n')
                    main()
            else:
                print('\n')
                main()
        elif func == 'E' or func == 'e':
            print('Are you Manager?:')
            Mrg_emp = input("Y=Yes, Anything Else = No:")
            Mgr= Mrg_emp.upper()
            if (Mgr == 'YES' or Mgr == 'Y'):
                password = getPassword()
                if validPassword(password) == True:
                    print(password + " is valid")
                    Edit()
                elif validPassword(password) == False:
                    print(password + " is invalid")
                    print('\n')
                    main()
            else:
                print('\n')
                main()
        elif func == 'R' or func == 'r':
            print('Are you Manager?:')
            Mrg_emp = input("Y=Yes, Anything Else = No:")
            Mgr= Mrg_emp.upper()
            if (Mgr == 'YES' or Mgr == 'Y'):
                password = getPassword()
                if validPassword(password) == True:
                    print(password + " is valid")
                    TimeReport()
                elif validPassword(password) == False:
                    print(password + " is invalid")
                    print('\n')
                    main()
            else:
                print('\n')
                main()
        elif func == "Q" or func == "q":
            quit()
        #if you press any random key it will bring you here
        else:
            print("Incorrect input please try again \n")
            func = input("enter A for Add, S for Search, D for Delete, E for Edit, R for Report:")

if __name__ == "__main__":
    main()

