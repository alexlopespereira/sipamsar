# coding=utf-8
# This file is part of image_indexer.
#
# image_indexer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# image_indexer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

# O ultimo parametro (id_imagem) eh opcional
#parametros para gerar arquivos para o windows: f:\proc_temp_amsar\scripts_proc_xml\spsar_17nov16_final.xml /home/alex/xml_campo f:\proc_temp_amsar_teste 3 windows 18066
#parametros para gerar arquivos para o linux: /indice_imagens/imagens/processadas/amazoniasar/ciclo_2016_2017/script_parametros/spsar_17nov16_final_linux.xml /media/alex/DADOS/proc_temp_amsar /media/alex/DADOS/proc_temp_amsar 100 linux  4705

import xml.etree.ElementTree as xml
from updatexml import UpdateXML
import sys, os
from lib.bd import gerenciador
#Caminho do arquivo xml de parametros
paramfile=sys.argv[1] #'/indice_imagens/proc_amsar/script_param/spsar_17nov16_final.xml'
#caminho onde serao gravados os XMLs
xmls_path = sys.argv[2] #"/home/alex/indice_imagens/imagens/processadas/amazoniasar/ciclo_2016_2017"
#caminho onde o script IDL vai salvar os resultados
result_path = sys.argv[3] #"/home/alex/indice_imagens/imagens/processadas/amazoniasar/ciclo_2016_2017"
#Numero maximo de imagens por processamento
max_n_images = sys.argv[4]
#Sistema operacional onde o script IDL sera executado (Windows ou Linux)
OS = sys.argv[5].upper()

#caminho do xml de modelo
model_path = os.path.join(os.path.dirname(sys.argv[0]),"modelo.xml")

####################### Busca no Banco de dados ########################
conexao = gerenciador.Banco()

## Select dos grupos de todas as imagens originais
##idlist = conexao.consultar('''SELECT count(id_grupo) as ng, id_grupo FROM amazoniasar.vw_grupos_processamento_maior40 group by id_grupo order by ng desc;''')
## Select dos grupos das imagens originais que ainda nao foram processadas e nao contem nuvem
idlist=[]
if len(sys.argv) == 6:
    idlist = conexao.consultar('''SELECT count(id_grupo) as ng, id_grupo FROM amazoniasar.vw_grupos_processamento_maior40_tudo
    where co_seq_imagem in (
        SELECT j.co_seq_imagem
        FROM indice_imagens.tb_imagem j
        JOIN indice_imagens.rl_imagem_responsavel rlir ON j.co_seq_imagem = rlir.co_imagem
        WHERE  j.st_original = TRUE AND rlir.tp_operacao = 1 AND rlir.st_operacao = FALSE AND j.co_seq_imagem not in
        (
          SELECT j.co_seq_imagem
          FROM indice_imagens.tb_imagem j
          JOIN indice_imagens.rl_imagem_produto rlip ON j.co_seq_imagem = rlip.co_imagem_orig
          WHERE  j.st_original = true
          ORDER BY j.co_seq_imagem
        )
    )
    group by id_grupo order by ng desc;''')
elif len(sys.argv) == 7:
    idlist = conexao.consultar('SELECT count(id_grupo) as ng, id_grupo FROM amazoniasar.vw_grupos_processamento_maior40_tudo where co_seq_imagem=%s  group by id_grupo order by ng desc;',[sys.argv[6]])
########################################################################

######################### Criacao dos Arquivos XML #####################
for id_grupo in idlist:
    if OS == 'WINDOWS':
        image_paths = conexao.consultar('SELECT no_caminho_windows FROM amazoniasar.vw_grupos_processamento_maior40_tudo where id_grupo = %s order by dt_coleta desc limit %s', [id_grupo['id_grupo'], max_n_images])
        if len(image_paths) < 3:
            continue
        image_list = [d['no_caminho_windows'] for d in image_paths]
    else:
        image_paths = conexao.consultar(
            'SELECT no_caminho_arquivo FROM amazoniasar.vw_grupos_processamento_maior40 where id_grupo = %s order by dt_coleta desc limit %s',
            [id_grupo['id_grupo'], max_n_images])
        image_list = [d['no_caminho_arquivo'] for d in image_paths]
    xmlHandler = UpdateXML(result_path, xmls_path, model_path, paramfile, image_list, OS)
    xmlHandler.run()
    xmlHandler.createDirectory()
    xmlHandler.writeXML()


########################################################################