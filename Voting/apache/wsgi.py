"""
WSGI config for ClassCard project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

#import os
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ClassCard.settings")

#from django.core.wsgi import get_wsgi_application
#application = get_wsgi_application()

"""


import os
import sys

apache_dir = os.path.dirname(__file__)
project = os.path.dirname(apache_dir)
workspace = os.path.dirname(project)
if workspace not in sys.path:
    sys.path.append(workspace)

os.environ['DJANGO_SETTINGS_MODULE'] = 'ClassCard.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
print >> sys.stderr, sys.path 

"""