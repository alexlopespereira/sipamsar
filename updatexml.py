# coding=utf-8
# This file is part of image_indexer.
#
# image_indexer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# image_indexer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
import xml.etree.ElementTree as xml
#from xml.etree.ElementTree import Element
import re
import errno
import os
import ntpath
import platform

class UpdateXML:

    def __init__(self, result_path, xml_dest_path, modelpath, paramfile_path, image_list, OS):
        self.OS = OS.upper()
        self.tree = xml.parse(modelpath)
        self.xmlRoot = self.tree.getroot()
        self.image_list = image_list
        self.xmls_path = xml_dest_path
        if OS == 'LINUX':
            self.paramfile_path=paramfile_path
            self.image_list=image_list
            self.result_path = result_path
            self.dirname = self.createDirName(image_list)
            self.root_dir = self.result_path + "/" + self.dirname
            self.remove_dir = self.root_dir + "/remover/"
        else:
            self.paramfile_path = paramfile_path.replace(os.sep, ntpath.sep)
            self.result_path = result_path.replace(os.sep, ntpath.sep)
            self.dirname = self.createDirName(image_list)
            self.dirname.replace(os.sep, ntpath.sep)
            self.root_dir = self.result_path + "\\" + self.dirname
            self.root_dir.replace(os.sep, ntpath.sep)
            self.remove_dir = self.root_dir + "\\remover\\"
            self.remove_dir.replace(os.sep, ntpath.sep)

    def createDirName(self, imagelist):
        n = len(imagelist)
        last=imagelist[-1]
        first=imagelist[0]
        lastpart = re.findall('((CSKS[1-4]_)|(20\d{12}))', last)
        firstpart = re.findall('((CSKS[1-4]_)|(20\d{12}))', first)
        # dirname = firstpart[0][0] + firstpart[1][0] + "_"+ lastpart[0][0] + lastpart[1][0] + "_" + str(n)
        dirname = lastpart[0][0] + lastpart[1][0] + "_"+ firstpart[0][0] + firstpart[1][0] + "_" + str(n)
        return dirname
        #"((CSKS[1-4]_).*)(((20|19)(0([1-9])|\d{2})\d{2}\d{2}\d{6}_){2})"

    def writeXML(self):
        if False:
            if platform.system().upper() == 'WINDOWS':
                curr_dir = self.xmls_path + '\\' + self.dirname + '\\'
                filepath = self.xmls_path + '\\' + self.dirname + '\\' + self.dirname + '.xml'
            else:
                curr_dir = self.xmls_path + '/' + self.dirname + '/'
                filepath = self.xmls_path + '/' + self.dirname + '/' + self.dirname + '.xml'
            try:
                os.makedirs(curr_dir,mode=0777)
            except OSError as exc:  # Python >2.5
                if exc.errno == errno.EEXIST and os.path.isdir(self.remove_dir):
                    pass
                else:
                    raise
        else:
            if platform.system().upper() == 'WINDOWS':
                filepath = self.xmls_path + '\\' + self.dirname + '.xml'
            else:
                filepath = self.xmls_path + '/' + self.dirname + '.xml'
        #os.umask(0777)
        self.tree.write(filepath)
        os.chmod(filepath, 0o777)

    def createDirectory(self):
        try:
            os.makedirs(self.remove_dir)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(self.remove_dir):
                pass
            else:
                raise

    def lookupMethod(self, command):
        return getattr(self, 'do_' + command.upper(), None)

    def do_PARAMFILE(self, rest):
        rest.text = self.paramfile_path
        return 'updated paramfile'

    def do_IMPORT_OUTPUTDIR(self, rest):
        rest.text = self.remove_dir
        return 'updated import_outputdir'

    def do_MULTILOOK_OUTPUTDIR(self, rest):
        rest.text = self.remove_dir
        return 'updated multilook_outputdir'

    def do_COREGISTRO_OUTPUTDIR(self, rest):
        rest.text = self.remove_dir
        return 'updated coregistro_outputdir'

    def do_DEGRANDI_OUTPUTDIR(self, rest):
        rest.text = self.remove_dir
        return 'updated degrandi_outputdir'

    def do_GEOCODING_OUTPUTDIR(self, rest):
        rest.text = self.root_dir
        return 'updated geocoding_outputdir'

    def do_MTF_OUTPUTDIR(self, rest):
        rest.text = self.root_dir
        return 'updated mtf_outputdir'

    def do_INPUT_FILES(self, rest):
        array = rest.find('array')
        array.attrib['dimensions'] = str(len(self.image_list))
        for l in self.image_list:
            element = xml.SubElement(array, 'element')
            element.text = l


        return 'updated mtf_outputdir'

    def do_UNKNOWN(self, rest):
        raise NotImplementedError, 'received unknown command'

    def state_COMMAND(self, line):
        line = line.strip()
        parts = line.split(None, 1)
        if parts:
            method = self.lookupMethod(parts[0]) or self.do_UNKNOWN
            if len(parts) == 2:
                return method(parts[1])
            else:
                return method('')
        else:
            raise SyntaxError, 'bad syntax'

    def run(self):
        for option in self.xmlRoot.findall('option'):
            #print option.tag, option.attrib
            name = option.get('name')
            try:
                self.lookupMethod(name)(option) # => 'Howdy foo.bar.com'
            except (BaseException) as e:
                pass
