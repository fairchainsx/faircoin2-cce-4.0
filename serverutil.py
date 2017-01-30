#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# utility.py
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


import sys
import time
import ConfigParser
import re
import pymysql
from DBUtils.PooledDB import PooledDB
from decimal import *
from collections import OrderedDict


# Configuration file reader
config_parse = ConfigParser.ConfigParser()
config_parse.read('cce.conf')
CONFIG = {section: {option: config_parse.get(section, option) for option in config_parse.options(section)} for section
          in config_parse.sections()}
URL = str('http://' + CONFIG["coind"]["rpcuser"] + ':' + CONFIG["coind"]["rpcpass"] + '@' + CONFIG["coind"]["rpchost"] + ':' + CONFIG["coind"][
    "rpcport"])

pool = PooledDB(pymysql, 50, db=CONFIG['database']['dbname'], host=CONFIG['database']['mysqlip'], port=int(CONFIG['database']['mysqlport']),
                user=CONFIG['database']['dbuser'],
                passwd=CONFIG['database']['dbpassword'], use_unicode=True, charset="utf8",
                setsession=['SET AUTOCOMMIT = 1'])

# Convert Unix timestamp to date/time
def format_time(nTime):
    try:

        return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(nTime)))
    except:
        return "???"


# Convert Unix timestamp to time only
def format_hour(nTime):
    try:

        return time.strftime('%H:%M:%S', time.gmtime(int(nTime)))
    except:
        return "???"


# Calculate time passed from block timestamp to server time.
def time_passed(nTime):
    try:
        seconds = int(time.time()) - nTime
        if seconds < 0:
            # Block is time is ahead of server time. Three examples of a response are shown.
            # return str(abs(seconds)) + ' seconds in the future')
            # return str('0 minutes 0 seconds')
            return str('Ahead of server time')
        elif seconds < 60:
            return str(seconds) + ' seconds'
        else:
            minutes = int(seconds / 60)
            if minutes == 1:
                seconds = int(seconds % 60)
                return str(minutes) + ' minute ' + str(seconds) + ' seconds'
            else:
                return str(minutes) + ' minutes'
    except:
        return format_hour(nTime)


# Trim excess zeros in a decimal
def normalize(n):
    try:
        num = Decimal(n).normalize()
        ret = num.__trunc__() if not num % 1 else Decimal(num)
        return ret
    except:
        return n


# The next three functions are database query handlers.
# Each one will get a connection from the pool and release it after the query is finished.
def query_single(sql, *parms):
    try:
        db = pool.connection(shareable=False)
        cur = db.cursor()
        cur.execute(sql, parms)
        ret = cur.fetchone()
        cur.close()
        db.close()
        return ret
    except Exception as e:
        print >> sys.stderr, e, str('query_single: ' + sql)
        cur.close()
        db.close()
        return None


def query_multi(sql, *parms):
    try:
        db = pool.connection(shareable=False)
        cur = db.cursor()
        cur.execute(sql, parms)
        ret = cur.fetchall()
        cur.close()
        db.close()
        return ret
    except Exception as e:
        print >> sys.stderr, e, str('query_multi: ' + sql)
        cur.close()
        db.close()
        return None


def query_noreturn(sql, *parms):
    try:
        db = pool.connection(shareable=False)
        cur = db.cursor()
        ret = cur.execute(sql, parms)
        cur.close()
        db.close()
        return ret
    except Exception as e:
        print >> sys.stderr, e, str('query_noreturn: ' + sql)
        cur.close()
        db.close()
        return None


def homepage(num, height):
    try:
        if num is None:
            num = 25
        else:
            num = int(num)
            if num > 100:
                num = 100

        stats = query_single('SELECT * FROM stats')
        base_query = """select b.*,a.alias, GROUP_CONCAT(m.nodeId) missing from block b 
            LEFT JOIN cvnalias a on a.nodeId = b.creator 
            LEFT JOIN missingCreatorIds m on m.height = b.height """
        if height is None:
            topblocks = query_multi(base_query + 'GROUP BY b.height ORDER BY height DESC LIMIT %s', num)
            height = topblocks[0][0];
        else:
            topblocks = query_multi(base_query + 'WHERE b.height <= %s GROUP BY b.height ORDER BY height DESC LIMIT %s', height, num)

        return num, int(height), {'Status': 'ok', 'stats': stats, 'topblocks': topblocks}
    except Exception as e:
        print >> sys.stderr, e, 'Homepage'
        return {'Status': 'error', 'Data': 'Unknown error'}

def get_blocks(block_type):
    try:
        if block_type is None:
            block_type = 0

        payload = "cvninfo"
        if block_type == 'params':
            payload = "params"
        elif block_type == 'admins':
            payload = "admins"

        blocks = query_multi('SELECT b.*,a.alias, count(m.height) n FROM block b LEFT JOIN cvnalias a on a.nodeId = b.creator LEFT JOIN missingCreatorIds m on m.height = b.height WHERE b.payload LIKE %s GROUP BY b.height ORDER BY height DESC', ('%' + payload + '%'))

        return {'Status': 'ok', 'blocks': blocks}, payload
    except Exception as e:
        print >> sys.stderr, e, 'get_blocks'
        return {'Status': 'error', 'Data': 'Unknown error'}



# Regular expression:  re.sub(r'[^a-zA-Z0-9]', '', <input string>)
# The expression is used to filter out all but alpha-numeric charcters from user input.
# This serves a security function and cuts spaces which can causes searches to fail.
def search_type(sterm):
    try:
        sterm = str(re.sub(r'[^a-zA-Z0-9]', '', sterm))
        if sterm.isdigit():
            ret = query_single('SELECT * FROM block WHERE height = %s', sterm)
        else:
            ret = query_single('SELECT * FROM block WHERE hash = %s', sterm)
        if ret is None:
            ret = query_single('SELECT * FROM tx_out WHERE tx_hash = %s', sterm)
            if ret is None:
                ret = query_single('SELECT * FROM address WHERE address = %s', sterm)
                if ret is None:
                    raise Exception
                else:
                    return {'Status': 'ok', 'Data': '/address?address=' + sterm}
            else:
                return {'Status': 'ok', 'Data': '/transaction?transaction=' + sterm}
        else:
            return {'Status': 'ok', 'Data': '/block?block=' + sterm}
    except:
        return {'Status': 'error', 'Data': 'Not Found'}


# Block page generation is separated into 2 functions due to the complexity of the generating the block transaction display.
# These two functions could be combined, but at the cost of reduced readability.
# The unique function of the coinbase transaction in both POW and POS blocks, coupled with the generation aspect
# of the second transaction in POS blocks, makes this level of complexity necessary.

# The get coinbase function parses out the first tx in all blocks and the second TX in POS blocks.
def get_coinbase(height):
    try:
        base_txin = {}
        base_txout = {}
        tx_hash = query_single('SELECT tx_hash FROM tx_in WHERE coinbase != "0" AND height = %s', height)[0]
        base_txin['PoC Fees'] = query_single('SELECT value_in FROM tx_in WHERE coinbase != "0" AND height = %s', height)[0]
        coinbase_out = query_multi('SELECT address,value FROM tx_out WHERE tx_hash = %s', tx_hash)
        for outrow in coinbase_out:
            if outrow[0] != 'Unknown':
                if outrow[0] in base_txout:
                    base_txout[outrow[0]] = Decimal(base_txout[outrow[0]] + outrow[1])
                else:
                    base_txout[outrow[0]] = outrow[1]
        transactions[tx_hash] = {'txin': base_txin, 'txout': base_txout}
    except Exception as e:
        raise Exception('Coinbase Function : ' + str(e))


def get_block(block):
    try:
        if block == '-1':
            blk = query_single('SELECT b.*,GROUP_CONCAT(m.nodeId) missing, count(m.height) n FROM block b LEFT JOIN missingCreatorIds m on m.height = b.height ORDER BY b.height DESC LIMIT 1')
        elif str(block).isdigit():
            blk = query_single('SELECT b.*,GROUP_CONCAT(m.nodeId) missing, count(m.height) n FROM block b LEFT JOIN missingCreatorIds m on m.height = b.height WHERE b.height = %s', block)
        else:
            block = str(re.sub(r'[^a-zA-Z0-9]', '', block))
            blk = query_single('SELECT b.*,GROUP_CONCAT(m.nodeId) missing, count(m.height) n FROM block b LEFT JOIN missingCreatorIds m on m.height = b.height WHERE b.hash = %s', block)

        if blk is None:
            raise Exception('Block not found')

        creatorAlias = query_single('SELECT alias FROM cvnalias WHERE nodeId = %s', blk[3])

        # The return dict is global to simplify the two function nature of the block page display generation.
        global transactions
        transactions = OrderedDict()
        get_coinbase(blk[0])
        temp_txin = {}
        temp_txout = {}
        # Only get hashes of transactions that are not related to coinbase as those are parsed by get_coinbase
        txhash = query_multi('SELECT tx_hash FROM tx_in WHERE height = %s AND coinbase = "0" GROUP BY tx_hash', blk[0])
        # txhash will be None if only coinbase transactions exist in the block
        if txhash:
            for row in txhash:
                txin = query_multi('SELECT address,value_in FROM tx_in WHERE tx_hash = %s', row[0])
                for inrow in txin:
                    # Unknown addresses are from non-standard transactions that have no value with the exception
                    # of coinbase which is handled in the get_coinbase function.
                    if inrow[0] != 'Unknown':
                        # If address already exists in this transaction, add to the address current value.
                        # This is to avoid long lists of the same address with multiple tx_in values.
                        # The same process is used below with txout.
                        if inrow[0] in temp_txin:
                            temp_txin[inrow[0]] = Decimal(temp_txin[inrow[0]] + inrow[1])
                        else:
                            temp_txin[inrow[0]] = inrow[1]
                txout = query_multi('SELECT address,value FROM tx_out WHERE tx_hash = %s', row[0])
                for outrow in txout:
                    if outrow[0] != 'Unknown':
                        if outrow[0] in temp_txout:
                            temp_txout[outrow[0]] = Decimal(temp_txout[outrow[0]] + outrow[1])
                        else:
                            temp_txout[outrow[0]] = outrow[1]

                transactions[row[0]] = {'txin': temp_txin, 'txout': temp_txout}
                temp_txin = {}
                temp_txout = {}

        cvns = []

        cvnrows = query_multi('SELECT c.nodeId, c.heightAdded, c.pubKey, a.alias FROM cvn c LEFT JOIN cvnalias a on a.nodeId = c.nodeId WHERE c.height = %s ORDER BY c.heightAdded', blk[0])
        if cvnrows:
            for row in cvnrows:
                cvns.append({'nodeId': row[0], 'heightAdded': row[1], 'pubKey': row[2] , 'alias': row[3]})

        chainAdmins = []

        chainAdminrows = query_multi('SELECT c.adminId, c.heightAdded, c.pubKey, a.alias FROM chainAdmin c LEFT JOIN cvnalias a on a.nodeId = c.adminId WHERE c.height = %s ORDER BY c.heightAdded', blk[0])
        if chainAdminrows:
            for row in chainAdminrows:
                chainAdmins.append({'adminId': row[0], 'heightAdded': row[1], 'pubKey': row[2] , 'alias': row[3]})

        chainParameter = {}
        params = query_single('SELECT version,minAdminSigs,maxAdminSigs,blockSpacing,blockSpacingGracePeriod,transactionFee,dustThreshold,minSuccessiveSignatures,blocksToConsiderForSigCheck,percentageOfSignaturesMean,maxBlockSize FROM chainParameter WHERE height = %s', blk[0])

        if params:
            chainParameter['version'] = params[0]
            chainParameter['minAdminSigs'] = params[1]
            chainParameter['maxAdminSigs'] = params[2]
            chainParameter['blockSpacing'] = params[3]
            chainParameter['blockSpacingGracePeriod'] = params[4]
            chainParameter['transactionFee'] = params[5]
            chainParameter['dustThreshold'] = params[6]
            chainParameter['minSuccessiveSignatures'] = params[7]
            chainParameter['blocksToConsiderForSigCheck'] = params[8]
            chainParameter['percentageOfSignaturesMean'] = params[9]
            chainParameter['maxBlockSize'] = params[10]

        return {'Status': 'ok', 'blk': blk, 'transactions': transactions, 'cvns': cvns, 'chainParameter': chainParameter, 'realVersion': (blk[11] & 0xff), 'creatorAlias': creatorAlias, 'chainAdmins': chainAdmins}
    except Exception as e:
        print >> sys.stderr, e, 'Block Page'
        return {'Status': 'error', 'Data': 'Block not found'}


def get_transaction(transaction):
    try:
        transaction = str(re.sub(r'[^a-zA-Z0-9]', '', transaction))
        txin = query_multi('SELECT * FROM tx_in WHERE tx_hash = %s', transaction)
        txout = query_multi('SELECT * FROM tx_out WHERE tx_hash = %s', transaction)
        tx = query_single('SELECT * FROM tx WHERE tx_hash = %s', transaction)
        if txin is None or txout is None or tx is None:
            return {'Status': 'error', 'Data': 'Transaction not found'}
        blk = query_single('SELECT b.*, 0 as size FROM block b WHERE b.height = %s', txout[0][6])
        return {'Status': 'ok', 'blk': blk, 'txin': txin, 'txout': txout, 'tx': tx}
    except Exception as e:
        print >> sys.stderr, e, 'Transactions'
        return {'Status': 'error', 'Data': 'Unknown error'}


def get_peerinfo():
    try:
        peerinfo = query_multi('SELECT * FROM peers')
        if peerinfo is None:
            return {'Status': 'error', 'Data': 'Not Found'}
        else:
            return {'Status': 'ok', 'Data': peerinfo}

    except Exception as e:
        print >> sys.stderr, e, 'Peerinfo'
        return {'Status': 'error', 'Data': 'Unknown error'}


def get_rich():
    try:
        rich = query_multi('SELECT * FROM top_address ORDER BY rank ASC')
        if rich is None:
            return {'Status': 'error', 'Data': 'Not Found'}
        else:
            return {'Status': 'OK', 'Data': rich}

    except Exception as e:
        print >> sys.stderr, e, 'Rich List'
        return {'Status': 'error', 'Data': 'Unknown error'}


def get_active_cvns():
    try:
        cvns = query_multi(
                    'SELECT s.nodeId, s.heightAdded, s.pubKey, s.predictedNextBlock, s.lastBlocksSigned, a.alias FROM cvnstatus as s '
                    'LEFT JOIN cvnalias as a on a.nodeId = s.nodeId '
                    'ORDER BY s.predictedNextBlock')
        if cvns is None:
            return {'Status': 'error', 'Data': 'Not Found'}
        else:
            return {'Status': 'OK', 'Data': cvns}

    except Exception as e:
        print >> sys.stderr, e, 'Active CVNs List'
        return {'Status': 'error', 'Data': 'Unknown error'}


def get_largetx():
    try:
        largetx = query_multi('SELECT * FROM large_tx ORDER BY amount DESC')
        if largetx is None:
            return {'Status': 'error', 'Data': 'Not Found'}
        else:
            return {'Status': 'OK', 'Data': largetx}

    except Exception as e:
        print >> sys.stderr, e, 'Large TX'
        return {'Status': 'error', 'Data': 'Unknown error'}


def get_address(address):
    try:
        address = str(re.sub(r'[^a-zA-Z0-9]', '', address))
        balance = query_single('SELECT balance FROM address WHERE address = %s', address)
        if balance is None:
            return {'Status': 'error', 'Data': 'Unknown error'}
        txin = []
        txout = []
        retxin = query_multi('SELECT * FROM tx_in WHERE address = %s ORDER BY height DESC LIMIT 100', address)
        retxout = query_multi('SELECT * FROM tx_out WHERE address = %s ORDER BY height DESC LIMIT 100', address)
        if retxin:
            for row in retxin:
                txtime = format_time(int(query_single('SELECT time FROM block WHERE height = %s', row[8])[0]))
                txin += [[txtime, row[0], row[6]]]
        for row in retxout:
            txtime = format_time(int(query_single('SELECT time FROM block WHERE height = %s', row[6])[0]))
            txout += [[txtime, row[0], row[2]]]
        return {'Status': 'OK', 'balance': balance, 'txin': txin, 'txout': txout, 'address': address}

    except Exception as e:
        print >> sys.stderr, e, 'Address Page'
        return {'Status': 'error', 'Data': 'Unknown error'}
