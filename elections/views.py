from django.http import HttpResponse ,HttpResponseRedirect , Http404
from django.shortcuts import render
from django.core.urlresolvers import reverse
#from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required,user_passes_test
#from django.views.decorators.cache import never_cache
#from users.models import User
from django.contrib import messages
from elections.models import Election,Question,Candidate,Voter,Vote
from elections.forms import *


#@require_safe #for link checkers SSL

@login_required(login_url='/login/')
@user_passes_test(lambda x: x.verified_email,login_url='/users/not-verified/',redirect_field_name=None)     
def CreateElection(request):    
    if request.method=='POST':
        form = ElectionCreateForm(user=request.user,data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Election Successfully Created.")
            return HttpResponseRedirect(reverse('elections:EditElection',kwargs={'election_slug' : form.cleaned_data.get("slug"),'edit_id' : '3' }))
        return render(request,"elections/ElectionForm.html",{'form' : form})
    else:
        return render(request,"elections/ElectionForm.html",{'form' : ElectionCreateForm(user=request.user)})



from django.forms.models import inlineformset_factory


@login_required(login_url='/login/')
@user_passes_test(lambda x: x.verified_email,login_url='/users/not-verified/',redirect_field_name=None)
def EditElection(request,election_slug=None,edit_id=None):
    if election_slug is None or edit_id is None:
        raise Http404("The requested URL was not found on this server.")
    try:
        elections = Election.objects.only('user__username','election_id','name','state').select_related('user').get(slug=election_slug)
    except Election.DoesNotExist:
        raise Http404("The requested URL was not found on this server.")

    if request.user.username != elections.user.username:
        return HttpResponse("ACCESS DENIED",status=403)

    if elections.state in ['Activated','Started','Finished','Closed']:
        return HttpResponse("ACCESS DENIED. The Election Cannot be Edited anymore")    

    context = {}
    context['elections'] = elections
    if edit_id == '1':
        context['editform'] = True
        context['EditNumber'] = 1
        context['EditNumberNext'] = 2
        if request.method=='POST':
            form = ElectionEditForm(request.POST, user=request.user,instance=elections)
            """ADD FUNCTION OF FIELD.HAS_CHANGED AND model.save(update_fields['fieldnames'])"""
            if form.is_valid():
                form.save()
                messages.success(request, "Election Updated Successfully.")
            else:
                messages.error(request,"Error in Form Submission.")
            context['form'] = form
            return render(request,"elections/ElectionForm.html",context)

        elif request.method == 'GET':
            form = ElectionEditForm(user=request.user,instance=elections)
            context['form'] = form
            return render(request,"elections/ElectionForm.html",context)
        else:
            return HttpResponse("BAD REQUEST",status=400)
    #EDIT ELECTION DATETIME FORM
    elif edit_id == '2':        
        context['EditNumber'] = 2
        context['EditNumberNext'] = 3
        context['EditNumberPrevious'] =1
        if request.method=='POST':
            form = ElectionDateTimeEditForm(request.POST, user=request.user,instance=elections)
            if form.is_valid():
                form.save()
                messages.success(request, "%s's Date and Time Successfully Updated" % (elections.name))
            else:
                messages.error(request,"One or more dates incorrectly configured. Changes Not Saved.")
            context['form'] = form
            return render(request,"elections/Election_Time_Edit.html",context)
        elif request.method == 'GET':
            form = ElectionDateTimeEditForm(user=request.user,instance=elections)
            context['form'] = form
            return render(request,"elections/Election_Time_Edit.html",context)
        else:
            return HttpResponse("BAD REQUEST",status=400)


    elif edit_id == '3': #Questions and FORMSETS
        context['EditNumber'] = 3
        context['EditNumberNext'] = 4
        context['EditNumberPrevious'] = 2
        if request.method == 'GET':
            try:
                candidates = Candidate.objects.filter(question__election_id=elections.election_id).only('question__qid','question__text','question__qtype','name').select_related('question').order_by('question__qid')
            except:
                raise Http404("Error No Election Id Found")

            if not candidates.exists():
                messages.warning(request,"Atleast 1 Question is needed to activate the Election.")
                return render(request,"elections/QuestionsList.html",context)

            #CHANGE qdict to dict (JSON)
            qdict = []
            dicr = {}
            prev_id = -1
            for i in candidates:
                if i.question.qid != prev_id:
                    if prev_id != -1:
                        qdict.append(dicr)
                        #qdict[prev_id] =dicr for dictionary container(JSON)
                    dicr = {}
                    dicr['qid'] = i.question.qid
                    dicr['text'] = i.question.text
                    dicr['type'] = i.question.get_qtype_display()
                    dicr['candidates'] = []
                    prev_id = i.question.qid
                    dicr['candidates'].append(i.name)
                    #print dicr
                else:
                    dicr['candidates'].append(i.name)
            
            if prev_id != -1:
                qdict.append(dicr)
                #qdict[prev_id] =dicr for dictionary container (JSON)

            context["Questions_List"] = qdict

            return render(request,"elections/QuestionsList.html",context)
        else:
            return HttpResponse("BAD REQUEST",status=400)

    elif edit_id == '4': #EmailsBulk
        context['EditNumber'] = 4
        context['EditNumberPrevious'] = 3
        context['EditNumberNext'] = 5

        if request.method == 'POST':
            form = EmailBulkForm(request.POST)
            if form.is_valid():
                #candidateformset = inlineformset_factory(Question,Candidate,formset = CandidatesInlineFormset,fields=('name','description',),extra=0,can_delete=True,min_num=2,validate_min=True,widgets=widgets,help_texts=help_texts)
                print form.cleaned_data["email"]                
                for emails in form.cleaned_data["email"]:
                    if not Voter.objects.only('id').filter(email=emails,election_id=elections).exists():
                        Voter.objects.create(election_id=elections,email=emails)
                messages.success(request,"Emails Added Successfully")
                return HttpResponseRedirect(reverse('elections:EditElection',kwargs={'election_slug' : election_slug,'edit_id' : '5' }))

            context['form'] = form
            return render(request,"elections/EmailBulk.html",context)
        elif request.method == 'GET':
            context['form'] = EmailBulkForm()
            return render(request,"elections/EmailBulk.html",context)
        else:
            return HttpResponse("BAD REQUEST",status=400)

    elif edit_id == '5': #EmailsIndividual
        context['EditNumber'] = 5
        context['EditNumberPrevious'] = 4


        help_texts = {
            'email' : "Email Address", 
            'name' : "Voter Name(optional)",  
        }
        votersformset = inlineformset_factory(Election,Voter,formset = EmailsInlineFormset,fields=('email','name',),extra=0,can_delete=True,min_num=1,validate_min=True,help_texts=help_texts)
        if request.method == 'POST':
            
            Voter_Formset = votersformset(request.POST,instance = elections,prefix='votersform')
            if Voter_Formset.is_valid():
                """try:
                    for obj in Voter_Formset.deleted_objects:
                        obj.delete()
                except AttributeError,AssertionError:
                    pass"""
                Voter_Formset.save()
                messages.success(request,"Voters Successfully Edited.")
                context['VoterFormset'] = Voter_Formset
                return HttpResponseRedirect(reverse('elections:EditElection',kwargs={'election_slug' : election_slug,'edit_id' : '5' }))
            
            messages.error(request,"There is an error in the emails provided for the Voters.")
            context['VoterFormset'] = Voter_Formset
            return render(request,"elections/VotersEdit.html",context)

        
        elif request.method == 'GET':
            Voter_Formset = votersformset(instance = elections,prefix='votersform')
            context['VoterFormset'] = Voter_Formset
            return render(request,"elections/VotersEdit.html",context)
        
        else:
            return HttpResponse("BAD REQUEST", status=400)

    else:
        raise Http404("The requested URL was not found on this server.")



@login_required(login_url='/login/')
@user_passes_test(lambda x: x.verified_email,login_url='/users/not-verified/',redirect_field_name=None)
def CreateQuestion(request,election_slug=None):
    if election_slug is None:
        raise Http404("The requested URL was not found on this server.")
    try:
        elections = Election.objects.only('user__username','election_id','name','state').select_related('user').get(slug=election_slug)
    except Election.DoesNotExist:
        raise Http404("The requested URL was not found on this server.")

    if request.user.username != elections.user.username:
        return HttpResponse("ACCESS DENIED",status=403)

    if elections.state in ['Activated','Started','Finished','Closed']:
        return HttpResponse("ACCESS DENIED. The Election Cannot be Edited anymore.")

    widgets = {
            'description' : forms.Textarea(attrs={"rows" : "2"}),  
    }
    help_texts = {
            'description' : "Description about the Candidate or Choice", 
            'name' : "Name of the Candidate or Choice",  
    }
    candidateformset = inlineformset_factory(Question,Candidate,formset = CandidatesInlineFormset,fields=('name','description',),extra=0,can_delete=True,min_num=2,validate_min=True,widgets=widgets,help_texts=help_texts)
    context = {}
    context['elections'] = elections
    context['EditNumber'] = 3

    if request.method == 'POST':
        questionform = QuestionForm(request.POST,prefix = 'questions')

        if questionform.is_valid():
            q = super(QuestionForm, questionform).save(commit=False)
            q.election_id = elections

            Candidate_Formset = candidateformset(request.POST,instance = q,prefix='candidatesforms')

            if Candidate_Formset.is_valid():
                """try:
                    for obj in Candidate_Formset.deleted_objects:
                        obj.delete()
                except AttributeError,AssertionError:
                    pass"""
                q.save()
                Candidate_Formset.save()
                messages.success(request,"Question Successfully Added.")
                return HttpResponseRedirect(reverse('elections:EditElection',kwargs={'election_slug' : election_slug,'edit_id' : '3' }))
            
            messages.error(request,"There is an error in the details provided for the Choices.")
            context['QuestionForm'] = questionform
            context['CandidateFormset'] = Candidate_Formset
            return render(request,"elections/QuestionAddEdit.html",context)

        messages.error(request,"There is an error in the details provided for Question.")
        context['QuestionForm'] = questionform
        context['CandidateFormset'] = Candidate_Formset
        return render(request,"elections/QuestionAddEdit.html",context)
    
    elif request.method == 'GET':
        questionform = QuestionForm(prefix = 'questions')
        Candidate_Formset = candidateformset( prefix= 'candidatesforms')
        context['QuestionForm'] = questionform
        context['CandidateFormset'] = Candidate_Formset
        return render(request,"elections/QuestionAddEdit.html",context)
    
    else:
        return HttpResponse("BAD REQUEST", status=400)



@login_required(login_url='/login/')
@user_passes_test(lambda x: x.verified_email,login_url='/users/not-verified/',redirect_field_name=None)
def EditQuestion(request,election_slug=None,question_id=None):
    if election_slug is None or question_id is None:
        raise Http404("The requested URL was not found on this server.")
    try:
        elections = Election.objects.only('user__username','election_id','name','state').select_related('user').get(slug=election_slug)
    except Election.DoesNotExist:
        raise Http404("The requested URL was not found on this server.")

    try:
        questions = Question.objects.only('qid','qtype','text','election_id__election_id').select_related('election_id').get(qid=question_id)
    except Question.DoesNotExist:
        raise Http404("The requested URL was not found on this server.")

    if request.user.username != elections.user.username or questions.election_id.election_id != elections.election_id:
        return HttpResponse("ACCESS DENIED",status=403)

    if elections.state in ['Activated','Started','Finished','Closed']:
        return HttpResponse("ACCESS DENIED. The Election Cannot be Edited anymore.")

    context = {}
    context['elections'] = elections
    context['questions'] = questions
    context['EditNumber'] = 3
    context['EditForm'] = True
    widgets = {
            'description' : forms.Textarea(attrs={"rows" : "2"}),  
    }
    help_texts = {
            'description' : "Description about the Candidate or Choice", 
            'name' : "Name of the Candidate or Choice",  
    }
    candidateformset = inlineformset_factory(Question,Candidate,formset = CandidatesInlineFormset,fields=('name','description',),extra=0,can_delete=True,min_num=2,validate_min=True,widgets=widgets,help_texts=help_texts)

    if request.method == 'POST':

        if 'SaveButton' in request.POST:
            questionform = QuestionForm(request.POST,prefix = 'questions',instance=questions)
            if questionform.is_valid():
                q = super(QuestionForm, questionform).save(commit=False)
                Candidate_Formset = candidateformset(request.POST,instance = q,prefix='candidatesforms')

                if Candidate_Formset.is_valid():
                    """try:
                        for obj in Candidate_Formset.deleted_objects:
                            obj.delete()
                    except AttributeError,AssertionError:
                        pass"""
                    q.save()
                    Candidate_Formset.save()
                    messages.success(request,"Question Successfully Edited.")
                    return HttpResponseRedirect(reverse('elections:EditElection',kwargs={'election_slug' : election_slug,'edit_id' : '3' }))
                
                messages.error(request,"There is an error in the details provided for the Choices.")
                context['QuestionForm'] = questionform
                context['CandidateFormset'] = Candidate_Formset
                return render(request,"elections/QuestionAddEdit.html",context)

            messages.error(request,"There is an error in the details provided for Question.")
            context['QuestionForm'] = questionform
            context['CandidateFormset'] = Candidate_Formset
            return render(request,"elections/QuestionAddEdit.html",context)

        elif 'Deletebutton' in request.POST:
            questions.delete()
            messages.success(request,"Question Deleted Successfully.")
            return HttpResponseRedirect(reverse('elections:EditElection',kwargs={'election_slug' : election_slug,'edit_id' : '3' }))
        else:
            return HttpResponse("BAD REQUEST",status=400)
    
    elif request.method == 'GET':
        questionform = QuestionForm(instance=questions , prefix = 'questions')
        Candidate_Formset = candidateformset(instance=questions , prefix= 'candidatesforms')
        context['QuestionForm'] = questionform
        context['CandidateFormset'] = Candidate_Formset
        return render(request,"elections/QuestionAddEdit.html",context)
    
    else:
        return HttpResponse("BAD REQUEST", status=400)

import requests
from django.template.loader import get_template
from django.core import mail
from django.template import Context
import random
import string
from elections.mycrypt import check_password,make_password

#RIGHT NOW make_ids + emails. No queues
def make_ids_emails(elections,user):
    try:
        connection = mail.get_connection()
        connection.open()
        emaillist = []
        v = Voter.objects.only('id','email','voter_id','password').filter(election_id=elections)
        template = get_template('elections/voter_email.txt')
        count = 0
        for voters in v:
            count += 1
            s1 = "%s%d" % (elections.voter_prefix,voters.id)
            voters.voter_id = s1
            password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for i in range(7))
            voters.password = make_password(password)   
            if not check_password(password,make_password(password)):
                print "KEYERROR"
                raise KeyError
            voters.save()
            context = Context({
                              'organisation' : elections.organisation,
                              'first_name' : user.first_name,
                              'last_name' : user.last_name,
                              'user_email' : user.email,
                              'election_name' : elections.name,
                              'description' : elections.description,
                              'starts' : elections.starts,
                              'ends' : elections.ends,
                              'timezones' : elections.timezone,
                              'instructions' : elections.instructions,
                              'voterid' : s1,
                              'password' : password,
                              })
            content = template.render(context)

            email = mail.EmailMessage("%s Vote Invite"%(elections.name),content,"iVote" ,
                                  ["%s" %(voters.email)],
                                  headers = { 'Reply-To' : "ashish.sareen2013@vit.ac.in" }
                                 )
            
            emaillist.append(email)
        elections.num_voters = count
        elections.save()
        connection.send_messages(emaillist)
        connection.close()
    except:
        return False

    return True


from django.utils import timezone

@login_required
@user_passes_test(lambda x: x.verified_email,login_url='/users/not-verified/',redirect_field_name=None)
def ActivateElection(request,election_slug=None):
    if election_slug is None:
        raise Http404("The requested URL was not found on this server.")
    try:
        elections = Election.objects.only('user__username','election_id','state','instructions','description','timezone','starts','ends').select_related('user').get(slug=election_slug)
    except Election.DoesNotExist:
        raise Http404("The requested URL was not found on this server.")

    if request.user.username != elections.user.username:
        return HttpResponse("ACCESS DENIED",status=403)

    #print elections.state
    if request.method=='POST':
        if elections.state not in ['Activated','Started','Finished','Closed']:
            if elections.starts > timezone.now():
                questions_check = False
                if Question.objects.only('qid').filter(election_id=elections).exists():
                    questions_check = True
                else:
                    messages.error(request,"The %s has been No Questions! Please Add atleast 1 to Activate it" %(elections.name))

                voter_check = False
                if Voter.objects.only('id').filter(election_id=elections).exists():
                    voter_check = True
                else:
                    messages.error(request,"The %s has been No Voters! Please Add atleast 1 to Activate it" %(elections.name))
                
                if(voter_check and questions_check):
                    #SEND EMAILS
                    if make_ids_emails(elections,request.user):
                        elections.state = 'Activated'
                        elections.save()
                        messages.success(request,"The %s has been Successfully Activated."%(elections.name))   
                    else:
                        messages.error(request,"There is some error Generating VoterIds. Please try again later.")    

                return HttpResponseRedirect(reverse("users:dashboard"))
            else:
                messages.error(request,"The current UTC time has already exceeded the %s's start time." %(elections.name))
                messages.error(request,"Please Edit the %s's Timings to Activate it." %(elections.name))
                return HttpResponseRedirect(reverse("users:dashboard"))
        else:
            messages.error(request,"ACCESS DENIED. The Election Cannot be Edited anymore.It's already %s" % (elections.state) )
            return HttpResponseRedirect(reverse("users:dashboard"))
            #return HttpResponse("ACCESS DENIED. The Election Cannot be Edited anymore.It has already %s" % (elections.state) ,status=403)

    else:#GET
        return render(request,"elections/ActivatePage.html",{ 'elections' : elections })

def VoterLogin(request):
    if request.method=='GET':
        verify = request.session.get('voter_session',None)
        if not verify:
            request.session.set_test_cookie()
            return render(request,"elections/VoterLogin.html")
        else:
            return HttpResponseRedirect(reverse('elections:VoterDashboard'))
    elif request.method=='POST':
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
        else:
            messages.error(request,"Please enable cookies and try again.")
            request.session.set_test_cookie()
            return render(request, "elections/VoterLogin.html")
        voterid = request.POST.get('voterid',None)
        password = request.POST.get('password',None)
        #voter_user = Voter.objects.
        voters = Voter.objects.only('password','voter_id').filter(voter_id=voterid)
        if voters.exists():
            if check_password(password,voters[0].password):
                request.session.flush()
                request.session['voter_session']  = voters[0].voter_id
                request.session.set_expiry(3600)
                messages.success(request,"Successfully Logged in")
                return HttpResponseRedirect(reverse('elections:VoterDashboard'))
            else:    
                request.session.set_test_cookie()
                messages.error(request,"Incorrect VoterId/Password Combination.")
                return render(request,"elections/VoterLogin.html")
        else:
            request.session.set_test_cookie()
            messages.error(request,"No VoterId exists.")
            return render(request,"elections/VoterLogin.html")
    else:
        return HttpResponse("BAD REQUEST",status=403)





def VoterDashboard(request):
    voter_name = request.session.get('voter_session',None)
    if voter_name:
        elections = Election.objects.only('name','privacy','starts','ends','timezone').filter(voter__name=voter_name)
        print elections
        return render(request,"elections/VoterDashboard.html")
    else:
        messages.error(request,"No Session exists")
        return HttpResponseRedirect(reverse('elections:VoterLogin'))

    