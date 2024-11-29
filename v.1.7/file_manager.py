# Copyright (c) 2024, [Tymofii Dubovyi]
# Licensed under the MIT License.
# See LICENSE file for details.

import sys
from functools import lru_cache
from os import path, mkdir, scandir
from datetime import datetime
from json import load, JSONDecodeError, dump
from settings import directory_name
from minecraft_launcher_lib.utils import get_minecraft_directory

class Manager:
    def __init__(self):
        self.minecraft_directory = get_minecraft_directory().replace('minecraft', directory_name)
        self.launcher_properties_path = path.join(self.minecraft_directory, 'launcher_properties.json')
        self.logs_path = path.join(self.minecraft_directory, '.pit_logs')
        self.workspace_path = path.join(self.minecraft_directory, '.pit')
        self.images_path: str = self.resource_path('assets/images/')
        self.fonts_path: str = self.resource_path('assets/fonts/')
        self.base_styles_path: str = self.resource_path('assets/styles')
        self.styles_path = path.join(self.workspace_path, 'styles')
        #
        self.logo_path = path.join(self.images_path, 'logos/logo.png')
        self.main_icon_path = path.join(self.images_path, "logos/icon.png")
        self.main_font_path = path.join(self.fonts_path, 'main_font.ttf')
        self.sub_font_path = path.join(self.fonts_path, 'sub_font.ttf')
        #
        self.time_start = datetime.now()
        #
        try:
            mkdir(self.minecraft_directory)
        except FileExistsError:
            print('Minecraft folder exists')
        #
        try:
            mkdir(self.workspace_path)
        except FileExistsError:
            print('Workspace folder exists')
        #
        try:
            with open(self.launcher_properties_path, 'x'):
                ...
        except FileExistsError:
            print('Json exists')
        #
        try:
            mkdir(self.logs_path)
        except FileExistsError:
            print('Logs Folder exists')
        #
        try:
            mkdir(self.styles_path)
        except FileExistsError:
            print('Styles Folder exists')

    def load(self, arg):
        try:
            with open(self.launcher_properties_path, 'r+', encoding='utf-8') as launcher_properties:
                properties = load(launcher_properties)
                return properties[arg]
        except JSONDecodeError:
            self.log(['Error in loading: ' + arg])
            return None
        except KeyError as Error:
            self.log(['Error in loading: ' + arg])
            return None


    def save(self, **kwargs):
        try:
            with open(self.launcher_properties_path, 'r', encoding='utf-8') as launcher_properties:
                properties = load(launcher_properties)
        except (FileNotFoundError, JSONDecodeError):
            properties = {}

        properties.update(kwargs)

        with open(self.launcher_properties_path, 'w', encoding='utf-8') as launcher_properties:
            dump(properties, launcher_properties, indent=4)

    def log(self, logs:list):
        with open(path.join(self.logs_path, str(self.time_start).split('.')[0].replace(':', '-')
                .replace(' ', '_')) + '.log', 'a+', encoding='utf-8') as log:
            for log_ in logs:
                log.write(str(log_) + '\n' + '-' * 20 + '\n')


    @lru_cache
    def load_styles(self) -> dict:
        styles = {}
        for style_file in sorted(scandir(self.base_styles_path), key=lambda d: d.stat().st_mtime):
            with open(path.join(self.base_styles_path, style_file.name), 'r+', encoding='utf-8') as style:
                style = load(style)
                style_file = style_file.name.replace('.json','')
                styles.update({style_file: style[style_file]})
        for style_file in sorted(scandir(self.styles_path), key=lambda d: d.stat().st_mtime):
            with open(path.join(self.styles_path, style_file.name), 'r+', encoding='utf-8') as style:
                style = load(style)
                style_file = style_file.name.replace('.json','')
                styles.update({style_file: style[style_file]})
        return styles

    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            return path.join(sys._MEIPASS, relative_path)
        return path.join(path.abspath("."), relative_path)
