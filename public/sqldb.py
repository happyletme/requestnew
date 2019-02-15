#-*-coding:utf-8-*-s
#mysql和sqlserver的库
import pymysql,pymssql,json,requests
from DBUtils.PooledDB import PooledDB
class Database:
    def __init__(self,*db):
        if len(db)==5:
            #mysql数据库
            self.host=db[0]
            self.port=int(db[1])
            self.user=db[2]
            self.pwd=db[3]
            self.db=db[4]
        else:
            #sqlserver数据库
            self.host=db[0]
            self.port=None
            self.user=db[1]
            self.pwd=db[2]
            self.db=db[3]
        self._CreatePool()
    def _CreatePool(self):
        if not self.db:
            raise NameError+"没有设置数据库信息"
        if (self.port==None):
            self.Pool=PooledDB(creator=pymssql,mincached=2, maxcached=5,maxshared=3, maxconnections=6, blocking=True,host=self.host,user=self.user, \
                               password=self.pwd,database=self.db,charset="utf8")
        else:
            self.Pool=PooledDB(creator=pymysql,mincached=2, maxcached=5,maxshared=3, maxconnections=6, blocking=True,host=self.host,port=self.port, \
                               user=self.user,password=self.pwd,database =self.db,charset="utf8")
    def _Getconnect(self):
        self.conn=self.Pool.connection()
        cur=self.conn.cursor()
        if not cur:
            raise ("数据库连接不上")
        else:
            return cur
    #查询sql
    def ExecQuery(self,sql):
        cur=self._Getconnect()
        cur.execute(sql)
        relist=cur.fetchall()
        cur.close()
        self.conn.close()
        return relist
    #非查询的sql
    def ExecNoQuery(self,sql):
        cur=self._Getconnect()
        cur.execute(sql)
        self.conn.commit()
        cur.close()
        self.conn.close()


class MakeSqlData:
    def __init__(self,sqldatabaseobj,variable,sql,is_select=1):
        self.variable=variable
        self.sql=sql
        self.sqldatabaseobj = sqldatabaseobj
        self.is_select=is_select
        self.variableObj={}
        self.__SplitVariable()
    def __SplitVariable(self):
        variables=self.variable.split(',')
        try:
            for i in range(len(variables)):
                #拿的都是第一行的数据
                if self.is_select==1:
                    self.variableObj[variables[i]] = self.sqldatabaseobj.ExecQuery(self.sql)[0][i]
                    # 如果数据库返回内容是字符串带",替换成'号，避免后面脚本json转换出错
                    #如果数据库返回内容是字符串带,号,替换成+号，避免后面脚本切割字符串出错
                    if isinstance(self.variableObj[variables[i]], str):
                        self.variableObj[variables[i]] = self.variableObj[variables[i]].replace("\"", "\'")
                        self.variableObj[variables[i]] = self.variableObj[variables[i]].replace(",", "+")
        except:
            errormessage = '查询sql替换变量出错'
            raise RuntimeError(errormessage)

#启动数据库对象和ip属性
def create_db(db_dict,env_ip,redis):
    global db,ip,NoSqlredis
    ip=env_ip
    db=db_dict
    NoSqlredis=redis
#create_db(0,"192.168.100.211",3307,"akmysql", "mysql123", "bt_hyaline")
#allocation=configuration()
#db=Database(allocation.Mysqlhost,allocation.Mysqlport,allocation.Mysqluser,allocation.Mysqlpwd,allocation.Mysqldb)
'''
sql="select  FID,FSystemCode from t_SystemAccess where FIsDelete=0"
variable="FID,FSystemCode"
is_select=0

makesqldata=MakeSqlData(variable,sql)
print (makesqldata.variableObj)
'''

#传递全局变量IP和数据库对象
class Transferip_db:
    def __init__(self):
        self.ip=ip
        self.db=db
        self.NoSqlredis=NoSqlredis

