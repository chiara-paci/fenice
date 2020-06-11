
class JsonPostCase(object):

    def __init__(self,test):
        self._test=test

    def _data_post(self,test): 
        questions=self._test.random_question_list(settings.REGISTRATION_NUM_QUESTIONS)
        num_questions=len(questions)
        data={
            "username": self._test.random_string(),
            "password": self._test.random_string(),
            "email": self._test.random_string(),
        }
        for n in range(num_questions):
            data[ "questions-%d-question" % n ]=questions[n]
            data[ "questions-%d-answer" % n ]=self._test._registration_questions[questions[n]]
        return data

    def check(self,response):
        assert True
