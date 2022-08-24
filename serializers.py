from rest_framework import serializers

from db.models import AdmissionStatus, Semester, Sex, EventType, AttendanceSessionStatus, RecordTypes


class AdmissionStatusSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = AdmissionStatus
        fields = "__all__"


class SemesterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Semester
        fields = "__all__"


class SexSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sex
        fields = "__all__"

    
class EventTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventType
        fields = "__all__"


class AttendanceSessionStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = AttendanceSessionStatus
        fields = "__all__"


class RecordTypesSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecordTypes
        fields = "__all__"