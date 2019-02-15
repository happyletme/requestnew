import logging
class Log:
    def __init__(self,filename,level="INFO"):
        self.filename=filename
        self.level=level
        self.logger=logging.getLogger() #得到logger实体
        self.logger.setLevel(logging.DEBUG)#设置日志最低输出级别默认为WARN
        self.formatter=logging.Formatter("[time:%(asctime)s - file:%(filename)s] - %(levelname)s : %(message)s")#设置日志格式

    def __createHandler(self):
        #创建FileHandler,日志输入到文件
        fh=logging.FileHandler(self.filename,'a')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(self.formatter)
        self.logger.addHandler(fh)

        # 创建FileHandler,日志输入到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(self.formatter)
        self.logger.addHandler(ch)
        return fh,ch

    def __console(self,message):
        if self.level == "INFO":
            self.logger.info(message)
        if self.level == "DEBUG":
            self.logger.debug(message)
        if self.level == "WARN":
            self.logger.warn(message)
        if self.level == "ERROR":
            self.logger.error(message)

    def __call__(self,fuc):
        def wrapper(*args,**kwargs):
            fh, ch=self.__createHandler()
            for i in range(len(args)):
                self.__console(args[i])
            self.logger.removeHandler(fh)
            self.logger.removeHandler(ch)
            fuc(*args, **kwargs)
        return wrapper
