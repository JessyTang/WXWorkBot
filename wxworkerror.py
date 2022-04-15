class WXWorkError(Exception):
    def __init__(self, errcode, errmsg):
        self.__errcode = errcode
        self.__errmsg = errmsg

    def __str__(self):
        return f'errcode: {self.__errcode}; errmsg: {self.__errmsg}'

    __repr__ = __str__

    def getErrcode(self):
        return self.__errcode

    def getErrmsg(self):
        return self.__errmsg
