# -*- coding: utf-8 -*-
"""
/***************************************************************************
 sipamsar
                                 A QGIS plugin
 Atribui uma feição a um usuário
                              -------------------
        begin                : 2016-02-02
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Alex Lopes Pereira
        email                : alex.pereira@sipam.gov.br
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
from sipamsar_dialog import sipamsarDialog
from dbconnection_dialog import dbconnectionDialog
from Upload_Images_dialog import UploadImagesDialog
from Upload_Images import UploadImages
import os.path
from PyQt4.QtSql import *
from PyQt4.QtSql import QSqlQuery
import qgis
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import QgsAttributeTableModel
import PyQt4.QtGui

class sipamsar:
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
            'sipamsar_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = sipamsarDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Gerenciador de Tarefas')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'sipamsar')
        self.toolbar.setObjectName(u'sipamsar')
        self.dlg.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        self.dlg.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.dbInsertData)
        self.dlg.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.cancelAction)

        self.dbdialog = dbconnectionDialog()




        # self.dbdialog.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        # self.dbdialog.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.getCredentials)
        # self.dbdialog.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.cancelAction)

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
        return QCoreApplication.translate('sipamsar', message)


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
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)
        return action

    def initGui(self):

        # create taskAction that will start metadata editor
        self.taskAction = QAction(QIcon(":/plugins/sipamsar/icon.png"), QCoreApplication.translate("sipamsar", "Task Manager"), self.iface.mainWindow())
        self.taskAction.setStatusTip(QCoreApplication.translate("sipamsar", "Task Manager"))
        self.taskAction.setWhatsThis(QCoreApplication.translate("sipamsar", "Task Manager"))
        self.iface.addPluginToMenu("sipamsar", self.taskAction)

        # create editAction that will start metadata editor
        self.uploadAction = QAction(QIcon(":/plugins/sipamsar/upload.png"), QCoreApplication.translate("sipamsar", "Task Manager"), self.iface.mainWindow())
        self.uploadAction.setStatusTip(QCoreApplication.translate("sipamsar", "Task Manager"))
        self.uploadAction.setWhatsThis(QCoreApplication.translate("sipamsar", "Task Manager"))
        self.iface.addPluginToMenu("sipamsar", self.taskAction)

        self.toolBar = self.iface.addToolBar(QCoreApplication.translate("sipamsar", "Task Manager"))
        self.toolBar.setObjectName(QCoreApplication.translate("sipamsar", "Task Manager"))

        self.taskAction.triggered.connect(self.doTask)
        self.uploadAction.triggered.connect(self.doUpload)

        self.toolBar.addAction(self.taskAction)
        self.toolBar.addAction(self.uploadAction)


    def doTask(self):
        self.run()

    def doUpload(self):
        dlg2  = UploadImages(self.iface)
        dlg2.run()


    def unload(self):

        """Removes the plugin menu item and icon from QGIS GUI."""

        self.iface.removePluginVectorMenu(self.tr("sipamsar"),self.taskAction)
        self.iface.removePluginVectorMenu(self.tr("sipamsar"),self.uploadAction)

        self.iface.removeToolBarIcon(self.taskAction)
        self.iface.removeToolBarIcon(self.uploadAction)


    def dbInsertData(self):
        actlayer = qgis.utils.iface.activeLayer()
        index = self.modelt.index(0,0)
        columnindex=0
        for i in range(0,self.modelt.columnCount(index)):
            qresult = self.modelt.headerData(i, Qt.Horizontal, 0)
            if self.keycolumn == qresult:
                columnindex=i
        #print "columnindex: ",columnindex,"row count: ", modelt.rowCount()
        idlist = []
        curruid = self.dlg.comboBox.itemData(self.dlg.comboBox.currentIndex())
        for row in range(self.modelt.rowCount()):
            index = self.modelt.index(row,columnindex)
            id = self.modelt.data(index,columnindex)
            idlist.append(id)

        querystr = "SELECT pg_catalog.obj_description(c.oid) AS table_comment FROM pg_class c WHERE c.relname = '" + actlayer.name() + "' limit 1"
        query = db.exec_(querystr)
        query.next()
        record = query.record()
        tablename = record.value(0)

        querystr2 = "SELECT d.nspname AS schema_name FROM pg_class c LEFT JOIN pg_namespace d ON d.oid = c.relnamespace WHERE c.relname = '" + tablename + "'"
        query = db.exec_(querystr2)
        query.next()
        record = query.record()
        schemaname = record.value(0)
        fullname = schemaname + "." + tablename
        for id in idlist:
            # create an item with a caption
            queryinsert = QSqlQuery()
            querystr3 = "INSERT INTO " + fullname + " (ref_index, ref_user) VALUES (:ref_index, :ref_user)"
            queryinsert.prepare(querystr3)
            queryinsert.bindValue(":ref_user", curruid)
            queryinsert.bindValue(":ref_index", id)
            print "id="+str(id)+", curruid="+str(curruid)+", fullname="+fullname
            testquery = queryinsert.exec_()
            if testquery:
                print "inserted: ", id
            else:
                print "not inserted: "+ id

        actlayer.setSubsetString("")
        self.dlg.accept()

    def cancelAction(self):
        self.dlg.reject()

    # def getCredentials(self):


    def populateTable(self):
        actlayer = qgis.utils.iface.activeLayer()
        label = "Feicoes selecionadas em " + actlayer.name() + ":"
        self.dlg.label_2.setText(label)

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
        self.dlg.comboBox.clear()
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
                query = db.exec_("""select * from prodser.user""")
                # iterate over the rows
                while query.next():
                    record = query.record()
                    name = record.value(1)
                    uid = record.value(0)
                    self.dlg.comboBox.addItem(name, uid)
                self.populateTable()
            else:
                self.dbdialog.setRealm(realmsc)
                self.dbdialog.setUsername(QgsDataSourceURI( actlayer.dataProvider().dataSourceUri()).username())
                if self.dbdialog.exec_() == QDialog.Accepted:
                    db.setUserName(self.dbdialog.getUsername())
                    db.setPassword(self.dbdialog.getPassword())
                    ok = db.open()
                    if ok:
                        query = db.exec_("""select * from prodser.user""")
                        # iterate over the rows
                        while query.next():
                            record = query.record()
                            name = record.value(1)
                            uid = record.value(0)
                            self.dlg.comboBox.addItem(name, uid)
                        self.populateTable()
                    else:
                        print db.lastError().text()







