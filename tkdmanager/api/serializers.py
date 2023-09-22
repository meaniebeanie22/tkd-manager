from django.contrib.auth.models import User
from rest_framework import serializers, fields
from dashboard.models import GradingResult, AssessmentUnit


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']

class AssessmentUnitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AssessmentUnit
        fields = ['unit','achieved_pts','max_pts','grading_result']


class GradingResultSerializer(serializers.HyperlinkedModelSerializer):
    assessmentunit_set = AssessmentUnitSerializer(many=True)

    class Meta:
        model = GradingResult
        fields = ['member','date','type','forbelt','assessor','comments','award', 'assessmentunit_set']
    
    def create(self, validated_data):
        print(validated_data)
        assessmentunits_data = validated_data.pop('assessmentunit_set')
        assessor = validated_data.pop('assessor')
        gradingresult = GradingResult.objects.create(**validated_data)
        for a in assessor:
            gradingresult.assessor.add(a.idnumber)
        gradingresult.save()
        for assessmentunit_data in assessmentunits_data:
            AssessmentUnit.objects.create(gradingresult=gradingresult, **assessmentunit_data)
        return gradingresult
    
    def update(self, instance, validated_data):
        assessmentunits_data = validated_data.pop('assessmentunit_set')
        assessmentunits = (instance.assessmentunit_set).all()
        assessmentunits = list(assessmentunits)
        instance.member = validated_data.get('member', instance.member)
        instance.date = validated_data.get('date', instance.date)
        instance.type = validated_data.get('type', instance.type)
        instance.forbelt = validated_data.get('forbelt', instance.forbelt)
        instance.assessor.set(validated_data.get('assessor', instance.assessor))
        instance.comments = validated_data.get('comments', instance.comments)
        instance.award = validated_data.get('award', instance.award)
        instance.save()

        for assessmentunit_data in assessmentunits_data:
            assessmentunit = assessmentunits.pop(0)
            assessmentunit.unit = assessmentunit_data.get('unit', assessmentunit.unit)
            assessmentunit.achieved_pts = assessmentunit_data.get('achieved_pts', assessmentunit.achieved_pts)
            assessmentunit.max_pts = assessmentunit_data.get('max_pts', assessmentunit.max_pts)
            assessmentunit.grading_result = assessmentunit_data.get('grading_result', assessmentunit.grading_result)
            assessmentunit.save()
        return instance

"""
class AlbumSerializer(serializers.ModelSerializer):

    class Meta:
        model = Album
        fields = ('id', 'artist', 'name', 'release_date', 'num_stars')


class MusicianSerializer(serializers.ModelSerializer):
    album_musician = AlbumSerializer(many=True)

    class Meta:
        model = Musician
        fields = ('id', 'first_name', 'last_name', 'instrument', 'album_musician')

    def create(self, validated_data):
        assessmentunits_data = validated_data.pop('album_musician')
        musician = Musician.objects.create(**validated_data)
        for album_data in assessmentunits_data:
            Album.objects.create(artist=musician, **album_data)
        return musician

    def update(self, instance, validated_data):
        assessmentunits_data = validated_data.pop('album_musician')
        albums = (instance.album_musician).all()
        albums = list(albums)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.instrument = validated_data.get('instrument', instance.instrument)
        instance.save()

        for album_data in assessmentunits_data:
            album = albums.pop(0)
            album.name = album_data.get('name', album.name)
            album.release_date = album_data.get('release_date', album.release_date)
            album.num_stars = album_data.get('num_stars', album.num_stars)
            album.save()
        return instance

"""