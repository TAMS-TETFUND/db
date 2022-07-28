import json
import os
from pathlib import Path
import re
import secrets

import numpy as np
from django.db.models import Value, Q, F
from django.db.models.functions import Upper, Replace
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

# configuring the staff_number and studnet reg number format
config_file_path = os.path.join(
    Path(os.path.abspath(__file__)).parent.parent, "config.json"
)

if not os.path.exists(config_file_path):
    raise FileNotFoundError("File: config.json not found")

with open(config_file_path, "r") as data:
    config_dict = json.loads(data.read())

STAFF_NO_FORMAT = r"{}".format(config_dict["STAFF_NO_FORMAT"])
STUDENT_REG_NO_FORMAT = r"{}".format(config_dict["STUDENT_REG_NO_FORMAT"])
SESSION_FORMAT = r"{}".format(config_dict["SESSION_FORMAT"])


def face_enc_to_str(encodings):
    """Convert face encodings from numpy array to string"""
    encodings_str = ",".join(str(item) for item in encodings)
    return encodings_str


def str_to_face_enc(enc_str):
    """Convert encodings formatted as a string to numpy array"""
    encodings = np.array([float(item) for item in enc_str.split(",")])
    return encodings


class AppIntegerChoices(models.IntegerChoices):
    @classmethod
    def str_to_value(cls, string):
        return eval(f"{cls.__name__}.{string.upper()}.value")


class AdmissionStatusChoices(AppIntegerChoices):
    REGULAR = 1, "Regular"
    GRADUATE = 2, "Graduated"
    EXTERNAL = 3, "External"
    OVERSTAY = 4, "Overstay"
    WITHDRAWN = 5, "Withdrawn"
    SUSPENDED = 6, "Suspended"


class SemesterChoices(AppIntegerChoices):
    FIRST = 1, "First"
    SECOND = 2, "Second"


class SexChoices(AppIntegerChoices):
    MALE = 1, "Male"
    FEMALE = 2, "Female"


class EventTypeChoices(AppIntegerChoices):
    LECTURE = 1, "Lecture"
    LAB = 2, "Lab"
    QUIZ = 3, "Quiz"
    EXAMINATION = 4, "Examination"


class AttendanceSessionStatusChoices(AppIntegerChoices):
    ACTIVE = 1, "Active"
    ENDED = 2, "Ended"


class RecordTypesChoices(AppIntegerChoices):
    SIGN_IN = 1, "Sign In"
    SIGN_OUT = 2, "Sign Out"


class StaffTitle(models.Model):
    id = models.BigAutoField(primary_key=True)
    title_full = models.CharField(max_length=50)
    title = models.CharField(max_length=25)

    class Meta:
        ordering = ["title"]
        constraints = [
            models.UniqueConstraint(
                Upper(Replace("title", Value("."), Value(""))),
                name="conflicting_title_abbreviation",
            ),
            models.UniqueConstraint(Upper("title_full"), name="unique_title"),
        ]

    def __str__(self):
        return f"{self.title}"


class Faculty(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=500)

    class Meta:
        constraints = [
            models.UniqueConstraint(Upper("name"), name="unique_faculty_name")
        ]

    @staticmethod
    def get_all_faculties():
        return list(
            Faculty.objects.all()
            .order_by("name")
            .values_list("name", flat=True)
        )


class Department(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=500)
    alias = models.CharField(max_length=20, null=True, blank=True)
    faculty = models.ForeignKey(to=Faculty, on_delete=models.CASCADE)
    # program_duration = models.IntegerField() :what program are you considering; there are many program types: new model may be necessary

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Upper("name"), name="unique_department_name"
            ),
            models.UniqueConstraint(
                Upper("alias"), name="unique_department_short_name"
            ),
        ]

    @staticmethod
    def get_departments(faculty=None):
        departments = Department.objects.all()
        if faculty and Faculty.objects.filter(name__iexact=faculty).exists():
            departments = departments.filter(faculty__name__iexact=faculty)
        return list(departments.order_by("name").values_list("name", flat=True))

    @staticmethod
    def get_id(department_name):
        return Department.objects.get(name__iexact=department_name).id


class AppUser(AbstractUser):
    other_names = models.CharField(max_length=255, null=True, blank=True)
    fingerprint_template = models.TextField(null=True, blank=True)
    face_encodings = models.TextField(null=True, blank=True)
    sex = models.IntegerField(choices=SexChoices.choices)
    is_active = models.BooleanField(default=True)


class Staff(AppUser):
    staff_number = models.CharField(primary_key=True, max_length=25, unique=True)
    department = models.ForeignKey(to=Department, on_delete=models.CASCADE)
    is_exam_officer = models.BooleanField(default=False)
    staff_titles = models.ManyToManyField(StaffTitle)

    def clean(self):
        self.staff_number = self.staff_number.upper()
        if not Staff.is_valid_staff_number(self.staff_number):
            raise ValidationError(
                {"staff_number": "Invalid staff number provided"}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @staticmethod
    def is_valid_staff_number(staff_no):
        return bool(re.search(STAFF_NO_FORMAT, staff_no.upper()))


class AppAdmin(AppUser):
    clearance_number = models.IntegerField(default=1)


class Student(models.Model):
    reg_number = models.TextField(primary_key=True, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    other_names = models.CharField(max_length=255, null=True, blank=True)
    department = models.ForeignKey(to=Department, on_delete=models.CASCADE)
    possible_grad_yr = models.IntegerField()
    admission_status = models.IntegerField(
        choices=AdmissionStatusChoices.choices,
        default=AdmissionStatusChoices.REGULAR,
    )
    level_of_study = models.IntegerField(null=True, blank=True)
    fingerprint_template = models.TextField(null=True, blank=True)
    face_encodings = models.TextField(null=True, blank=True)
    sex = models.IntegerField(choices=SexChoices.choices)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.reg_number}),\
            {self.admission_status}"

    def clean(self):
        if not Student.is_valid_student_reg_number(self.reg_number):
            raise ValidationError(
                {"reg_number": "Invalid student registration number provided"}
            )

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    @staticmethod
    def is_valid_student_reg_number(reg_no):
        return bool(re.search(STUDENT_REG_NO_FORMAT, reg_no))


class Course(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(max_length=8)
    title = models.CharField(max_length=255)
    level_of_study = models.IntegerField()
    department = models.ForeignKey(to=Department, on_delete=models.CASCADE)
    unit_load = models.IntegerField()
    semester = models.IntegerField(choices=SemesterChoices.choices)
    elective = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["code", "title", "unit_load"],
                name="unique_course_details",
            ),
            models.CheckConstraint(
                check=Q(semester__in=SemesterChoices.values),
                name="check_valid_semester",
            ),
        ]

    @classmethod
    def get_courses(
        cls,
        *,
        semester=None,
        faculty=None,
        department=None,
        level_of_study=None,
    ):
        course_list = cls.objects.all().exclude(is_active=False)
        if semester and semester in SemesterChoices.labels:
            course_list = course_list.filter(
                semester=SemesterChoices.values[
                    SemesterChoices.labels.index(semester)
                ]
            )

        if (
            department
            and Department.objects.filter(name__iexact=department).exists()
        ):
            course_list = course_list.filter(
                department__name__iexact=department
            )
        elif faculty and Faculty.objects.filter(name__iexact=faculty).exists():
            course_list = course_list.filter(
                department__faculty__name__iexact=faculty
            )

        if level_of_study:
            course_list = level_of_study.filter(level_of_study=level_of_study)

        return [f"{item.code} : {item.title}" for item in course_list]

    @classmethod
    def str_to_course(cls, course_str):
        split_course_str = course_str.split(" : ")
        try:
            course_obj = cls.objects.exclude(is_active=False).get(
                code__iexact=split_course_str[0],
                title__iexact=" : ".join(split_course_str[1:]),
            )
        except Exception:
            return None
        else:
            return course_obj.id


class AcademicSession(models.Model):
    id = models.BigAutoField(primary_key=True)
    session = models.CharField(max_length=10, unique=True)
    is_current_session = models.BooleanField(default=False)

    def clean(self):
        if not AcademicSession.is_valid_session(self.session):
            raise ValidationError({"session": "Invalid session value"})

    def save(self, *args, **kwargs):
        self.clean
        if self.is_current_session:
            qs = type(self).objects.filter(is_current_session=True)

            if self.pk:
                qs = qs.exclude(pk=self.pk)

            qs.update(is_current_session=False)
        super().save(*args, **kwargs)

    @staticmethod
    def get_all_academic_sessions():
        return list(
            AcademicSession.objects.all()
            .order_by("-is_current_session")
            .values_list("session", flat=True)
        )

    @staticmethod
    def is_valid_session(session):
        if re.search(SESSION_FORMAT, session):
            session_yrs = session.split("/")
            if (int(session_yrs[1]) - int(session_yrs[0])) == 1:
                return True
        return False


class AttendanceSession(models.Model):
    id = models.BigAutoField(primary_key=True)
    # node_device = models.ForeignKey(to=NodeDevice, on_delete=models.CASCADE)
    initiator = models.ForeignKey(
        to=Staff, on_delete=models.CASCADE, null=True, blank=True
    )
    course = models.ForeignKey(to=Course, on_delete=models.CASCADE)
    session = models.ForeignKey(to=AcademicSession, on_delete=models.CASCADE)
    event_type = models.IntegerField(choices=EventTypeChoices.choices)
    start_time = models.DateTimeField(default=timezone.now())
    duration = models.DurationField()
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(
        choices=AttendanceSessionStatusChoices.choices,
        default=AttendanceSessionStatusChoices.ACTIVE,
    )
    recurring = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["course", "session", "start_time", "duration"],
                name="unique_attendance_session",
            ),
            models.CheckConstraint(
                check=Q(start_time__lt=(F("start_time") + F("duration"))),
                name="check_valid_stop_time",
            ),
        ]


class AttendanceRecord(models.Model):
    id = models.BigAutoField(primary_key=True)
    attendance_session = models.ForeignKey(
        to=AttendanceSession, on_delete=models.CASCADE
    )
    student = models.ForeignKey(to=Student, on_delete=models.CASCADE)
    record_type = models.IntegerField(
        choices=RecordTypesChoices.choices, default=RecordTypesChoices.SIGN_IN
    )
    check_in_by = models.DateTimeField(auto_now_add=True)
    check_out_by = models.DateTimeField(blank=True, null=True)
    is_valid = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["attendance_session", "student", "record_type"],
                name="unique_attendance_record",
            ),
        ]

    def clean(self):
        if self.record_type != RecordTypesChoices.SIGN_IN:
            saved_record = AttendanceRecord.objects.get(pk=self.pk)
            if self.record_type != saved_record.record_type:
                self.check_out_by = timezone.now()

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)


class CourseRegistration(models.Model):
    id = models.BigAutoField(primary_key=True)
    session = models.ForeignKey(to=AcademicSession, on_delete=models.CASCADE)
    semester = models.IntegerField(choices=SemesterChoices.choices)
    course = models.ForeignKey(to=Course, on_delete=models.CASCADE)
    student = models.ForeignKey(to=Student, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course", "session"],
                name="unique_course_registration",
            )
        ]

    def clean(self):
        if self.semester != self.course.semester:
            raise ValidationError(
                {"semester": "Course is not offered in selected semester"}
            )

    def save(self, *args, **kwargs):
        self.clean()
        return super(CourseRegistration, self).save(*args, **kwargs)


class NodeDevice(models.Model):
    """A model that keeps record of every legitimate node device
    to avoid processing data from unauthorized/unknown devices.
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    token = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if self.id is None:
            self.id = self.next_valid_id()
        if self.name in (None, ""):
            self.name = self.next_device_name(self.next_valid_id())
        if self.token in (None, ""):
            self.token = secrets.token_urlsafe(32)
        super(NodeDevice, self).save(*args, **kwargs)

    @staticmethod
    def next_valid_id():
        next_id = NodeDevice.objects.filter(id__gt=0).order_by("id").last()
        next_id = 1 if next_id is None else (next_id.pk + 1)
        return next_id

    @staticmethod
    def next_device_name(next_valid_id):
        return f"TAMS {next_valid_id}"
