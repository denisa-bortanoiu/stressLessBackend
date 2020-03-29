from connexion import ProblemException
from connexion.exceptions import BadRequestProblem
from werkzeug.exceptions import Unauthorized, Forbidden


class UnauthorizedProblem(ProblemException, Unauthorized):
    def __init__(self, detail='Provided authorization is not valid',
                 title='Unauthorized', **kwargs):
        super(UnauthorizedProblem, self).__init__(
            detail=detail,
            title=title,
            type='unauthorized',
            status=401,
            **kwargs
        )


class ForbiddenProblem(ProblemException, Forbidden):
    def __init__(self, detail='Action not allowed',
                 title='Forbidden', **kwargs):
        super(ForbiddenProblem, self).__init__(
            detail=detail,
            title=title,
            type='forbidden',
            status=403,
            **kwargs
        )
