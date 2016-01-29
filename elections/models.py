from django.db import models
from users.models import User
from django.utils import timezone
from timezones import TIMEZONES

class Election(models.Model):
    ptypes = (
        ('Public','Public'),
        ('Private','Private'),
    )
    States = (
        ('Incomplete','Incomplete Election Details'),
        ('Reviewing','Review'),
        ('Activated','Activated'),
        ('Started','Started'),
        ('Finished','Finished'),
        ('Closed','Closed'),
    )
    election_id = models.AutoField(primary_key = True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=255 , blank=False,help_text="Election Name")
    organisation = models.CharField(max_length=255 , blank = False,help_text="Organisation Name")
    #election_type = models.CharField(max_length = 255 , choices = etypes , default = 'Single_Vote',help_text="Type of The Election. Cannot be edited once chosen.")
    privacy = models.CharField(max_length = 255 , choices = ptypes , default = 'Public',help_text="Whether Voter's List is Viewable by all Voters")
    description = models.CharField(max_length = 1024 , blank = False,help_text="Description about the Election")
    created = models.DateTimeField(default=timezone.now)
    starts = models.DateTimeField(help_text = 'Election\'s start Time : Atleast 1 hour from current UTC Time')
    ends = models.DateTimeField(help_text = 'Election\'s End Time : Minimum 3 hours after Starting time and Maximum 48 Hours.')
    timezone = models.CharField(max_length=100, blank=False, null=False,default='Asia/Kolkata', choices=TIMEZONES,help_text="Select Your Timezone")
    voter_prefix = models.CharField(max_length=30,unique=True,blank=False,help_text="Custom prefix for automatically generated unique voter id for your voters")
    num_voters = models.PositiveIntegerField(default=0,help_text = 'Total Number of Registered Voters')
    #num_candidates = models.PositiveIntegerField(default=0,help_text = 'Total Number of Candidates')
    slug = models.SlugField(unique=True,max_length=50,help_text="Your custom unqiue Slug for Election URL",blank=True)
    instructions = models.CharField(max_length=1024,blank=True,help_text="Additional Instructions to be sent in email")

    state = models.CharField(max_length=20,default='Incomplete',choices=States,blank=False)
    check_question = models.BooleanField(default=False,help_text="Check : Atleast 1 question and Minimum 2 candidates per question")
    check_voters = models.BooleanField(default=False,help_text="Voters. Atleast 1 Voter")
    check_election = models.BooleanField(default=True,help_text="Check Election")
    extra_emails = models.PositiveIntegerField(default=0,help_text="extra_emails voters that can be added")

    class Meta:
        #ordering = ('starts',)
        app_label = 'elections'
        #related_name = 'users'

    def __unicode__(self):
        return "%s" % (self.name)

    def delete(self, *args, **kwargs):
        super(Election, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('elections:election_details', args=(self.slug,))

    #@property
    def all_reviewed(self):
        return (self.check_question and self.check_voters and self.check_election)

    def question_review(self):
        for q in self.question_set.all():
            cnt =  q.candidate_set.count()
            if cnt<2:
                return False 
                #Raise Error
        return True

class Question(models.Model):
    etypes = (
        ('Single_Vote','One User One Vote One Value'),
    )
    election_id = models.ForeignKey(Election,on_delete=models.CASCADE)
    text = models.CharField(help_text="Question Text",max_length=255,blank=False)
    #description = models.CharField(help_text="Question Details",max_length=255,blank=False)
    qtype = models.CharField(max_length = 55 , choices = etypes , default = 'Single_Vote',help_text="Type of The Poll/Question.")
    qid = models.AutoField(primary_key=True,help_text="Unique Question ID")
    #min_req = models.BooleanField(default=False,help_text="Minimum 2 candidates to choose from")

    class Meta:
        app_label = 'elections'
        #ordering = ('election_id',)
        #related_name = 'elections'

    def delete(self, *args, **kwargs):
        super(Question, self).delete(*args, **kwargs)
     
    def __unicode__(self):
        return "%s" % (self.qid)

    def question_review(self):
        cnt = self.candidate_set.count()
        if cnt<2:
            return False 
        return True

class Candidate(models.Model):

    cid = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, on_delete = models.CASCADE)
    name = models.CharField(max_length = 255 ,help_text="The Choice" ,blank = False)
    description = models.CharField(max_length=1024, help_text = "Description about your Choice",blank=True)
    votes_rank = models.PositiveIntegerField(default=0,help_text="Total Votes/Rank Ratings")
    #abstain_option = models.BooleanField(default=False,editable=False)
    #FOR SOME OTHER DAY
    class Meta:
        app_label = 'elections'    
        #related_name = 'questions'

    def __unicode__(self):
        return "%s" % (self.name)

    #FOR SOME OTHER DAY : DELETING CANDIDATE IN MIDDLE OF ELECTION
    def delete(self, *args, **kwargs):
        super(Candidate, self).delete(*args, **kwargs)

class Voter(models.Model):
    election_id = models.ForeignKey(Election, on_delete = models.CASCADE)
    email  = models.EmailField(max_length = 254 , blank =False,help_text="Voter's Email")
    name = models.CharField(max_length = 50 , blank = True,help_text="Voter's Name")
    voter_id = models.CharField(max_length = 50 , blank=True,help_text="Unique voter id")#unique = True Also but for now lets add ro prefix
    password = models.CharField(max_length = 256 , blank=True, help_text="KEY generated")
    email_verify = models.BooleanField(default=False)
    hashcheck = models.CharField(blank=True,max_length=256)#uuid for email activation_key
    email_expires = models.DateTimeField(null=True,blank=True)
    email_error = models.BooleanField(default=False)
    otp = models.CharField(blank=True,max_length=30,help_text="OTP")
    voter_added_time = models.DateTimeField(default=timezone.now)
    otp_time_expires = models.DateTimeField(blank=True,null=True)
    otp_tries = models.PositiveIntegerField(default=0)
    voted_id = models.PositiveIntegerField(blank=True,null=True)
    vote_weight = models.PositiveIntegerField(default=1)
    id = models.AutoField(primary_key=True)
    has_voted = models.BooleanField(default=False)

    class Meta:
        #ordering = ('election_id','voter_id',)
        app_label = 'elections'    
        unique_together = (("election_id", "email"),)

    def delete(self, *args, **kwargs):
        super(Voter, self).delete(*args, **kwargs)

class Vote(models.Model):
    candidate_id = models.ForeignKey(Candidate,on_delete = models.CASCADE)
    voter_id = models.ForeignKey(Voter,on_delete=models.CASCADE)  
    comments = models.CharField(max_length=255 , blank=True,help_text="Your Comments")
    vote_weight = models.PositiveIntegerField(default=1)

    class Meta:
        #ordering = ('candidate_id',)
        app_label = 'elections'
        unique_together = (("candidate_id", "voter_id"),)

    def delete(self, *args, **kwargs):
        super(Vote, self).delete(*args, **kwargs)