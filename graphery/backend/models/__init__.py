from .mixins import *
from .user import User
from .tag import *
from .tutorial import *
from .graph import *
from .code import *
from .executioinresult import *
from .uploads import *


model_list = [
    User,
    TagAnchor,
    Tag,
    TutorialAnchor,
    Tutorial,
    GraphAnchor,
    Graph,
    GraphDescription,
    Code,
    ExecutionResult,
    Uploads,
]
