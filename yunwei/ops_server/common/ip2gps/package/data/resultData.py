class resultData():
    def __init__(self,success=False,res=None,msg="failed"):
        self.result={
            "success":success,
            "res":res,
            "msg":msg
        }
    def success(self,res=None,success=True,msg="success"):
        self.__init__(success,res,msg)
        return self.result

    def fail(self,success=False,res=None,msg="failed"):
        self.__init__(success,res,msg)
        return self.result