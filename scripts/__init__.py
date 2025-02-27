# __init__.py

from .course import get_course
from .courses import add_course

from .person import get_person_roles, get_person
from .personnel import get_training_data, download_training_data, get_fully_qualified

from .role import get_role_courses
from .roles import add_role, get_roles

from .user_details import update_user_details

from .settings import set_user_access

__all__ = [
            'add_course',
            'get_training_data',
            'update_user_details',
            'get_person_roles',
            'download_training_data', 
            'get_fully_qualified',
            'add_role',
            'get_roles',
            'get_person',
            'set_user_access'
            ]