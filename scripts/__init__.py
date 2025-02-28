# __init__.py

from .course import get_course
from .courses import get_courses, set_course

from .person import get_person, set_person
from .personnel import get_personnel, set_personnel

from .role import get_role
from .roles import set_role, get_roles

from .settings import set_user_access

__all__ = [
            'get_courses',
            'get_course',
            'set_course',
            'get_role',
            'set_role',
            'get_roles',
            'get_person',
            'set_person',
            'get_personnel',
            'set_personnel',
            'set_user_access'
            ]