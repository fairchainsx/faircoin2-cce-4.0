#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# websrv.py
#
# Copyright 2015 Hartland PC LLC
#
# This file is part of the open source version of CCE 4.0.
#
# This package is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This package is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this package.  If not, see <http://www.gnu.org/licenses/>.

import os
import cherrypy
import jinja2
import simplejson as json
from cherrypy.process.plugins import Daemonizer
from cherrypy.process.plugins import PIDFile
from serverutil import *

# Set up log and pid file. Run the server as a daemon.
pid = str(os.getcwd() + "/cherrypy.pid")
log = str(os.getcwd() + "/server.log")
Daemonizer(cherrypy.engine, stderr=log).subscribe()
PIDFile(cherrypy.engine, pid).subscribe()

# Set up jinja2 environment and filters that point to functions in serverutil.py.
templateLoader = jinja2.FileSystemLoader(searchpath=str(os.getcwd() + '/html/'))
templateEnv = jinja2.Environment(loader=templateLoader)
templateEnv.filters['format_time'] = format_time
templateEnv.filters['format_hour'] = format_hour
templateEnv.filters['time_passed'] = time_passed
templateEnv.filters['normalize'] = normalize


class explorer:
    @cherrypy.expose
    def index(self, **args):
        try:
            num, height, ret = homepage(args.get('num', 10), args.get('height', None))
            stats = ret.get('stats', None)
            topblocks = ret.get('topblocks', None)
            template = templateEnv.get_template('index.html')
            templateVars = {
                'stats': stats,
                'topblocks': topblocks,
                'name': CONFIG['chain']['name'],
                'ratelabel': CONFIG['stat']['ratelabel'],
                'numberOfBlocks': num,
                'nextPage': height + num,
                'prevPage': height - num,
                'navItem': 'home'
            }
            return template.render(templateVars)
        except Exception as e:
            sys.stderr.write(e+ 'Homepage')
            raise cherrypy.HTTPError(503)



    @cherrypy.expose
    def block(self, **args):
        try:
            if args:
                arg = args.get('block', '-1')
                blk = get_block(arg)
            else:
                blk = get_block('-1')
            template = templateEnv.get_template('block.html')
            templateVars = {
                "block": blk,
                "name": CONFIG['chain']['name']
            }
            return template.render(templateVars)
        except Exception as e:
            sys.stderr.write(e+ 'Block page')
            raise cherrypy.HTTPError(503)

    @cherrypy.expose
    def search(self, **args):
        stype = search_type(args['sterm'])
        if stype['Status'] == 'ok':
            raise cherrypy.HTTPRedirect(stype['Data'])
        else:
            template = templateEnv.get_template('search.html')
            templateVars = {
                'name': CONFIG['chain']['name']
                    }
            return template.render(templateVars)

    @cherrypy.expose
    def peers(self, **args):
        try:
            peerinfo = get_peerinfo()
            template = templateEnv.get_template('peers.html')
            templateVars = {
                    'peerinfo': peerinfo,
                    'name': CONFIG['chain']['name'],
                    'navItem': 'peers'
                        }
            return template.render(templateVars)
        except Exception as e:
            sys.stderr.write(e+ 'Peer page')
            raise cherrypy.HTTPError(503)

    @cherrypy.expose
    def rich(self, **args):
        try:
            rich = get_rich()
            template = templateEnv.get_template('rich.html')
            templateVars = {
                    'rich': rich,
                    'name': CONFIG['chain']['name'],
                    'navItem': 'rich'
                        }
            return template.render(templateVars)
        except Exception as e:
            sys.stderr.write(e+ 'Rich page')
            raise cherrypy.HTTPError(503)

    @cherrypy.expose
    def activecvns(self, **args):
        try:
            cvns = get_active_cvns()
            template = templateEnv.get_template('cvns.html')
            templateVars = {
                    'cvns': cvns,
                    'name': CONFIG['chain']['name'],
                    'navItem': 'activecvns'
                        }
            return template.render(templateVars)
        except Exception as e:
            sys.stderr.write(e+ 'Cvns page')
            raise cherrypy.HTTPError(503)

    @cherrypy.expose
    def cvnstats(self, **args):
        try:
            stats = get_cvn_stats()
            template = templateEnv.get_template('cvnstats.html')
            templateVars = {
                    'stats': stats,
                    'name': CONFIG['chain']['name'],
                    'navItem': 'cvnstats'
                        }
            return template.render(templateVars)
        except Exception as e:
            sys.stderr.write(e+ 'Cvn stats page')
            raise cherrypy.HTTPError(503)

    @cherrypy.expose
    def blocks(self, **args):
        try:
            list_type = args.get('block_type', 0)
            blocks, payload = get_blocks(list_type)
            template = templateEnv.get_template('blocks.html')
            templateVars = {
                    'blocks': blocks,
                    'name': CONFIG['chain']['name'],
                    'payload': payload,
                    'navItem': list_type
                        }
            return template.render(templateVars)
        except Exception as e:
            sys.stderr.write(e+ 'Blocks page')
            raise cherrypy.HTTPError(503)

    @cherrypy.expose
    def transaction(self, **args):
        try:
            transaction = get_transaction(args['transaction'])
            template = templateEnv.get_template('transaction.html')
            templateVars = {
                    'transaction': transaction,
                    'name': CONFIG['chain']['name']
                        }
            return template.render(templateVars)
        except Exception as e:
            sys.stderr.write(e+ 'Transaction page')
            raise cherrypy.HTTPError(503)


    @cherrypy.expose
    def address(self, **args):
        try:
            address = get_address(args['address'])
            template = templateEnv.get_template('address.html')
            templateVars = {
                    'address': address,
                    'name': CONFIG['chain']['name']
                        }
            return template.render(templateVars)
        except Exception as e:
            sys.stderr.write(e+ 'Address page')
            raise cherrypy.HTTPError(503)

    @cherrypy.expose
    def largetx(self, **args):
        try:
            largetx = get_largetx()
            template = templateEnv.get_template('largetx.html')
            templateVars = {
                    'largetx': largetx,
                    'name': CONFIG['chain']['name'],
                    'navItem': 'largetx'
                        }
            return template.render(templateVars)
        except Exception as e:
            sys.stderr.write(e+ 'Large TX page')
            raise cherrypy.HTTPError(503)

    # Explorer API. Simple commands are queried directly. More complex returns should use functions coded into serverutil.py.
    @cherrypy.expose
    def api(self, command, **args):
        try:
            if command == 'difficulty':
                diff_q = query_single('SELECT curr_diff FROM stats')
                difficulty = {'difficulty': diff_q[0]}
                return json.dumps(difficulty)
            elif command == 'totalmint':
                total_m = query_single('SELECT total_mint FROM stats')
                minted = {'total minted': total_m[0]}
                return json.dumps(minted)
            elif command == 'getsigs':
                if args.get('adm', 'False') == 'False':
                    signatures = query_multi(
                        "SELECT s.signerId, s.signature,a.alias FROM signatures s "
                        "LEFT JOIN cvnalias a on s.signerId = a.nodeId "
                        "where s.height = %s",
                        args.get('block', '-1'))
                else:
                    signatures = query_multi(
                        "SELECT s.adminId, s.signature, a.alias FROM adminSignatures s "
                        "LEFT JOIN cvnalias a on s.adminId = a.nodeId "
                        "where height = %s",
                        args.get('block', '-1'))
                data = []
                if signatures:
                    for row in signatures:
                        data.append({'signer': row[0], 'sig': row[1], 'alias': row[2]})
                else:
                    data.append({'signer': 'no data', 'sig': 'available'})
                return json.dumps(data)
            return json.dumps({'error':'invalid'})
        except Exception:
            raise cherrypy.HTTPError(503)

if __name__ == '__main__':
    cherrypy.quickstart(root=explorer(), config="../server.conf")
