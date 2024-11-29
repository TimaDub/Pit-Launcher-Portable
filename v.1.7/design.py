def apply_style(style, font):
    background_color, text_color, button_color, progress_bar_color, progress_bar_text_color, selected_tab_color, selected_tab_background_color = style

    main_style = f"""
                QWidget {{
                    background-color: {background_color};
                    color: {text_color};
                }}
                QPushButton {{
                    background-color: {background_color};
                    color: {text_color};
                    border: 1px solid {button_color};
                    border-radius: 5px;
                    padding: 5px;
                }}
                QPushButton:disabled {{
                    background-color: {background_color};
                    color: gray;
                    border: 1px solid gray;
                    border-radius: 5px;
                    padding: 5px;
                }}
                QLineEdit {{
                    background: {background_color};
                    color: {text_color};
                    border: 1px solid {button_color};
                    border-radius: 5px;
                    padding: 5px;
                }}
                QComboBox {{
                    background-color: {background_color};
                    color: {text_color};
                    border: 1px solid {button_color};
                    border-radius: 5px;
                }}
                QCheckBox {{
                    color: {text_color};
                }}
                QTabWidget::pane {{
                    border: 1px solid {button_color};
                }}
                QTabBar::tab {{
                    background: {background_color};
                    color: {text_color};
                    border: 1px solid {button_color};
                    border-top-left-radius: 5px;
                    border-top-right-radius: 5px;
                    padding: 5px;
                }}
                QProgressBar {{
                color: {progress_bar_text_color};
                text-align: center;
                font-family : {font};
                font-size : 28px;
                background: {background_color};
                border-radius: 5px;
                }}
                QProgressBar::chunk{{
                    border-radius: 5px;
                    background: {progress_bar_color};
                }}
                QCheckBox::indicator::disabled{{
                    image: url(assets/images/checkbox/checkbox_disabled.ico);
                }}

                QComboBox QAbstractItemView {{
                    background-color: {background_color};
                    selection-background-color: {text_color};
                    selection-color: {background_color};
                    color: {text_color};
                }}
                """
    tab_style = f"""
                        QTabBar::tab:selected {{
                            background: {selected_tab_background_color};
                            font-family : {font};
                            font-size : 18px;
                            color: {selected_tab_color}
                        }}
                    """
    return main_style, tab_style