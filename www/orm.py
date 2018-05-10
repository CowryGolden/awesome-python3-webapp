#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r'''
    # 在一个Web App中，所有数据，包括用户信息、发布的日志、评论等，都存储在数据库中。在awesome-python3-webapp中，我们选择MySQL作为数据库。
    Web App里面有很多地方都要访问数据库。访问数据库需要创建数据库连接、游标对象，然后执行SQL语句，最后处理异常，清理资源。这些访问数据库的代码如果分散到各个函数中，势必无法维护，也不利于代码复用。
    所以，我们要首先把常用的SELECT、INSERT、UPDATE和DELETE操作用函数封装起来。
    由于Web框架使用了基于asyncio的aiohttp，这是基于协程的异步模型。在协程中，不能调用普通的同步IO操作，因为所有用户都是由一个线程服务的，协程的执行速度必须非常快，才能处理大量用户的请求。而耗时的IO操作不能在协程中以同步的方式调用，否则，等待一个IO操作时，系统无法响应任何其他用户。
    这就是异步编程的一个原则：一旦决定使用异步，则系统每一层都必须是异步，“开弓没有回头箭”。
    幸运的是aiomysql为MySQL数据库提供了异步IO的驱动。
    具体操作步骤如下：
        创建连接池
        编写执行查询语句的select函数
        编写执行insert、update、delete的execute函数
        设计ORM
        定义Model

'''
__author__ = 'Cowry Golden'

# 导入依赖
import asyncio, logging

import aiomysql

# sql语句日志
def log(sql, args=()):
    logging.info('SQL: %s' % sql)

# 创建连接池
async def create_pool(loop, **kw):
    logging.info('Create database connection pool...')
    global __pool
    __pool = await aiomysql.create_pool(
        host=kw.get('host', 'localhost'),
        port=kw.get('port', 3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['db'],
        charset=kw.get('charset', 'utf8'),
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        loop=loop
    )

# 销毁连接池
async def destory_pool():
    global __pool
    if __pool is not None:
        __pool.close()
        await __pool.wait_closed()


# 编写执行查询语句的select函数
async def select(sql, args, size=None):
    log(sql, args)
    global __pool
    async with __pool.get() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql.replace('?', '%s'), args or ())
            if size:
                rs = await cur.fetchmany(size)
            else:
                rs = await cur.fetchall()
        logging.info('Rows returned: %s' % len(rs))
        return rs

# SQL语句的占位符是?，而MySQL的占位符是%s，select()函数在内部自动替换。注意要始终坚持使用带参数的SQL，而不是自己拼接SQL字符串，这样可以防止SQL注入攻击。
# 注意到await将调用一个子协程（也就是在一个协程中调用另一个协程）并直接获得子协程的返回结果。

# 编写执行insert、update、delete的execute函数，因为这3种SQL的执行都需要相同的参数，以及返回一个整数表示影响的行数：
async def execute(sql, args, autocommit=True):
    log(sql, args)
    async with __pool.get() as conn:
        if not autocommit:
            await conn.begin()
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql.replace('?', '%s'), args)
                affected = cur.rowcount
            if not autocommit:
                await conn.commit()
        except BaseException as e:
            if not autocommit:
                await conn.rollback()
            raise
        return affected

# execute()函数和select()函数所不同的是，cursor对象不返回结果集，而是通过rowcount返回结果数。

# 创建拥有几个占位符的字符串
def create_args_string(num):
    L = []
    for n in range(num):
        L.append('?')
    return ', '.join(L)         

# 数据库列属性基类（包括列名、列类型、该列是否为主键、默认值等）
class Field(object):
    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default
    
    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)

# 以下是数据库中常用的字段类型的具体定义
# 字符串类型字段
class StringField(Field):  
    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)'):
        super().__init__(name, ddl, primary_key, default)     

# Boolean类型字段
class BooleanField(Field):  
    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', False, default)    

# 整型类型字段
class IntegerField(Field):  
    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, 'bigint', primary_key, default)    

# 浮点型类型字段
class FloatField(Field):  
    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, 'real', primary_key, default)    

# Text类型字段
class TextField(Field):  
    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)    

# 定义Model类的元类
class ModelMetaclass(type):
    def __new__(cls, name, bases, attrs):
        # 排除Model基类本身，因为其中没有字段属性
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)

        # 获取数据库表名，如果没有则把类名做表名
        tableName = attrs.get('__table__', None) or name
        logging.info('Found model: %s (table: %s)' % (name, tableName))    
        # 保存列类型对象
        mappings = dict()
        # 保存列名的list
        fields = []
        # 主键列名称
        primaryKey = None
        for k, v in attrs.items():
            if isinstance(v, Field):
                # 是列类型的就保存
                logging.info('  found mapping: %s ==> %s' % (k, v))
                mappings[k] = v
                if v.primary_key:    # 保存为主键的字段 
                    if primaryKey:
                        raise StandardError('Duplicate primary key for field: %s' % k)
                    primaryKey = k
                else:    # 保存非主键字段
                    fields.append(k)
        if not primaryKey:
            raise StandardError('Primary key not found.')
        for k in mappings.keys():    # 避免类属性值覆盖实例属性值，故将类属性移除
            attrs.pop(k)
        # 根据MySQL数据库特性转义字段名，避免与其关键字冲突
        escaped_fields = list(map(lambda f: '`%s`' % f, fields))
        attrs['__mappings__'] = mappings    # 保存实例属性和列的映射关系
        attrs['__table__'] = tableName    # 表名
        attrs['__primary_key__'] = primaryKey    # 主键属性名
        attrs['__fields__'] = fields    # 除主键外的属性名
        # 以下四种方法保存了默认了增删改查操作,其中添加的反引号``,是为了避免与sql关键字冲突的,否则sql语句会执行出错
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (primaryKey, ','.join(escaped_fields), tableName)
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (tableName, ','.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (tableName, ','.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primaryKey)
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName, primaryKey)

        return type.__new__(cls, name, bases, attrs)

# 模型的基类,继承于dict
class Model(dict, metaclass=ModelMetaclass):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)
    
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'." % key)
    
    def __setattr__(self, key, value):
        self[key] = value
    
    def getValue(self, key):
        # 调用getattr获取一个未存在的属性,也会走__getattr__方法,但是因为指定了默认返回的值,__getattr__里面的错误永远不会抛出
        return getattr(self, key, None)

    # 获取属性值，不存在时使用默认值
    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('Using default value for %s: %s.' % (key, str(value)))
                setattr(self, key, value)
        return value

    # 获取表里符合条件的所有数据，类方法的第一个参数为该类名
    # 装饰器@classmethod用于把类里面定义的方法声明为该类的方法
    @classmethod
    async def findAll(cls, where=None, args=None, **kw):
        ' find objects by where clause.'
        sql = [cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args = []
        orderBy = kw.get('orderBy', None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)
        limit = kw.get('limit', None)
        if limit is not None:
            sql.append('limit')
            if isinstance(limit, int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append('?, ?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value: %s' % str(limit))
        rs = await select(' '.join(sql), args)
        return [cls(**r) for r in rs]

    # 查找符合条件的记录数
    @classmethod
    async def findNumber(cls, selectField, where=None, args=None):
        ' find number by select and where.'
        sql = ['select %s _num_ from `%s`' % (selectField, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs = await select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']

    # 按住键进行查找
    @classmethod
    async def findByPriKey(cls, pk):
        ' find object by primary key.'
        rs = await select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])

    # 以下为对象方法，可以被实例对象直接调用，可以不用传任何参数方法内部可以使用该对象所有属性
    # 将实例对象保存到数据库，这就是ORM的功效
    async def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))    # 除主键外所有字段的值
        args.append(self.getValueOrDefault(self.__primary_key__))    # 主键字段的值
        rows = await execute(self.__insert__, args)
        if rows != 1:
            logging.warn('failed to insert record: affected rows: %s' % rows)
    
    # 更新对象对应的数据库数据
    async def update(self):
        args = list(map(self.getValue, self.__fields__))    # 除主键外所有字段的值
        args.append(self.getValue(self.__primary_key__))    # 主键字段的值
        rows = await execute(self.__update__, args)
        if rows != 1:
            logging.warn('failed to update by primary key: affected rows: %s', rows)

    # 删除对象对应的数据库数据(根据主键字段)
    async def remove(self):
        args = [self.getValue(self.__primary_key__)]
        rows = await execute(self.__delete__, args)
        if rows != 1:
            logging.warn('failed to remove by primary key: affected rows: %s' % rows)



