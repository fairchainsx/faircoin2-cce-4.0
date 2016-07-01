#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# stats.py
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

from comm import *
from decimal import *


# Error Logging

def stat_error_log(error, function_name='No function name provided'):
    currtime = time.strftime('%m-%d %H:%M:%S', time.gmtime())
    logging.basicConfig(filename=str(os.getcwd() + "/stats.log"), level=logging.ERROR)
    logging.error(currtime + ' ' + str(error) + ' : ' + str(function_name))


def main():
    try:
        # Process rich list
        lgth = int(CONFIG['stat']['richlistlen'])
        topadd = query_multi('SELECT * FROM address ORDER BY balance DESC LIMIT %s', lgth)
        for i in range(min(lgth,len(topadd))):
            ret = query_noreturn(
                'UPDATE top_address SET address = %s, balance = %s, n_tx = %s WHERE rank = %s',
                topadd[i][0], topadd[i][1], topadd[i][2], i + 1)

        # Retrieve 'getinfo' and 'getmininginfo' from coin daemon
        ret = jsonrpc('getinfo')
        if ret['Status'] == 'error':
            errstr = 'getinfo: ' + str(ret['Data'])
            raise Exception(errstr)
        else:
            getinfo = ret['Data']

        # Coins minted record. Get information from coin daemon if indicated in the configuration file.
        # If 'calc' is indicated, sum all the address balances to get the information.
        if CONFIG['stat']['mint'] == 'daemon':
            mintfield = CONFIG['stat']['mintfield']
            ret = query_noreturn('UPDATE stats SET total_mint = %s', getinfo[mintfield])
        elif CONFIG['stat']['mint'] == 'calc':
            ret = query_noreturn('UPDATE stats SET total_mint = (SELECT SUM(balance) FROM address)')

        # Daemon peer information
        ret = jsonrpc('getpeerinfo')
        if ret['Status'] == 'error':
            errstr = str('Peer info: ' + ret['Data'])
            raise Exception(errstr)
        else:
            peers = ret['Data']
        ret = query_noreturn('TRUNCATE peers')
        for row in peers:
            # Remove port information as it is not useful information.
            # Only information after the last ':' is removed to accommodate IPV6 addresses
            address = row['addr'].rsplit(':',1)[0]
            ret = query_noreturn('INSERT INTO peers (IP,version,sub, connection) VALUES(%s,%s,%s,%s)', address, row['version'],
                                 row['subver'], 'inbound' if row['inbound'] else 'outbound')
        peertxt =  json.dumps(peers, sort_keys=False, indent=1)
        ret = query_noreturn('UPDATE stats SET peers = %s, peer_txt = %s', len(peers), peertxt)

        # Daemon CVN information
        ret = jsonrpc('getactivecvns')
        if ret['Status'] == 'error':
            errstr = str('Active CVNs: ' + ret['Data'])
            raise Exception(errstr)
        else:
            cvns = ret['Data']['cvns']
        ret = query_noreturn('TRUNCATE cvnstatus')

        for row in cvns:
            ret = query_noreturn('INSERT INTO cvnstatus (nodeId,heightAdded,pubKey,predictedNextBlock,lastBlocksSigned) VALUES(%s,%s,%s,%s,%s)',
                            row['nodeId'], row['heightAdded'], row['pubKey'], row['predictedNextBlock'], row['lastBlocksSigned'])
        cvnstxt =  json.dumps(cvns, sort_keys=False, indent=1)
        ret = query_noreturn('UPDATE stats SET cvns = %s, cvn_txt = %s', len(cvns), cvnstxt)
        conn.commit()


    except Exception as e:
        stat_error_log(e, 'General stat module error')

# This module can be run independent of the database loader module.
if __name__ == '__main__':
    main()
    conn.close()
