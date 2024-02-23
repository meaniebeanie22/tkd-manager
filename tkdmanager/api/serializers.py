from dashboard.models import (
    AssessmentUnit,
    Award,
    Class,
    Grading,
    GradingInvite,
    GradingResult,
    Member,
    Payment,
    PaymentType,
    MemberProperty,
    MemberPropertyType,
    RecurringPayment,
    Belt,
    ClassType,
    GradingType,
    AssessmentUnitType,
    Style,
)
from django.contrib.auth.models import User
from rest_framework import serializers


class MemberPropertySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MemberProperty
        fields = ["url", "propertytype", "member", "name"]


class MemberPropertyTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MemberPropertyType
        fields = ["url", "name", "searchable"]


class BeltSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Belt
        fields = ["url", "style", "degree", "name"]


class RecurringPaymentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RecurringPayment
        fields = [
            "url",
            "member",
            "payments",
            "last_payment_date",
            "interval",
            "amount",
            "next_due",
            "paymenttype",
        ]


class ClassSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Class
        fields = ["url", "type", "date", "start", "end", "instructors", "students"]


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email"]


class AssessmentUnitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AssessmentUnit
        fields = ["url", "unit", "achieved_pts", "max_pts", "grading_result"]


class MemberSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Member
        fields = [
            "url",
            "first_name",
            "last_name",
            "idnumber",
            "address_line_1",
            "address_line_2",
            "address_line_3",
            "date_of_birth",
            "belts",
            "email",
            "phone",
            "team_leader_instructor",
            "active",
            "properties",
        ]


class GradingResultSerializer(serializers.HyperlinkedModelSerializer):
    assessmentunits = AssessmentUnitSerializer(many=True, read_only=True)

    class Meta:
        model = GradingResult
        fields = [
            "url",
            "member",
            "grading",
            "forbelt",
            "assessor",
            "comments",
            "award",
            "assessmentunits",
            "is_letter",
            "gradinginvite",
        ]


class GradingInviteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GradingInvite
        fields = ["url", "member", "forbelt", "issued_by", "payment", "grading"]


class PaymentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "url",
            "member",
            "paymenttype",
            "date_created",
            "date_due",
            "date_paid_in_full",
            "amount_due",
            "amount_paid",
        ]


class GradingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Grading
        fields = ["url", "grading_type", "grading_datetime"]


class PaymentTypeSerialzer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PaymentType
        fields = ["url", "name", "standard_amount"]


class AwardSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Award
        fields = ["url", "name", "style"]


class ClassTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ClassType
        fields = ["url", "name", "style"]


class AssessmentUnitTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AssessmentUnitType
        fields = ["url", "name", "style"]


class GradingTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GradingType
        fields = ["url", "name", "style"]


class StyleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Style
        fields = ["url", "name"]
