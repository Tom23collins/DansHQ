# __init__.py

from .course import get_course_status
from .courses import add_course

from .person import get_person_status, add_person
from .personnel import get_training_data, download_training_data, get_fully_qualified

from .role import get_role_status
from .roles import add_role, get_roles

from .user_role_data import get_role_data_for_user
from .user_details import update_user_details
from .user_roles import update_user_roles

from .settings import update_user_role

__all__ = [
            'add_course',
            'get_role_data_for_user', 
            'get_training_data',
            'update_user_details',
            'update_user_roles',
            'download_training_data', 
            'get_fully_qualified',
            'add_role',
            'get_roles', 
            'update_user_role'
            ]