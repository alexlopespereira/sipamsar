# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Producao
                                 A QGIS plugin
 teste
                              -------------------
        begin                : 2016-11-18
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Luis
        email                : engnavalmb@yahoo.com
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
import resources
from producao_dialog import ProducaoDialog
import os.path
from PyQt4.QtSql import *
from PyQt4.QtSql import QSqlQuery
import qgis
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import os.path
import time
from datetime import date
import datetime
import sys, csv

class Producao:
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
            'Producao_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = ProducaoDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Producao')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Producao')
        self.toolbar.setObjectName(u'Producao')

        self.contador = 0
        self.dlg.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(lambda: self.popula(1))
        self.dlg.buttonBox.button(QDialogButtonBox.Save).clicked.connect(self.salvar_tabela)


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
        return QCoreApplication.translate('Producao', message)


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

        icon_path = ':/plugins/Producao/producao.png'
        action = self.add_action(icon_path, text=self.tr(u'Produção'), callback=self.run, parent=self.iface.mainWindow())
        #action.setCheckable(True)
        #self.nearestFeatureMapTool.setAction(action)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&Producao'),action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def conexao(self, camada):
        try:
            self.db = QSqlDatabase.addDatabase("QPSQL")
            if self.db.isValid():
                dsu = QgsDataSourceURI(camada.dataProvider().dataSourceUri() )
                self.schema = dsu.schema()
                self.db.setHostName(dsu.host())
                self.db.setDatabaseName(dsu.database())
                self.db.setUserName(dsu.username())
                self.db.setPassword(dsu.password())
                self.db.setPort(int(dsu.port()))
                self.keycolumn = dsu.keyColumn()
                self.ok = self.db.open()
        except:
            raise

    def popula(self,flag):

        if flag == 0:
            hoje = datetime.datetime.now()
            ano_corrente = hoje.year
            mes_corrente = hoje.month
            dia_corrente = hoje.day
            data1 = str(ano_corrente) + '-'+ str(1) + '-' + str(1)
            data2 = str(ano_corrente) + '-'+ str(mes_corrente) + '-' + str(dia_corrente)
            self.dlg.data1.setDateTime(datetime.datetime.strptime(data1, "%Y-%m-%d"))
            self.dlg.data2.setDateTime(datetime.datetime.strptime(data2, "%Y-%m-%d"))
        else:
            dt1 = self.dlg.data1.date()
            dt2 = self.dlg.data2.date()
            if dt1 > dt2:
                QMessageBox.about(None, 'Erro',u'Data de início tem que ser anterior a data de fim')

            data1 = str(dt1.year()) + '-'+ str(dt1.month()) + '-' + str(dt1.day())
            data2 = str(dt2.year()) + '-'+ str(dt2.month()) + '-' + str(dt2.day())

        consulta = QSqlQuery(self.db)
        consulta_producao = 'select * from amazoniasar.retorna_producao(:data1,:data2)'
        consulta.prepare(consulta_producao)
        consulta.bindValue(':data1', data1)
        consulta.bindValue(':data2', data2)
        consulta.exec_()
        self.model = QSqlTableModel()
        self.model.setQuery(consulta)
        self.model.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.model.select()
        self.model = QSqlTableModel()
        self.model.setQuery(consulta)
        self.model.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.model.select()
        self.view = self.dlg.tableView
        self.view.setModel(self.model)
        self.dlg.show()
        self.dlg.exec_()

    def salvar_tabela(self):
        path = QFileDialog.getSaveFileName(None, 'Salvar arquivo', '', 'CSV(*.csv)')
        if path != '':
            with open(path, 'wb') as stream:
                writer = csv.writer(stream)
                writer.writerow(['Analista', 'Área_total', 'Quantidade_polígonos'])
                for row in range(self.model.rowCount()):
                    rowdata = []
                    for column in range(self.model.columnCount()):
                        index = self.model.index(row, column)
                        item = unicode(self.model.data(index)).encode('utf8')
                        if item is not None:
                            rowdata.append(item)
                        else:
                            rowdata.append('')
                    writer.writerow(rowdata)


    def run(self):
        try:
            camada = qgis.utils.iface.activeLayer()
            if camada == None:
                raise Exception(u'Carregue e ative a camada vw_desmatamento_current.geom_desmatamento')
            else:
                nome = camada.name()
            if nome != 'vw_desmatamento_current.geom_desmatamento':
                raise Exception(u'Carregue e ative a camada vw_desmatamento_current.geom_desmatamento')

            if self.contador == 0:
                self.conexao(camada)
                self.contador = 1

            self.popula(0)
        except Exception, erro:
                QMessageBox.about(None, 'Erro',erro.message)







