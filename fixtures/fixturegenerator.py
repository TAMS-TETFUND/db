import csv
import json


def generate_department_json():
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