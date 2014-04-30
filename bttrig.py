#!/usr/bin/python

import os, sys, time, logging, subprocess, urllib2, json
from optparse import OptionParser

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

##############################################################################
options = None
config = {}

##############################################################################
def exec_cmd(cmd):
    logging.debug('executing: %s' % cmd)
    p = subprocess.Popen(cmd, shell=True, env=os.environ, 
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (stdout, stderr) = p.communicate()
    return (p.returncode, stdout)

##############################################################################
def open_url(url):
    try:
        r = urllib2.urlopen(url, timeout=10)
        o = r.read()
    except urllib2.HTTPError, e:
        logging.error('HTTP_ERROR: %s (%s)' % (e.code, e.msg))
        return None
    except urllib2.URLError, e:
        logging.error('URL_ERROR: %s' % e.reason)
        return None
    except:
        logging.exception('ERROR: exception')
        return None
    return o

##############################################################################
def trigger(present):
    for trigger in config['triggers']:
        name = trigger['name']
        if ! trigger['enabled']:
            logging.debug('trigger %s disabled' % name)
            continue
        ttype = trigger['type']
        if present:
            action = trigger['on_present']
        else:
            action = trigger['on_absent']
        if ttype == 'exec':
            logging.info('triggering on_present on %s' % name)
            exec_cmd(action)
        elif ttype == 'url':
            logging.info('triggering on_absent on %s' % name)
            open_url(action)

##############################################################################
def check_devices():
    present_count = 0
    present = False

    pingcmd = config['bluetooth_ping_command']
    if ! os.path.isabs(pingcmd):
        pingcmd = os.path.join(os.path.join(os.path.dirname(__file__), pingcmd)

    for bt_dev in config['bluetooth_devices']:
        (ret, out) = exec_cmd('%s %s' % (pingcmd, bt_dev))
        logging.debug(out.rstrip('\n'))
        if ret:
            logging.debug('%s not available' % bt_dev)
        else:
            logging.debug('%s available' % bt_dev)
            present_count += 1

    if config['trigger_only_on_all']:
        if present_count == len(config['bluetooth_devices']):
            present = True
    else
        if present_count > 0:
            present = True
    
    trigger(present)
    
    return present

##############################################################################
def check_devices_forver():
    while True:
        if check_devices():
            sleep_time = 120
        else:
            sleep_time = 10
        time.sleep(sleep_time)
        
##############################################################################
def main():
    global options, config
    
    parser = OptionParser(usage='Usage: %prog [options]\n')
    
    # funtionality options
    parser.add_option('-c', '--config', default=None,
                      action='store', type='string', dest='config',
                      help='Configuration file')
    parser.add_option('-d', '--daemon', dest='daemon',
                      action='store_true', default=False,
                      help='Run as daemon')
    parser.add_option('-v', '--verbose', dest='verbose',
                      action='store_true', default=False,
                      help='Update its own record')
    (options, args) = parser.parse_args()
    
    # configure logging
    log_level = logging.INFO
    if options.verbose:
        log_level = logging.DEBUG
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%y/%m/%d %H:%M:%S',
                        level=log_level)
    
    # read configuration file
    if options.config:
        if os.path.exists(options.config):
            config = load(file(options.config, 'r'), Loader=Loader)
        else:
            logging.error('ERROR: configuration file %s does not exist' %
                  options.config)
            sys.exit(1)
    else:
        cfn = 'vera_bt_trigger.yaml'
        for config_file in [os.path.join('/', 'etc', cfn),
                            os.path.expanduser('~/.%s' % cfn),
                            os.path.join(os.path.dirname(__file__), cfn)]:
            if os.path.exists(config_file):
                config = load(file(config_file, 'r'), Loader=Loader)
                break
    
    if options.daemon:
        while True:
            check_devices_forver()
    else:
        check_devices()

##############################################################################
if __name__ == "__main__":
    main()

##############################################################################
