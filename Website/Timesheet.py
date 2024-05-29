############################################
#Source code for Time Card System
#BY: Lodo Loro
############################################
#create settings page with these options below eventually apply to html for easy changing in application 
##############################################################################################################
import os
import tempfile
import logging
import pandas as pd
import xlwings as xw 
import pytz
from datetime import datetime
from Website import models
from . import db
#variable for location of csv(change accordingly!!)
Time_Card = '/Users/lodoloro/programs/RMSPOPEProjects/Rms_Terminal_APP/Terminal/Website/timelog.csv'
backup_sheet = '/Users/lodoloro/programs/RMSPOPEProjects/Rms_Terminal_APP/Terminal/Website/backup_sheet.csv'
Timelog = '/Users/lodoloro/programs/RMSPOPEProjects/Rms_Terminal_APP/Terminal/Website/Timelog.xlsx'

#CSV file into dataframe
df = pd.read_csv(Time_Card)
table = pd.DataFrame(df, columns = ['Employee', 'Date', 'Description', 'Vehicle', 'Runs', 'Location', 'Clock-IN', 'Vehicle-2', 'Clock-Out'])

#opens workbook TimeCard.xlsx
wb = xw.Book(Timelog)
ws = wb.sheets['timelog']
my_date_handler = lambda year, month, day, **kwargs: "%04i/%02i/%02i" % (year, month, day)
ws.range('A1').options(index=False, dates=my_date_handler,column=['Employee', 'Date', 'Description', 'Vehicle', 'Runs', 'Location', 'Clock-IN', 'Vehicle2', 'Clock-Out']).value = table

#Timezone settings
desired_timezone = 'Canada/Newfoundland'
timezone_obj = pytz.timezone(desired_timezone)
now = datetime.now(timezone_obj)
###################################################################################
def Add(EmpName='',EmpDes='',EmpVeh='',EmpRuns='',EmpArea=''):
    check_columns()
    try:
        with open(Time_Card, 'a') as TimeCard_file:
            # Add clock in time in file with current time.
            Emp_Name = EmpName.upper()
            Emp_Des = EmpDes.upper()
            Emp_Veh = EmpVeh.upper()
            Emp_Runs = EmpRuns.upper()
            Emp_Area = EmpArea.upper()
            Current  = now.strftime("%Y/%m/%d")
            Clock_in = now.strftime("%H:%M")

            #Append data to the file
            TimeCard_file.write(f"{Emp_Name}, {Current}, {Emp_Des}, {Emp_Veh}, {Emp_Runs}, {Emp_Area}, {Clock_in},\n")
            check_columns()
            update_backup()
    except FileNotFoundError:
        logging.error(f"File not found: {Time_Card}. Please ensure the file exists and the path is correct.")
    except PermissionError:
        logging.error(f"Permission denied: {Time_Card}. Please ensure you have the necessary permissions to write to the file.")
    except Exception as e:
        logging.error(f"An error occurred while writing to the file: {e}")
def Clock_out(EmpVeh_='', EmpName_=''):
    try:
        df = pd.read_csv(Time_Card)
    except FileNotFoundError:
        return f"File not found: {Time_Card}. Please ensure the file exists and the path is correct."
    except ValueError:
        backup_sheet()
        check_columns()
        backup_sheet()
    except Exception as e:
        return f"An error occurred while reading the file: {e}"
        
    employee = EmpName_.upper()
    vehicle = EmpVeh_.upper()
    # Search for the employee in the DataFrame
    result = df[df['Employee'].str.contains(employee)]
    if not result.empty:
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
            message = (True,'Congratulations you are Clocked OUT!')
        else:
            message = (False,'An Error occured please check that you are Clocked-In before trying again.')
# Save the updated DataFrame back to the file
        try:
            df.to_csv(Time_Card, index=False)
            update_backup()
        except ValueError:
            check_columns()
    else:
       message = ( False,'No matching records found.')
    return message
def Edit(empname='', date=''):
    check_columns()
    found_records = []
    remaining_records = []

    emp_name = str(empname).upper()
    date = str(date)
    
    primary_search = emp_name + ', ' + date
    secondary_search = emp_name
    
    try:
        with open(Time_Card, 'r') as file:
            for line in file:
                if line.upper().startswith(primary_search):
                    found_records.append(line)
                elif line.upper().startswith(secondary_search):
                    remaining_records.append(line)
    except FileNotFoundError:
        logging.exception("File not found")
        return remaining_records, found_records, "File not found. Please ensure the file exists and the path is correct."
    except PermissionError:
        logging.exception("Permission denied")
        return remaining_records, found_records, "Permission denied. Please ensure you have the necessary permissions to read the file."
    except ValueError:
        logging.exception("value error")
        check_columns()
        return remaining_records, found_records, "Permission denied. Please ensure you have the necessary permissions to read the file."
    except Exception as e:
        logging.exception("An error occurred while reading the file")
        return remaining_records, found_records, f"An error occurred while reading the file: {e}"
    return remaining_records, found_records
def update_records(empname='', Date='', emp_des='', emp_veh='', emp_runs='', emp_area='', clock_in='', veh2='', clock_out='',confirmed=False):
    emp_name = str(empname).upper()
    date = str(Date)

    primary_search = f'{emp_name}, {date}'
    secondary_search = emp_name

    all_records = []
    found_records = []
    remaining_records = []

    try:
        with open(Time_Card, 'r') as timecard_file:
            for line in timecard_file:
                if line.upper().startswith(primary_search):
                    found_records.append(line)
                elif line.upper().startswith(secondary_search):
                    remaining_records.append(line)
                else:
                    all_records.append(line)
    except FileNotFoundError:
        logging.error("File not found")
        return remaining_records, found_records, False, "File not found. Please ensure the file exists and the path is correct."
    except PermissionError:
        logging.error("Permission denied")
        return remaining_records, found_records, False, "Permission denied. Please ensure you have the necessary permissions to read the file."
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return remaining_records, found_records, False, f"An error occurred while reading the file: {e}"

    new_entry = f"{emp_name}, {date}, {emp_des}, {emp_veh}, {emp_runs}, {emp_area}, {clock_in}, {veh2}, {clock_out}\n"
    try:
        if confirmed and found_records:
            all_records.append(new_entry)
            with open(Time_Card, 'w') as file:
                for line in all_records:
                    file.write(line)
            return remaining_records, found_records, True, f"Record for {emp_name} on {date} has been updated successfully."
        else:
            found_records = ['None found']
            check_columns()
            return remaining_records, found_records, False, f"No records found for {emp_name} on {date}."
    except Exception as e:
        logging.error(f"an error occured: {e}")
        return remaining_records, found_records, False, f"an error occured for: {Time_Card}. Please ensure the file exists and the path is correct."
def Search(EmpName_=''):#main function for retrieving hours by employee code
    check_columns()
    emp_id = str(EmpName_).upper()

    lst = []
    sum_h = 0
    sum_m = 0

    try:
        with open(Time_Card, 'r') as file:
            for line in file:
                if line.startswith(emp_id):
                    word = line.split(',')
                    start = datetime.strptime(word[6], ' %H:%M')
                    if len(word[-1]) < 5:
                        end = 00
                    else:
                        end = datetime.strptime(word[-1].strip(), '%H:%M')
                    
                    if end != 0:
                        hours = (end - start).seconds // 3600
                        minutes = ((end - start).seconds // 60) % 60
                        
                        if hours < 0:
                            hours = 0
                            minutes = 0
                        
                        sum_h += hours
                        sum_m += minutes
                    lst.append(line)
    except FileNotFoundError:
        logging.error(f"File not found: {Time_Card}. Please ensure the file exists and the path is correct.")
    except PermissionError:
        logging.error(f"Permission denied: {Time_Card}. Please ensure you have the necessary permissions to read the file.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    sum_h += sum_m // 60
    sum_m %= 60
    total_hours = f"{str(sum_h).zfill(2)}:{str(sum_m).zfill(2)}"
    new_list = [item.strip('\n').split(',') for item in lst]
    return new_list, total_hours
def Delete(EmpName_='', Date_='', confirmed=False): #this function will remove unwanted records from the file
    check_columns()
    emp_name = str(EmpName_).upper()
    date = str(Date_)
    delete_all = False
    if date == 'delete':
        delete_all = True
    primary_search = f'{emp_name}, {date}'
    secondary_search = emp_name

    found_records = []
    remaining_records = []
    all_records = []
    try:
        with open(Time_Card, 'r') as file:
            for line in file:
                if line.startswith(primary_search):
                    found_records.append(line)
                elif line.startswith(secondary_search) and line not in found_records:
                    remaining_records.append(line)                 
                else:
                    all_records.append(line)
        print(found_records)
        print('-------------------')
        print(remaining_records)
    except FileNotFoundError:
        logging.error("File not found")
        return [], [], False, f"File not found: {Time_Card}. Please ensure the file exists and the path is correct."
    except PermissionError:
        logging.error("Permission denied")
        return [], [], False, f"Permission denied: {Time_Card}. Please ensure you have the necessary permissions to read the file."
    except Exception as e:
        logging.error("An error occurred while reading the file")
        return [], [], False, f"An error occurred while reading the file: {e}"
    
    if delete_all == True:
        found_records.extend(remaining_records)
        for k in found_records:
            if k in all_records:
                all_records.remove(k)
                remaining_records.clear()
    if confirmed and len(found_records) > 0 and date != '':
        if delete_all != True:
            all_records.extend(remaining_records)
        try:
            with tempfile.NamedTemporaryFile('w', delete=False) as temp_file:
                for line in all_records:
                    temp_file.write(line)
            check_columns()
            os.replace(temp_file.name, Time_Card)
            remaining_records.clear()
            return found_records, remaining_records, True, f"Record for {emp_name} on {date} deleted successfully."
        except Exception as e:
            logging.error(f"An error occurred while writing to the file: {e}")
            return found_records, remaining_records, False, f"An error occurred while writing to the file. Please try again."
    else:
        if date == '':
            return found_records, remaining_records, False, f"Please input a date for {emp_name}, OR enter 'delete' to remove all hours for {emp_name}."
        else:
            return found_records, remaining_records, False, f"No records found for {emp_name} on {date}."
def delete_all_records(emp_name):
    try:
        user = db.session.query(models.ClockIn).filter_by(Employee = emp_name).first()
        if user:
            db.session.query(models.ClockOut).filter_by(user_id = user.user_id).delete()
            db.session.query(models.ClockIn).filter_by(Employee = emp_name).delete()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return False
def delete_records_by_date(emp_name, date):
    try:
        time_in_query = db.session.query(models.ClockIn).filter_by(Employee = emp_name).all()
        for time_in in time_in_query:
            rows = str(time_in).split(',')
            clean_rows = str(rows[1]).lstrip()
            dates = clean_rows.split(' ', 1)[0]
            dates_cleaned = dates.replace('-','/')
            if date == dates_cleaned:
                db.session.delete(time_in)
                time_out_query = db.session.query(models.ClockOut).filter_by(in_id = time_in.out_id).first()
                if time_out_query:
                    db.session.delete(time_out_query)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
def check_columns():
    try:
        with open(Time_Card, 'r') as file:
            for line in file:
                if len(line.split(',')) != 9:
                    update_columns()            
                    return True
    except Exception as e:
        logging.error(f"An error occurred: {e}")
def update_columns():
    try:    
        update_backup()
        updated_lines = []
        with open(Time_Card, 'r') as file:
            for line in file:
                line = line.strip('\n')
                if len(line.split(',')) < 9:
                    line += ', ' * (9 - len(line.split(',')))
                elif len(line.split(',')) > 9:
                    line = ', '.join(line.split(',')[:9])
                line += '\n'
                updated_lines.append(line)
        with open(Time_Card, 'w') as file:
            file.writelines(updated_lines)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
def update_backup():
    try:
        with open(backup_sheet, 'w') as backup:
            with open(Time_Card, 'r') as file:
                for line in file:
                    backup.write(line)   
    except Exception as e:  
        logging.error(f"An error occurred: {e}")
def get_date(empname='', date=''):
    check_columns()

    emp_name = str(empname).upper()
    date = str(date)
    
    primary_search = emp_name + ', ' + date
    with open(Time_Card, 'r') as file:
        for line in file:
            if line.startswith(primary_search):
                line.split(',')
                new_date = f'{date}{line.split(",")[6]}'
                return new_date
        return "No records found."

#for auto clockout
"""""
def time_from_now(date_string, date_format="%Y/%m/%d %H:%M:%S"):
    past_date = datetime.strptime(date_string, date_format)
    now = datetime.now()
    delta = now - past_date

    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return days, hours, minutes, seconds

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
    except Exception as e:
        logging.error(f"Unexpected error: {e}")


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
    """