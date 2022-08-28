import csv
import json


def generate_department_json():
    """
    Converts csv files with department data to json that can be installed 
    as fixtures in the server db. The csv must be in the format provided at 
    the api/v1/admin/upload-format url path on the server.
    """
    deparments = []
    with open('db/fixtures/unn/dept_uploads.csv') as data_file:
        csvreader = csv.reader(data_file)
        for row in csvreader:
            print(row[0])
            if row[0] == 'id':
                continue
            deparments.append({
                'model':'db.department', 
                'pk':int(row[0]), 
                'fields':{
                    'name': row[1], 
                    'faculty_id': int(row[3])}})
    print(deparments)
    serialized_dept = json.dumps(deparments, indent=4)

    with open("departments_serialized.json", "w") as output_file:
        output_file.write(serialized_dept)

def generate_faculty_json():
    """
    Converts csv files with faculty data to json that can be installed 
    as fixtures in the server db. The csv must be in the format provided at 
    the api/v1/admin/upload-format url path on the server.
    """
    faculties = []
    with open('db/fixtures/unn/faculties.csv') as data_file:
        csvreader = csv.reader(data_file)
        for row in csvreader:
            print(row)
            if row[0] == 'id':
                continue
            faculties.append({
                'model': 'db.faculty',
                'pk': int(row[0]),
                'fields': {
                    'name': row[1]
                }
            })
        print(faculties)
        serialized_faculties = json.dumps(faculties, indent=4)

        with open("faculties_serilized.json", "w") as output_file:
            output_file.write(serialized_faculties)

def generate_course_json():
    """
    Converts csv files with course data to json that can be installed 
    as fixtures in the server db. The csv must be in the format provided at 
    the api/v1/admin/upload-format url path on the server.
    """
    courses = []
    with open('db/fixtures/unn/courses_upload.csv') as data_file:
        csvreader = csv.reader(data_file)
        for row in csvreader:
            print(row)
            if row[0] == 'id':
                continue
            courses.append({
                'model': 'db.course',
                'pk': int(row[0]),
                'fields': {
                    'code': row[1],
                    'title': row[2],
                    'level_of_study': int(row[3]),
                    'department_id': int(row[4]),
                    'unit_load': int(row[5]),
                    'semester': int(row[6]),
                    'elective': (True if row[7] == 't' else False),
                    'is_active': (True if row[8] == 't' else False)
                }
            })
        print(courses)
        serialized_courses = json.dumps(courses, indent=4)

        with open("db/fixtures/unn/courses.json", "w") as output_file:
            output_file.write(serialized_courses)

def generate_dummy_attendance(staff_number='SS.325', attendance_sessions=20):
    """
    generate some attendance data for test purposes.
    currently works only after dummy data provided in 
    db/fixtures have been installed.
    """
    from django.utils import timezone
    from db.models import AttendanceRecord, AttendanceSession, Course, Student
    from datetime import timedelta

    course = Course.objects.filter(title='Physical Electronics').first()
    students = Student.objects.values_list("reg_number", flat=True)

    for count in range(attendance_sessions):
        att_session = AttendanceSession.objects.create(
            node_device_id=1,
            initiator_id=staff_number,
            course=course,
            session_id=1,
            event_type=(2 if count % 4 == 0 else 1), 
            duration=timedelta(hours=1),
            start_time=timezone.now()+timedelta(days=count)
        )
        
        for idx, student_reg_num in enumerate(students, 1):
            if idx % 5 == 1:
                AttendanceRecord.objects.create(
                    attendance_session=att_session,
                    student_id=student_reg_num
                )
            elif idx % 5 == 2:
                if count % 4 == 0:
                    AttendanceRecord.objects.create(
                        attendance_session=att_session,
                        student_id=student_reg_num
                    )
                else:
                    AttendanceRecord.objects.create(
                        attendance_session=att_session,
                        student_id=student_reg_num
                    )
            elif idx % 5 == 3:
                if count % 2 == 0:
                    AttendanceRecord.objects.create(
                        attendance_session=att_session,
                        student_id=student_reg_num
                    )
            else:
                if count % 3 == 1:
                    AttendanceRecord.objects.create(
                        attendance_session=att_session,
                        student_id=student_reg_num
                    )
                else:
                    AttendanceRecord.objects.create(
                        attendance_session=att_session,
                        student_id=student_reg_num
                    )
    print("Done!!!")