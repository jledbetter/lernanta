from django import forms
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext as _

from users.models import UserProfile

from badges.models import Badge, Submission, Assessment, Rating


class BadgeForm(forms.ModelForm):

    class Meta:
        model = Badge
        fields = ('name', 'description', 'image',
            'assessment_type', 'badge_type', 'rubrics')
        widgets = {
            'assessment_type': forms.RadioSelect,
            'badge_type': forms.RadioSelect,
        }


class SubmissionForm(forms.ModelForm):

    class Meta:
        model = Submission
        fields = ('url', 'content',)


class AssessmentForm(forms.ModelForm):

    class Meta:
        model = Assessment
        fields = ('comment',)

class ProjectAddOrganizerForm(forms.Form):
    user = forms.CharField()

    def __init__(self, school, *args, **kwargs):
        super(ProjectAddOrganizerForm, self).__init__(*args, **kwargs)
        self.school = school

    def clean_user(self):
        username = self.cleaned_data['user']
        try:
            user = UserProfile.objects.get(username=username)
            if user.deleted:
                raise forms.ValidationError(
                    _('That user account was deleted.'))
        except UserProfile.DoesNotExist:
            raise forms.ValidationError(
                _('There is no user with username: %s.') % username)
        if self.school.organizers.filter(id=user.id).exists():
            raise forms.ValidationError(
                _('User %s is organizing the school.') % username)
        return user

class PeerAssessmentForm(forms.ModelForm):
    peer = forms.CharField()

    class Meta:
        model = Assessment
        fields = ('comment',)

    def __init__(self, badge, profile, *args, **kwargs):
        super(PeerAssessmentForm, self).__init__(*args, **kwargs)
        self.badge = badge
        self.profile = profile

    def clean_peer(self):
        username = self.cleaned_data['peer']
        if self.profile.username == username:
            raise forms.ValidationError(
                 _('You cannot give a badge to yourself.'))
        try:
            user = UserProfile.objects.get(username=username)
            if user.deleted:
                raise forms.ValidationError(
                    _('That user account was deleted.'))
        except UserProfile.DoesNotExist:
            raise forms.ValidationError(
                _('There is no user with username: %s.') % username)
        if not self.badge.get_peers(self.profile).filter(id=user.id).exists():
            raise forms.ValidationError(
                _('User %s needs to be your peer.') % username)
        return user


class RatingForm(forms.ModelForm):

    class Meta:
        model = Rating
        fields = ('score',)
        widgets = {
            'score': forms.RadioSelect,
        }
