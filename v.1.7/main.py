# Copyright (c) 2024, [Tymofii Dubovyi]
# Licensed under the MIT License.
# See LICENSE file for details.

import sys
from sys import argv
from PyQt5.QtCore import QThread, pyqtSignal, QSize, Qt
from PyQt5.QtGui import QIcon, QFontDatabase, QFont, QPixmap
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget, QLineEdit, QTabWidget, QVBoxLayout, QComboBox, QProgressBar, \
    QPushButton, QApplication, QSpacerItem, QSizePolicy, QAction, QMessageBox
from minecraft_launcher_lib.quilt import get_stable_minecraft_versions as get_stable_minecraft_versions_quilt
from minecraft_launcher_lib.command import get_minecraft_command
from minecraft_launcher_lib.fabric import get_stable_minecraft_versions
from minecraft_launcher_lib.forge import supports_automatic_install, install_forge_version, run_forge_installer, \
    forge_to_installed_version, find_forge_version
from minecraft_launcher_lib.install import install_minecraft_version
from minecraft_launcher_lib.utils import get_version_list, get_installed_versions, get_java_executable, \
    get_latest_version
import fabric_install
import quilt_install
import settings
from file_manager import Manager
from generate_username_r import generate_username
from uuid import uuid1
from minecraft_launcher_lib.types import MinecraftOptions
from subprocess import call
from design import apply_style


class LaunchThread(QThread):
    launch_setup_signal = pyqtSignal(str, str, str, str)
    progress_update_signal = pyqtSignal(int, int, str)
    state_update_signal = pyqtSignal(bool)
    #
    manager = Manager()
    #
    username = ''
    #
    version_id = ''
    loader_version = ''
    loader = ''
    #
    loader_dict:dict = ''
    #
    progress = 0
    progress_max = 0
    progress_label = ''
    #
    fabric_minecraft_version = ''
    quilt_minecraft_version = ''
    #

    def __init__(self):
        super().__init__()
        self.launch_setup_signal.connect(self.launch_setup)
        self.manager.log(['Starting Thread'])

    def launch_setup(self, version_id, username, loader, loader_version) -> None:
        self.version_id = version_id
        self.username = username
        self.loader = loader
        self.loader_version = loader_version

    def update_progress_label(self, value) -> None:
        self.progress_label = value
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)

    def update_progress(self, value) -> None:
        self.progress = value
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)

    def update_progress_max(self, value) -> None:
        self.progress_max = value
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)

    def run(self) -> None:
        #
        self.manager.log(['Username: ' + self.username])
        #
        self.manager.save(username=self.username)
        self.manager.save(version = self.version_id)
        self.manager.save(loader = self.loader)
        #
        try:
            self.loader_dict:dict = self.manager.load('loaders_dict')
            self.loader_dict.update({self.loader: self.version_id})
            self.manager.save(loaders_dict=self.loader_dict)
        except:
            self.manager.save(loaders_dict={
        "forge": "1.21.1",
        "vanila": get_latest_version()['release'],
        "fabric": get_stable_minecraft_versions()[0],
        "quilt": get_stable_minecraft_versions_quilt()[0]
            })
            self.loader_dict: dict = self.manager.load('loaders_dict')
            self.loader_dict.update({self.loader: self.version_id})
            self.manager.save(loaders_dict=self.loader_dict)
        #
        self.state_update_signal.emit(True)
        #
        #
        options: dict = {
            'username': self.username,
            'uuid': str(uuid1()),
            'token': '',
            'disableMultiplayer': False,
            'jvmArguments': ["-Xmx8G", "-Xms2G"]
        }
        minecraft_options = MinecraftOptions(
            username=options['username'],
            uuid=options['uuid'],
            token=options['token'],
            disableMultiplayer=options['disableMultiplayer'],
            jvmArguments=options['jvmArguments']
        )
        #
        self.manager.log([f'Installing and running: {self.loader} version: {self.version_id} {self.loader_version}'])
        java_not_found: bool
        java_not_found = get_java_executable().lower() in ['javaw', 'java']
        self.manager.log(['Java not installed or not found ! Install Java version >= 17.0' if java_not_found else 'Found Java !'])
        if java_not_found:
            self.manager.log(['Java not Found !!!'])
            QMessageBox.critical(None, 'Error', 'Java version >= 17 is required.')
            return
        #
        match self.loader:
            case 'vanila':
                install_minecraft_version(versionid=self.version_id, minecraft_directory=self.manager.minecraft_directory,
                                          callback={'setStatus': self.update_progress_label,
                                                    'setProgress': self.update_progress,
                                                    'setMax': self.update_progress_max})
                call(get_minecraft_command(version=self.version_id, minecraft_directory=self.manager.minecraft_directory,
                                   options=minecraft_options))
            case 'forge':
                if self.loader_version != '':
                    self.version_id = f'{self.version_id}-{self.loader_version}'
                else:
                    self.version_id = find_forge_version(self.version_id)
                if supports_automatic_install(self.version_id):
                    install_forge_version(versionid=self.version_id, path=self.manager.minecraft_directory,
                                          callback={'setStatus': self.update_progress_label,
                                                    'setProgress': self.update_progress,
                                                    'setMax': self.update_progress_max})
                else:
                    try:
                        run_forge_installer(self.version_id)
                    except Exception as e:
                        self.manager.log([e])

                call(get_minecraft_command(version=forge_to_installed_version(self.version_id),
                                           minecraft_directory=self.manager.minecraft_directory, options=minecraft_options))
            case 'fabric':
                try:
                    self.fabric_minecraft_version = fabric_install.install_fabric(minecraft_version=self.version_id, minecraft_directory=self.manager.minecraft_directory,
                                   callback={'setStatus': self.update_progress_label,
                                             'setProgress': self.update_progress, 'setMax': self.update_progress_max},
                                   loader_version=self.loader_version)
                except Exception as e:
                    self.manager.log(e)

                call(get_minecraft_command(version=self.fabric_minecraft_version, minecraft_directory=self.manager.minecraft_directory,
                                           options=minecraft_options))

            case 'quilt':
                try:
                    self.quilt_minecraft_version = quilt_install.install_quilt(minecraft_version=self.version_id,
                                                                                  minecraft_directory=self.manager.minecraft_directory,
                                                                                  callback={
                                                                                      'setStatus': self.update_progress_label,
                                                                                      'setProgress': self.update_progress,
                                                                                      'setMax': self.update_progress_max},
                                                                                  loader_version=self.loader_version)
                except Exception as e:
                    self.manager.log(e)

                call(get_minecraft_command(version=self.quilt_minecraft_version,
                                           minecraft_directory=self.manager.minecraft_directory,
                                           options=minecraft_options))



        self.state_update_signal.emit(False)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_tab_index = 0
        self.manager = LaunchThread.manager
        self.manager.log([f'Creating window: {settings.WINDOW_WIDTH}x{settings.WINDOW_WIDTH}'])
        #
        self.setFixedSize(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
        self.central_widget = QWidget(self)
        #
        self.logo = QLabel(self.central_widget)
        self.logo.setMaximumSize(QSize(256, 92))
        self.logo.setText('Pit Launcher')
        self.setWindowTitle('Pit Launcher')
        self.setWindowIcon(QIcon(self.manager.main_icon_path))
        self.logo.setPixmap(QPixmap(self.manager.logo_path))
        self.logo.setScaledContents(True)
        #
        self.main_font_id = QFontDatabase.addApplicationFont(self.manager.main_font_path)
        self.main_font_family = QFontDatabase.applicationFontFamilies(self.main_font_id)[0]
        self.main_font = QFont(self.main_font_family)
        self.main_font.setPointSize(settings.main_font_size)
        #
        self.sub_font_id = QFontDatabase.addApplicationFont(self.manager.sub_font_path)
        self.sub_font_family = QFontDatabase.applicationFontFamilies(self.sub_font_id)[0]
        self.sub_font = QFont(self.sub_font_family)
        self.sub_font.setPointSize(settings.sub_font_size)
        #
        self.title_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.play_spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        #
        self.username = QLineEdit(self.central_widget)
        #
        self.username.setPlaceholderText('Username')
        #
        try:
            username = self.manager.load('username')
            if username is None or username == '':
                username =  generate_username()[0]
                self.manager.save(username = username)
            self.username.setText(username)
            self.username.setFont(self.main_font)
        except KeyError:
            self.username.setText(generate_username()[0])
        #
        def save_username() -> None:
            self.manager.save(username=self.username.text())
        self.username.textChanged.connect(save_username)
        #
        self.tab_widget = QTabWidget()
        self.current_loader = {0:'vanila', 1:'forge', 2:'fabric', 3:'quilt'}
        self.current_tab = {'vanila': 0, 'forge':1, 'fabric':2, 'quilt':3}
        #
        self.vanila_tab = QWidget()
        self.vanila_layout = QVBoxLayout(self.vanila_tab)

        self.vanilla_combobox = QComboBox()
        self.vanila_list = [version['id'] for version in get_version_list() if version['type'] == 'release']
        self.vanila_layout.addWidget(self.vanilla_combobox)
        self.vanilla_combobox.setFont(self.main_font)
        self.vanilla_combobox.addItems(self.vanila_list)
        self.vanila_tab.setMinimumWidth(200)
        #
        self.forge_tab = QWidget()
        self.forge_layout = QVBoxLayout(self.forge_tab)

        self.forge_combobox = QComboBox()
        self.forge_list = [version for version in self.vanila_list if find_forge_version(version) is not None]
        self.forge_combobox.addItems(self.forge_list)
        self.forge_layout.addWidget(self.forge_combobox)
        self.forge_combobox.setFont(self.main_font)
        #
        self.fabric_tab = QWidget()
        self.fabric_layout = QVBoxLayout(self.fabric_tab)

        self.fabric_combobox = QComboBox()
        self.fabric_list = get_stable_minecraft_versions()
        self.fabric_combobox.addItems(self.fabric_list)
        self.fabric_layout.addWidget(self.fabric_combobox)
        self.fabric_combobox.setFont(self.main_font)
        #
        self.quilt_tab = QWidget()
        self.quilt_layout = QVBoxLayout(self.quilt_tab)

        self.quilt_combobox = QComboBox()
        self.quilt_list = get_stable_minecraft_versions_quilt()
        self.quilt_combobox.addItems(self.quilt_list)
        self.quilt_layout.addWidget(self.quilt_combobox)
        self.quilt_combobox.setFont(self.main_font)
        #
        try:
            self.manager.log(['Adding Vanila versions'])
            self.vanilla_combobox.setCurrentText(self.manager.load('loaders_dict')['vanila'])
            self.manager.log(['Adding Forge versions'])
            self.forge_combobox.setCurrentText(self.manager.load('loaders_dict')['forge'])
            self.manager.log(['Adding Fabric versions'])
            self.fabric_combobox.setCurrentText(self.manager.load('loaders_dict')['fabric'])
            self.manager.log(['Adding Quilt versions'])
            self.quilt_combobox.setCurrentText(self.manager.load('loaders_dict')['quilt'])
        except:
            self.manager.log(['Error ! {', 'Failed adding versions !', '} Skipping !'])
        #
        self.settings_tab = QWidget()
        self.theme_combobox = QComboBox()
        #
        self.tab_widget.addTab(self.vanila_tab, "Vanilla")
        self.tab_widget.addTab(self.forge_tab, "Forge")
        self.tab_widget.addTab(self.fabric_tab, "Fabric")
        self.tab_widget.addTab(self.quilt_tab, "Quilt")
        #
        self.settings_layout = QVBoxLayout(self.settings_tab)
        self.settings_layout.addWidget(self.theme_combobox)
        #
        self.theme_combobox.addItems([key.capitalize() for key in self.manager.load_styles().keys()])
        self.theme_combobox.currentIndexChanged.connect(self.apply_current_style)
        self.theme_combobox.setFont(self.main_font)
        #
        gap_tab = QWidget()
        gap_tab2 = QWidget()
        self.tab_widget.addTab(gap_tab, " | ")

        self.tab_widget.tabBar().setTabEnabled(self.tab_widget.indexOf(gap_tab), False)
        self.tab_widget.tabBar().setUsesScrollButtons(False)
        self.tab_widget.tabBar().setStyleSheet("""QTabBar::tab:disabled {background: transparent;border: none;}""")
        #
        self.installed_tab = QWidget()
        #
        self.installed_combobox = QComboBox()
        self.installed_versions_list = [version['id'] for version in get_installed_versions(minecraft_directory=self.manager.minecraft_directory)]
        self.installed_combobox.addItems(self.installed_versions_list)
        #
        self.installed_search = QLineEdit()
        self.installed_search.setPlaceholderText('Search for version')
        self.installed_search.setFont(self.main_font)
        self.installed_search.textChanged.connect(self.filter_items)

        self.installed_layout = QVBoxLayout(self.installed_tab)
        self.installed_layout.addWidget(self.installed_search)
        self.installed_layout.addWidget(self.installed_combobox)
        self.installed_combobox.setFont(self.main_font)
        #
        self.tab_widget.addTab(self.installed_tab, 'Installed')
        self.tab_widget.addTab(gap_tab2, " | ")
        self.tab_widget.tabBar().setTabEnabled(self.tab_widget.indexOf(gap_tab2), False)
        self.tab_widget.addTab(self.settings_tab, "Theme")
        #
        self.tab_widget.setFont(self.main_font)
        try:
            self.tab_widget.setCurrentIndex(self.current_tab[self.manager.load('loader')])
        except:
            self.manager.log(['Error !', 'No tab index found !', 'Skipping !'])
        self.progress_spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        #
        self.start_progress_label = QLabel(self.central_widget)
        self.start_progress_label.setText('')
        self.start_progress_label.setVisible(False)
        #
        self.start_progress = QProgressBar(self.central_widget)
        self.start_progress.setProperty('value', 24)
        self.start_progress.setVisible(False)
        #
        self.start_button = QPushButton(self.central_widget)
        self.start_button.setFont(self.sub_font)
        self.start_button.setText('Play')
        self.start_button.clicked.connect(self.launch_game)
        #
        def on_tab_changed() -> None:
            self.current_tab_index = self.tab_widget.currentIndex()
            match self.current_tab_index:
                case 7:
                    self.start_button.setDisabled(True)
                case 5:
                    if len(self.installed_versions_list) == 0:
                        self.start_button.setDisabled(True)
                    else:
                        self.start_button.setDisabled(False)
                case _:
                    self.start_button.setDisabled(False)
        #
        self.tab_widget.currentChanged.connect(on_tab_changed)
        #
        self.vertical_layout = QVBoxLayout(self.central_widget)
        self.vertical_layout.setContentsMargins(15, 15, 15, 15)
        self.vertical_layout.addWidget(self.logo, 0, Qt.AlignmentFlag.AlignHCenter)
        self.vertical_layout.addItem(self.title_spacer)
        self.vertical_layout.addWidget(self.username)
        self.vertical_layout.addItem(self.progress_spacer)
        self.vertical_layout.addWidget(self.start_progress_label)
        self.vertical_layout.addWidget(self.start_progress)
        self.vertical_layout.addWidget(self.start_button)
        self.vertical_layout.addItem(self.play_spacer)
        self.vertical_layout.addWidget(self.tab_widget)

        self.launch_thread = LaunchThread()
        self.launch_thread.state_update_signal.connect(self.state_update)
        self.launch_thread.progress_update_signal.connect(self.update_progress)

        self.setCentralWidget(self.central_widget)

        self.apply_loaded_style()

    def closeEvent(self, event):
        try:
            self.manager.save(loader=self.current_loader[self.current_tab_index])
        except:
            ...
        reply = QMessageBox.question(self, 'Quit?',
                                     'Are you sure you want to quit?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.manager.log(['Closing App'])
            if not type(event) == bool:
                event.accept()
            else:
                exit()
        else:
            if not type(event) == bool:
                event.ignore()

    def filter_items(self) -> None:
        """
        Filter items based on a search text, update the installed selection based on the filtered items,
        and enable or disable the start button accordingly.
        """
        filter_text = self.installed_search.text().lower()
        self.installed_combobox.clear()
        filtered_items = [item for item in self.installed_versions_list if filter_text in item.lower()]
        self.installed_combobox.addItems(filtered_items)
        if len(filtered_items) == 0:
            self.start_button.setDisabled(True)
        else:
            self.start_button.setDisabled(False)

    def state_update(self, value) -> None:
        self.start_button.setDisabled(value)
        self.start_progress_label.setVisible(value)
        self.start_progress.setVisible(value)

    def update_progress(self, progress, max_progress, label) -> None:
        self.start_progress.setValue(progress)
        self.start_progress.setMaximum(max_progress)
        self.start_progress_label.setText(label)

    def apply_current_style(self):
        style_name = self.theme_combobox.currentText().lower()
        style = apply_style(self.manager.load_styles()[style_name], self.sub_font_family)
        self.setStyleSheet(style[0])
        self.tab_widget.setStyleSheet(style[1])
        self.manager.save(current_style = style_name)

    def apply_loaded_style(self):
        style_name = self.manager.load('current_style') or 'dark'
        #
        try:
            style = apply_style(self.manager.load_styles()[style_name], self.sub_font_family)
            self.setStyleSheet(style[0])
            self.tab_widget.setStyleSheet(style[1])
            #
            self.theme_combobox.setCurrentText(style_name.capitalize())
        except KeyError:
            self.manager.log([f'No style {style_name} found !'])

    def launch_game(self) -> None:
        current_combobox = {0:self.vanilla_combobox.currentText(), 1:self.forge_combobox.currentText(), 2:self.fabric_combobox.currentText(), 3:self.quilt_combobox.currentText()}
        match self.current_tab_index:
            case 5:
                version = self.installed_combobox.currentText()
                loader = 'vanila'
                loader_version = ''
                if 'fabric' in version:
                    version, loader_version = version.split('-')[-1], version.split('-')[2]
                    loader = 'fabric'
                elif 'quilt' in version:
                    version, loader_version = version.split('-')[-1], version.split('-')[2]
                    loader = 'quilt'
                elif 'forge' in version:
                    version, loader_version = version.split('-')[0], version.split('-')[-1]
                    loader = 'forge'
            case _:
                version = current_combobox[self.current_tab_index]
                loader_version = ''
                loader = self.current_loader[self.current_tab_index]

        self.launch_thread.launch_setup_signal.emit(version, self.username.text() if self.username.text() != '' else generate_username()[0], loader, loader_version)
        self.launch_thread.start()


if __name__ == '__main__':
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app = QApplication(argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())