############################################
#*Source code for Time Card System
#*BY: Lodo Loro
############################################
#TODO: Create settings page with these options below eventually apply to html for easy changing in application
###########################################################
import sys
import os
import tempfile
import logging
from datetime import datetime
import openpyxl
import pandas as pd # type: ignore
#import xlwings as xw # type: ignore
import pytz # type: ignore
from Website import models
from . import db

#* variable for location of csv(change accordingly!!)
Time_Card = "/Users/lodoloro/programs/RMSPOPEProjects/Rms_Terminal_APP/Terminal/Website/timelog.csv"
backup_sheet = "/Users/lodoloro/programs/RMSPOPEProjects/Rms_Terminal_APP/Terminal/Website/backup_sheet.csv"
Timelog = "/Users/lodoloro/programs/RMSPOPEProjects/Rms_Terminal_APP/Terminal/Website/Timelog.xlsx"
roles = {"DRIVER": 20, "IT": 10}
columns=[
        "Employee",
        "Date",
        "Description",
        "Vehicle",
        "Runs",
        "Location",
        "Clock-IN",
        "Vehicle-2",
        "Clock-Out",
    ]
df = pd.read_csv(Time_Card)
table = pd.DataFrame(
    df,
    columns=columns,
)

#* opens workbook TimeCard.xlsx
table.to_excel(Timelog, sheet_name="timelog", index=False)

#*Timezone settings
desired_timezone = "Canada/Newfoundland"
timezone_obj = pytz.timezone(desired_timezone)
now = datetime.now(timezone_obj)
################################################################################
#* Backup configuration
def update_timelog():
    df = pd.read_csv(Time_Card)
    df.to_excel(Timelog, sheet_name="timelog", index=False)

def update_backup():
    #*Update the backup sheet with the current time card data.
    if not os.path.exists(backup_sheet):
        print("Backup sheet does not exist")
    else:
        with open(backup_sheet, "w", encoding="utf-8") as backup:
            with open(Time_Card, "r", encoding="utf-8") as file:
                for line in file:
                    backup.write(line)
    try:
        #* Update the timelog with the current time card data.
        update_timelog()
    except Exception as e:
        logging.error(
            "An error occurred: %s",
            e,
            exc_info=True
            )

def update_columns():
    try:
        update_backup()
        updated_lines = []
        with open(Time_Card, "r", encoding='UTF-8') as file:
            for line in file:
                line = line.strip("\n")
                if len(line.split(",")) < 9:
                    line += "," * (9 - len(line.split(",")))
                elif len(line.split(",")) > 9:
                    line = ",".join(line.split(",")[:9])
                line += "\n"
                updated_lines.append(line)
        with open(Time_Card, "w", encoding='UTF-8') as file:
            file.writelines(updated_lines)
    except Exception as e:
        logging.error(
            "An error occurred: %s",
            e,
            exc_info=True
            )
def check_columns():
    try:
        with open(Time_Card, "r") as file:
            for line in file:
                if len(line.split(",")) != 9:
                    update_columns()
                    return True
    except Exception as e:
        logging.error(
            "An error occurred: %s",
            e,
            exc_info=True
            )
################################################################################
def Add(EmpName="", EmpDes="", EmpVeh="", EmpRuns="", EmpArea=""):
    check_columns()
    try:
        with open(Time_Card, "a", encoding="utf-8") as TimeCard_file:
            #*Add clock in time in file with current time.
            Emp_Name = EmpName.upper()
            Emp_Des = EmpDes.upper()
            Emp_Veh = EmpVeh.upper()
            Emp_Runs = EmpRuns.upper()
            Emp_Area = EmpArea.upper()
            Current = now.strftime("%Y/%m/%d")
            Clock_in = now.strftime("%H:%M")

            TimeCard_file.write(
                f"{Emp_Name},{Current},{Emp_Des},{Emp_Veh},{Emp_Runs},{Emp_Area},{Clock_in},\n"
            )

        try:
        #* Save the updated DataFrame back to the file
            update_backup()
        except ValueError:
            check_columns()
    except FileNotFoundError:
        logging.error(
            "File not found: %s. Please ensure the file exists and the path is correct.",
            Time_Card,
            exc_info=True
        )
    except PermissionError:
        logging.error(
            "Permission denied: %s. Please ensure you have the necessary permissions to write to the file.",
            Time_Card,
            exc_info=True
        )
    except (IOError, OSError) as e:
        logging.error(
            "An I/O error occurred while writing to the file: %s",
            e,
            exc_info=True
            )
    except ValueError as e:
        logging.error(
            "A value error occurred while writing to the file: %s",
            e,
            exc_info=True
            )


def Clock_out(EmpVeh_="", EmpName_=""):
    try:
        df = pd.read_csv(Time_Card)
    except FileNotFoundError:
        logging.error(
            "File not found: %s. Please ensure the file exists and the path is correct.",
            Time_Card,
            exc_info=True
        )
    except ValueError:
        check_columns()
    except Exception as e:
        return logging.error(
            "An error occurred while reading the file: %s",
            e,
            exc_info=True
        )
    employee = EmpName_.upper()
    vehicle = EmpVeh_.upper()
    #* Search for the employee in the DataFrame and returns matching clockin date
    result = df[df["Employee"].str.contains(employee)]
    if not result.empty:
        index = result.index[-1]
        day_check = str(df.loc[index, "Date"]  ).format("%Y/%m/%d")

        #* Add clock-out time in the file with the current time
        now = datetime.now(timezone_obj)
        Clock_out_time = now.strftime("%H:%M")
        Current_day = now.strftime("%Y/%m/%d")

        #* logic to determine if the found clockin record date is equal to the current date, Update the 'Clock-Out' column in the DataFrame.
        if day_check == Current_day:
            df.iat[index, 7] = vehicle
            df.iat[index, 8] = Clock_out_time
            message = (True, "Congratulations you are Clocked OUT!")
        else:
            message = (
                False,
                "An Error occured please check that you are Clocked-In before trying again.",
            )
        #* Save the updated DataFrame back to the file
        try:
            df.to_csv(Time_Card, index=False)
            update_backup()
        except ValueError:
            check_columns()
    else:
        message = (False, "No matching records found.")
    return message


def Edit(empname="", date=""):
    check_columns()
    found_records = []
    remaining_records = []
    msg = None
    emp_name = str(empname).upper()
    date = str(date)

    primary_search = f'{emp_name},{date}'
    secondary_search = emp_name

    try:
        with open(Time_Card, "r", encoding='utf-8') as file:
            for line in file:
                if line.startswith(primary_search):
                    found_records.append(line.strip())
                    msg = 'Record found'
                elif line.upper().startswith(secondary_search):
                    remaining_records.append(line.strip())
    except Exception as e:
        logging.error(
            "An error occurred while reading the file",
            exc_info=True
            )
        return (
            remaining_records,
            found_records,
            "An error occurred while reading the file: %s", e
        )
    return remaining_records, found_records, msg


def update_records(
    empname="",
    Date="",
    emp_des="",
    emp_veh="",
    emp_runs="",
    emp_area="",
    clock_in="",
    veh2="",
    clock_out="",
    confirmed=False,
):
    #* This function will update the records in the time card file.
    emp_name = str(empname).upper()
    date = str(Date)

    primary_search = f"{emp_name},{date}"
    secondary_search = emp_name

    all_records = []
    found_records = []
    remaining_records = []

    try:
        with open(Time_Card, "r", encoding="utf-8") as timecard_file:
            for line in timecard_file:
                print(line[:15],primary_search)
                if line[:15] == primary_search:
                    print("found")
                    found_records.append(line)
                elif line.upper().startswith(secondary_search):
                    remaining_records.append(line)
                else:
                    all_records.append(line)
    except FileNotFoundError:
        logging.error(
            "File not found",
            exc_info=True
                      )
        return (
            remaining_records,
            found_records,
            False,
            "File not found. Please ensure the file exists and the path is correct.",
        )
    except PermissionError:
        logging.error(
            "Permission denied",
            exc_info=True
            )
        return (
            remaining_records,
            found_records,
            False,
            "Permission denied. Please ensure you have the necessary permissions to read the file.",
        )
    except Exception as e:
        logging.error(
            "An error occurred: %s",
            e,
            exc_info=True
        )

    new_entry = f"{emp_name}, {date}, {emp_des}, {emp_veh}, {emp_runs}, {emp_area}, {clock_in}, {veh2}, {clock_out}\n"
    try:
        print(1)
        print(confirmed)
        print(found_records)
        if confirmed is True and len(found_records) > 0:
            print(2)
            all_records.append(new_entry)
            with open(Time_Card, "w") as file:
                for line in all_records:
                    file.write(line)
            return (
                remaining_records,
                found_records,
                True,
                f"Record for {emp_name} on {date} has been updated successfully.",
            )
        else:
            found_records = ["None found"]
            check_columns()
            return (
                remaining_records,
                found_records,
                False,
                f"No records found for {emp_name} on {date}.",
            )
    except Exception as e:
        logging.error(
            "an error occured: %s", 
            e,
            exc_info=True
            )
        return (
            remaining_records,
            found_records,
            False,
            (
                f"an error occured for: {Time_Card}. Please ensure the file "
                f"exists and the path is correct."
            ),
        )


def calculate_pay(hours=0, minutes=0, role="", total_pay=0):
    individual_pay = 0
    if role in roles:
        individual_pay = hours * roles[role]
        individual_pay += minutes * (roles[role] / 60)
    formatted_individual_pay = "${:,.2f}".format(individual_pay)
    total_pay += individual_pay
    return formatted_individual_pay, total_pay


def Search(EmpName_=""):
    #* main function for retrieving hours by employee code
    #* and displaying the total hours worked and pay.
    check_columns()
    emp_id = str(EmpName_).upper()
    display = []
    individual_hours = []
    group_hours = []

    i_sum_h = 0
    i_sum_m = 0
    g_sum_h = 0
    g_sum_m = 0

    num_line = 0

    total_hours = ""
    running_total = ""
    formatted_total_pay = ""
    total_pay = 0

    try:
        with open(Time_Card, "r", encoding='utf-8') as file:
            for line in file:
                num_line += 1
                if line.startswith(emp_id):
                    word = line.strip("\n").split(",")
                    start = datetime.strptime(word[6], "%H:%M")

                    if len(word[-1]) < 5:
                        end = 00
                    else:
                        end = datetime.strptime(word[-1].strip(), "%H:%M")

                    if end != 0 and word[2] in roles:
                        hours = (end - start).seconds // 3600
                        minutes = ((end - start).seconds // 60) % 60

                        if hours < 0:
                            hours = 0
                            minutes = 0
                    else:
                        hours = 0
                        minutes = 0
                    i_sum_h += hours
                    i_sum_m += minutes
                    i_sum_h += i_sum_m // 60
                    i_sum_m %= 60

                    total_hours = f"{str(hours).zfill(2)}:{str(minutes).zfill(2)}"
                    running_total = f"{str(i_sum_h).zfill(2)}:{str(i_sum_m).zfill(2)}"

                    pay, total_pay = calculate_pay(i_sum_h, i_sum_m, word[2], total_pay)
                    if formatted_total_pay == "":
                        formatted_total_pay = "0.00"
                    else:
                        formatted_total_pay = pay
                    individual_hours.append(word)
                    display = individual_hours
                elif emp_id == "ALL":
                    if num_line >= 2:
                        word = line.strip("\n").split(",")
                        start = datetime.strptime(word[6], "%H:%M")

                        if len(word[-1]) < 5:
                            end = 0
                        else:
                            end = datetime.strptime(word[-1].strip(), "%H:%M")

                        if end != 0 and word[2] in roles:
                            hours = (end - start).seconds // 3600
                            minutes = ((end - start).seconds // 60) % 60

                            if hours < 0:
                                hours = 0
                                minutes = 0
                        else:
                            hours = 0
                            minutes = 0

                        g_sum_h += hours
                        g_sum_m += minutes
                        g_sum_h += g_sum_m // 60
                        g_sum_m %= 60

                        total_hours = f"{str(hours).zfill(2)}:{str(minutes).zfill(2)}"
                        running_total = (
                            f"{str(g_sum_h).zfill(2)}:{str(g_sum_m).zfill(2)}"
                        )

                        pay, total_pay = calculate_pay(
                            hours, minutes, word[2], total_pay
                        )
                        formatted_total_pay = "${:,.2f}".format(total_pay)

                        word.append(total_hours)
                        word.append(pay)
                        group_hours.append(word)
                        display = group_hours

    except FileNotFoundError:
        logging.error(
            "File not found: %s. Please ensure the file exists and the path is correct.",Time_Card
        )
    except PermissionError:
        logging.error(
            "Permission denied: %s. Please ensure you have the necessary permissions to read the file.", Time_Card
        )
    except Exception:
        logging.error(
            "An error occurred",
            exc_info=True
            )
        
    return display, running_total, formatted_total_pay


def Delete(EmpName_="", Date_="", confirmed=False):  # this function will remove unwanted records from the file
    check_columns()
    emp_name = str(EmpName_).upper()
    date = str(Date_)
    delete_all = False
    if date == "delete":
        delete_all = True
    primary_search = f"{emp_name}, {date}"
    secondary_search = emp_name

    found_records = []
    remaining_records = []
    all_records = []
    try:
        with open(Time_Card, "r",encoding="utf-8") as file:
            for line in file:
                if line.startswith(primary_search):
                    found_records.append(line)
                elif line.startswith(secondary_search) and line not in found_records:
                    remaining_records.append(line)
                else:
                    all_records.append(line)
    except FileNotFoundError:
        logging.error("File not found")
        return (
            [],
            [],
            False,
            f"File not found: {Time_Card}. Please ensure the file exists and the path is correct.",
        )
    except PermissionError:
        logging.error("Permission denied")
        return (
            [],
            [],
            False,
            f"Permission denied: {Time_Card}. Please ensure you have the necessary permissions to read the file.",
        )
    except Exception as e:
        logging.error("An error occurred while reading the file")
        return [], [], False, f"An error occurred while reading the file: {e}"

    if delete_all is True:
        found_records.extend(remaining_records)
        for k in found_records:
            if k in all_records:
                all_records.remove(k)
                remaining_records.clear()
    if confirmed and len(found_records) > 0 and date != "":
        if delete_all is not True:
            all_records.extend(remaining_records)
        try:
            with tempfile.NamedTemporaryFile("w", delete=False) as temp_file:
                for line in all_records:
                    temp_file.write(line)
            check_columns()
            os.replace(temp_file.name, Time_Card)
            remaining_records.clear()
            return (
                found_records,
                remaining_records,
                True,
                f"Record for {emp_name} on {date} deleted successfully.",
            )
        except Exception as e:
            logging.error(
                "An error occurred while writing to the file: %s",
                e,
                exc_info=True
                )
            return (
                found_records,
                remaining_records,
                False,
                "An error occurred while writing to the file. Please try again.",
            )
    else:
        if date == "":
            return (
                found_records,
                remaining_records,
                False,
                f"Please input a date for {emp_name}, OR enter 'delete' to remove all hours for {emp_name}.",
            )
        else:
            return (
                found_records,
                remaining_records,
                False,
                f"No records found for {emp_name} on {date}.",
            )

def delete_all_records(emp_name):
    try:
        user = db.session.query(models.ClockIn).filter_by(Employee=emp_name).first()
        if user:
            db.session.query(models.ClockOut).filter_by(user_id=user.user_id).delete()
            db.session.query(models.ClockIn).filter_by(Employee=emp_name).delete()
    except Exception as e:
        logging.error(
            "An error occurred: %s",
            e,
            exc_info=True
            )
        return False

def delete_records_by_date(emp_name, date):
    try:
        time_in_query = (
            db.session.query(models.ClockIn).filter_by(Employee=emp_name).all()
        )
        for time_in in time_in_query:
            rows = str(time_in).split(",")
            clean_rows = str(rows[1]).lstrip()
            dates = clean_rows.split(" ", 1)[0]
            dates_cleaned = dates.replace("-","/")
            if date == dates_cleaned:
                db.session.delete(time_in)
                time_out_query = (
                    db.session.query(models.ClockOut)
                    .filter_by(in_id=time_in.out_id)
                    .first()
                )
                if time_out_query:
                    db.session.delete(time_out_query)
    except Exception as e:
        logging.error(
                    "An error occurred: %s",
                    e,
                    exc_info=True
                    )


def get_date(empname="", date=""):
    check_columns()

    emp_name = str(empname).upper()
    date = str(date)

    primary_search = emp_name + "," + date
    with open(Time_Card, "r", encoding="utf-8") as file:
        for line in file:
            if line.startswith(primary_search):
                line.split(",")
                new_date = f'{date}{line.split(",")[6]}'
                return new_date
        return "No records found."


#TODO for auto clockout
#//
#// def time_from_now(date_string, date_format="%Y/%m/%d %H:%M:%S"):
#//    past_date = datetime.strptime(date_string, date_format)
#//    now = datetime.now()
#//    delta = now - past_date
#//
#//    days = delta.days
#//    hours, remainder = divmod(delta.seconds, 3600)
#//    minutes, seconds = divmod(remainder, 60)
#//
#//    return days, hours, minutes, seconds
#//
#//def write_to_last_row(data):
#//    try:
#//        # Open the Excel workbook using 'with open'
#//        workbook = wb
#//        sheet = ws
#//        # Determine the last row of the table
#//        last_row = sheet.range('A' + str(sheet.cells.last_cell.row)).end('up').row + 1
#//        # Write data to the last row
#//        for i, value in enumerate(data, start=1):
#//            sheet.cells(last_row, i).value = value
#//        # Save the workbook (closing is not needed with 'with open')
#//        workbook.save()
#//        workbook.close()
#//    except Exception as e:
#//        logging.error(f"Unexpected error: {e}")

#*Main function to run the Time Card System locally
#//def main():
#//    #Select the option what you like to do in you time card
#//    print("What would you like to do in Time Card System?")
    #//print("IN = Clock-IN :: OUT = Clock-OUT :: S = Search :: D = Delete :: E = Edit :: R = Report :: Q = Quit")
#//    func = input("Please select a function from the list above:")
#//
#//    #Use while loop to enter in time card as selected option
    #//while func == '' or func != 'in'  or func != 'IN' or func != 'out'  or func != 'OUT' or func != 'S' or func != 's' or func != 'D' or func != 'd' or func != 'E' or func != 'e' or func != 'R' or func != 'r':
#//        if func == 'in' or func == 'IN':
#//            Add(EmpName='',EmpDes='',EmpVeh='',EmpRuns='',EmpArea='')
#//        elif func == 'out' or func == 'OUT':
#//            Clock_out()
#//        elif func == 'S' or func == 's':
#//            Search()
#//        
#//        # only manager can use Report, Delete and Edit Options
#//        elif func == 'D' or func == 'd':
#//            print('Are you Manager?:')
#//            Mrg_emp = input("Y=Yes, Anything Else = No:")
#//            Mgr= Mrg_emp.upper()
#//            if (Mgr == 'YES' or Mgr == 'Y'):
#//                password = getPassword()
#//                if validPassword(password) == True:
#//                    print(password + " is valid")
#//                    Delete('ll50','2023/06/22')
#//                elif validPassword(password) == False:
#//                    print(password + " is invalid")
#//                    print('\n')
#//                    main()
#//            else:
#//                print('\n')
#//                main()
#//        elif func == 'E' or func == 'e':
#//            print('Are you Manager?:')
#//            Mrg_emp = input("Y=Yes, Anything Else = No:")
#//            Mgr= Mrg_emp.upper()
#//            if (Mgr == 'YES' or Mgr == 'Y'):
#//                password = getPassword()
#//                if validPassword(password) == True:
#//                    print(password + " is valid")
#//                    Edit('ll50','2023/05/10')
#//                elif validPassword(password) == False:
#//                    print(password + " is invalid")
#//                    print('\n')
#//                    main()
#//            else:
#//                print('\n')
#//                main()
#//        #if you press any random key it will bring you here
#//        else:
#//            print("Incorrect input please try again \n")
#//            func = input("enter A for Add, S for Search, D for Delete, E for Edit, R for Report:")
#//
#//if __name__ == "__main__":
#//    main()
#//    """
