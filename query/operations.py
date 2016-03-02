# -*- coding: utf-8 -*-

from django.conf import settings

def engine_specific(engines, operation):
    """ Modify `operation` to only operate for particular `engines`. """
    
    def nullop(*args, **kwargs):
        pass
    
    configured_engine = settings.DATABASES['default']['ENGINE']
    
    for engine in engines:
        if engine in configured_engine:
            break
    else:
        operation.state_forwards = nullop
        operation.database_forwards = nullop
        operation.database_backwards = nullop
    
    return operation
