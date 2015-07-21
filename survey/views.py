from django.shortcuts import render
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
# from django.forms.models import inlineformset_factory

from survey.models import Commutersurvey, Employer, Leg, Month
from survey.forms import CommuterForm, ExtraCommuterForm
from survey.forms import MakeLegs
from survey.forms import NormalFromWorkSameAsAboveForm, WalkRideFromWorkSameAsAboveForm, NormalIdenticalToWalkrideForm

import json
import mandrill
from datetime import date


from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect




def html_thankyou(name, date):
    return ('<p>Dear {name},</p><p>Thank you for checking'
            ' in your Walk/Ride Day commute! This email confirms your'
            'participation in {survey_date}\'s Walk/Ride Day! Feel '
            'free to show it to our <a href="http://checkin'
            '-greenstreets.rhcloud.com/retail" style="color:'
            '#2ba6cb;text-decoration: none;">Retail Partners</a> '
            'to take advantage of their offers of freebies, '
            'discounts, and other goodies!</p><p>Now <a href="http://'
            'checkin2015-greenstreets.rhcloud.com/leaderboard/" '
            'style="color: #2ba6cb;text-decoration: none;">CLICK HERE'
            '</a> to see how your company is doing in the Corporate'
            ' Challenge! Share with your friends and colleagues!</p>'
            '<p>Thank you for being involved! Remember to check-in '
            'for next month\'s Walk/Ride Day.</p><p>Warmly,<br>'
            '<span style="color:#006600;font-weight:bold;">Janie Katz'
            '-Christy, Director <br>Green Streets Initiative<br> '
            '<span class="mobile_link">617-299-1872 (office)</p>'
            '<p>Share with your friends and colleagues! '
            '<a href="http://checkin.gogreenstreets.org" '
            'style="color: #2ba6cb;text-decoration: none;">Make sure'
            ' they get a chance to check in</p>'.format(name=name, 
                                                        survey_date=date))

def plaintext_thankyou(date):
    return ('Dear Supporter, Thank you for checking in '
            'your Walk/Ride Day commute! This email confirms your'
            'participation in {}\'s Walk/Ride Day! Feel free to '
            'show it to our Retail Partners to take advantage of '
            'their offers of freebies, discounts, and other goodies!'
            ' Thank you for being involved! Remember to check-in for '
            'next month\'s Walk/Ride Day. Warmly, Green Streets'
            ' Initiative'.format(date))



def add_checkin(request):

    try:
        wr_day = Month.objects.get(open_checkin__lte=date.today(),
                                   close_checkin__gte=date.today())
    except Month.DoesNotExist:
        return redirect('/')

    leg_formset_NormalTW = MakeLegs(instance=Commutersurvey(), prefix='ntw')
    leg_formset_NormalFW = MakeLegs(instance=Commutersurvey(), prefix='nfw')
    leg_formset_WRTW = MakeLegs(instance=Commutersurvey(), prefix='wtw')
    leg_formset_WRFW = MakeLegs(instance=Commutersurvey(), prefix='wfw')

    normal_copy = NormalFromWorkSameAsAboveForm(
        {'normal_same_as_reverse': True})
    wrday_copy = WalkRideFromWorkSameAsAboveForm(
        {'walkride_same_as_reverse': True})
    commute_copy = NormalIdenticalToWalkrideForm(
        {'normal_same_as_walkride': True})

    if request.method == 'POST':
        # send the filled out forms in!
        # if the forms turn out to be not valid, they will still retain
        # the form data from the POST request this way.
        commute_form = CommuterForm(request.POST)
        extra_commute_form = ExtraCommuterForm(request.POST)

        # if the main form is correct
        if commute_form.is_valid():
            commutersurvey = commute_form.save(commit=False)
            commutersurvey.wr_day_month = wr_day
            commutersurvey.email = commute_form.cleaned_data['email']
            commutersurvey.employer = commute_form.cleaned_data['employer']
            commutersurvey.team = commute_form.cleaned_data['team']
            extra_commute_form.is_valid() # creates cleaned_data
            commutersurvey.share = extra_commute_form.cleaned_data['share']
            commutersurvey.comments = extra_commute_form.cleaned_data['comments']


            leg_formset_WRTW = MakeLegs(request.POST, prefix='wtw',
                                        instance=commutersurvey)

            # time for convoluted logic!
            if request.POST['walkride_same_as_reverse']:
                # set w/r legs from work = w/r legs to work
                leg_formset_WRFW = MakeLegs(request.POST, prefix='wtw',
                                            instance=commutersurvey)
                # need to correct for the hidden fields
                for form in leg_formset_WRFW:
                    leg = form.save(commit=False)
                    leg.direction = 'fw'
            else:
                # set w/r legs from work based on user input
                leg_formset_WRFW = MakeLegs(request.POST, prefix='wfw',
                                            instance=commutersurvey)

            if request.POST['normal_same_as_walkride']:
                # set normal legs to work = w/r legs to work
                leg_formset_NormalTW = MakeLegs(request.POST, prefix='wtw', 
                                                instance=commutersurvey)
                # need to correct for the hidden fields
                for form in leg_formset_NormalTW:
                    leg = form.save(commit=False)
                    leg.day = 'n'

                # AND set normal legs from work based on w/r legs from work
                if request.POST['walkride_same_as_reverse']:
                    # if w/r legs from work = w/r legs to work,
                    #use w/r legs to work to set normal legs from work
                    
                    leg_formset_NormalFW = MakeLegs(request.POST, prefix='wtw', 
                                                    instance=commutersurvey)
                    # need to correct for the hidden fields
                    for form in leg_formset_NormalFW:
                        leg = form.save(commit=False)
                        leg.day = 'n'
                        leg.direction = 'fw'
                else:
                    # if w/r legs from work =/= w/r legs to work,
                    #use w/r legs from work to set normal legs from work
                    leg_formset_NormalFW = MakeLegs(request.POST, prefix='wfw', 
                                                    instance=commutersurvey)
                    # need to correct for the hidden fields
                    for form in leg_formset_NormalFW:
                        leg = form.save(commit=False)
                        leg.day = 'n'
            else:
                # set normal legs to work based on user input
                leg_formset_NormalTW = MakeLegs(request.POST, prefix='ntw',
                                                instance=commutersurvey)
                if request.POST['normal_same_as_reverse']:
                    # set normal legs from work = normal legs to work
                    leg_formset_NormalFW = MakeLegs(request.POST, prefix='ntw',
                                                    instance=commutersurvey)
                    # need to correct for the hidden fields
                    for form in leg_formset_NormalFW:
                        leg = form.save(commit=False)
                        leg.direction = 'fw'
                else:
                    # set normal legs from work based on user input
                    leg_formset_NormalFW = MakeLegs(request.POST, prefix='nfw',
                                                    instance=commutersurvey)

            # finally! we're good to go.
            if (leg_formset_WRTW.is_valid() and
                leg_formset_NormalTW.is_valid() and
                leg_formset_NormalFW.is_valid() and
                leg_formset_WRFW.is_valid()):

                commutersurvey.save()
                leg_formset_WRTW.save()
                leg_formset_WRFW.save()
                leg_formset_NormalTW.save()
                leg_formset_NormalFW.save()
                # very simple email sending - replace using Mandrill API later
                name = commutersurvey.name or 'Supporter'
                subject = ('Walk/Ride Day ' +
                           commutersurvey.wr_day_month.month + ' Checkin')
                message_html = html_thankyou(name, 
                                             commutersurvey.wr_day_month.month)
                message_plain = plaintext_thankyou(
                                commutersurvey.wr_day_month.month)

                recipient_list = [commutersurvey.email,]
                from_email = 'checkin@gogreenstreets.org'
                send_mail(subject, message_plain, from_email, recipient_list,
                          html_message=message_html, fail_silently=True)
                return render_to_response(
                        'survey/thanks.html',
                        {
                            'person': commutersurvey.name,
                            'calories_burned': commutersurvey.calories_total,
                            'calorie_change': commutersurvey.calorie_change,
                            'carbon_savings': commutersurvey.carbon_savings,
                            'change_type': commutersurvey.change_type
                        })
        else:
            pass
    else:
        # initialize empty forms for everything
        commute_form = CommuterForm()
        extra_commute_form = ExtraCommuterForm()
    return render(request, "survey/new_checkin.html",
                  {
                      'wr_day': wr_day,
                      'form': commute_form,
                      'extra_form': extra_commute_form,
                      'NormalTW_formset': leg_formset_NormalTW,
                      'NormalFW_formset': leg_formset_NormalFW,
                      'WRTW_formset': leg_formset_WRTW,
                      'WRFW_formset': leg_formset_WRFW,
                      'normal_copy': normal_copy,
                      'wrday_copy': wrday_copy,
                      'commute_copy': commute_copy
                  })

