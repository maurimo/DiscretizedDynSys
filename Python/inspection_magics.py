from IPython.core.magic import magics_class, \
 no_var_expand, needs_local_scope, cell_magic, Magics
from IPython.core.interactiveshell import InteractiveShell
import ast
from ast import Module
from collections import OrderedDict
from types import ModuleType
import re

DEFAULT_PARAMS = {
    'do_data': True,
    'do_funcs': True,
    'do_mods': True,
    'excludes_reg': None,
    'trap_reg': None,
    'show_values': False
}

def parse_args(line, params = {}):
    args = line.split()
    for a in args:
        if a.startswith('#'):
            break
        elif a == '--show-values':
            params['show_values'] = True
        elif a == '--no-show-values':
            params['show_values'] = False
        elif a == '--mods':
            params['do_mods'] = True
        elif a == '--funcs':
            params['do_funcs'] = True
        elif a == '--data':
            params['do_data'] = True
        elif a == '--no-mods':
            params['do_mods'] = False
        elif a == '--no-funcs':
            params['do_funcs'] = False
        elif a == '--no-data':
            params['do_data'] = False
        elif a.startswith('--trap-reg='):
            params['trap_reg'] = re.compile(a.split('=', 1)[1])
        elif a.startswith('--exclude-mods='):
            excludes = a.split('=', 1)[1]
            if not re.match(r'[\.\w\,]*$', excludes):
                print("inspection_magics: expected a comma separated of module patterns eg. a,b.c - got:", excludes)
                return False
            params['excludes_reg'] = re.compile(r'(?:'+excludes.replace('.', r'\.').replace(',', r'|')+r')\.') if excludes else None
        else:
            print("inspection_magics: argument not understood:", a)
            return False
    return True

def set_defaults(line):
    parse_args(line, DEFAULT_PARAMS)

T_GRAY = '\x1b[0;37m'
T_B_RED = '\x1b[1;31m'
T_B_BLUE = '\x1b[1;34m'
T_B_YELLOW = '\x1b[1;33m'
T_RESET = '\x1b[0m'

@magics_class
class InspectionMagics(Magics):
    @no_var_expand
    @cell_magic
    def open_vars(self, line, cell):
        params = DEFAULT_PARAMS.copy()
        if not parse_args(line, params):
            return
        do_data = params['do_data']
        do_funcs = params['do_funcs']
        do_mods = params['do_mods']
        excludes_reg = params['excludes_reg']
        trap_reg = params['trap_reg']
        show_values = params['show_values']

        def check_mod(v):
            if excludes_reg is None:
                return True
            if not hasattr(v, '__module__') or not isinstance(v.__module__, str):
                return True
            return not excludes_reg.match(v.__module__+'.')

        written = set()
        accessed = OrderedDict()
        
        class MyHack:
            def __init__(self, d):
                self.d = d

            def __setitem__(self, k, v):
                # print('wtest:', k)
                if trap_reg and trap_reg.match(k):
                    raise RuntimeError(f"trapped write to variable `{k}`")
                written.add(k)
                self.d.__setitem__(k, v)

            def __getitem__(self, k):
                # print('rtest:', k)
                if trap_reg and trap_reg.match(k):
                    raise RuntimeError(f"trapped read of variable `{k}`")
                # may throw if not present
                v = self.d.__getitem__(k)
                if not k in written:
                    accessed[k] = v
                return v

            def __contains__(self, k):
                return self.d.__contains__(k)
            
            def get(self, k, default=None):
                try:
                    return self[k]
                except KeyError:
                    return default
            
            def update(self, E, **F):
                if hasattr(E, 'keys'):
                    for k in E:
                        self[k] = E[k]
                else:
                    for k, v in E:
                        self[k] = v
                for k in F:
                    self[k] = F[v]

        orig = self.shell.user_ns
        self.shell.user_ns = MyHack(orig)
        
        try:
            self.shell.run_cell(cell)
        finally:
            self.shell.user_ns = orig
        
        accessed_data = [
            T_B_RED + a + ("=" + str(v) if show_values else "") for a,v in accessed.items()
             if not a.startswith('_') and not callable(v) and not isinstance(v, ModuleType)
            ] if do_data else []
        accessed_func = [
            T_B_BLUE + a for a,v in accessed.items()
             if not a.startswith('_') and callable(v) and check_mod(v)
            ] if do_funcs else []
        accessed_mod = [
            T_B_YELLOW + a for a,v in accessed.items()
            if not a.startswith('_') and isinstance(v, ModuleType)
            ] if do_mods else []
        if accessed_data or accessed_func or accessed_mod:
            print(T_GRAY + "used vars: " + (T_GRAY+", ").join(accessed_data + accessed_func + accessed_mod) + T_RESET)
        else:
            print(T_GRAY + "(no used vars)" + T_RESET)

InteractiveShell.instance().register_magics(InspectionMagics)