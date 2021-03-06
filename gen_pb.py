#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function

import datetime
import time
import subprocess
import logging
import json
import os
import argparse


class Generator:
    def __init__(self):
        self._pb_ext = '.proto'
        self._dir = os.getcwd()
        self._pb_exec = 'protoc'
        self._force = False
        self._show_syntax_missing_warning = True
        self._conf_path = None
        self._conf = {}
        self._target_conf = {}
        self._has_err = False

    def gen(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-b', '--base_dir', help='base dir for pb. default: CURRENT_DIR')
        parser.add_argument('-d', '--pb_dir', help='base dir containing .proto files. default: base_dir')
        parser.add_argument('-t', '--target', help='single target name')
        parser.add_argument('-f', '--force', help='force generation', action='store_true', default=False)
        parser.add_argument('--protoc', help='protoc path. default protoc')
        parser.add_argument('--show-syntax-missing-warning', help='show syntax missing warning of protoc', action='store_true', default=False)
        parser.add_argument("--log-level", default=logging.INFO, help="cjonfigure the logging level. default: INFO", type=lambda x: getattr(logging, x))
        parser.add_argument('--conf-file', help='config file path. default base_dir/gen_pb.conf')
        args = parser.parse_args()

        if args.base_dir:
            self._dir = args.base_dir

        if args.protoc:
            self._pb_exec = args.protoc

        self._force = args.force
        self._show_syntax_missing_warning = args.show_syntax_missing_warning

        if args.conf_file:
            self._conf_path = args.conf_file
        else:
            self._conf_path = os.path.join(self._dir, 'gen_pb.conf')
        self._conf_path = os.path.abspath(self._conf_path)

        logging.basicConfig(
            level=args.log_level,
            format='[%(asctime)s] [%(levelname)s] %(message)s'
        )

        logging.debug('Config file: ' + self._conf_path)
        self._read_config()

        if args.target:
            self._gen_target(args.target)
        elif args.pb_dir:
            self._gen_dir(args.pb_dir)
        else:
            self._gen_dir(self._dir)

        self._write_config()
        logging.info('Generation finished')
        if self._has_err:
            logging.error('*** *** Some error occurred, please check log! *** ***')

    def _gen_target(self, target):
        logging.info("Generating target... %s", target)

        if target not in self._target_conf:
            raise RuntimeError('Target not found: ' + target)

        target_conf = self._target_conf[target]
        for rel_path in target_conf:
            self._do_gen(rel_path)

    def _gen_dir(self, path):
        logging.info("Generating dir... %s", path)

        for root, subdirs, files in os.walk(path):
            for f in files:
                if not f.endswith(self._pb_ext):
                    continue

                f_path = os.path.normpath(os.path.join(root, f))
                if self._check_need_gen(f_path):
                    self._do_gen(f_path)

    def _check_need_gen(self, f_path):
        if self._force:
            return True

        # check need override
        target_key = self._get_target_key(f_path)
        rel_path = os.path.relpath(f_path, self._dir)
        try:
            last_gen_time = self._target_conf[target_key][rel_path]
            if not last_gen_time:
                return True

            last_gen_time = time.mktime(time.strptime(last_gen_time, '%Y-%m-%d %H:%M:%S'))

            mod_time = os.stat(f_path).st_mtime
            if mod_time > last_gen_time:
                return True

            logging.debug('file not update, ignore: %s', f_path)
            return False
        except KeyError:
            return True
        except ValueError as e:
            logging.error('Value error when check need gen: %s', f_path)
            self._has_err = True
            return True

    def _do_gen(self, pb_path):
        if not os.path.isabs(pb_path):
            pb_path = os.path.normpath(os.path.join(self._dir, pb_path))
        logging.info("Generate proto: %s", pb_path)

        if not os.path.isfile(pb_path):
            logging.error('proto file not found: %s', pb_path)
            self._has_err = True
            return

        gen_cmd = [
            self._pb_exec,
            '-I', self._dir,
            '--cpp_out', self._dir,
            pb_path
        ]

        logging.debug('gen_cmd: %s', str(gen_cmd))
        ret = 0
        try:
            output = subprocess.check_output(gen_cmd, shell=False, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            output = e.output
            ret = e.returncode

        for line in output.split('\n'):
            if not line:
                continue
            if not self._show_syntax_missing_warning:
                if line.find('No syntax specified for the proto file') != -1:
                    continue
            logging.info('protoc output: ' + line)

        target_key = self._get_target_key(pb_path)
        rel_path = os.path.relpath(pb_path, self._dir)
        cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if ret == 0:
            logging.debug('gen pb succ: %s', pb_path)
            self._strip_gened_files(pb_path, cur_time)
            self._target_conf.setdefault(target_key, {})[rel_path] = cur_time
        else:
            self._target_conf.setdefault(target_key, {})[rel_path] = ''
            logging.error('gen pb failed')
            self._has_err = True

    def _strip_gened_files(self, pb_path, gen_time):
        # remove extension
        if pb_path.endswith(self._pb_ext):
            pb_path = pb_path[:-len(self._pb_ext)]

        # remove xxx.pb.cc file
        cpp_path = pb_path + '.pb.cc'
        os.remove(cpp_path)

        # remove inline content in xxx.pb.h
        hpp_path = pb_path + '.pb.h'
        with open(hpp_path, 'r+') as f:
            content = f.readlines()
            out = []
            out.append('// -------------------------- This File has striped by gen_pb.py ------------------- \n')
            out.append('// ' + gen_time + '\n')
            out.append('// --------------------------------------------------------------------------------- \n')
            out.append('\n')
            it = iter(content)

            def get_pp_cmd(str):
                str = str.lstrip()
                if not str:
                    return None
                if str[0] != '#':
                    return None

                str = str[1:6].upper()
                if str.startswith('IF'):
                    # #if, #ifdef, #ifndef
                    return 'IF'

                if str.startswith('ENDIF'):
                    return 'ENDIF'

                return None

            # find #if !PROTOBUF_INLINE_NOT_IN_HEADERS
            unmatch = 0  # count of unmatched #if
            while True:
                try:
                    line = next(it)
                    out.append(line)
                    if get_pp_cmd(line) == 'IF':
                        if line.find('PROTOBUF_INLINE_NOT_IN_HEADERS') != -1:
                            unmatch = 1
                            break

                except StopIteration:
                    break

            # skip #if def
            line = None
            while unmatch > 0:
                try:
                    line = next(it)
                    cmd = get_pp_cmd(line)
                    if cmd == 'IF':
                        unmatch += 1
                    elif cmd == 'ENDIF':
                        unmatch -= 1
                    else:
                        continue
                except StopIteration:
                    break

            if line:
                out.append(line)

            # read to end
            while True:
                try:
                    line = next(it)
                    out.append(line)
                except StopIteration:
                    break

            # save
            f.seek(0)
            f.truncate(0)
            f.writelines(out)

    def _get_target_key(self, path):
        file_name = os.path.basename(path)
        # remove extension
        if file_name.endswith(self._pb_ext):
            file_name = file_name[:-len(self._pb_ext)]
        return file_name

    def _read_config(self):
        conf_path = self._conf_path
        self._conf = {}
        if os.path.exists(conf_path):
            with open(conf_path, 'r') as f:
                content = f.read()
                self._conf = json.loads(content)

        self._target_conf = self._conf.get('target', {})

    def _write_config(self):
        conf_path = self._conf_path
        with open(conf_path, 'w') as f:
            self._conf['target'] = self._target_conf
            content = json.dumps(self._conf, indent=4)
            f.write(content)
            logging.info('Write config done: %s', conf_path)


if __name__ == '__main__':
    Generator().gen()
