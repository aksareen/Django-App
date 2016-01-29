from django.contrib import admin
from elections.models import Election,Candidate,Voter,Vote,Question

class CustomElectionAdmin(admin.ModelAdmin):
    list_display = ('id','election_name', 'election_admin', 'starts', 'ends', 'data_complete')
    list_filter = ('starts', 'ends')
    #search_fields = ('election_name', 'election_admin','data_complete')
    ordering = ('starts',)

class CutsomCandidate(admin.ModelAdmin):
    list_display = ('election_name', 'election_admin', 'starts', 'ends', 'data_complete')
    list_filter = ('starts', 'ends')
    #search_fields = ('election_name', 'election_admin','data_complete')
    ordering = ('starts',)

class CustomVoterAdmin(admin.ModelAdmin):
    list_display = ('election_name', 'election_admin', 'starts', 'ends', 'data_complete')
    list_filter = ('starts', 'ends')
    #search_fields = ('election_name', 'election_admin','data_complete')
    ordering = ('starts',)
class CustomVoteAdmin(admin.ModelAdmin):
    list_display = ('election_name', 'election_admin', 'starts', 'ends', 'data_complete')
    list_filter = ('starts', 'ends')
    #search_fields = ('election_name', 'election_admin','data_complete')
    ordering = ('starts',)

#admin.site.unregister(Election)    
admin.site.register(Election)
admin.site.register(Question)
admin.site.register(Candidate)
admin.site.register(Voter)
admin.site.register(Vote)

