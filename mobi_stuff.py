# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
__license__   = 'GPL v3'
__docformat__ = 'restructuredtext en'

import os
import struct

import calibre_plugins.kindleunpack_plugin.config as cfg
import calibre_plugins.kindleunpack_plugin.kindleunpackcore.kindleunpack as _mu
from calibre_plugins.kindleunpack_plugin.kindleunpackcore.compatibility_utils import bstr, unicode_str
from calibre_plugins.kindleunpack_plugin.kindleunpackcore.mobi_split import mobi_split
from calibre_plugins.kindleunpack_plugin.__init__ import PLUGIN_NAME, PLUGIN_VERSION
from calibre.gui2 import warning_dialog

# Pull in translations for this module's translatable strings.
load_translations()

class SectionizerLight:
    """ Stolen from Mobi_Unpack and slightly modified. """
    def __init__(self, filename):
        self.data = open(filename, 'rb').read()
        if self.data[:3] == b'TPZ':
            self.ident = 'TPZ'
        else:
            self.palmheader = self.data[:78]
            self.ident = self.palmheader[0x3C:0x3C+8]
        try:
            self.num_sections, = struct.unpack_from(b'>H', self.palmheader, 76)
        except:
            return
        self.filelength = len(self.data)
        try:
            sectionsdata = struct.unpack_from(bstr('>%dL' % (self.num_sections*2)), self.data, 78) + (self.filelength, 0)
            self.sectionoffsets = sectionsdata[::2]
        except:
            pass

    def loadSection(self, section):
        before, after = self.sectionoffsets[section:section+2]
        return self.data[before:after]

class MobiHeaderLight:
    """ Stolen from Mobi_Unpack and slightly modified. """
    def __init__(self, sect, sectNumber):
        self.sect = sect
        self.start = sectNumber
        self.header = self.sect.loadSection(self.start)
        self.records, = struct.unpack_from(b'>H', self.header, 0x8)
        self.length, self.type, self.codepage, self.unique_id, self.version = struct.unpack(b'>LLLLL', self.header[20:40])
        self.mlstart = self.sect.loadSection(self.start+1)[0:4]
        self.crypto_type, = struct.unpack_from(b'>H', self.header, 0xC)

    def isEncrypted(self):
        return self.crypto_type != 0

    def isPrintReplica(self):
        return self.mlstart[0:4] == b'%MOP'

    # Standalone KF8 file
    def isKF8(self):
        return self.start != 0 or self.version == 8

    def isJointFile(self):
        # Check for joint MOBI/KF8
        for i in range(len(self.sect.sectionoffsets)-1):
            before, after = self.sect.sectionoffsets[i:i+2]
            if (after - before) == 8:
                data = self.sect.loadSection(i)
                if data == b'BOUNDARY' and self.version != 8:
                    return True
                    break
        return False


def makeFileNames(prefix, infile, outdir, kf8=False):
    if kf8:
        return os.path.join(outdir, prefix+os.path.splitext(os.path.basename(infile))[0] + '.azw3')
    return os.path.join(outdir, prefix+os.path.splitext(os.path.basename(infile))[0] + '.mobi')

class mobiProcessor:
    def __init__(self, infile):
        self.infile = infile
        self.sect = SectionizerLight(self.infile)
        if (self.sect.ident != b'BOOKMOBI' and self.sect.ident != b'TEXtREAd') or self.sect.ident == 'TPZ':
            raise Exception(_('Unrecognized Kindle/MOBI file format!'))
        mhl = MobiHeaderLight(self.sect, 0)
        self.version = mhl.version
        self.isEncrypted = mhl.isEncrypted()
        if self.sect.ident == b'TEXtREAd':
            self.isPrintReplica = False
            self.isComboFile = False
            self.isKF8 = False
            return
        self.isPrintReplica = mhl.isPrintReplica()
        self.isKF8 = mhl.isKF8()
        self.isComboFile = mhl.isJointFile()

        self.ePubVersion = cfg.plugin_prefs['Epub_Version']
        self.useHDImages = cfg.plugin_prefs['Use_HD_Images']
        self.zipCompressType = cfg.plugin_prefs['Zip_Compress_Type']
        self.kindleContentDir = cfg.plugin_prefs['Kindle_Content_Folder']

    def setZipCompressType(self, zipCompressType):
        self.zipCompressType = zipCompressType
        
    def setKindleContentDir(self, kindleContentDir):
        self.kindleContentDir = kindleContentDir

    def getPDFFile(self, outdir):
        _mu.unpackBook(self.infile, outdir)
        pdf_path = next(
            (
                os.path.join(outdir, filename)
                for filename in os.listdir(outdir)
                if filename.lower().endswith('.pdf')
            ),
            None,
        )
        if pdf_path is None:
            raise Exception(_('Problem locating unpacked pdf.'))
        if not os.path.exists(pdf_path):
            raise Exception(_('Problem locating unpacked pdf: {0}').format(pdf_path))
        return pdf_path

    def unpackMOBI(self, outdir):
        _mu.unpackBook(self.infile, outdir, epubver=self.ePubVersion, use_hd=self.useHDImages, contentdir=self.kindleContentDir)

    def unpackEPUB(self, outdir):
        _mu.unpackBook(self.infile, outdir, epubver=self.ePubVersion, use_hd=self.useHDImages, contentdir=self.kindleContentDir, format='EPUB')
        kf8dir = os.path.join(outdir, 'mobi8')
        kf8BaseName = os.path.splitext(os.path.basename(self.infile))[0]
        epub = os.path.join(kf8dir, '{0}.epub'.format(kf8BaseName))
        if not os.path.exists(epub):
            raise Exception(_('Problem locating unpacked epub: {0}').format(epub))
        return epub

    def unpackZIP(self, outdir):
        _mu.unpackBook(self.infile, outdir, epubver=self.ePubVersion, use_hd=self.useHDImages, contentdir=self.kindleContentDir, format='ZIP', zipcompresstype=self.zipCompressType)
        kf8dir = os.path.join(outdir, 'mobi8')
        kf8BaseName = os.path.splitext(os.path.basename(self.infile))[0]
        zip_path = os.path.join(kf8dir, '{0}.zip'.format(kf8BaseName))
        if not os.path.exists(zip_path):
            raise Exception(_('Problem locating unpacked zip: {0}').format(zip_path))
        return zip_path

    def writeSplitCombo(self, outdir):
        mobi_to_split = mobi_split(unicode_str(self.infile))
        outMobi = makeFileNames('MOBI-', self.infile, outdir)
        outKF8 = makeFileNames('KF8-', self.infile, outdir, True)
        try:
            open(outMobi, 'wb').write(mobi_to_split.getResult7())
        except:
            warning_dialog(None, _('{0} v{1}').format(PLUGIN_NAME, PLUGIN_VERSION),
                _('Could not create MOBI portion of the split'), show=True, show_copy_button=False)
        try: 
            open(outKF8, 'wb').write(mobi_to_split.getResult8())
        except:
            warning_dialog(None, _('{0} v{1}').format(PLUGIN_NAME, PLUGIN_VERSION),
                _('Could not create KF8 portion of the split'), show=True, show_copy_button=False)
