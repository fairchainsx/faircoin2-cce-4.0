#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# dbload.py
#
# Copyright 2015 Hartland PC LLC
#
# This file is part of the  of the database loader for CCE 4.0 (open source version).
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

import sys
import stats
import traceback
from comm import *
from decimal import *


def startcheck(lockdir, recheckdir):
    # Check to see if the loader is already running and set lock file
    if os.access(os.path.expanduser(lockdir), os.F_OK):
        pidfile = open(os.path.expanduser(lockdir), "r")
        pidfile.seek(0)
        old_pid = pidfile.readline()
        if os.path.exists("/proc/%s" % old_pid):
            sys.exit(0)
        else:
            os.remove(os.path.expanduser(lockdir))
    pidfile = open(os.path.expanduser(lockdir), "w")
    pidfile.write("%s" % os.getpid())
    pidfile.close()


    # Check for recheck file
    ret = 'normal'
    if os.access(os.path.expanduser(recheckdir), os.F_OK):
        ret = 'recheck'
    else:
        checkfile = open(os.path.expanduser(recheckdir), "w")
        checkfile.close()
    return ret


# Error Logging
def loader_error_log(msg, function_name='No function name provided'):
    currtime = time.strftime('%m-%d %H:%M:%S', time.gmtime())
    logging.basicConfig(filename=str(os.getcwd() + "/loader.log"), level=logging.ERROR)
    logging.error(currtime + ' ' + str(msg) + ' : ' + str(function_name))


# Address accounting. If credit is true, amount is added to address, else amount is subtracted.
# count_tx determines if the number of transactions on an account is incremented, decremented or unchanged.
def accounting(address, amount, credit, count_tx):
    ret = query_single('SELECT balance FROM address WHERE address = %s', address)
    if ret is None:
        ret = query_noreturn('INSERT INTO address (address,balance) VALUES(%s,%s)', address, "{:.8f}".format(amount))
        conn.commit()
    else:
        if credit:
            balance = Decimal(ret[0] + amount)
        else:
            balance = Decimal(ret[0] - amount)
            if balance < 0:
                balance = Decimal(0)
        ret = query_noreturn('UPDATE address SET balance = %s WHERE address = %s', "{:.8f}".format(balance), address)
    if count_tx == 'add':
        ret = query_noreturn('UPDATE address SET n_tx = n_tx + 1 WHERE address = %s', address)
    elif count_tx == 'subtract':
        ret = query_noreturn('UPDATE address SET n_tx = abs(n_tx - 1) WHERE address = %s', address)
    conn.commit()


# Place data in table rows
def add_row(table, row_data):
    cur = conn.cursor()
    cur.execute("describe %s" % table)
    allowed_keys = set(row[0] for row in cur.fetchall())
    keys = allowed_keys.intersection(row_data)
    columns = ", ".join(keys)
    data_template = ", ".join(["%s"] * len(keys))
    sql = "insert into %s (%s) values (%s)" % (table, columns, data_template)
    data_tuple = tuple(row_data[key] for key in keys)
    cur.execute(sql, data_tuple)
    cur.close()


# Parse Transaction
def process_tx(tx, blk_height):
    jsn_decode = json.dumps(tx)
    total_out = Decimal(0)
    # Transaction addresses are stored in tx_address to determine duplicate addresses in tx_in / tx_out.
    # If a duplicate address is found, the tx count for address will only be incremented once.

    tx['tx_hash'] = tx['txid']
    add_row('tx', tx)

    tx_address = []
    for key in tx['vout']:
        hasAddresses = True if 'addresses' in key['scriptPubKey'] else False
        if hasAddresses:
            key['address'] = key['scriptPubKey']['addresses'][0]
            tx_address.append(key['address'])
        key['asm'] = key['scriptPubKey']['asm']
        key['type'] = key['scriptPubKey']['type']
        key['height'] = blk_height
        key['tx_hash'] = tx['txid']
        key['value'] = Decimal(key['value']).quantize(Decimal('1.00000000')).normalize()

        add_row('tx_out', key)

        if hasAddresses:
            # commit performed inside of accounting()
            accounting(key['address'], key['value'], True, 'add')
        else:
            conn.commit()
        total_out = Decimal(total_out + key['value'])
    # If the transaction total out is larger then the lowest entry on the large tx table,
    # replace the lowest transaction with this transaction
    low = query_single('SELECT * FROM large_tx ORDER BY amount ASC LIMIT 1')
    if low is not None and total_out > low[1]:
        ret = query_noreturn('UPDATE large_tx SET tx = %s,amount = %s WHERE tx = %s', tx['txid'], total_out,low[0])

    for key in tx['vin']:
        if 'coinbase' in key:
            key['value_in'] = total_out
        else:
            key['asm'] = key['scriptSig']['asm']
            key['hex'] = key['scriptSig']['hex']
            key['prev_out_hash'] = key['txid']
            ret = query_single('SELECT * FROM tx_out WHERE tx_hash = %s AND n = %s', key['prev_out_hash'], key['vout'])
            if not ret:
                key['address'] = 'Not Available'
                key['value_in'] = Decimal(total_out)
            else:
                count_tx = 'add'
                key['address'] = str(ret[4])
                key['value_in'] = ret[2]
                if key['address'] in tx_address:
                    count_tx = 'no'
                accounting(key['address'],key['value_in'],False,count_tx)

        key['tx_hash'] = tx['txid']
        key['height'] = blk_height
        add_row('tx_in', key)
    return {'Status': 'ok', 'Data': {'out': total_out}}


# Parse block
def process_block(blk_height):
        if blk_height == -1:
            raise Exception('Bad block height (-1)')
        counter = 0
        total_sent = Decimal(0)
        b_hash = jsonrpc("getblockhash", blk_height)['Data']
        block = jsonrpc("getblock", b_hash, 5)['Data']

        for key in block['tx']:
            prostx = process_tx(key, blk_height)
            if prostx['Status'] == 'error':
                raise Exception(prostx['Data'])
            total_sent = Decimal(total_sent + prostx['Data']['out'])

        add_row('block', block)

        for sig in block['signatures']:
            ret = query_noreturn('INSERT INTO signatures (height,version,signerId,signature) VALUES(%s,%s,%s,%s)', blk_height, sig['version'], sig['signerId'], sig['signature'])

        for sig in block['adminSignatures']:
            ret = query_noreturn('INSERT INTO adminSignatures (height,version,adminId,signature) VALUES(%s,%s,%s,%s)', blk_height, sig['version'], sig['adminId'], sig['signature'])

        for cvn in block['cvnInfo']:
            cvn['height'] = blk_height
            add_row('cvn', cvn)

        for admin in block['chainAdmins']:
            admin['height'] = blk_height
            add_row('chainAdmin', admin)

        if block['chainParameters']:
            cp = block['chainParameters']
            cp['height'] = blk_height
            add_row('chainParameter', cp)

        conn.commit()
        ret = query_noreturn('UPDATE block SET total_sent = %s, n_tx = %s WHERE height = %s',
                             total_sent, len(block['tx']), blk_height)
        conn.commit()
        return {'Status':'ok'}


# Orphan correction. Copy to orphan tables,delete block/tx information, and re-parse block.
# If recheck is true, block/tx information is not copied to orphan tables.
def orphan(blk_height, recheck=False):
    try:
        if not recheck:
            loader_error_log("Orphan routine called", blk_height)
            ret = query_noreturn('INSERT INTO orph_block SELECT * FROM block WHERE height = %s', blk_height)
            ret = query_noreturn('INSERT INTO orph_tx_raw SELECT * FROM tx_raw WHERE height = %s', blk_height)
        ret = query_noreturn('DELETE FROM block WHERE height = %s', blk_height)
        ret = query_noreturn('DELETE FROM tx_raw WHERE height = %s', blk_height)
        txin = query_multi('SELECT * FROM tx_in WHERE height = %s', blk_height)
        for key in txin:
            if key[7] != '0':
                accounting(str(key[7]),key[6], True,'subtract')
        txout = query_multi('SELECT * FROM tx_out WHERE height = %s', blk_height)
        for key in txout:
            accounting(str(key[4]),key[2], False,'subtract')
        if not recheck:
            ret = query_noreturn('INSERT INTO orph_tx_in SELECT * FROM tx_in WHERE height = %s', blk_height)
            ret = query_noreturn('INSERT INTO orph_tx_out SELECT * FROM tx_out WHERE height = %s', blk_height)
            ret = query_noreturn('INSERT INTO orph_tx_raw SELECT * FROM tx_raw WHERE height = %s', blk_height)
        ret = query_noreturn('DELETE FROM tx_in WHERE height = %s', blk_height)
        ret = query_noreturn('DELETE FROM tx_out WHERE height = %s', blk_height)
        ret = query_noreturn('DELETE FROM tx_raw WHERE height = %s', blk_height)
        ret = process_block(blk_height)
        if ret['status'] == 'error':
            raise Exception(ret['Data'])
        conn.commit()
    except Exception as e:
        loader_error_log(e, "Orphan loop error")
        conn.rollback()
    if not recheck:
        loader_error_log('Successful orphan recovery: ', str(blk_height))


def main(argv):
    lockdir = str(os.getcwd() + "/" + "dataload.lock")
    recheckdir = str(os.getcwd() + "/" + "recheck")
    startmode = startcheck(lockdir, recheckdir)
    verbose = False
    doWait = True
    # Set cowtime (loader timeout) to 5 minutes
    cowtime = 60 * 5
    try:
        for opt in argv:
            # Set new database mode and cowtime to 24 hours if  -n flag
            if opt == '-n':
                startmode = 'newdb'
                cowtime = 60 * 60 * 24
            # Run recheck if -r flag
            elif opt == '-r' and startmode != 'newdb':
                startmode = 'recheck'
            # Send verbose messages to stderr if -v flag
            elif opt == '-v':
                verbose = True
            # Wait
            elif opt == '-w':
                doWait = False
            # Set cowtime to 24 hours if -l flag
            elif opt == '-l':
                cowtime = 60 * 60 * 24
    except:
        pass
    try:
        with timeout(cowtime, exception=Exception('DBLoader Timeout')):
            # Get block heights
            daemon = jsonrpc("getblockcount")
            if daemon['Status'] != 'error':
                top_height = daemon['Data']
                blk_height = query_single('SELECT height FROM block ORDER BY height DESC LIMIT 1')
                if not blk_height:
                    blk_height = 1
                else:
                    blk_height = int(blk_height[0] + 1)
            else:
                loader_error_log(daemon['Data'], 'Get Block Height')
                raise Exception(daemon['Data'])

            # Sleep is needed to allow the daemon time to catch orphans
            if startmode != 'newdb' and doWait:
                time.sleep(3)

            # Recheck mode, re-parse the last 5 blocks in the database
            if startmode == 'recheck' and blk_height > 5:
                if verbose:
                    print >> sys.stderr, "Recheck Called"
                for blk in range(blk_height - 5, blk_height):
                    orphan(blk, True)

            # Check last (blockcheck) blocks for orphans and fix if needed
            blockcheck = int(CONFIG["loader"]["blockcheck"])
            if blk_height > blockcheck:
                for blk in range(blk_height - blockcheck, blk_height):
                    d_hash = jsonrpc('getblockhash', blk)
                    db_hash = query_single('SELECT hash FROM block where height = %s', blk)[0]
                    if d_hash['Data'] != db_hash:
                        orphan(blk)


            if startmode == 'newdb':
                # Set up top_address table
                for i in range(int(CONFIG['stat']['richlistlen'])):
                    ret = query_noreturn('INSERT INTO top_address (rank) VALUES(%s)', i + 1)
                # Set up stats table
                ret = query_noreturn('INSERT INTO stats (peer_txt) VALUES("None")')
                blk_height = 0

            # Process blocks loop
            while blk_height <= top_height:
                ret = process_block(blk_height)
                if ret['Status'] == 'error':
                    raise Exception(ret['Data'])
                if startmode == 'newdb' and blk_height == 101:
                    ret = query_noreturn('TRUNCATE large_tx')
                    time.sleep(1)
                    ret = query_noreturn('INSERT INTO large_tx SELECT tx_hash,SUM(value) FROM tx_out GROUP BY tx_hash ORDER BY SUM(value) DESC LIMIT 100')
                blk_height += 1
                if verbose:
                    print >> sys.stderr, 'Processing Block: ', blk_height, ' of ', top_height, '\r',


            # Call Statistics module
            if CONFIG['loader']['stats'] == 'true':
                if verbose:
                    print >> sys.stderr, '\nCalling Statistics Module'
                stats.main()


    except Exception as e:
        print "Exception in user code:"
        print '-'*60
        traceback.print_exc(file=sys.stdout)
        print '-'*60

        loader_error_log(str(e), 'Main loop')
        conn.close()
        os.remove(os.path.expanduser(lockdir))
        if verbose:
            print >> sys.stderr, '\nMain Loop', str(e)
        sys.exit(0)

    # Clean up
    conn.close()
    if verbose:
        print >> sys.stderr, "Database load complete"
    os.remove(os.path.expanduser(recheckdir))
    os.remove(os.path.expanduser(lockdir))

if __name__ == '__main__':
    main(sys.argv[1:])
