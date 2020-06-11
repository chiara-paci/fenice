class AssertionMethod(object):
    def __init__(self,assert_cls,*args,**kwargs):
        self._assert_cls=assert_cls
        self._args=args
        self._kwargs=kwargs

    def __get__(self,instance,instance_type):
        return self._assert_cls(instance,*self._args,**self._kwargs)

