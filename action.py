# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
__license__   = 'GPL v3'
__docformat__ = 'restructuredtext en'

import os
import shutil

from functools import partial

try:
    from qt.core import QMenu, QToolButton, QApplication
except ImportError:
    from PyQt5.Qt import QMenu, QToolButton, QApplication

from calibre.gui2 import choose_dir, info_dialog, open_local_file
from calibre.gui2.actions import InterfaceAction

from calibre.ptempfile import PersistentTemporaryDirectory
from calibre_plugins.kindleunpack_plugin.__init__ import (PLUGIN_NAME,
                                PLUGIN_VERSION, PLUGIN_DESCRIPTION)
import calibre_plugins.kindleunpack_plugin.config as cfg
from calibre_plugins.kindleunpack_plugin.dialogs import ProgressDialog, ResultsSummaryDialog
# from calibre_plugins.kindleunpack_plugin.mobi_stuff import mobiProcessor
from calibre_plugins.kindleunpack_plugin.utilities import (get_icon, KindleFormats, set_plugin_icon_resources,
                                showErrorDlg, create_menu_item, create_menu_action_unique, build_log)

# Pull in translations for this module's translatable strings.
load_translations()

class InterfacePlugin(InterfaceAction):
    name = 'KindleUnpack'
    action_spec = ('KindleUnpack', None,
            _(PLUGIN_DESCRIPTION), None)
    popup_type = QToolButton.InstantPopup
    # dont_add_to = frozenset(['menubar-device', 'toolbar-device', 'context-menu-device'])
    dont_add_to = frozenset(['context-menu-device'])
    action_type = 'current'

    def genesis(self):
        self.menu = QMenu(self.gui)
        icon_resources = self.load_resources(cfg.PLUGIN_ICONS)
        set_plugin_icon_resources(cfg.PLUGIN_NAME, icon_resources)

        self.qaction.setMenu(self.menu)
        self.qaction.setIcon(get_icon(cfg.PLUGIN_ICONS[0]))
        # Setup hooks so that we only enable the relevant submenus for available formats for the selection.
        self.menu.aboutToShow.connect(self.about_to_show_menu)

        # Refresh icon when user switches light/dark theme.
        # paletteChanged was introduced in Qt5.0 / calibre 2.x so is safe for all supported versions.
        try:
            QApplication.instance().paletteChanged.connect(self.on_palette_changed)
        except Exception:
            pass

    def on_palette_changed(self, palette):
        self.qaction.setIcon(get_icon(cfg.PLUGIN_ICONS[0]))

    def about_to_show_menu(self):
        book_ids = self.gui.library_view.get_selected_ids()
        if len(book_ids) > 1:
            self.build_multiple_book_menus(book_ids)
        elif len(book_ids):
            self.build_single_book_menus(book_ids[0])

    def build_multiple_book_menus(self, book_ids):
        '''
        If multiple books are selected, the only choices are to
        extract PDFs from AZW4 formats and EPUBs from AZW3 format.
        '''
        m = self.menu
        m.clear()

        tool_tip = _('Convert the KF8 portions of the selected AZW3s to ePubs and add them to their respective books.')
        create_menu_action_unique(self, m, _('KF8 to ePubs')+'...', 'mimetypes/epub.png', tool_tip,
                                                 False, triggered=partial(self.multi_dispatcher, book_ids, u'AZW3'))

        tool_tip = _('Convert the KF8 portions of the selected AZW3s to ZIPs and add them to their respective books.')
        create_menu_action_unique(self, m, _('KF8 to ZIPs')+'...', 'mimetypes/zip.png', tool_tip,
                                                 False, triggered=partial(self.multi_dispatcher, book_ids, u'ZIP'))

        tool_tip = _('Extract the PDFs from the AZW4 formats and add them to their respective books.')
        create_menu_action_unique(self, m, _('Extract PDFs')+'...', 'mimetypes/pdf.png', tool_tip,
                                                 False, triggered=partial(self.multi_dispatcher, book_ids, u'AZW4'))

        m.addSeparator()
        tool_tip = _('Configure the KindleUnpack plugin\'s settings.')
        create_menu_action_unique(self, m, _('Customize plugin')+'...', 'config.png', tool_tip,
                                  None, triggered=self.show_configuration)
        self.gui.keyboard.finalize()

    def build_single_book_menus(self, book_id):
        '''
        Build the menus that change on the fly based on selected ebook's
        formats and their various properties.
        '''
        m = self.menu
        m.clear()
        kindle_formats = ['MOBI', 'AZW', 'AZW3', 'AZW4', 'PRC']
        book_list = self.gatherKindleFormats([book_id], kindle_formats)
        if not book_list:
            tool_tip = _('No suitable format to unpack.')
            error_menu = create_menu_item(self, m, tool_tip+'...', None, tool_tip, None, None)
            error_menu.setEnabled(False)
            m.addSeparator()
            tool_tip = _('Configure the KindleUnpack plugin\'s settings.')
            create_menu_action_unique(self, m, _('Customize plugin')+'...', 'config.png', tool_tip,
                                      None, triggered=self.show_configuration)
            self.gui.keyboard.finalize()
            return

        format_dict = book_list[0][2]
        for format_name in format_dict.keys():
            format_details = format_dict[format_name].get_format_details()
            # Weird and unlikely possiblity that there is no file on disk for this format at this point.
            if format_details['errors'] is not None and format_details['errors'] == 'path':
                tool_tip = _('No file on disk. Can\'t unpack.')
                mnu_msg = _('{0} Has no file associated with it.').format(format_name)
                error_menu = create_menu_item(self, m, mnu_msg+'...', None, tool_tip,
                                            None, None)
                error_menu.setEnabled(False)
                continue
            # Topaz format. Punt.
            elif format_details['errors'] is not None and format_details['errors'] == 'topaz':
                tool_tip = _('Can\'t unpack Topaz books.')
                mnu_msg = _('{0} format is a Topaz book. Can\'t unpack.').format(format_name)
                error_menu = create_menu_item(self, m, mnu_msg+'...', None, tool_tip,
                                        None, None)
                error_menu.setEnabled(False)
                continue
            # Unknown error. Very likely not a valid kindlebook file. Exact error found in format_details['errors'].
            elif format_details['errors'] is not None:
                tool_tip = _('Unknown issues with this format.')
                mnu_msg = _('{0} format might not be a valid mobi/kindlebook.').format(format_name)
                error_menu = create_menu_item(self, m, mnu_msg+'...', None, tool_tip,
                                            None, None)
                error_menu.setEnabled(False)
                continue

            kindle_obj = format_details['kindle_obj']

            mnu_img = 'drm-unlocked.png'
            mnu_tip = _('This {0} file is DRM-Free.').format(format_name)
            if kindle_obj.isEncrypted:
                print('isEncrypted = {0}'.format(kindle_obj.isEncrypted))
                mnu_tip = _('This {0} file has DRM... can\'t unpack.').format(format_name)
                mnu_img = 'drm-locked.png'
            ac = create_menu_item(self, m, format_name, mnu_img, mnu_tip, None)
            sm = QMenu()
            ac.setMenu(sm)
            # Standard unpack to external folder ... disable menu if kindlebook encrypted.
            tool_tip = _('Unpack the {0}\'s source components').format(format_name)
            unpack_menu = create_menu_action_unique(self, sm, _('Unpack {0}').format(format_name), 'images/explode3.png',
                                                tool_tip, False, triggered=partial(self.unpack_ebook, kindle_obj))
            if kindle_obj.isEncrypted:
                unpack_menu.setEnabled(False)

            # Extract PDF file from AZW4
            if kindle_obj.isPrintReplica:
                tool_tip = _('Extract the PDF from the Print Replica format and add it to the library.')
                create_menu_action_unique(self, sm, _('Extract PDF')+'...', 'mimetypes/pdf.png', tool_tip, False,
                                            triggered=partial(self.extract_element, kindle_obj, book_id, u'AZW4', False))

            # Offer to split kindlegen dual format output.
            if kindle_obj.isComboFile:
                tool_tip = _('Split the combo KF8/MOBI file into its two components.')
                create_menu_action_unique(self, sm, _('Split KF8/MOBI')+'...', 'edit-cut.png', tool_tip,
                                            False, triggered=partial(self.combo_split, kindle_obj))

            # Extract ePub from the unpacked contents and add to current book's formats.
            convert_menu = None
            if kindle_obj.isKF8 or kindle_obj.isComboFile:
                tool_tip = _('Convert standalone KF8 file to its original ePub.')
                convert_menu = create_menu_action_unique(self, sm, _('KF8 to ePub')+'...', 'mimetypes/epub.png', tool_tip,
                                            False, triggered=partial(self.extract_element, kindle_obj, book_id, u'AZW3', False))
            if kindle_obj.isEncrypted and convert_menu is not None:
                convert_menu.setEnabled(False)

            # Extract ZIP from the unpacked contents and add to current book's formats.
            convert_menu = None
            if kindle_obj.isKF8 or kindle_obj.isComboFile:
                tool_tip = _('Convert standalone KF8 file to ZIP.')
                convert_menu = create_menu_action_unique(self, sm, _('KF8 to ZIP')+'...', 'mimetypes/zip.png', tool_tip,
                                            False, triggered=partial(self.extract_element, kindle_obj, book_id, u'ZIP', False))
            if kindle_obj.isEncrypted and convert_menu is not None:
                convert_menu.setEnabled(False)

        # Add menu item to go to plugin configuration.
        m.addSeparator()
        tool_tip = _('Configure the KindleUnpack plugin\'s settings.')
        create_menu_action_unique(self, m, _('Customize plugin')+'...', 'config.png', tool_tip,
                                  None, triggered=self.show_configuration)
        self.gui.keyboard.finalize()
        return

    def update_db(self, bookfile, output_format, book_id):
        '''
        Update the calibre ebook entry with the extracted EPUB/PDF format.
        (never overwriting a pre-existing one)
        '''
        db = self.gui.library_view.model().db
        stream = lopen(bookfile, 'rb')
        return db.add_format(book_id, output_format, stream, index_is_id=True, replace=False, notify=True)

    def show_configuration(self):
        '''
        Show plugin's configuration widget.
        '''
        self.interface_action_base_plugin.do_user_config(self.gui)

    def directoryChooser(self):
        '''
        Select a folder, or use the one specified in the config widget.
        '''
        if cfg.plugin_prefs['Always_Use_Unpack_Folder']:
            return cfg.plugin_prefs['Unpack_Folder']
        else:
            return choose_dir(self.gui, PLUGIN_NAME + 'dir_chooser',
                _('Select Directory To Unpack Kindle/Mobi Book To'))

    def gatherKindleFormats(self, book_ids, target_formats, goal_format=None):
        '''
        Gathers all the kindle formats for the book(s) and uses the KindleFormats class
        in utlities.py to collect details about each one. Including an initialized
        mobiProcessor object.
        '''
        db = self.gui.library_view.model().db
        books_info = []
        for book_id in book_ids:
            title = db.get_metadata(book_id, index_is_id=True, get_user_categories=False).title
            book = KindleFormats(book_id, db, target_formats, goal_format)
            details = book.get_formats()
            if details:
                books_info.append((book_id, title, details))
        return books_info

    def multi_dispatcher(self, book_ids, target_format):
        '''
        Prepares the necessaries to feed to ProgressDialog in dialogs.py
        '''
        db = self.gui.library_view.model().db
        if target_format == 'AZW3':
            attr = 'isKF8'
            goal_format = 'EPUB'
        elif target_format == 'ZIP':
            target_format = 'AZW3'
            attr = 'isKF8'
            goal_format = 'ZIP'
        elif target_format == 'AZW4':
            attr = 'isPrintReplica'
            goal_format = 'PDF'
        books_info = self.gatherKindleFormats(book_ids, [target_format], goal_format)
        # If we have stuff ... send it on its way to the pretty ProgressDialog.
        if books_info:
            book_count = len(books_info)
            if target_format == 'AZW4':
                status_msg_type = ngettext('Print Replica book', 'Print Replica books', book_count)
                status_msg_type_singular = ngettext('Print Replica book', 'Print Replica books', 1)
            else:
                status_msg_type = ngettext('KF8 book', 'KF8 books', book_count)
                status_msg_type_singular = ngettext('KF8 book', 'KF8 books', 1)
            if goal_format == 'PDF':
                action_type = ngettext('Extracting {0} from', 'Extracting {0}s from', book_count).format(goal_format)
            else:
                action_type = ngettext('Unpacking {0} from', 'Unpacking {0}s from', book_count).format(goal_format)
            d = ProgressDialog(self.gui, books_info, self.extract_element, db, target_format, attr, goal_format,
                                   status_msg_type=status_msg_type, action_type=action_type)
            if d.wasCanceled():
                return
            successes, failures = d.get_results()
            if successes:
                ids_to_highlight = []
                for i in successes:
                    ids_to_highlight.append(i[0])
                self.highlight_entries(ids_to_highlight)
            title = PLUGIN_NAME + ' v' + PLUGIN_VERSION
            success_count = len(successes)
            failure_count = len(failures)
            msg = ngettext(
                '<p>{0} {1} format added to library. {2} not added. See log for details.</p>',
                '<p>{0} {1} formats added to library. {2} not added. See log for details.</p>',
                success_count,
            ).format(success_count, goal_format, failure_count)
            log = build_log(failures, successes, target_format, goal_format, status_msg_type_singular)
            # print (log)
            sd = ResultsSummaryDialog(self.gui, title, msg, log)
            sd.exec_()
        else:
            return info_dialog(None, _('{0} v{1}').format(PLUGIN_NAME, PLUGIN_VERSION),
                _('<p>Nothing to do. Perhaps no books selected had {0} formats.').format(target_format), show=True)

    def highlight_entries(self, ids_to_highlight):
        # self.gui.library_view.model().books_added(len(ids_to_highlight))
        # self.gui.library_view.model().refresh()
        # self.gui.tags_view.recount()
        # self.gui.library_view.model().set_highlight_only(True)
        self.gui.library_view.select_rows(ids_to_highlight)
        return

    def unpack_ebook(self, kindle_obj):
        '''
        Unpack kindlebook to external folder.
        '''
        outdir = self.directoryChooser()
        if outdir:
            kindle_obj.setKindleContentDir(cfg.plugin_prefs['Kindle_Content_Folder'])
            try:
                kindle_obj.unpackMOBI(outdir)
            except Exception as e:
                return showErrorDlg(str(e), self.gui, True)
            open_local_file(outdir)

    def extract_element(self, kindle_obj, book_id, target, quiet=False):
        '''
        ExtractPDFs/EPUBs from AZW4/AZW3 format(s).
        '''
        outdir = PersistentTemporaryDirectory()
        kindle_obj.setZipCompressType(cfg.plugin_prefs['Zip_Compress_Type'])
        kindle_obj.setKindleContentDir(cfg.plugin_prefs['Kindle_Content_Folder'])
        if target == 'AZW3':
            output_format = 'EPUB'
            try:
                bookfile = kindle_obj.unpackEPUB(outdir)
            except Exception as e:
                if quiet:
                    return False, str(e)
                return showErrorDlg(str(e), self.gui, True)
        elif target == 'ZIP':
            output_format = 'ZIP'
            try:
                bookfile = kindle_obj.unpackZIP(outdir)
            except Exception as e:
                if quiet:
                    return False, str(e)
                return showErrorDlg(str(e), self.gui, True)
        elif target == 'AZW4':
            output_format = 'PDF'
            try:
                bookfile = kindle_obj.getPDFFile(outdir)
            except Exception as e:
                if quiet:
                    return False, str(e)
                return showErrorDlg(str(e), self.gui, True)

        if os.path.exists(bookfile):
            if not self.update_db(bookfile, output_format, book_id):
                errmsg = _('This book already has the {0} format in this library; it will not be overwritten.').format(output_format)
                if quiet:
                    return False, None
                return showErrorDlg(errmsg, self.gui)
            current_idx = self.gui.library_view.currentIndex()
            # delete outdir
            if cfg.plugin_prefs['Always_Delete_Temp_Files']:
                shutil.rmtree(outdir)
            #
            if current_idx.isValid():
                self.gui.library_view.model().current_changed(current_idx, current_idx)
            if quiet:
                return True, None
            if output_format in ('EPUB', 'ZIP'):
                success_msg = _('<p>The {0} was successfully unpacked and added to the book\'s formats in the library.</p>').format(output_format)
            elif output_format == 'PDF':
                success_msg = _('<p>The PDF was successfully extracted and added to the book\'s formats in the library.</p>')
            return info_dialog(None, _('{0} v{1}').format(PLUGIN_NAME, PLUGIN_VERSION), success_msg, show=True)

        errmsg = _('Could not find {0} in the unpacked Kindle book.').format(output_format)
        if quiet:
            return False, errmsg
        return showErrorDlg(errmsg, self.gui)

    def combo_split(self, kindle_obj):
        '''
        Split kindlegen output into its AZW3/MOBI pieces.
        '''
        outdir = self.directoryChooser()
        if outdir:
            try:
                kindle_obj.writeSplitCombo(outdir)
            except Exception as e:
                return showErrorDlg(str(e), self.gui, True)
            open_local_file(outdir)
