#Timesheet Application
#BY: lodo loro
from datetime import datetime
import pandas as pd
import xlwings as xw
import pytz 
#variable for location of csv(change accordingly!!)
Time_Card = '/Users/lodoloro/programs/RMSPOPEProjects/Rms_Terminal_APP/Terminal/Website/timelog.csv'
Timelog = '/Users/lodoloro/programs/RMSPOPEProjects/Rms_Terminal_APP/Terminal/Website/Timelog.xlsx'
#read CSV file into dataframe
df = pd.read_csv(Time_Card)
#creating Data frame table
table = pd.DataFrame(df, columns = ['Employee', 'Date', 'Description', 'Vehicle', 'Runs', 'Location', 'Clock-IN', 'Vehicle-2', 'Clock-Out'])
#opens workbook TimeCard.xlsx 
wb = xw.Book(Timelog)
#adds to and updates Timecard sheet displays as TimeCard(2)
ws = wb.sheets['timelog']
my_date_handler = lambda year, month, day, **kwargs: "%04i/%02i/%02i" % (year, month, day)
#sets excel values and formats table
ws.range('A1').options(index=False, dates=my_date_handler,column=['Employee', 'Date', 'Description', 'Vehicle', 'Runs', 'Location', 'Clock-IN', 'Vehicle2', 'Clock-Out']).value = table
#Timezone setting
desired_timezone = 'Canada/Newfoundland'
timezone_obj = pytz.timezone(desired_timezone)
def write_to_last_row(data):
    try:
        # Open the Excel workbook using 'with open'
        workbook = wb
        sheet = ws

        # Determine the last row of the table
        last_row = sheet.range('A' + str(sheet.cells.last_cell.row)).end('up').row + 1

        # Write data to the last row
        for i, value in enumerate(data, start=1):
            sheet.cells(last_row, i).value = value

        # Save the workbook (closing is not needed with 'with open')
        workbook.save()
        workbook.close()
    except xw.exceptions.AppscriptError as e:
                # Handle the error here, e.g., log it or provide an error message to the user
        print(f"Error: {e}")
 

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
        now = datetime.now(timezone_obj)
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
        TimeCard_file.write('\n')
        #Close the file
        TimeCard_file.close()


def Clock_out(EmpVeh_='', EmpName_=''):
    #global variable passed as an argument
    global Time_Card
    global timezone_obj

    # Load the time card file
    df = pd.read_csv(Time_Card)

    # Input the name to search
    employee = EmpName_.upper()
    vehicle = EmpVeh_.upper()

    # Search for the employee in the DataFrame
    result = df[df['Employee'].str.contains(employee, case=False)]
    
    # Check if any matching rows are found
    if not result.empty:
        # Get the index of the last matching entry
        index = result.index[-1]
        day_check = df.loc[index,' Date']#returns matching clockin date

        # Add clock-out time in the file with the current time
        now = datetime.now(timezone_obj)
        Clock_out_time = now.strftime("%H:%M")
        Current_day  = now.strftime(" %Y/%m/%d")

#logic to determine if the found clockin record date is equal to the current date else...
        if day_check == Current_day:
            # Update the 'Clock-Out' column in the DataFrame
            df.iat[index, 7] = vehicle
            df.iat[index, 8] = Clock_out_time
            message1 = f'Congratulations you are Clocked OUT!'
        else:
            message1 = f'An Error occured please check that you are Clocked-In before trying again.'
        
# Save the updated DataFrame back to the file
        df.to_csv(Time_Card, index=False)
    else:
       message1 = f'No matching records found.'
#add function to delete incomplete rows
    return message1


#fix this so it calls add function to append new data to file for clock in/clock out
def Edit(empname='', date=''):
    found_records = []
    remaining_records = []
    # input the name you want to search
    emp_name = str(empname).upper()
    date = str(date).upper()

    primary_search = emp_name + ', ' + date
    secondary_search = emp_name
    with open(Time_Card, 'r') as file:
            for line in file:
                if line.startswith(primary_search):
                    found_records.append(line)
                elif line.startswith(secondary_search):
                    remaining_records.append(line)
    return remaining_records, found_records

def update_records(empname='', Date='', emp_des='', emp_veh='', emp_runs='', emp_area='', clock_in='', veh2='', clock_out='',confirmed=False):
    emp_name = str(empname).upper()
    date = str(Date).upper()

    primary_search = emp_name + ', ' + date
    secondary_search = emp_name

    all_records = []
    found_records = []
    remaining_records = []

    with open(Time_Card, 'r') as timecard_file:
        for line in timecard_file:
            if not line.startswith(primary_search):
                all_records.append(line)
            if line.startswith(primary_search):
                found_records.append(line)
            elif line.startswith(secondary_search):
                remaining_records.append(line)

    new_entry = f"{emp_name}, {date}, {emp_des}, {emp_veh}, {emp_runs}, {emp_area}, {clock_in}, {veh2}, {clock_out}\n"
    all_records.append(new_entry)

    if confirmed and found_records:
        with open(Time_Card, 'w') as file:
            for line in all_records:
                file.write(line)

            message = f"Record for {emp_name} on {date} has been updated successfully."
            return remaining_records, found_records, True,message
    else:
        confirmed = False
        message = f"No records found for {emp_name} on {date}."
        found_records = found_records.append(message)
        return remaining_records, found_records, False, message  


#This function will search employee and his working hours 
def Search(EmpName_='',date=''):
    emp_id = str(EmpName_).upper()
    date = str(date).upper()

    lst = []
    sum_h = 0
    sum_m = 0

    with open(Time_Card, 'r') as file:
        for line in file:
            if line.startswith(emp_id):
                word = line.split(',')
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
    # Convert excess minutes to hours
    sum_h += sum_m // 60
    sum_m %= 60
    total_hours = f"{sum_h}:{str(sum_m).zfill(2)}"
    new_list = [item.strip('\n').split(',') for item in lst]
    return new_list, total_hours


#this function will remove unwanted data from report
def Delete(EmpName_='', Date_='',confirmed=False):
    emp_name = str(EmpName_).upper()
    date = str(Date_).upper()

    primary_search = emp_name + ', ' + date
    secondary_search = emp_name

    found_records = []
    remaining_records = []
    all_records = []

    with open(Time_Card, 'r') as file:
        for line in file:
            if not line.startswith(primary_search):
                all_records.append(line)
            if line.startswith(primary_search):
                found_records.append(line)
            elif line.startswith(secondary_search):
                remaining_records.append(line)

    if confirmed and found_records:
        with open(Time_Card, 'w') as file:
            for line in all_records:
                file.write(line)

            message = f"Record for {emp_name} on {date} deleted successfully."
            return remaining_records, found_records, True,message
    else:
        confirmed = False
        message = f"No records found for {emp_name} on {date}."
        found_records = found_records.append(message)
        return found_records, remaining_records, False, message
    

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
                    Delete('ll50','2023/06/22')
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
                    Edit('ll50','2023/05/10')
                elif validPassword(password) == False:
                    print(password + " is invalid")
                    print('\n')
                    main()
            else:
                print('\n')
                main()
        #if you press any random key it will bring you here
        else:
            print("Incorrect input please try again \n")
            func = input("enter A for Add, S for Search, D for Delete, E for Edit, R for Report:")

if __name__ == "__main__":
    main()