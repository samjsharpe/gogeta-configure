#!/usr/bin/python
import argparse
import json
import requests
import sys
import yaml

from gogeta_configure import __version__

def parse_options():
    parser = argparse.ArgumentParser(description='Update gogeta via etcd')
    parser.add_argument('config_file', nargs='?', help='YAML config file (use "-" to read from STDIN)', default=None)
    parser.add_argument('--debug', '-d', action='store_true', default=False, help='Show debug logging')
    parser.add_argument('--silent', '-s', action='store_true', default=False, help='Hide error logging')
    parser.add_argument('--update', '-u', action='store_true', default=False, help='Update services')
    parser.add_argument('--list', '-l', action='store_true', default=False, help='List services')
    parser.add_argument('--dry-run', '-D', action='store_true', default=False, help='Do not change configuration')
    parser.add_argument('--purge', action='store_true', default=False, help='Purge all gogeta config from etcd')
    parser.add_argument('--version', '-v', action='version', version='%(prog)s {0}'.format(__version__))
    return parser.parse_args()


def load_config(config_file):
    if config_file == None:
        debug('Config file not supplied, assuming etcd is 127.0.0.1:4001')
        config = {}
        config['etcd'] = '127.0.0.1:4001'
    elif config_file == '-':
        debug('Reading config from STDIN')
        config = yaml.load(sys.stdin.read())
    else:
        try:
            config = yaml.load(open(config_file,'r').read())
        except IOError:
            print '[error] Could not load config file {0}'.format(config_file)
            sys.exit(1)
    return config


def debug(message):
    if options.debug:
        print '[debug]: {0}'.format(message)


def error(message,exitcode=None):
    if not options.silent:
        print '[error]: {0}'.format(message.rstrip())
    if exitcode:
        sys.exit(exitcode)


def set_key(key, value):
    url = 'http://{0}/v2/keys{1}'.format(config['etcd'],key)
    old_value = get_key(key)
    if value == old_value:
        debug('Key {0} is already set to {1}'.format(key,value))
    else:
        print 'Setting {0} => {1}'.format(key, value)
        if not options.dry_run:
            data = {}
            data['value'] = value
            response = requests.put(url, data=data)
            if response.status_code == 200:
                debug('Key {0} set to {1}'.format(key,value))
            elif response.status_code == 201:
                debug('Key {0} created as {1}'.format(key,value))
            else:
                error('Cannot set {0} to {1}'.format(key,value))
                error('Etcd: {0} ({1})'.format(response.text, response.status_code))


def get_key(key):
    url = 'http://{0}/v2/keys{1}'.format(config['etcd'],key)
    response = requests.get(url)
    try:
        value = json.loads(response.text)['node']['value']
    except:
        debug('Key {0} not found'.format(key))
        value = ''
    return value


def rm_key(key):
    print 'Deleting key {0}'.format(key)
    if not options.dry_run:
        url = 'http://{0}/v2/keys{1}?recursive=true'.format(config['etcd'],key)
        requests.delete(url)


def list_dir(key):
    url = 'http://{0}/v2/keys{1}'.format(config['etcd'],key)
    dir_list = []
    response = requests.get(url)
    json_response = json.loads(response.text)
    if 'node' in json_response:
        if 'nodes' in json_response['node']:
            sub_keys = json_response['node']['nodes']
            for directory in sub_keys:
                dir_list.append(directory['key'])
            return dir_list
        else:
            error('Key {0} is not a directory'.format(key),2)
    else:
        error('Key {0} does not exist, perhaps the service is not configured'.format(key),2)


def get_services():
    domains = list_dir('/domains')
    service_list = {}
    for domain_key in domains:
        domain = domain_key.split('/')[2]
        servers = list_dir('/services/{service}'.format(service=domain))
        server_list = []
        for server in servers:
            location = json.loads(get_key('{0}/location'.format(server)))
            server_list.append(location['host'].encode('ascii'))
        service_list[domain.encode('ascii')] = server_list
    return service_list


def list_services(service_list):
    print "---"
    print yaml.dump({"etcd": config['etcd'], "services": service_list},
                    default_flow_style=False)


def deleted_items(prefix, service_list,config):
    deleted_items = []
    items = list_dir(prefix)
    slash_number = len(prefix.split('/'))
    for item_key in items:
        item = item_key.split('/')[slash_number]
        if item not in config['services']:
            deleted_items.append(item_key)
    return deleted_items


def deleted_backends(service_list, config):
    backend_list = []
    for service in service_list:
        if service in config['services']:
            config_backends = len(config['services'][service])
            service_backends = len(service_list[service])
            if config_backends < service_backends:
                backends_to_delete = range(config_backends + 1, service_backends + 1)
                for backend in backends_to_delete:
                     backend_list.append('/services/{0}/{1}'.format(service,backend))
    return backend_list


def cleanup(config):
    debug('Running cleanup of unconfigured domains, services and backends')
    services = get_services()
    keys = deleted_items('/domains',services,config)
    keys += deleted_items('/services',services,config)
    keys += deleted_backends(services,config)
    for key in keys:
        rm_key(key)


def update_services(config):
    if 'services' in config:
        for service, servers in config['services'].items():
            set_key('/domains/{0}/type'.format(service), 'service')
            set_key('/domains/{0}/value'.format(service), service)
            for server in servers:
                server_number = servers.index(server) + 1
                value = '{"host":"' + server + '","port":80}'
                set_key('/services/{0}/{1}/location'.format(service,server_number), value)
    else:
        error('No config file supplied or no services defined in the config',4)


def main():
    global config
    global options
    options = parse_options()
    config = load_config(options.config_file)
    if options.purge:
        rm_key('/domains')
        rm_key('/services')
    if options.list:
        list_services(get_services())
    if options.update:
        update_services(config)
        cleanup(config)


if __name__ == '__main__':
    main()
