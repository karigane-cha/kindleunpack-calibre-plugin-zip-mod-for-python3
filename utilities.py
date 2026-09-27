# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
__license__   = 'GPL v3'
__docformat__ = 'restructuredtext en'


import os
from io import StringIO
from traceback import print_exc

try:
    from qt.core import QPixmap, QIcon, QApplication, QPalette
except ImportError:
    from PyQt5.Qt import QPixmap, QIcon, QApplication, QPalette

from calibre.utils.config import config_dir
from calibre.constants import iswindows
from calibre.gui2 import error_dialog
from calibre.gui2.actions import menu_action_unique_name

from calibre_plugins.kindleunpack_plugin.mobi_stuff import mobiProcessor
from calibre_plugins.kindleunpack_plugin.__init__ import PLUGIN_NAME, PLUGIN_VERSION

# Pull in translations for this module's translatable strings.
load_translations()

plugin_name = None
plugin_icon_resources = {}

def set_plugin_icon_resources(name, resources):
    '''
    Set our global store of plugin name and icon resources for sharing between
    the InterfaceAction class which reads them and the ConfigWidget
    if needed for use on the customization dialog for this plugin.
    '''
    global plugin_icon_resources, plugin_name
    plugin_name = name
    plugin_icon_resources = resources

def get_icon(icon_name):
    '''
    Retrieve a QIcon for the named image from the zip file if it exists,
    or if not then from Calibre's image cache.
    '''
    if icon_name:
        pixmap = get_pixmap(icon_name)
        if pixmap is None:
            # Look in Calibre's cache for the icon
            return QIcon(I(icon_name))
        else:
            return QIcon(pixmap)
    return QIcon()

def is_dark_theme():
    '''
    Detect whether calibre is currently using a dark theme.
    Compatible with Qt4, Qt5 (PyQt5) and Qt6 (qt.core).
    Returns False if detection fails for any reason.
    '''
    try:
        app = QApplication.instance()
        if not app:
            return False
        palette = app.palette()
        # Qt6 uses QPalette.ColorRole.Window; Qt5/Qt4 use QPalette.Window
        try:
            bg = palette.color(QPalette.ColorRole.Window)
        except AttributeError:
            bg = palette.color(QPalette.Window)
        return bg.lightness() < 128
    except Exception:
        return False

def get_pixmap(icon_name):
    '''
    Retrieve a QPixmap for the named image
    Any icons belonging to the plugin must be prefixed with 'images/'
    Supports light/dark theme icon variants via -for-light-theme/-for-dark-theme suffix.
    Falls back to plain filename if no themed variant exists.
    '''
    if not icon_name.startswith('images/'):
        # We know this is definitely not an icon belonging to this plugin
        pixmap = QPixmap()
        pixmap.load(I(icon_name))
        return pixmap

    # Check to see whether the icon exists as a Calibre resource
    # This will enable skinning if the user stores icons within a folder like:
    # ...\AppData\Roaming\calibre\resources\images\Plugin Name\
    if plugin_name:
        local_images_dir = get_local_images_dir(plugin_name)
        bare_name = icon_name.replace('images/', '')
        base, ext = os.path.splitext(bare_name)
        theme_suffix = '-for-dark-theme' if is_dark_theme() else '-for-light-theme'
        for candidate in [base + theme_suffix + ext, bare_name]:
            local_image_path = os.path.join(local_images_dir, candidate)
            if os.path.exists(local_image_path):
                pixmap = QPixmap()
                pixmap.load(local_image_path)
                return pixmap

    # As we did not find an icon elsewhere, look within our zip resources
    if icon_name in plugin_icon_resources:
        pixmap = QPixmap()
        pixmap.loadFromData(plugin_icon_resources[icon_name])
        return pixmap
    return None

def get_local_images_dir(subfolder=None):
    '''
    Returns a path to the user's local resources/images folder
    If a subfolder name parameter is specified, appends this to the path
    '''
    images_dir = os.path.join(config_dir, 'resources/images')
    if subfolder:
        images_dir = os.path.join(images_dir, subfolder)
    if iswindows:
        images_dir = os.path.normpath(images_dir)
    return images_dir

def topaz(f):
    with open(f,'rb') as kindle_file:
        return kindle_file.read(3) == b'TPZ'

def showErrorDlg(errmsg, parent, trcbk=False):
    if trcbk:
        error= ''
        f=StringIO()
        print_exc(file=f)
        error_mess = f.getvalue().splitlines()
        for line in error_mess:
            error = error + str(line) + '\n'
        errmsg = errmsg + '\n\n' + error
    # TODO(Phase 2B): define whether callers pass msgids, translated text, or errors.
    return error_dialog(parent, _('{0} v{1}').format(PLUGIN_NAME, PLUGIN_VERSION),
                _(errmsg), show=True)


def create_menu_item(ia, parent_menu, menu_text, image=None, tooltip=None,
                     shortcut=(), triggered=None, is_checked=None):
    '''
    Create a menu action with the specified criteria and action
    Note that if no shortcut is specified, will not appear in Preferences->Keyboard
    This method should only be used for actions which either have no shortcuts,
    or register their menus only once. Use create_menu_action_unique for all else.
    '''
    if shortcut is not None:
        if len(shortcut) == 0:
            shortcut = ()
        else:
            shortcut = _(shortcut)
    ac = ia.create_action(spec=(menu_text, None, tooltip, shortcut),
        attr=menu_text)
    if image:
        ac.setIcon(get_icon(image))
    if triggered is not None:
        ac.triggered.connect(triggered)
    if is_checked is not None:
        ac.setCheckable(True)
        if is_checked:
            ac.setChecked(True)

    parent_menu.addAction(ac)
    return ac

def create_menu_action_unique(ia, parent_menu, menu_text, image=None, tooltip=None,
                       shortcut=None, triggered=None, is_checked=None, shortcut_name=None,
                       unique_name=None):
    '''
    Create a menu action with the specified criteria and action, using the new
    InterfaceAction.create_menu_action() function which ensures that regardless of
    whether a shortcut is specified it will appear in Preferences->Keyboard
    '''
    orig_shortcut = shortcut
    kb = ia.gui.keyboard
    if unique_name is None:
        unique_name = menu_text
    if shortcut is not False:
        full_unique_name = menu_action_unique_name(ia, unique_name)
        if full_unique_name in kb.shortcuts:
            shortcut = False
        else:
            if shortcut is not None and shortcut is not False:
                if len(shortcut) == 0:
                    shortcut = None
                else:
                    shortcut = _(shortcut)

    if shortcut_name is None:
        shortcut_name = menu_text.replace('&','')

    ac = ia.create_menu_action(parent_menu, unique_name, menu_text, icon=None, shortcut=shortcut,
        description=tooltip, triggered=triggered, shortcut_name=shortcut_name)
    if shortcut is False and orig_shortcut is not False:
        if ac.calibre_shortcut_unique_name in ia.gui.keyboard.shortcuts:
            kb.replace_action(ac.calibre_shortcut_unique_name, ac)
    if image:
        ac.setIcon(get_icon(image))
    if is_checked is not None:
        ac.setCheckable(True)
        if is_checked:
            ac.setChecked(True)
    return ac

class KindleFormats:
    '''
    Build dictionary of details about kindle formats (and what formats they will be converted to).
    '''
    def __init__(self, book_id, db, target_formats, goal_format):
        self.book_id, self.db, self.target_formats, self.goal_format = book_id, db, target_formats, goal_format
        self.__kindle_formats = {}

    def get_formats(self):
        if len(self.__kindle_formats):
            return self.__kindle_formats
        all_formats = self.db.formats(self.book_id, index_is_id=True, verify_formats=True)
        if all_formats is not None:
            all_formats = all_formats.split(',')
        else:
            all_formats = []
        for format_name in all_formats:
            if format_name in self.target_formats:
                self.__kindle_formats[format_name] = KindleFormatDetails(format_name, self.book_id, self.db, self.goal_format)
        return self.__kindle_formats


class KindleFormatDetails:
    '''
    Build dictionary of errors accessing the internals of the kindlebook through the mobiProcessor object.
    Include the initialized mobiProcessor object (from mobi_stuff.py) as well.
    '''
    def __init__(self, format_name, book_id, db, goal_format):
        self.format, self.book_id, self.db, self.goal_format = format_name, book_id, db, goal_format
        self.__details = {}

    def get_format_details(self):
        if len(self.__details):
            return self.__details
        self.__details['errors'] = None
        self.__details['goal_format'] = self.goal_format
        path = self.db.format_abspath(self.book_id, self.format, index_is_id=True) or None
        self.__details['path'] = path
        if path is None:
            self.__details['errors'] = 'path'
            return self.__details
        elif topaz(path):
            self.__details['errors'] = 'topaz'
            return self.__details
        try:
            mobi = mobiProcessor(path)
        except Exception as e:
            self.__details['errors'] = str(e)
            return self.__details
        self.__details['kindle_obj'] = mobi
        return self.__details

def build_log(failures, successes, target, goal, name):
    ENCRYPTED = NOSPECIAL = UNKNOWN = EXISTS = 0
    ENCRYPTED_titles, NOSPECIAL_titles, UNKNOWN_titles, EXISTS_titles = [], [], [], []

    html = ''
    html += _('<h2>Successes - {0}</h2>\n').format(len(successes))
    if len(successes) == 1:
        html += _('<h4>1 {0} format successfully extracted and added to book.</h4>\n').format(goal)
    else:
        html += _('<h4>{0} {1} formats successfully extracted and added to books.</h4>\n').format(len(successes), goal)
    if len(successes):
        html += '<ul>\n'
    for success in successes:
        html += '<li>{0}</li>\n'.format(success[1])
    if len(successes):
        html += '</ul>\n'
    html += '<p>&nbsp;</p>\n'
    html += _('<h2>Issues - {0}</h2>\n').format(len(failures))
    for detail in failures:
        if detail[0] == 1:
            continue
        elif detail[0] == 2:
            ENCRYPTED +=1
            ENCRYPTED_titles.append(detail[1])
        elif detail[0] == 3:
            NOSPECIAL +=1
            NOSPECIAL_titles.append(detail[1])
        elif detail[0] == 4:
            UNKNOWN +=1
            UNKNOWN_titles.append(detail[1])
        else:
            EXISTS +=1
            EXISTS_titles.append(detail[1])
    # if ENCRYPTED:
    if ENCRYPTED == 1:
        msg = _('<h4>1 book had encrypted {0} format.</h4>\n').format(target)
    else:
        msg = _('<h4>{0} books had encrypted {1} formats.</h4>\n').format(ENCRYPTED, target)
    if ENCRYPTED:
        msg += '<ul>\n'
    for title in ENCRYPTED_titles:
        msg += '<li>{0}</li>\n'.format(title)
    if ENCRYPTED:
        msg += '</ul>\n'
    msg += '<p>&nbsp;</p>\n'
    html += msg
    # if NOSPECIAL:
    if NOSPECIAL == 1:
        msg = _('<h4>1 book\'s {0} format contained no {1}.</h4>\n').format(target, name)
    else:
        msg = _('<h4>{0} books\' {1} formats contained no {2}.</h4>\n').format(NOSPECIAL, target, name)
    if NOSPECIAL:
        msg += '<ul>\n'
    for title in NOSPECIAL_titles:
        msg += '<li>{0}</li>\n'.format(title)
    if NOSPECIAL:
        msg += '</ul>\n'
    msg += '<p>&nbsp;</p>\n'
    html += msg
    # if EXISTS:
    if EXISTS == 1:
        msg = _('<h4>1 book already had {0} format -- will not overwrite.</h4>\n').format(goal)
    else:
        msg = _('<h4>{0} books already had {1} formats -- will not overwrite.</h4>\n').format(EXISTS, goal)
    if EXISTS:
        msg += '<ul>\n'
    for title in EXISTS_titles:
        msg += '<li>{0}</li>\n'.format(title)
    if EXISTS:
        msg += '</ul>\n'
    msg += '<p>&nbsp;</p>\n'
    html += msg
    # if UNKNOWN:
    if UNKNOWN == 1:
        msg = _('<h4>1 book had unknown errors processing the {0} format.</h4>\n').format(target)
    else:
        msg = _('<h4>{0} books had unknown errors processing the {1} formats.</h4>\n').format(UNKNOWN, target)
    if UNKNOWN:
        msg += '<ul>\n'
    for title in UNKNOWN_titles:
        msg += '<li>{0}</li>\n'.format(title)
    if UNKNOWN:
        msg += '</ul>'
    html += msg
    html += '<p>&nbsp;</p>\n<p>&nbsp;</p>\n'
    html += _('<h3>Books that had no {0} format were ignored.</h3>\n').format(target)
    return html
