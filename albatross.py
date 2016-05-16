#!/usr/bin/env python3

import sys
import os
import time
import html
import bottle
from bottle import jinja2_template as template
from bottle import request

# Config
ROOTDIR = '/home/liu/test/'
TEMPLATESDIR = './templates/'
STATICDIR = './static/'
#TEMPLATESDIR = os.path.abspath('./templates/')
#STATICDIR = os.path.abspath('./static/')

app = bottle.Bottle()
bottle.TEMPLATE_PATH.append(TEMPLATESDIR)
bottle.TEMPLATE_PATH.append(ROOTDIR)


@app.get('/')
@app.get('/<uri:path>')
def list_files(uri=''):
    urlroot = (request.urlparts.scheme + '://' +
               request.urlparts.netloc)
    path = os.path.abspath('%s/%s' % (ROOTDIR, uri))
    request_raw = False
    if 'raw' in request.GET and \
            bottle.request.GET['raw'] == 'true':
        request_raw = True
    if os.path.exists(path):
        pieces = uri.split('/')
        if '' in pieces:
            pieces.remove('')
        splitpath = list()
        home = {'name': '', 'link': '/'}
        splitpath.append(home)
        for i in range(len(pieces)):
            item = dict()
            item['name'] = pieces[i]
            item['link'] = '/' + '/'.join(pieces[:(i+1)])
            splitpath.append(item)
        if os.path.isdir(path):
            files = os.listdir(path)
            files_info = list()
            updir = {
                'name': '..',
                'link': '/' + '/'.join(pieces[:-1]),
                'isdir': True,
                'mtime': '',
                'size': ''
            }
            if uri:
                files_info.append(updir)
            for filename in files:
                fileabs = '%s/%s' % (path, filename)
                statinfo = os.stat(fileabs)
                file_info = dict()
                file_info['name'] = filename
                file_info['link'] = fileabs[len(ROOTDIR):]
                file_info['isdir'] = os.path.isdir(fileabs)
                file_info['mtime'] = \
                        time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime(statinfo.st_mtime))
                if file_info['isdir']:
                    file_info['size'] = ''
                else:
                    file_info['size'] = fmtsize(statinfo.st_size)
                files_info.append(file_info)
            return template('dir.html',
                            path=splitpath,
                            urlroot=urlroot,
                            files=sorted(files_info,
                                        key=sortfile))
        else:  # not dir
            if request_raw:
                return bottle.static_file(uri, ROOTDIR)
            content = {'status': 'error'}
            try:
                file_raw = ''
                statinfo = os.stat(path)
                Brush, brush = filetype(path)
                content['Brush'] = Brush
                content['brush'] = brush
                if int(statinfo.st_size) > 100*1024:
                    content['error'] = 'File is too large to review.'
                    raise Exception('file too large')
                with open(path, 'rb') as f:
                    file_raw = f.read()
                if isinstance(file_raw, bytes):
                    content['html'] = html.escape(file_raw.decode('utf8'))
                content['status'] = 'OK'
            except UnicodeDecodeError:  # fix the Error
                content['error'] = 'Error at reading file.'
            except:
                if 'error' not in content or not content['error']:
                    content['error'] = 'Unknown error.'
            return template('file.html',
                            path=splitpath,
                            urlroot=urlroot,
                            content=content)
    else:  # not exist
        return bottle.static_file(uri, STATICDIR)

def sortfile(fileinfo):
    return (not fileinfo['isdir'], fileinfo['name'])

def filetype(name):
    root, ext = os.path.splitext(name)
    if ext and ext[0] == '.':
        ext = ext[1:]
    brushes = {
        'AS3': ['as3'],
        'Bash': ['bash', 'sh'],
        'CodeFusion': ['cf'],
        'CSharp': ['cs'],
        'Cpp': ['c', 'cpp', 'cc', 'h', 'hh'],
        'Css': ['css'],
        'Delphi': ['delphi'],
        'Diff': ['diff', 'patch'],
        'Erlang': ['erl', 'erlang'],
        'Groovy': ['groovy'],
        'JScript': ['js', 'jscript', 'javascript', 'json'],
        'Java': ['java'],
        'JavaFX': ['jfx', 'javafx'],
        'Perl': ['perl', 'pl'],
        'Php': ['php'],
        'Plain': ['plain', 'text'],
        'PowerShell': ['ps', 'powershell'],
        'Python': ['python', 'py'],
        'Ruby': ['ruby', 'rails', 'ror'],
        'Scala': ['scala'],
        'Sql': ['sql'],
        'Vb': ['vb', 'vbnet'],
        'Xml': ['xml', 'xhtml', 'xslt', 'html'],
    }
    for k, v in brushes.items():
        if ext.lower() in v:
            return k, v[0]
    return 'Plain', 'plain'


def fmtsize(insize):
    try:
        size = int(insize)
        if size < 1024:  # 0~1023
            return '%d bytes' % size
        elif size < 10240:  # 1K ~ 10K
            return '%.2f kB' % (size/1024)
        elif size < 1048576:  # 10K ~ 1M
            return '%.1f kB' % (size/1024)
        elif size < 10485760:  # 1M ~ 10M
            return '%.2f MB' % (size/1048576)
        elif size < 1073741824:  # 10M ~ 1G
            return '%.1f MB' % (size/1048576)
        elif size < 1099511627776:  # 1G ~ 1T
            return '%.1f GB' % (size/1073741824)
        else:  # > 1T
            return '%.1f TB' % (size/1099511627776)
    except:
        return insize


if __name__ == '__main__':
    if not os.path.isdir(ROOTDIR):
        raise Exception('rootdir is invalid')
    else:
        ROOTDIR = os.path.abspath(ROOTDIR)
    bottle.run(app, host='0.0.0.0', port=9080,
               server='cherrypy',
               debug='debug' in sys.argv)
