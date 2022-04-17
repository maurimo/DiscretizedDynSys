import sqlite3
import hashlib
import pickle
import json

DEFAULT_PATH = 'db.db'
DEFAULT_TABLE = 'objects'

GLOBAL_INSTANCE = None

class MemoDB:
    @staticmethod
    def instance():
        global GLOBAL_INSTANCE
        if not GLOBAL_INSTANCE:
            GLOBAL_INSTANCE = MemoDB()
        return GLOBAL_INSTANCE
    
    def __init__(self, path=DEFAULT_PATH, table=DEFAULT_TABLE):
        self.conn = sqlite3.connect(path)
        self.table = table
        self.pkey = 'hash'
        self.notnull = {'hash'}
        self.columns = ['hash', 'fname', 'args', 'data']
        self.coltypes = {'hash': 'BLOB', 'data': 'BLOB', 'args': 'BLOB', 'fname': 'TEXT'}
        self.indices = ['fname', 'args']
        self.accessed_hashes = None
        self.create()
        
    def enable_tracking(self):
        self.accessed_hashes = set()
        
    def clear_not_accessed(self):
        if self.accessed_hashes is None:
            print("Tracking is disabled, no key was deleted")
            return
        hashes = self.select('hash')
        for h, in hashes:
            if h not in self.accessed_hashes:
                self.delete(hash=h)
        
    def count(self):
        c = self.conn.cursor()
        c.execute('SELECT COUNT(*) from ' + self.table)
        return c.fetchone()[0]

    def drop(self):
        c = self.conn.cursor()
        c.execute('DROP TABLE ' + self.table)
        self.conn.commit()

    def create(self, drop_if_exists = False):

        if drop_if_exists:
            try: self.drop()
            except: pass

        c = self.conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS '+
                  self.table+' '+
                  '('+', '.join(f'{c} {self.coltypes.get(c,"TEXT")}'+(' NOT NULL' if c in self.notnull else '') for c in self.columns)+
                  ', PRIMARY KEY('+self.pkey+')'
                  ')')
        for index in self.indices:
            c.execute('CREATE INDEX IF NOT EXISTS ' + f'{self.table}_idx_{index} ON {self.table}({index})')
        self.conn.commit()
    
    def insert(self, **kwargs):
        c = self.conn.cursor()
        items = [[kwargs.get(c) for c in self.columns]]
        c.executemany('INSERT OR REPLACE INTO ' + self.table + ' VALUES (' + ','.join('?' for _ in self.columns) + ')', items)
        self.conn.commit()

    def select(self, *what, **kwargs):
        c = self.conn.cursor()
        wstr = '*'
        if what:
            assert(not (set(what) - set(self.columns)))
            wstr = ','.join(what)
        where = '' if len(kwargs) == 0 else ' WHERE '+' and '.join(f'{k}=:{k}' for k in kwargs.keys())
        c.execute(f'SELECT {wstr} FROM {self.table}' + where, kwargs)
        return c.fetchall()

    def delete(self, **kwargs):
        c = self.conn.cursor()
        where = '' if len(kwargs) == 0 else ' WHERE '+' and '.join(f'{k}=:{k}' for k in kwargs.keys())
        c.execute(f'DELETE FROM {self.table}' + where, kwargs)
        self.conn.commit()

def full_name(f):
    if hasattr(f, '__module__') and f.__module__:
        return f.__module__ + '.' + f.__qualname__
    else:
        return f.__qualname__
    
def func_checksum(f):
    #from types import ModuleType
    #globs = [f.__globals__[g] 
    #         for g in f.__code__.co_names
    #         if g in f.__globals__ and not isinstance(f.__globals__[g], ModuleType)
    #            and not callable(f.__globals__[g])]
    return [f.__code__.co_code, 
            [c.co_code if hasattr(c,'co_code') else c for c in 
             f.__code__.co_consts],
            f.__code__.co_names]

import sage
ALLOWED_ARG_TYPES = (int, float, str, sage.rings.integer.Integer, sage.rings.real_mpfr.RealNumber)

def check_arg(arg):
    if isinstance(arg, (list, set, tuple)):
        for a in arg:
            check_arg(a)
    elif isinstance(arg, dict):
        for a in arg.keys():
            check_arg(a)
        for a in arg.values():
            check_arg(a)
    elif not isinstance(arg, ALLOWED_ARG_TYPES):
        raise RuntimeError(f'Got arg of not alower type {type(arg)}, allowed are: {ALLOWED_ARG_TYPES}')

def check_args(*argv, **kwargs):
    for a in argv:
        check_arg(a)
    for a in kwargs.values():
        check_arg(a)

fcheck = None

def memodb(f):
    memo = MemoDB.instance()
    f_name = full_name(f)
    global fcheck
    fcheck = func_checksum(f)
    f_checksum = hashlib.md5(pickle.dumps(func_checksum(f))).digest() # byte array
    def helper(*argv, **kwargs):
        check_args(*argv, **kwargs)

        exec_checksum = hashlib.md5(pickle.dumps([f_checksum, f_name, argv, kwargs])).digest()
        if memo.accessed_hashes is not None:
            memo.accessed_hashes.add(exec_checksum)
        select_res = memo.select('data', hash=exec_checksum)
        if select_res:
            # print('LOAD', f_name, argv, kwargs)
            return pickle.loads(select_res[0][0])
        
        jargs = pickle.dumps([argv, kwargs])
        
        # print('COMP', f_name, argv, kwargs)
        retv = f(*argv, **kwargs)
        
        retv_data = pickle.dumps(retv)
        memo.delete(fname=f_name, args=jargs)
        memo.insert(hash=exec_checksum, fname=f_name, args=jargs, data=retv_data)
        
        return retv
    return helper
