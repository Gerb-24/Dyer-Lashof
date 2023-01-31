import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QFileDialog
from PyQt6 import uic
from PyQt6.QtGui import QIcon, QIntValidator

from E_inf import operad as E_inf_operad
from E_n import operad as E_n_operad
from Lie import operad as Lie_operad
from mdf_to_json import mdf_to_json_func
from json_to_tex import json_to_tex_func
import json

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('gui.ui', self)
        self.setWindowTitle("Dyer Lashof")
        self.setWindowIcon(QIcon('ui_images/appicon.ico'))
        self.setFixedSize(self.size())

        self.data = {
            'txt_file':                     '',
            'txt_dir':                      '',

            'dl_file':                      '',
            'dl_dir':                       '',

            'json_file':                    '',
            'json_dir':                     '',

            'operad':                       'E_n',

            'n':                            '',
            'max_dim':                      '',
            'max_weight':                   '',
        }

        self.le_data = {
            'n':                self.n_le,
            'max_dim':          self.max_dim_le,
            'max_weight':       self.max_weight_le,
        }

        self.file_le_data = {
            'txt_file':     self.txt_file_le,
            'dl_file':      self.dl_file_le,
            'json_file':    self.json_file_le,
        }

        self.file_type_data = {
            'txt_file':         'txt',
            'dl_file':          'json',
            'json_file':        'json',
        }

        self.file_btn_data = {
            'txt_file':     self.txt_file_btn,
            'dl_file':      self.dl_file_btn,
            'json_file':    self.json_file_btn,
        }

        self.file_dir_data = {
            'txt_file':     'txt_dir',
            'dl_file':      'dl_dir',
            'json_file':    'json_dir',
        }

        self.dir_le_data = {
        }

        self.dir_btn_data = {
        }

        # radio button data
        self.rb_btn_data = {
            'operad':  {
                'E_n':          self.E_n_btn,
                'E_inf':        self.E_inf_btn,
                'sLie':         self.sLie_btn,
                },
        }

        self.rb_bool_data = {
            'operad':  {
                'E_n':          True,
                'E_inf':        False,
                'sLie':         False,
            },
        }

        self.rb_default_data = {
            'operad':          'E_n',
        }
       
        # connecting and initialising radiobutton logic
        for var_key in self.rb_btn_data:
            for sub_key in self.rb_btn_data[var_key]:
                self.rb_btn_data[ var_key ][ sub_key ].clicked.connect( lambda _, var=var_key, sub=sub_key: self.set_rb( var_key=var, sub_key=sub ) )
            self.set_rb( var_key=var_key, sub_key=self.rb_default_data[ var_key ] )

        # connecting string logic
        onlyInt = QIntValidator()
        for tex in self.le_data:
            onlyInt.setRange(0, 99)
            self.le_data[ tex ].setValidator(onlyInt)
            self.le_data[ tex ].textChanged.connect( lambda _, t=tex: self.assign_text_to_var( tex=t ) )

        # connecting file logic
        for file in self.file_btn_data:
            self.file_btn_data[ file ].clicked.connect( lambda _, f=file: self.load_file( file=f ) )

        # connecting dir logic
        for dir_key in self.dir_btn_data:
            self.dir_btn_data[ dir_key ].clicked.connect( lambda _, d=dir_key: self.load_dir( dir_key=d ) )

        self.txt_to_json_btn.clicked.connect( self.compile_txt_to_json )
        self.compile_btn.clicked.connect( self.compile )
        self.json_to_tex_btn.clicked.connect( self.compile_json_to_tex )

        # # handling settings
        # self.save_settings_btn.clicked.connect( self.save )
        # self.load_settings()

    # multi-bool handler
    def set_rb( self, var_key='', sub_key='' ):
        for key in self.rb_bool_data[ var_key ]:
            self.rb_bool_data[ var_key ][ key ] =  key == sub_key
        self.data[ var_key ] = sub_key

        # stylessheets
        off_style = '''
        QPushButton {
            background-color: #34495e;
            border-radius: 5px;
        }
        QPushButton::hover {
            background-color: #7f8c8d;
            border-radius: 5px;
        }
        '''
        on_style = '''
        QPushButton {
            background-color: #f1c40f;
            border-radius: 5px;
            color: #34495e;
        }
        '''
        
        for key in self.rb_btn_data[ var_key ]:
            stylesheet =  on_style if self.rb_bool_data[ var_key ][ key ] else off_style
            self.rb_btn_data[ var_key ][ key ].setStyleSheet( stylesheet )

    def assign_text_to_var( self, tex='' ):
        self.data[ tex ] = self.le_data[tex].text()

    def load_file( self, file='' ):
        dir_key = self.file_dir_data[ file ]
        file_type = self.file_type_data[ file ]
        filepath, _ = QFileDialog.getOpenFileName(self, f"Load {file_type}", self.data[ dir_key ], f"{file_type.upper()}(*.{file_type})")
        self.data[ file ] = filepath  
        self.data[ dir_key ] = os.path.dirname(filepath)
        self.file_le_data[ file ].setText( os.path.basename(filepath) )


    def compile_txt_to_json( self ):
        filename = self.data[ 'txt_file' ]
        if filename == '':
            return
        mdf_to_json_func( filename )

    def compile_json_to_tex( self ):
        filename = self.data[ 'json_file' ]
        if filename == '':
            return
        json_to_tex_func( filename )

    def compile( self ):
        filename = self.data[ 'dl_file' ]
        if filename == '':
            return
        operad = self.data[ 'operad' ]
        max_dim = int( self.data[ 'max_dim' ] )
        max_weight = int( self.data[ 'max_weight' ] )
        if operad == 'sLie':
            Lie_operad( filename, max_dim, max_weight )
        elif operad == 'E_inf':
            E_inf_operad( filename, max_dim, max_weight )
        elif operad == 'E_n':
            n = int( self.data[ 'n' ] )
            E_n_operad( filename, max_dim, max_weight, n )

    # settings functions
    def save( self ):
        save_data = self.data
        json_data = json.dumps( save_data, indent=2 )
        with open("settings.json", "w") as f:
            f.write(json_data)

    def load_settings(self):
        with open("settings.json", "r") as f:
            load_data = json.loads(f.read())
        for key in load_data:
            self.data[ key ] = load_data[ key ]
        for tex in self.le_data:
            self.le_data[ tex ].setText( self.data[ tex ] )
        for file in self.file_le_data:
            file_path = self.data[ file ]
            self.file_le_data[ file ].setText( os.path.basename( file_path ) )
        for dir_key in self.dir_le_data:
            dir_path = self.data[ dir_key ]
            self.dir_le_data[ dir_key ].setText( os.path.basename( dir_path ) )
        for key in self.bool_cb_data:
            self.bool_cb_data[ key ].setChecked( self.data[ key ] )


if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.setStyleSheet(open('cssfiles/stylesheet.css').read())

    window = MyApp()
    window.show()
    try:
        sys.exit(app.exec())
    except SystemExit:
        print(' Closing Window ... ')
