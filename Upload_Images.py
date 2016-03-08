# -*- coding: utf-8 -*-
"""
/***************************************************************************
 UploadImages
                                 A QGIS plugin
 Upload Images
                              -------------------
        begin                : 2016-02-22
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Mário Fraga
        email                : mariofraga@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from Upload_Images_dialog import UploadImagesDialog
from dbconnection_dialog import dbconnectionDialog
import os.path
from PyQt4.QtSql import *
from PyQt4.QtSql import QSqlQuery
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import qgis
from qgis.core import *
from qgis.gui import QgsAttributeTableModel
import PyQt4.QtGui
import os.path
import shutil





class UploadImages:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'UploadImages_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = UploadImagesDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Upload Images')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'UploadImages')
        self.toolbar.setObjectName(u'UploadImages')

        self.dlg.pushButton.clicked.connect(self.selectOutputFile)

        self.dlg.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        self.dlg.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.copyFiles)
        self.dlg.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.cancelAction)
        self.dbdialog = dbconnectionDialog()


    def selectOutputFile(self):
        #filename = QFileDialog.getSaveFileName(self.dlg, "Selecione ","", '*.txt')
        filename = QFileDialog.getExistingDirectory(self.dlg, "Selecione ","")
        self.dlg.lineEdit.setText(filename)

    def cancelAction(self):
        self.dlg.reject()

    def dbInsertData(self):
        pass

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&Task Manager'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar






    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('UploadImages', message)




    def copyFiles(self):

        actlayer1 = qgis.utils.iface.activeLayer()
        features1 = actlayer1.selectedFeatures()
        self.dlg.progressBar.setMaximum(len(features1))
        self.dlg.progressBar.setValue(0)

        msgBox = PyQt4.QtGui.QMessageBox()


        if(self.dlg.lineEdit.text()):
            pass
        else:
            msgBox.setText("Selecione a Pasta de Destino!")
            msgBox.setStandardButtons(QMessageBox.Ok);
            msgBox.exec_()
            return

        actlayer = qgis.utils.iface.activeLayer()
        index = self.modelt.index(0,0)
        columnindex=0

        codFilename = 0
        codFilepath = 0

        for i in range(0,self.modelt.columnCount(index)):
            qresult = self.modelt.headerData(i, Qt.Horizontal, 0)
            if qresult == "filename":
                codFilename = i
            if qresult == "filepath":
                codFilepath = i

        idlist = []
        curruid = 100 #self.dlg.comboBox.itemData(self.dlg.comboBox.currentIndex())
        contadorBarra = 0
        for row in range(self.modelt.rowCount()):
            str(self.moveArquivo(self.modelt.data(self.modelt.index(row,codFilepath),0), self.modelt.data(self.modelt.index(row,codFilename),0)))
            contadorBarra += 1

            id = self.modelt.data(self.modelt.index(row,columnindex),0)
            self.dlg.progressBar.setValue(contadorBarra)
            idlist.append(id)


        msgBox.setText("Imagens Copiadas com Sucesso!")
        msgBox.setStandardButtons(QMessageBox.Ok);
        msgBox.exec_()

        self.dlg.accept()

        print "Saiuuuu"

    def moveArquivo(self, caminhoArquivo, nomeArquivio):
        #print "Nome Original111 => " + str(caminhoArquivo)
        #print "Nome Original111 => " + str(nomeArquivio)
        diretorio = self.dlg.lineEdit.text()
        diretorioNovoArquivo = os.path.dirname(os.path.realpath(caminhoArquivo))
        if not os.path.exists(diretorio + diretorioNovoArquivo):
            os.makedirs(diretorio + diretorioNovoArquivo)

        shutil.copy2(caminhoArquivo, diretorio + caminhoArquivo)
        #print  "Pasta destino" + self.dlg.lineEdit.text
        return


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/UploadImages/upload.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Upload Images'),
            callback=self.run,
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/UploadImages/upload.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Upload Images11111'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Upload Images'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def populateTable(self):
        actlayer = qgis.utils.iface.activeLayer()
        #label = "Feicoes selecionadas em " + actlayer.name() + ":"
        # Add some textual items
        features = actlayer.selectedFeatures()
        fidlist = []

        for f in features:
            fidlist.append(f[self.keycolumn])

        selection=[]
        strsel=self.keycolumn + " IN ("



        for fid in fidlist:
            selection.append(fid)
            strsel=strsel+ "'" + str(fid) + "',"

        strsel=strsel[:-1] + ")"
        actlayer.setSubsetString(strsel)


        cache = QgsVectorLayerCache(actlayer, 50000)
        self.modelt = QgsAttributeTableModel(cache)
        self.modelt.loadLayer()
        table = self.dlg.tableView
        table.setModel(self.modelt)
         # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        # global curruid
        # curruid = self.dlg.comboBox.itemData(self.dlg.comboBox.currentIndex())
        self.dlg.exec_()


    def run(self):
        """Run method that performs all the real work"""
        #self.dlg.comboBox.clear()
        actlayer = qgis.utils.iface.activeLayer()
        global db
        db = QSqlDatabase.addDatabase("QPSQL")
        if db.isValid():
            dsu = QgsDataSourceURI( actlayer.dataProvider().dataSourceUri() )
            realmsc = actlayer.dataProvider().dataSourceUri()
            db.setHostName(dsu.host())
            db.setDatabaseName(dsu.database())
            db.setUserName(dsu.username())
            db.setPassword(dsu.password())
            db.setPort(int(dsu.port()))
            self.keycolumn = dsu.keyColumn()
            ok = db.open()
            if ok:
                teste = 1
                query = db.exec_("""select * from prodser.user""")
                    # iterate over the rows
                #while query.next():
                #    record = query.record()
                 #   name = record.value(1)
                 #   uid = record.value(0)
                 #   self.dlg.comboBox.addItem(name, uid)
                self.populateTable()
            else:
                self.dbdialog.setRealm(realmsc)
                self.dbdialog.setUsername(QgsDataSourceURI( actlayer.dataProvider().dataSourceUri()).username())
                if self.dbdialog.exec_() == QDialog.Accepted:
                    db.setUserName(self.dbdialog.getUsername())
                    db.setPassword(self.dbdialog.getPassword())
                    ok = db.open()
                    if ok:
                        pass
                        query = db.exec_("""select * from prodser.user""")
                        # iterate over the rows
                      #  while query.next():
                        #    record = query.record()
                        #    name = record.value(1)
                        #    uid = record.value(0)
                        #    self.dlg.comboBox.addItem(name, uid)
                        self.populateTable()
                    else:
                        print db.lastError().text()

