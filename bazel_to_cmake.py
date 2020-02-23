#!/usr/bin/env python

from __future__ import print_function

import os
import textwrap
import ast


class BuildFileFunctions(object):
    def __init__(self, build_info):
        self._build_info = build_info

    def _cc_library_binary(self, name, deps=None, includes=None, **kwargs):
        # add includes dir
        if includes:
            for d in includes:
                self._build_info.add_include(d)

        if deps:
            # do not handle include in deps now
            for label in deps:
                self._build_info.add_include_label(label)

        # TODO: handle include in copts

    def cc_library(self, **kwargs):
        self._cc_library_binary(**kwargs)

    def cc_binary(self, **kwargs):
        self._cc_library_binary(**kwargs)


class BuildInfo:
    def __init__(self):
        self.include_dir = set()

    def add_include(self, path):
        self.include_dir.add(path)

    def add_include_label(self, label):
        if label.startswith('@'):
            # ignore labels point to different package
            return

        if not label.startswith('//'):
            # current package
            self.include_dir.add(".")
            return

        # remove target name
        t_pos = label.rfind(':')
        if not t_pos == -1:
            label = label[:t_pos]

        self.include_dir.add('${BAZEL2C_BASE_PATH}/' + label[2:])


class Generator(object):
    @staticmethod
    def gen(path, build_info):
        inc_cmd = ''
        if build_info.include_dir:
            inc_cmd = 'include_directories(\n'
            for item in build_info.include_dir:
                inc_cmd += ('\t' + item + '\n')
            inc_cmd += ')'

        add_library_cmd = ''
        sources = Generator._get_sources(path)
        if sources:
            lib_name = os.path.basename(path)
            add_library_cmd = 'add_library(%s\n' % lib_name
            for f in sources:
                add_library_cmd += ('\t' + f + '\n')
            add_library_cmd += ')'

        return Generator.template % {
            'include_cmd': inc_cmd,
            'add_library_cmd': add_library_cmd
        }

    template = textwrap.dedent("""\
    cmake_minimum_required (VERSION 2.8)
    
    if(${CMAKE_VERSION} VERSION_LESS 3.12)
        cmake_policy(VERSION ${CMAKE_MAJOR_VERSION}.${CMAKE_MINOR_VERSION})
    else()
        cmake_policy(VERSION 3.12)
    endif()

    %(include_cmd)s
    
    %(add_library_cmd)s

  """)

    @staticmethod
    def _get_sources(path):
        ret = []
        for f_name in os.listdir(path):
            point_pos = f_name.rfind('.')
            if point_pos == -1:
                continue
            extension = f_name[point_pos + 1:]
            if extension in ['cpp', 'cc', 'h']:
                ret.append(f_name)

        return ret


def get_glob_def(obj):
    ret = {}
    for k in __builtins__.dir(obj):
        if not k.startswith("_"):
            ret[k] = getattr(obj, k)
    ret['__builtins__'] = None
    return ret


class FunctionCallFilter(ast.NodeTransformer):
    def __init__(self, func_defs):
        super(FunctionCallFilter, self).__init__()
        self._func_def = func_defs

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call):
            func_name = node.value.func.id
            if func_name not in self._func_def:
                return None
        return node


def convert_project(path):
    build_fpath = os.path.join(path, 'BUILD')
    out_fpath = os.path.join(path, 'CMakeLists.txt')

    if not os.path.isfile(build_fpath):
        return

    build_info = BuildInfo()
    with open(build_fpath, 'r') as f:
        file_content = f.read()

        file_ast = ast.parse(file_content, build_fpath, mode='exec')
        # print(ast.dump(file_ast))

        func_defs = get_glob_def(BuildFileFunctions(build_info))
        build_ast = FunctionCallFilter(func_defs).visit(file_ast)
        build_ast = ast.fix_missing_locations(build_ast)

        code = compile(build_ast, '<string>', 'exec')
        exec(code, func_defs)

    with open(out_fpath, "w") as f:
        content = Generator.gen(path, build_info)
        f.write(content)


convert_project('D:\\Code\\')
