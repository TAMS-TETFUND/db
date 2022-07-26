"""
This module will handle the data synching features of he attendance system.
It will be used for initial transfer of data to newly registered node devices.
It will also be used to periodically synch new data to/from the tams server.

Data transferred from server to node device includes:
    = StaffTitle
    = Faculty
    = Department
    = Staff
    = Student
    = Course
    = Academic Session **
    = Course Registration

    **serialization and use of serialized data must follow this order because of 
    foreign key relationships that exist between certain models in the db

Data transferred from node device to server
    = AttendanceSession
    = AtendanceRecord
"""
import os
import subprocess
from pathlib import Path
import json

import pandas as pd

EXCLUDED_TABLES = (
    'db.admissionstatus',
    'db.appadmin',
    'db.attendancerecord',
    'db.attendancesession',
    'db.attendancesessionstatus',
    'db.eventtype',
    'db.nodedevice',
    'db.recordtypes',
    'db.semester',
    'db.sex',

)

SERVER_DUMP = (
    "StaffTitle",
    "Faculty",
    "Department",
    "AppUser",
    "Staff",
    "Student",
    "Course",
    "AcademicSession",
    "CourseRegistration",
)
NODE_DUMP = ("AttendanceSession", "AttendanceRecord")

CURRENT_DIR = Path(os.path.abspath(__file__)).parent
DUMP_DIR = os.path.join(CURRENT_DIR.parent, "dumps")
os.makedirs(DUMP_DIR, exist_ok=True)


def csv_to_json(csv_file):
    try:
        df = pd.read_csv(csv_file, skipinitialspace=True)
    except Exception as e:
        print(e)

    json_file_path = csv_file.split(".csv")[0] + ".json"
    content = [el for idx, el in df.iterrows()]
    with open(json_file_path) as json_file:
        json_file.write(json.dumps(content, indent=4))
    return


def dump_data(from_server: bool = True):
    model_list = SERVER_DUMP if from_server else NODE_DUMP

    command_str = "python manage.py dumpdata "
    for model in model_list:
        command_str += "db.%s " % model

    cmd_run = subprocess.run(command_str, shell=True, capture_output=True)

    return cmd_run.stdout.decode("utf-8")


def save_dump(data: str, from_server: bool = True):
    dump_file_name = "server_dump.json" if from_server else "node_dump.json"
    dump_file = os.path.join(DUMP_DIR, dump_file_name)

    with open(dump_file, "w") as dump_file:
        json.dump(json.loads(data), dump_file)
    return True


def get_dump(from_server: bool = True):
    dump_file_name = "server_dump.json" if from_server else "node_dump.json"
    dump_file = os.path.join(DUMP_DIR, dump_file_name)

    if not os.path.exists(dump_file):
        raise FileNotFoundError(
            "%s dump file not found" % dump_file_name.split("_")[0]
        )

    with open(dump_file, "r") as dump_file:
        data = json.load(dump_file)

    return data


def load_data(to_server: bool = True):
    dump_file_name = "node_dump.json" if to_server else "server_dump.json"
    dump_file = os.path.join(DUMP_DIR, dump_file_name)

    if not os.path.exists(dump_file):
        raise FileNotFoundError(
            "%s dump file not found" % dump_file_name.split("_")[0]
        )

    command_str = "python manage.py loaddata %s" % dump_file

    try:
        cmd_run = subprocess.run(command_str, shell=True, capture_output=True)
    except Exception as e:
        e.args = ("Something went wrong. Contact admin. (%s)" % e,)
        raise

    return cmd_run


"""
Issue of verification of node device before synching begins.
Loading data to server will require different logic.

Since attendance sessions and records are coming from multiple sources,
rows from different dbs cannot maintain their pk's.
    = check if a row already exists with exact field values as the row about to be saved
        before the save operation.

"""
