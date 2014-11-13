import os
import glob
import logging
logger = logging.getLogger(__name__)
import time
from datetime import datetime
from functools import update_wrapper

def decorator(d):
    """Make function d a decorator: d wraps a function fn."""
    def _d(fn):
        return update_wrapper(d(fn), fn)
    update_wrapper(_d, d)
    return _d


@decorator
def memo(f):
    """Decorator that caches the return value for each call to f(args).
    Then when called again with same args, we can just look it up."""
    cache = {}
    def _f(*args):
        try:
            return cache[args]
        except KeyError:
            cache[args] = result = f(*args)
            return result
        except TypeError:
            # some element of args can't be a dict key
            return f(args)
    return _f


@decorator
def timeit(f):
    def new_f(*args, **kwargs):
        bt = time.time()
        r = f(*args, **kwargs)
        et = time.time()        
        logger.info("time spent on {0}: {1:.5f}s".format(f.func_name, et - bt))
        return r
    return new_f


def touch(fname, times=None):
    with open(fname, 'a') as opf:
        # write date and path to make it more informative
        opf.write('created: {0}'.format(unicode(datetime.now())))
        opf.write('path: {0}'.format(os.path.abspath('.')))
        os.utime(fname, times)


def get_lockers(locker_pattern):
    """get a locker(s)"""
    return glob.glob(locker_pattern)


def create_locker(locker):
    """create a locker"""
    logger.info('creating {0}'.format(locker))
    touch(locker)


def remove_locker(locker):
    """remove a locker"""
    logger.info('removing {0}'.format(locker))
    os.remove(locker)


def lockit(locker_pattern):
    """
    It creates a locker and prevent the same function from being run again
    before the previous one finishes

    locker_pattern should be composed of locker_path/locker_prefix, an example
    of a locker:
        locker_path/locker_prefix.%y-%m-%d_%H-%M-%S.locker

    """
    # dec: decrator, since it has been already used outside the namespace
    # deced: decorated
    @decorator
    def dec(func): 
        def deced(*args, **kwargs):
            lockers = get_lockers('{0}*.locker'.format(locker_pattern))
            if len(lockers) >= 1:
                logger.info('The previous {0} run hasn\'t completed yet with '
                            'the following locker(s) found: ({1}). '
                            'Nothing done.'.format(
                                func.__name__, ' '.join(lockers)))
                return
            else:
                now = datetime.now().strftime('%y-%m-%d_%H:%M:%S')
                locker = '{0}.{1}.locker'.format(locker_pattern, now)
                create_locker(locker)
                try:
                    res = func(*args, **kwargs)
                except Exception, err:
                    logger.exception(err)
                else: # this else could be in the try block, as well since it
                      # unlikely will raise any exception
                    return res                    
                finally:
                    # TIP: finally guarantees that even when sys.exit(1), the
                    # following block gets run
                    remove_locker(locker)
        return deced
    return dec
