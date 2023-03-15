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

            'n':                            0,
            'max_dim':                      0,
            'max_weight':                   0,
        }

        self.int_data = {
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

        # connecting int logic
        onlyInt = QIntValidator()
        for tex in self.int_data:
            onlyInt.setRange(0, 99) # this makes sure that we can only use integers
            self.int_data[ tex ].setValidator(onlyInt)
            self.int_data[ tex ].textChanged.connect( lambda _, t=tex: self.assign_int_to_var( tex=t ) )

        # connecting file logic
        for file in self.file_btn_data:
            self.file_btn_data[ file ].clicked.connect( lambda _, f=file: self.load_file( file=f ) )

        # connecting dir logic
        for dir_key in self.dir_btn_data:
            self.dir_btn_data[ dir_key ].clicked.connect( lambda _, d=dir_key: self.load_dir( dir_key=d ) )

        self.txt_to_json_btn.clicked.connect( self.compile_txt_to_json )
        self.compile_btn.clicked.connect( self.compile )
        self.json_to_tex_btn.clicked.connect( self.compile_json_to_tex )

        # handling settings
        self.save_settings_btn.clicked.connect( self.save )
        self.load_settings()

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

    def assign_int_to_var( self, tex='' ):
        str = self.int_data[tex].text()
        self.data[ tex ] = 0 if not str else int(str)

    def load_file( self, file='' ):
        dir_key = self.file_dir_data[ file ]
        file_type = self.file_type_data[ file ]
        filepath, _ = QFileDialog.getOpenFileName(self, f"Load {file_type}", self.data[ dir_key ], f"{file_type.upper()}(*.{file_type})")
        self.data[ file ] = filepath  
        self.data[ dir_key ] = os.path.dirname(filepath)
        self.file_le_data[ file ].setText( os.path.basename(filepath) )


    def compile_txt_to_json( self ):
        self.log_out('empty')
        filename = self.data[ 'txt_file' ]
        if filename == '':
            self.log_out('no_file')
            return
        try:
            mdf_to_json_func( filename )
            self.log_out('done')
        except FileNotFoundError:
            self.log_out('not_found')
        except Exception:
            self.log_out('general')
        
    def compile_json_to_tex( self ):
        self.log_out('empty')
        filename = self.data[ 'json_file' ]
        if filename == '':
            self.log_out('no_file')
            return
        try:
            json_to_tex_func( filename )
            self.log_out('done')
        except FileNotFoundError:
            self.log_out('not_found')
        except Exception:
            self.log_out('general')

    def compile( self ):
        self.log_out('empty')
        filename = self.data[ 'dl_file' ]
        if filename == '':
            self.log_out('no_file')
            return
        operad = self.data[ 'operad' ]
        max_dim = int( self.data[ 'max_dim' ] )
        max_weight = int( self.data[ 'max_weight' ] )
        if max_weight < 2:
            self.log_out('weight')
            return
        try:
            if operad == 'sLie':
                Lie_operad( filename, max_dim, max_weight )
            elif operad == 'E_inf':
                E_inf_operad( filename, max_dim, max_weight )
            elif operad == 'E_n':
                n = int( self.data[ 'n' ] )
                if n < 1:
                    self.log_out( 'n' )
                    return
                E_n_operad( filename, max_dim, max_weight, n )
            self.log_out('done')
        except FileNotFoundError:
            self.log_out('not_found')
        except Exception:
            self.log_out('general+')

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
        for tex in self.int_data:
            self.int_data[tex].setText( str( self.data[ tex ] ) )
        for file in self.file_le_data:
            file_path = self.data[ file ]
            self.file_le_data[ file ].setText( os.path.basename( file_path ) )
        for dir_key in self.dir_le_data:
            dir_path = self.data[ dir_key ]
            self.dir_le_data[ dir_key ].setText( os.path.basename( dir_path ) )

    def log_out(self, key):
        print('this is called')
        logging_dic = {
            'empty':        'Currently compiing...',
            'no_file':      'ERROR: No file currently opened',
            'not_found':    'ERROR: The input file does not seem to exist anymore',
            'general':      'ERROR: Something seems to be wrong in the input file',
            'general+':     'ERROR: Something seems to be wrong in the input file, or the maximal degree might be too low',
            'weight':       'ERROR: The input weight has to be at least 2',
            'n':            'ERROR: The input n has to be at least 1',
            'done':         'Done compiling, a new file is saved in the directory of the input file'
        }
        self.log.setText( logging_dic[ key ] )

if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.setStyleSheet(open('cssfiles/stylesheet.css').read())

    window = MyApp()
    window.show()
    try:
        sys.exit(app.exec())
    except SystemExit:
        print(' Closing Window ... ')
