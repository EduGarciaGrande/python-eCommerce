from .base import *
# from .production import *

# try:
#     from .local import *
#     print('Local settings imported successfully')
# except:
#     print('Error while importing local settings')

# Override production variables if DJANGO_DEVELOPMENT env variable is set
print('settings in ' + os.environ.get('DJANGO_SETTINGS_MODULE'))
