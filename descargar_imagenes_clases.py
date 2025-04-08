
#import sunpy.map
#import datetime as dt
import astropy.units as u
from astropy.io import fits
from sunpy.net import Fido, attrs as a
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
#import pdb
import numpy as np
import requests
#import calendar 
import subprocess
import requests

def initial_final_time(time_ini, time_final, delta_t=''):
    #Transformar esto en una funcion. Le doy T0, Tf, y deltaT y me devuelve ini y fin. ver como meter esta funcion en las clases e importarla.
    if not delta_t:
        delta_t = 20
    dt_i = datetime.strptime(time_ini, '%Y-%m-%d %H:%M:%S')
    dt_ini = dt_i - timedelta(minutes=delta_t)
    ini = dt_ini.strftime('%Y/%m/%d %H:%M:%S')
    dt_f = datetime.strptime(time_final, '%Y-%m-%d %H:%M:%S')
    dt_fin = dt_f + timedelta(minutes=delta_t)
    fin = dt_fin.strftime('%Y/%m/%d %H:%M:%S')
    return ini,fin

def convert_string(input_string):
    """Converts a string from AIA_ to aia. format
    Args:
        input_string: The string to convert.
    Returns:
        The converted string.
    """
    parts = input_string.split("_")
    #for i in range(len(parts)):
    #    print(parts[i])
    parts[0] = parts[0].lower()  # Convert first part to lowercase (aia)
    parts[1] = parts[1].lower()  # Convert second part to uppercase (LEV1)
    parts[2] = parts[2].upper()
    part1 = ".".join(parts[0:3])
    parts[5] = parts[5].replace("t", "T")  
    #parts[3] = parts[3][:4] + "-" + parts[3][4:6] + "-" + parts[3][6:8]  # Convert date format (2010-12-12)
    date = "-".join(parts[3:6]) 
    part2 = ".".join(parts[7:10])
    return "_".join([part1,date,parts[6],part2,parts[10]])

class lascoc2_downloader:
    """
    Definicion de la clase lasco C2 Downloader
    Mencionar ejemplo.
    """

    def __init__(self, start_time, end_time,nivel='',size='',nrl_download=''):
        try:
            self.start_time = start_time
            self.end_time = end_time
            self.instrumento = a.Instrument.lasco
            self.detector = a.Detector.c2
            self.nave  = 'SoHO'
            self.dir_descarga = '/gehme/data/soho/lasco/'
            #self.dir_descarga = '/data_local/GCS/gcs/Imagenes/'
            #self.dir_descarga = '/data1/work/gcs/Imagenes'
            self.nivel = nivel #puede ser level_05
            self.indices_descarga = '' #debe ser una lista
            self.size = size #puede ser 1 o 2
            self.nrl_download = nrl_download

        except TypeError:
            print("Be sure to add start_time, end_time, ship name, level/type of image when creating of object of this class.")
            raise
        except:
            print("WTF")

    def search(self):
        """
        Definir metodo search
        """
        search_lascoc2 = Fido.search(a.Time(self.start_time,self.end_time),self.instrumento,self.detector)
        if not search_lascoc2:
            print("No provider! No images available.")
            #global provider
            #provider = 0
            self.search_lascoc2 = search_lascoc2 #lista vacía
        else:
            self.search_lascoc2 = search_lascoc2['vso']
        if self.nivel != '':#asumo nivel definido correctamente
            self.filtro()

    def filtro(self):
        """
        Definicion del metodo filtro
        """
        match self.nivel:
            case 'que_son':
                string_search = "level_05"#"22"
                #size_True_False = (self.search_lascoc2['Size'] < (1.4*u.Mibyte))

            case 'level_05':
                string_search = "level_05"#"22"
                #size_True_False = (self.search_lascoc2['Size'] < (2.5*u.Mibyte)) & (self.search_lascoc2['Size'] > (1.5*u.Mibyte))
                
            case 'level_1':
                string_search = "25"
                #size_True_False = np.ones(search_size, dtype=bool).tolist()

            case '':
                string_search = ""

        lista_filtro = [] 
        for j in range(len(self.search_lascoc2)):
            if (string_search in self.search_lascoc2[j]['fileid']):
                lista_filtro.append(j)
        if not lista_filtro: 
            print('Filtered images')
        else:
            self.search_lascoc2 = self.search_lascoc2[lista_filtro]
        #print(lista_filtro)
        if self.size and lista_filtro: 
            lista_filtro2 = []
            for j in range(len(self.search_lascoc2)):
                if int(round(self.search_lascoc2[j]['Size'].value)) == self.size:
                    lista_filtro2.append(j)
            
            #resultado = [True if int(round(self.search_lascoc2['Size'][i].value)) == self.size else False for i in range(len(self.search_lascoc2))]
            #self.search_lascoc2[resultado]
            if not lista_filtro2:
                print('Filtered images')
            else:
                self.search_lascoc2 = self.search_lascoc2[lista_filtro2]
            #print(lista_filtro2)
        
    def display(self):
        """
        Definicion del metodo display
        """
        lista_dates=[]#revisar scope, esto modificaria una lista fuera de esta definicion?
        #lista_cant_images = []
        #lista_colores = []
        lista_color_azul = []
        lista_color_rojo = []
        lista_color_verde = []
        lista_cant_images_azul = []
        lista_cant_images_rojo = []
        lista_cant_images_verde = []
        search_size = len(self.search_lascoc2)
        for i in range(search_size):
            lista_dates.append(datetime.fromisoformat(str(self.search_lascoc2[i][0])))
            string_search_lvl05 = "level_05"
            string_search_lvl10 = "25"
            string_search_queesesto = "level_05"
            if string_search_lvl05    in self.search_lascoc2[i]['fileid'] and int(round(self.search_lascoc2[i]['Size'].value)) == 2: 
                lista_color_azul.append(datetime.fromisoformat(str(self.search_lascoc2[i][0])))
                lista_cant_images_azul.append(i)
            if string_search_lvl10 in self.search_lascoc2[i]['fileid']: 
                lista_color_rojo.append(datetime.fromisoformat(str(self.search_lascoc2[i][0])))
                lista_cant_images_rojo.append(i)
            if string_search_queesesto in self.search_lascoc2[i]['fileid'] and int(round(self.search_lascoc2[i]['Size'].value)) == 1: 
                lista_color_verde.append(datetime.fromisoformat(str(self.search_lascoc2[i][0])))
                lista_cant_images_verde.append(i)

        #labels = ['lvl_0.5','lvl_1.0','que son estas?']
        #fig, ax = plt.subplots()
        fig = plt.figure()
        ax  = fig.subplots()
        #ax.plot(lista_dates, lista_cant_images,c=lista_colores)
        ax.plot(lista_color_rojo,lista_cant_images_rojo,'ro',label='level 1.0')
        ax.plot(lista_color_azul,lista_cant_images_azul,'bo',label='level 0.5 2M')
        ax.plot(lista_color_verde,lista_cant_images_verde,'go',label='level 0.5 1M')
        ax.set_xlabel('Dates')
        ax.set_ylabel('Images')
        ax.set_title('Available images per time')
        fig.autofmt_xdate()
        ax.legend()
        ax.grid(True)
        plt.show()


    def nrl_navy_download(self, file_id, download_path_nrl):
        """
        Definicion del metodo que descarga desde la paw de nrl
        """
        url = "https://lasco-www.nrl.navy.mil/lz/level_1/"#101124/c2/25352163.fts.gz"  
        
        old_folder = file_id.split('/')[8]
        file_name_old = file_id.split('/')[-1]
        list_file = list(file_name_old)
        if list_file[1]=='2':
            list_file[1]='5'
        file_name_download = "".join(list_file)+".gz" # Nombre con el que se buscará y guardará el archivo 

        # Realizar la solicitud GET para obtener el contenido del archivo
        respuesta = requests.get(url+'/'+old_folder+'/c2/'+file_name_download)
        path_file = os.path.join(download_path_nrl,file_name_download)

        if os.path.exists(path_file):
            print(f"El archivo comprimido {path_file} ya existe, NO se procede a descargar.")
            return
        
        # Verificar si la solicitud fue exitosa (código de estado 200)
        
        if respuesta.status_code == 200:
            with open(path_file, "wb") as archivo:
                archivo.write(respuesta.content)
            print("El archivo se ha descargado exitosamente.")
            if os.path.exists(path_file[:-3]):
                print(f"El archivo a descomprimir {path_file[:-3]} ya existe, NO se procede a la descompresión del mismo.")
                return
            comando = f"gzip -d {path_file}"
            os.system(comando)
            print(f"unziping {path_file}")
            breakpoint()
            os.system(f"rm {path_file}")
            print(f"removing {path_file}")
        else:
            print("No se pudo descargar el archivo. Código de estado:", respuesta.status_code)
            print(f"Es posible que la imagen no se encuentre en {url+'/'+old_folder+'/c2/'+file_name_download}, o bien esté experimentando problemas de conectividad.")
        #return "".join(list_file)



    def download(self, download_path=None):
        """
        Definir metodo download
        """
        carpetas_creadas = []
        if getattr(self,'indices_descarga') == '': 
            cantidad = len(self.search_lascoc2)
            rango_descargas = range(cantidad)
        if getattr(self,'indices_descarga') != '':  #'indice_descarga' debe ser una lista de enteros contenidos en [0,len(self.search_cor2)]
            rango_descargas = self.indices_descarga

        for w in rango_descargas:
            folder_year_month_day = self.search_lascoc2[w]['fileid'].split('/')[8]
            #full_download_path = download_path+'/'+folder_year_month_day+'/'
            if not download_path:
                #download_path = self.dir_descarga+"/".join(self.search_lascoc2['fileid'][w].split('/')[0:-1])+'/'
                folder = self.search_lascoc2['fileid'][w].split('/')[-3]
                if int(folder[0:2]) < 50:
                    suffix = str(2000+int(folder[0:2]))
                else:
                    suffix = str(1900+int(folder[0:2]))                
                folder_full = suffix+folder[2:]+"/"
                if self.nrl_download:
                    download_path = self.dir_descarga+"level_1/c2/"+folder_full
                else:    
                    download_path = self.dir_descarga+"level_05/c2/"+folder_full

            if not os.path.exists(download_path):
                os.makedirs(download_path)
                print(f"Se ha creado el directorio {download_path}")
                carpetas_creadas.append(download_path)
            else:   
                print(f"El directorio {download_path} ya existe")

            if self.nrl_download:
                #breakpoint()
                downloaded_files = self.nrl_navy_download(self.search_lascoc2[w]['fileid'], download_path)
            else:   
                if not os.path.isfile(download_path+self.search_lascoc2[w]['fileid'].split('/')[-1]):#Si archivo no descargado entonces que descargue.
                    downloaded_files = Fido.fetch(self.search_lascoc2[w],path=download_path, max_conn=5, progress=True) 
                    downloaded_files2 = Fido.fetch(downloaded_files)

            #os.system('chgrp -R gehme {}'.format(download_path))
            #os.system('chmod -R 775 {}'.format(download_path))

        print(f'Archivos descargados en: {download_path}')






class lascoc3_downloader:
    def __init__(self, start_time, end_time, wavelength):
        self.start_time = start_time
        self.end_time = end_time
        self.wavelength = wavelength





class cor1_downloader:
    """
    Descripcion de la clase cor1 downloader
    Mencionar ejemplo.
    self.nivel = double, normal, sequential
    self.image_type = admite "img" o "seq". img puede ser self.nivel norm, seq; seq puede ser double o normal. 
    """
    def __init__(self, start_time, end_time,nave,nivel='',image_type='',size=''):
        try:
            self.start_time = start_time
            self.end_time = end_time
            self.instrumento = a.Instrument.secchi
            self.detector = a.Detector.cor1
            self.nave  = nave
            self.dir_descarga = '/gehme/data/stereo/'
            #self.dir_descarga = '/data_local/GCS/gcs/Imagenes/'
            #self.dir_descarga = '/data1/work/gcs/Imagenes'
            self.nivel = nivel #'s4c' es la calibracion sugerida que viene de a tríos
            self.indices_descarga = ''
            self.image_type = image_type #seq usualmente
            self.size = size #2M usualmente
            self.downloaded_error = ''
        except TypeError:
            print("Be sure to add start_time, end_time, ship name, level/type of image when creating of object of this class.")
            raise
        except:
            print("WTF")

    def search(self):
        """
        Definicion del metodo search
        """
        search_cor1 = Fido.search(a.Time(self.start_time,self.end_time),self.instrumento,self.detector)
        if not search_cor1:
            print("No provider! No images available.")
            self.search_cor1 = search_cor1 #lista vacía
        else:
            match self.nave:
                case 'STEREO_A':
                    search_cor1_ = search_cor1['vso'][search_cor1['vso']['Source'] == 'STEREO_A'].copy()
                case 'STEREO_B':
                    search_cor1_ = search_cor1['vso'][search_cor1['vso']['Source'] == 'STEREO_B'].copy()        
            self.search_cor1 = search_cor1_
            if self.nivel != '' or self.size!='':#asumo nivel definido correctamente
                self.filtro()

    def display(self):
        """
        Definicion del metodo display
        """
        lista_dates=[]
        search_size = len(self.search_cor1)
        lista_color_verde = []
        lista_cant_images_verde = []
        for i in range(search_size):
            lista_dates.append(datetime.fromisoformat(str(self.search_cor1[i][0])))
            string_search_sequence = "s4c"
            if string_search_sequence in self.search_cor1[i]['fileid']:
                lista_color_verde.append(datetime.fromisoformat(str(self.search_cor1[i][0])))
                lista_cant_images_verde.append(i)

        fig = plt.figure()
        ax  = fig.subplots()
        ax.plot(lista_color_verde,lista_cant_images_verde,'go',label='sequence')
        ax.set_xlabel('Dates')
        ax.set_ylabel('Images')
        ax.set_title('Available images per time, {}'.format(self.image_type))
        fig.autofmt_xdate()
        ax.legend()
        ax.grid(True)
        plt.show()

    def filtro(self):
        """
        Definicion del metodo filtro
        """
        match self.nivel:
            case 's4c':
                string_search_nivel = "s4c"
            case 's5c':
                string_search_nivel = "s5c"
            case '':
                string_search_nivel = ""
        match self.image_type:
            case 'seq':
                string_search_type = "seq"
            case '':
                string_search_type = ""

        lista_filtro = [] 
        for j in range(len(self.search_cor1)):
            if (string_search_nivel in self.search_cor1[j]['fileid'] and string_search_type in self.search_cor1[j]['fileid']): lista_filtro.append(j)
        self.search_cor1 = self.search_cor1[lista_filtro]
        if not lista_filtro: print('Filtered images') 

        if self.size and lista_filtro: 
            lista_filtro2 = []
            for j in range(len(self.search_cor1)):
                #if self.size == int(round(self.search_cor1[j]['Size'].value)):
                if self.size == round((self.search_cor1[j]['Size'].value) * 2) / 2:
                    lista_filtro2.append(j)
            self.search_cor1 = self.search_cor1[lista_filtro2]
            if not lista_filtro2: print('Filtered images')


    def download(self, download_path=None):
        """
        Definicion del metodo download.
        """
        carpetas_creadas = []
        if getattr(self,'indices_descarga') == '': 
            cantidad = len(self.search_cor1)
            rango_descargas = range(cantidad)
        if getattr(self,'indices_descarga') != '':  #'indice_descarga' debe ser una lista de enteros contenidos en [0,len(self.search_cor2)]
            rango_descargas = self.indices_descarga

        for w in rango_descargas:
            folder_year_month_day = self.search_cor1[w]['fileid'].split('/')[5]
            #full_download_path = download_path+'/'+folder_year_month_day+'/'
            if not download_path:
                download_path = self.dir_descarga+"/".join(self.search_cor1['fileid'][w].split('/')[0:-1])+'/'

            if not os.path.exists(download_path):
                os.makedirs(download_path)
                print(f"Se ha creado el directorio {download_path}")
                carpetas_creadas.append(download_path)
            else:   
                print(f"El directorio {download_path} ya existe")

            if not os.path.isfile(download_path+self.search_cor1[w]['fileid'].split('/')[-1]):#Si archivo no descargado entonces que descargue.
                downloaded_files = Fido.fetch(self.search_cor1[w],path=download_path, max_conn=5, progress=True)
                print(downloaded_files.errors) 
            #os.system('chgrp -R gehme {}'.format(download_path))
            os.system('chmod -R 775 {}'.format(download_path))
    

        print(f'Archivos descargados en: {download_path}')



class cor2_downloader:
    """
    Descripcion de la clase cor2 downloader
    self.nivel = double, normal, sequential
    self.image_type = admite "img" o "seq". img puede ser self.nivel norm, seq; seq puede ser double o normal. 
    t_ini="2011/11/28 10:00:00"
    t_ini=t_ini.replace('/', '-')
    t_fin="2011/11/28 16:30:00"
    t_fin=t_fin.replace('/', '-')
    ini,fin = initial_final_time(t_ini, t_fin, delta_t=10)
    nave='STEREO_A'
    cor2_images = cor2_downloader(start_time=ini,end_time=fin,nave=nave,image_type='img')
    cor2_images.search()
    cor2_images.filtro()
    cor2_images.display()
    cor2_images.download()
    """
    def __init__(self, start_time, end_time,nave,nivel='',image_type='',size=True,cadence=a.Sample(10*u.min)):
        try:
            self.start_time = start_time
            self.end_time = end_time
            self.instrumento = a.Instrument.secchi
            self.detector = a.Detector.cor2
            self.nave  = nave
            self.dir_descarga = '/gehme/gehme/data/stereo/'
            #self.dir_descarga = '/data_local/GCS/gcs/Imagenes/'
            self.nivel = nivel
            self.indices_descarga = ''
            self.image_type = image_type #puede ser img o seq
            self.size = size
            self.cadence = cadence
        except TypeError:
            print("Be sure to add start_time, end_time, ship name, level/type of image when creating of object of this class.")
            raise
        except:
            print("WTF")

    def search(self):
        """
        Definicion del metodo search
        """
        search_cor2 = Fido.search(a.Time(self.start_time,self.end_time),self.instrumento,self.detector,self.cadence)
        #breakpoint()
        if not search_cor2:
            print("No provider! No images available.")
            #global provider
            #provider = 0
            self.search_cor2 = search_cor2 #lista vacía
        else:
            match self.nave:
                case 'STEREO_A':
                    search_cor2_ = search_cor2['vso'][search_cor2['vso']['Source'] == 'STEREO_A'].copy()
                case 'STEREO_B':
                    search_cor2_ = search_cor2['vso'][search_cor2['vso']['Source'] == 'STEREO_B'].copy()        
            self.search_cor2 = search_cor2_
            if self.nivel != '':#asumo nivel definido correctamente
                self.filtro()


    def display(self):
        """
        Definicion del metodo display
        """
        lista_dates=[]
        search_size = len(self.search_cor2)
        #lista_colores = []
        lista_color_azul  = []
        lista_color_rojo  = []
        lista_color_verde = []
        lista_cant_images_azul  = []
        lista_cant_images_rojo  = []
        lista_cant_images_verde = []
        for i in range(search_size):
            lista_dates.append(datetime.fromisoformat(str(self.search_cor2[i][0])))
            #lista_cant_images.append(i)
            string_search_normal   = "n4c"
            string_search_double   = "d4c"
            string_search_sequence = "s4c"

            if string_search_normal in self.search_cor2[i]['fileid']: 
                lista_color_azul.append(datetime.fromisoformat(str(self.search_cor2[i][0])))
                lista_cant_images_azul.append(i)
            if string_search_double in self.search_cor2[i]['fileid']: 
                lista_color_rojo.append(datetime.fromisoformat(str(self.search_cor2[i][0])))
                lista_cant_images_rojo.append(i)
            if string_search_sequence in self.search_cor2[i]['fileid']:
                lista_color_verde.append(datetime.fromisoformat(str(self.search_cor2[i][0])))
                lista_cant_images_verde.append(i)

        #labels = ['double','pb']
        #fig, ax = plt.subplots()
        fig = plt.figure()
        ax  = fig.subplots()
        #ax.plot(lista_dates, lista_cant_images,c=lista_colores)
        ax.plot(lista_color_rojo,lista_cant_images_rojo  ,'ro',label='double')
        ax.plot(lista_color_azul,lista_cant_images_azul  ,'bo',label='normal')
        ax.plot(lista_color_verde,lista_cant_images_verde,'go',label='sequence')
        ax.set_xlabel('Dates')
        ax.set_ylabel('Images')
        ax.set_title('Available images per time, {}'.format(self.image_type))
        fig.autofmt_xdate()
        ax.legend()
        ax.grid(True)
        plt.show()



    def filtro(self):
        """
        Definicion del metodo filtro
        """
        #search_size = len(self.search_cor2)
        match self.nivel:
            case 'normal':
                string_search_nivel = "n4c"
                #search_cor2_ = self.search_cor2[self.search_cor2['Size'] == (8.03375*u.Mibyte)].copy()
            case 'double':
                string_search_nivel = "d4c"
                #search_cor2_ = self.search_cor2[self.search_cor2['Size'] == (8.0365*u.Mibyte)].copy()
            case 'sequence':
                string_search_nivel = "s4c"
            case '':
                string_search_nivel = ""
        match self.image_type:
            case 'img':
                string_search_type = "img"
            case 'seq':
                string_search_type = "seq"
            case '':
                string_search_type = ""

        lista_filtro = [] 
        for j in range(len(self.search_cor2)):
            if (string_search_nivel in self.search_cor2[j]['fileid'] and string_search_type in self.search_cor2[j]['fileid']): 
                lista_filtro.append(j)
        self.search_cor2 = self.search_cor2[lista_filtro]  
        if not lista_filtro: print('Filtered images')

        if self.size and lista_filtro: #en realidad no tiene que ser lista_filtro, sino mas bien self.search_cor2
            print("Filtrando por tamanio")
            lista_filtro2 = [] 
            for j in range(len(self.search_cor2)):
                if self.search_cor2[j]['Size'].value > 8.0:
                    lista_filtro2.append(j)
            if not lista_filtro2: 
                print('Filtered images')
            else:
                self.search_cor2 = self.search_cor2[lista_filtro2]

    def download(self, download_path=None):
        """
        Definicion del metodo download.
        """

        carpetas_creadas = []
        if getattr(self,'indices_descarga') == '': 
            cantidad = len(self.search_cor2)
            rango_descargas = range(cantidad)
        if getattr(self,'indices_descarga') != '':  #'indice_descarga' debe ser una lista de enteros contenidos en [0,len(self.search_cor2)]
            rango_descargas = self.indices_descarga

        for w in rango_descargas:
            folder_year_month_day = self.search_cor2[w]['fileid'].split('/')[5]
            #full_download_path = download_path+'/'+folder_year_month_day+'/'
            if not download_path:
                download_path = self.dir_descarga+"/".join(self.search_cor2['fileid'][w].split('/')[0:-1])+'/'
#Esta linea guarda en 1 sola carpeta, correspondiente al 1er dia de la lista!!
            if not os.path.exists(download_path):
                os.makedirs(download_path)
                print(f"Se ha creado el directorio {download_path}")
                carpetas_creadas.append(download_path)
            else:   
                print(f"El directorio {download_path} ya existe")

            if not os.path.isfile(download_path+self.search_cor2[w]['fileid'].split('/')[-1]):#Si archivo no descargado entonces que descargue.
                downloaded_files = Fido.fetch(self.search_cor2[w],path=download_path, max_conn=5, progress=True) 
                print(downloaded_files.errors) 
            #os.system('chgrp -R gehme {}'.format(download_path))
                #os.system('chmod -R 775 {}'.format(download_path+self.search_cor2[w]['fileid'].split('/')[-1]))
                #TODO: pasar el nombre a minuscula xq la descarga es en minuscula.
        print(f'Archivos descargados en: {download_path}')


class aia_downloader:
    """
    Definicion de la clase aia Downloader
    Example:
    t_ini='2010-12-12 10:00:00'
    t_fin='2010-12-12 15:00:00'
    ini,fin = initial_final_time(t_ini, t_fin, delta_t=50)
    aia_images = aia_downloader(start_time=ini,end_time=fin,cadence=15,wave=193)
    aia_images.search()
    aia_images.display()
    aia_images.dir_descarga='/data_local/work/gcs/Imagenes/193/'
    aia_images.download()
    """

    def __init__(self, start_time, end_time,size='',wave='',cadence=60,origin_download_path=False,band_folder=True):
        try:
            self.start_time = start_time
            self.end_time = end_time
            self.instrumento = a.Instrument.aia
            #3 wavelenght by default
            if wave == '':
                self.wave_171 = a.Wavelength(171*u.angstrom)
                self.wave_193 = a.Wavelength(193*u.angstrom)
                self.wave_211 = a.Wavelength(211*u.angstrom)
                self.wave = ''
            if wave != '':
                self.wave  = a.Wavelength(wave*u.angstrom) #171 - 193 - 211
                self.wave_integer = wave
            self.cadence = a.Sample(cadence*u.minute) #candence in minutes
            #If origin_download_path set True, then the real download path = dir_descarga+origin_download_path
            #This will allow to download the images maintaining the secchi oficial directory path.
            self.dir_descarga = '/media/gehme/gehme/data/sdo/aia/l1/'
            #If band_folder set True, then the real download path = origin_download_path+band_folder
            #This allow to separete the images in folders considering the band (171, 195, 284). Not official in secchi.
            self.band_folder = band_folder
            self.origin_download_path = origin_download_path
            #dir where the images will be decompressed using decompress method.
            self.dir_decompress = ''
            self.indices_descarga = '' #no utilizado en esta clase, ver definicion de filter en cor2_downloader.
            self.size = size

        except TypeError:
            print("Be sure to add start_time, end_time, ship name, level/type of image when creating of object of this class.")
            raise
        except:
            print("esto no deberia suceder. check.")

    def search(self):
        """
        Definir metodo search
        """
        if self.wave == '':
            search_aia_171 = Fido.search(a.Time(self.start_time,self.end_time),self.instrumento,self.wave_171,self.cadence)
            search_aia_193 = Fido.search(a.Time(self.start_time,self.end_time),self.instrumento,self.wave_193,self.cadence)
            search_aia_211 = Fido.search(a.Time(self.start_time,self.end_time),self.instrumento,self.wave_211,self.cadence)
            
            if not search_aia_171:
                print("No provider! No images available.")
                self.search_aia_171 = search_aia_171 #lista vacía
            else:
                self.search_aia_171 = search_aia_171#['vso']

            if not search_aia_193:
                print("No provider! No images available.")
                self.search_aia_193 = search_aia_193 #lista vacía
            else:
                self.search_aia_193 = search_aia_193#['vso']   

            if not search_aia_211:
                print("No provider! No images available.")
                self.search_aia_211 = search_aia_211 #lista vacía
            else:
                self.search_aia_211 = search_aia_211#['vso']

        if self.wave != '':
            search_aia = Fido.search(a.Time(self.start_time,self.end_time),self.instrumento,self.wave,self.cadence)
            if not search_aia:
                print("No provider! No images available.")
                self.search_aia = search_aia #lista vacía
            else:
                self.search_aia = search_aia#['vso']

    def display(self):
        """
        Definicion del metodo display
        V2
        """
        lista_dates=[]
        if self.wave != '':
            search_size = len(self.search_aia['vso'])
        if self.wave == '':    
            search_size_171 = len(self.search_aia_171['vso'])
            search_size_193 = len(self.search_aia_193['vso'])
            search_size_211 = len(self.search_aia_211['vso'])
        #lista_colores = []
        lista_color_azul  = []
        lista_color_rojo  = []
        lista_color_verde = []
        lista_cant_images_azul  = []
        lista_cant_images_rojo  = []
        lista_cant_images_verde = []
        if self.wave != '':
            for i in range(search_size):
                lista_dates.append(datetime.fromisoformat(str(self.search_aia['vso'][i][0])))
                lista_color_azul.append(datetime.fromisoformat(str(self.search_aia['vso'][i][0])))
                lista_cant_images_azul.append(i)

        if self.wave == '':
            for i in range(search_size_171):
                lista_dates.append(datetime.fromisoformat(str(self.search_aia_171['vso'][i][0])))
                lista_color_azul.append(datetime.fromisoformat(str(self.search_aia_171['vso'][i][0])))
                lista_cant_images_azul.append(i)
            for i in range(search_size_193):
                lista_dates.append(datetime.fromisoformat(str(self.search_aia_193['vso'][i][0])))
                lista_color_rojo.append(datetime.fromisoformat(str(self.search_aia_193['vso'][i][0])))
                lista_cant_images_rojo.append(i)
            for i in range(search_size_211):
                lista_dates.append(datetime.fromisoformat(str(self.search_aia_211['vso'][i][0])))
                lista_color_verde.append(datetime.fromisoformat(str(self.search_aia_211['vso'][i][0])))
                lista_cant_images_verde.append(i)                                
        if self.wave != '':
            fig=plt.figure(figsize=(15, 5))
            ax=plt.subplot(1,1,1)
            ax.plot(lista_color_azul,lista_cant_images_azul  ,'bo',label=str(self.wave_integer))
            ax.set_title(str(self.wave_integer))
            ax.text(0.95, 0.95, f'#images={search_size}', color='red', transform=ax.transAxes,fontsize=16, verticalalignment='top', horizontalalignment='right')
            ax.legend()
            ax.set_xlabel('Dates')
            ax.set_ylabel('Images')   
            fig.autofmt_xdate()
            ax.grid(True)
            
        if self.wave == '':
            fig=plt.figure(figsize=(15, 5))
            ax=plt.subplot(1, 3, 1)
            ax.plot(lista_color_azul,lista_cant_images_azul  ,'bo',label='171')
            ax.set_title('171')
            ax.text(0.95, 0.95, f'#images={search_size_171}', color='blue', transform=ax.transAxes,fontsize=16, verticalalignment='top', horizontalalignment='right')
            ax.legend()
            ax.set_xlabel('Dates')
            ax.set_ylabel('Images')            
            fig.autofmt_xdate()
            ax.grid(True)
            ax=plt.subplot(1, 3, 2)
            ax.plot(lista_color_rojo,lista_cant_images_rojo  ,'ro',label='193')
            ax.set_title('193')
            ax.text(0.95, 0.95, f'#images={search_size_193}', color='red', transform=ax.transAxes,fontsize=16, verticalalignment='top', horizontalalignment='right')
            ax.legend()
            ax.set_xlabel('Dates')
            ax.set_ylabel('Images')            
            fig.autofmt_xdate()
            ax.grid(True)
            ax=plt.subplot(1, 3, 3)
            ax.plot(lista_color_verde,lista_cant_images_verde,'go',label='211')
            ax.set_title('211')
            ax.text(0.95, 0.95, f'#images={search_size_211}', color='green', transform=ax.transAxes,fontsize=16, verticalalignment='top', horizontalalignment='right')
            ax.legend()
            ax.set_xlabel('Dates')
            ax.set_ylabel('Images')
            fig.autofmt_xdate()
            ax.grid(True)
            plt.show()

    def download(self, download_path=None):
        """
        Definicion del metodo download.
        """
        if not download_path:
            download_path = self.dir_descarga
        carpetas_creadas = []
        if getattr(self,'indices_descarga') == '': 
            if self.wave != '':
                cantidad = len(self.search_aia['vso'])
                rango_descargas = range(cantidad)
                vec_rangos = [rango_descargas]

            if self.wave == '':
                cantidad_171 = len(self.search_aia_171['vso'])
                rango_descargas_171 = range(cantidad_171)
                cantidad_193 = len(self.search_aia_193['vso'])
                rango_descargas_193 = range(cantidad_193)
                cantidad_211 = len(self.search_aia_211['vso'])
                rango_descargas_211 = range(cantidad_211)
                vec_rangos = [rango_descargas_171,rango_descargas_193,rango_descargas_211]

        if getattr(self,'indices_descarga') != '':  #'indice_descarga' debe ser una lista de enteros contenidos en [0,len(self.search_XXXX)]
            rango_descargas = self.indices_descarga


        if self.wave != '':
            for w in rango_descargas:
                if self.band_folder == True:
                    auxi = str(self.wave_integer)    
                    auxi = auxi+'/'
                if self.band_folder == False:
                    auxi=''
                #creating the folder
                individual_start_time=str(self.search_aia['vso'][w]['Start Time'])
                folder_string = individual_start_time[:10].replace('-', '')+'/'
                if self.origin_download_path == True:
                    full_download_path = download_path+auxi+folder_string
                if self.origin_download_path == False:
                    full_download_path = download_path+auxi
                self.dir_decompress = full_download_path
                if not os.path.exists(full_download_path):
                    os.makedirs(full_download_path)
                    print(f"Se ha creado el directorio {full_download_path}")
                    carpetas_creadas.append(full_download_path)

                if not os.path.isfile(full_download_path+self.search_aia['vso'][w]['fileid']):#Si archivo no descargado entonces que descargue.
                    downloaded_files = Fido.fetch(self.search_aia['vso'][w],path=full_download_path, max_conn=5, progress=True)
                    print(downloaded_files.errors)
        
        if self.wave == '':   
            list_errors=[]      
            search_total = [self.search_aia_171,self.search_aia_193,self.search_aia_211]
            for index,rangos in enumerate(vec_rangos):
                #for w in rangos:
                    if not download_path:
                        print("Download path is required")
                    if self.band_folder == True:
                        if index ==0:
                            auxi = '171/'
                        if index ==1:
                            auxi = '193/'
                        if index ==2:
                            auxi = '211/'    
                    if self.band_folder == False:
                        auxi=''
                    individual_start_time=search_total[index]['vso']['Start Time']
                    folder_string = individual_start_time.to_datetime()[0].tolist().strftime("%Y%m%d")
                    if self.origin_download_path == True:
                        full_download_path = download_path+auxi+folder_string
                    if self.origin_download_path == False:
                        full_download_path = download_path+auxi

                    if not os.path.exists(full_download_path):
                        os.makedirs(full_download_path)
                        print(f"Se ha creado el directorio {full_download_path}")
                        carpetas_creadas.append(full_download_path)
                    
                    downloaded_files = Fido.fetch(search_total[index],path=full_download_path, max_conn=5, progress=True)
                    downloaded_files2 = Fido.fetch(downloaded_files)
                    print(downloaded_files2.errors)
                    list_errors.append(downloaded_files2.errors)
                    #os.system('chgrp -R gehme {}'.format(download_path))
                #os.system('chmod -R 775 {}'.format(download_path))
            self.downloaded_error = downloaded_files2.errors 
            print(f'Archivos descargados en: {download_path}')

    def decompress(self,download_path=None):
        """
        If images are downloades from JSOC, then they are compressed in .fz file (rice compression). 
        This method decompresses them, Save the decompressed file and remove the compressed one.
        """
        if not download_path:
            download_path = self.dir_decompress
        #create a list of fits file that are in download_path
        fits_files = []
        # Iterate through the files in the download path
        for file_name in os.listdir(download_path):
            if file_name.endswith('z_image_lev1.fits'):
                #z sound like fz compressed images.
                fits_files.append(os.path.join(download_path, file_name))
        #decompress the files using astropy and save with a new filename
        #print('Removing compressed files')
        for file in fits_files:
            file2 = convert_string(file)
            with fits.open(file) as hdul:
                data = hdul[1].data
                header = hdul[1].header
                #removing 'nans' from odd header keys()
                header["OSCNMEAN"]=0
                header["OSCNRMS"]=0
            if not os.path.exists(file2):
                fits.writeto(file2, data, header, overwrite=True)
                print("removing:  "+file+"  and saving:  "+file2)
                os.system('chmod -R 751 {}'.format(file2))
                #os.system('chgrp -R gehme {}'.format(file2))
            #remove the compressed files
            os.remove(file)
        print('Files decompressed and removed')




class euvi_downloader:
    """
    TODO: 
    Definicion de la clase euvi Downloader
    Example:
    from descargar_imagenes_clases import euvi_downloader
    import sunpy.map
    import sunpy.data.sample 
    from descargar_imagenes_clases import initial_final_time
    import astropy.units as u
    from astropy.io import fits
    from sunpy.net import Fido, attrs as a
    from datetime import datetime, timedelta
    import os
    import matplotlib.pyplot as plt
    import pdb
    import numpy as np
    import requests

    t_ini='2010-12-12 10:00:00'
    t_fin='2010-12-12 15:00:00'
    ini,fin = initial_final_time(t_ini, t_fin, delta_t=50)

    euvi_images = euvi_downloader(start_time=ini,end_time=fin,cadence=15,wave=195)
    euvi_images.search()
    euvi_images.display()
    euvi_images.dir_descarga='/data_local/work/gcs/Imagenes/195/'

    euvi_images.download()
    
    """

    def __init__(self, start_time, end_time, nave, size='',wave='',cadence=60,origin_download_path=False,band_folder=True):
        try:
            self.start_time = start_time
            self.end_time = end_time
            self.instrumento = a.Instrument.secchi
            self.detector = a.Detector.euvi
            self.nave  = nave
            #3 wavelenght by default
            if wave == '':
                self.wave_171 = a.Wavelength(171*u.angstrom)
                self.wave_195 = a.Wavelength(195*u.angstrom)
                self.wave_284 = a.Wavelength(284*u.angstrom)
                self.wave = ''
            if wave != '':
                self.wave  = a.Wavelength(wave*u.angstrom) #171 - 195 - 284
                self.wave_integer = wave #Only used in display()
            self.cadence = a.Sample(cadence*u.minute) #candence in minutes
            self.dir_descarga = '/media/gehme/gehme/data/stereo/'
            #If origin_download_path set True, then the real download path = dir_descarga+origin_download_path
            #This will allow to download the images maintaining the secchi oficial directory path.
            self.origin_download_path = origin_download_path
            #If band_folder set True, then the real download path = origin_download_path+band_folder
            #This allow to separete the images in folders considering the band (171, 195, 284). Not official in secchi.
            self.band_folder = band_folder
            self.indices_descarga = '' #debe ser una lista
            self.size = size

        except TypeError:
            print("Be sure to add start_time, end_time, ship name, level/type of image when creating of object of this class.")
            raise
        except:
            print("WTF")

    def search(self):
        """
        Definir metodo search
        """
        if self.wave == '':
            search_euvi_171 = Fido.search(a.Time(self.start_time,self.end_time),self.instrumento,self.wave_171,self.cadence)
            search_euvi_195 = Fido.search(a.Time(self.start_time,self.end_time),self.instrumento,self.wave_195,self.cadence)
            search_euvi_284 = Fido.search(a.Time(self.start_time,self.end_time),self.instrumento,self.wave_284,self.cadence)
            
            if not search_euvi_171:
                print("No provider! No images available.")
                self.search_euvi_171 = search_euvi_171 #lista vacía
            else:
                match self.nave:
                    case 'STEREO_A':
                        search_euvi_171 = search_euvi_171['vso'][search_euvi_171['vso']['Source'] == 'STEREO_A'].copy()
                    case 'STEREO_B':
                        search_euvi_171 = search_euvi_171['vso'][search_euvi_171['vso']['Source'] == 'STEREO_B'].copy()
                self.search_euvi_171 = search_euvi_171#['vso']

            if not search_euvi_195:
                print("No provider! No images available.")
                self.search_euvi_195 = search_euvi_195 #lista vacía
            else:
                match self.nave:
                    case 'STEREO_A':
                        search_euvi_195 = search_euvi_195['vso'][search_euvi_195['vso']['Source'] == 'STEREO_A'].copy()
                    case 'STEREO_B':
                        search_euvi_195 = search_euvi_195['vso'][search_euvi_195['vso']['Source'] == 'STEREO_B'].copy()
                self.search_euvi_195 = search_euvi_195#['vso']   

            if not search_euvi_284:
                print("No provider! No images available.")
                self.search_euvi_284 = search_euvi_284 #lista vacía
            else:
                match self.nave:
                    case 'STEREO_A':
                        search_euvi_284 = search_euvi_284['vso'][search_euvi_284['vso']['Source'] == 'STEREO_A'].copy()
                    case 'STEREO_B':
                        search_euvi_284 = search_euvi_284['vso'][search_euvi_284['vso']['Source'] == 'STEREO_B'].copy()
                self.search_euvi_284 = search_euvi_284#['vso']

        if self.wave != '':
            search_euvi = Fido.search(a.Time(self.start_time,self.end_time),self.instrumento,self.wave,self.cadence)
            match self.nave:
                case 'STEREO_A':
                    search_euvi = search_euvi['vso'][search_euvi['vso']['Source'] == 'STEREO_A'].copy()
                case 'STEREO_B':
                    search_euvi = search_euvi['vso'][search_euvi['vso']['Source'] == 'STEREO_B'].copy() 

            if not search_euvi:
                print("No provider! No images available.")
                self.search_euvi = search_euvi #lista vacía
            else:
                self.search_euvi = search_euvi#['vso']


    def display(self):
        """
        Definicion del metodo display
        V2
        """
        lista_dates=[]
        if self.wave != '':
            search_size = len(self.search_euvi)
        if self.wave == '':    
            search_size_171 = len(self.search_euvi_171)
            search_size_195 = len(self.search_euvi_195)
            search_size_284 = len(self.search_euvi_284)
        #lista_colores = []
        lista_color_azul  = []
        lista_color_rojo  = []
        lista_color_verde = []
        lista_cant_images_azul  = []
        lista_cant_images_rojo  = []
        lista_cant_images_verde = []
        if self.wave != '':
            for i in range(search_size):
                lista_dates.append(datetime.fromisoformat(str(self.search_euvi[i][0])))
                lista_color_azul.append(datetime.fromisoformat(str(self.search_euvi[i][0])))
                lista_cant_images_azul.append(i)

        if self.wave == '':
            for i in range(search_size_171):
                lista_dates.append(datetime.fromisoformat(str(self.search_euvi_171[i][0])))
                lista_color_azul.append(datetime.fromisoformat(str(self.search_euvi_171[i][0])))
                lista_cant_images_azul.append(i)
            for i in range(search_size_195):
                lista_dates.append(datetime.fromisoformat(str(self.search_euvi_195[i][0])))
                lista_color_rojo.append(datetime.fromisoformat(str(self.search_euvi_195[i][0])))
                lista_cant_images_rojo.append(i)
            for i in range(search_size_284):
                lista_dates.append(datetime.fromisoformat(str(self.search_euvi_284[i][0])))
                lista_color_verde.append(datetime.fromisoformat(str(self.search_euvi_284[i][0])))
                lista_cant_images_verde.append(i)                                
        if self.wave != '':
            fig=plt.figure(figsize=(15, 5))
            ax=plt.subplot(1,1,1)
            ax.plot(lista_color_azul,lista_cant_images_azul  ,'bo',label=str(self.wave_integer))
            ax.set_title(str(self.wave_integer))
            ax.legend()
            ax.set_xlabel('Dates')
            ax.set_ylabel('Images')   
            fig.autofmt_xdate()
            ax.grid(True)
            
        if self.wave == '':
            fig=plt.figure(figsize=(15, 5))
            ax=plt.subplot(1, 3, 1)
            ax.plot(lista_color_azul,lista_cant_images_azul  ,'bo',label='171')
            ax.set_title('171')
            ax.legend()
            ax.set_xlabel('Dates')
            ax.set_ylabel('Images')            
            fig.autofmt_xdate()
            ax.grid(True)
            ax=plt.subplot(1, 3, 2)
            ax.plot(lista_color_rojo,lista_cant_images_rojo  ,'ro',label='195')
            ax.set_title('195')
            ax.legend()
            ax.set_xlabel('Dates')
            ax.set_ylabel('Images')            
            fig.autofmt_xdate()
            ax.grid(True)
            ax=plt.subplot(1, 3, 3)
            ax.plot(lista_color_verde,lista_cant_images_verde,'go',label='284')
            ax.set_title('284')
            ax.legend()
            ax.set_xlabel('Dates')
            ax.set_ylabel('Images')
            fig.autofmt_xdate()
            ax.grid(True)
            plt.show()

    def download(self, download_path=None):
        """
        Definicion del metodo download.
        """
        if not download_path:
            download_path = self.dir_descarga
        carpetas_creadas = []
        if getattr(self,'indices_descarga') == '': 
            if self.wave != '':
                cantidad = len(self.search_euvi)
                rango_descargas = range(cantidad)
                vec_rangos = [rango_descargas]

            if self.wave == '':
                cantidad_171 = len(self.search_euvi_171)
                rango_descargas_171 = range(cantidad_171)
                cantidad_195 = len(self.search_euvi_195)
                rango_descargas_195 = range(cantidad_195)
                cantidad_284 = len(self.search_euvi_284)
                rango_descargas_284 = range(cantidad_284)
                vec_rangos = [rango_descargas_171,rango_descargas_195,rango_descargas_284]

        if getattr(self,'indices_descarga') != '':  #'indice_descarga' debe ser una lista de enteros contenidos en [0,len(self.search_XXX)]
            rango_descargas = self.indices_descarga

        if self.wave != '':
            list_errors=[]
            if self.band_folder == True:
                auxi = str(self.wave_integer)    
                auxi = auxi+'/'
            if self.band_folder == False:
                auxi=''

            for w in rango_descargas:

                if self.origin_download_path == True:
                    full_download_path = download_path+self.search_euvi['fileid'][w].rsplit('/', 1)[0] + '/'+auxi
                if self.origin_download_path == False:
                    full_download_path = download_path+auxi
                if not os.path.exists(full_download_path):
                    os.makedirs(full_download_path)
                    print(f"Se ha creado el directorio {full_download_path}")
                    carpetas_creadas.append(full_download_path)
                #else:   
                #    print(f"El directorio {download_path} ya existe")
                #chek if the file allready exists -> Obsolet since overwrite=False as default -> NOT obsolet!
                file_name_string = self.search_euvi[w]['fileid'].rsplit('/', 1)[-1]
                if not os.path.isfile(full_download_path+file_name_string):#Si archivo no descargado entonces que descargue.
                    downloaded_files = Fido.fetch(self.search_euvi[w],path=full_download_path, max_conn=10, progress=True)
                    list_errors.append(downloaded_files.errors)
                    print("Downloaded: "+full_download_path+file_name_string)
                else:
                    print("File allready exists: "+full_download_path+file_name_string)
            self.download_errors = list_errors

        if self.wave == '':
            list_errors=[]         
            search_total = [self.search_euvi_171,self.search_euvi_195,self.search_euvi_284]
            for index,rangos in enumerate(vec_rangos):
                #for w in rangos:
                if not download_path:
                    print("Download path is required")
                    breakpoint()
                if self.band_folder == True:
                    if index ==0:
                        auxi = '171/'
                    if index ==1:
                        auxi = '195/'
                    if index ==2:
                        auxi = '284/'     
                if self.band_folder == False:
                    auxi=''

                if self.origin_download_path == True:
                    full_download_path = download_path+search_total['fileid'][index].rsplit('/', 1)[0] + '/'+auxi
                if self.origin_download_path == False:
                    full_download_path = download_path+auxi

                if not os.path.exists(full_download_path):
                    os.makedirs(full_download_path)
                    print(f"Se ha creado el directorio {full_download_path}")
                    carpetas_creadas.append(full_download_path)
                # chequing if the file allready exists
                file_name_string = search_total[index]['fileid'].rsplit('/', 1)[-1]
                if not os.path.isfile(download_path+file_name_string):
                    downloaded_files = Fido.fetch(search_total[index],path=full_download_path, max_conn=10, progress=True)
                    downloaded_files2 = Fido.fetch(downloaded_files)
                    print(downloaded_files2.errors)
                    list_errors.append(downloaded_files2.errors)
                    os.system('chmod -R 751 {}'.format(full_download_path+search_total[index]))
                    #os.system('chgrp -R gehme {}'.format(full_download_path+search_total[index]))
            self.downloaded_error = list_errors
            print(f'Archivos descargados en: {download_path}')


class nrl_massive_downloader:
    """
    TODO: convert the display method in a table with the dates and the images available.
    descarga masiva de imagenes de NRL 0.5 de c2/c3/
    La descarga minima es diara.
    descarga_test = nrl_massive_downloader(start_time,end_time)
    descarga_test.create() #creates the list of dates to download in format YYMMDD
    descarga_test.display() #display the list of dates
    descarga_test.download() #downloads the images from the list
    """
    def __init__(self, start_time, end_time,instrument='c2'):
        try:
            self.start_time = start_time
            self.end_time = end_time
            self.instrument = instrument
            self.dir_descarga = '/gehme/data/soho/lasco/level_05/c2/'
        except TypeError:
            print("Be sure to add start_time, end_time, ship name when creating of object of this class.")
            raise
        except:
            print("WTF")
            
    def create(self, download_path=None):
        """
        Definicion del metodo download.
        """
        string_list = []
        folder_list = []
        current_date = self.start_time
        while current_date <= self.end_time:
            year_aux = str(current_date.year)[2:]  # Extract last two digits of year
            string_month = "{:02d}".format(current_date.month)
            string_day = "{:02d}".format(current_date.day)
            string_list.append(year_aux + string_month + string_day)
            folder_list.append(str(current_date.year)+ string_month + string_day)
            current_date += timedelta(days=1)   # Increment date by 1 day
        self.list_dates = string_list
        self.folder_list = folder_list

    def display(self,):
        print(self.list_dates)
        #we can download the txt file in the url and show that as a table.

    def download(self,directory=None):
        # Mirror the directory with wget command
        #"https://lasco-www.nrl.navy.mil/lz/level_05/200104/c2/"

        if directory:
            self.dir_descarga = directory
        for index,date in enumerate(self.list_dates):
            url = f"https://lasco-www.nrl.navy.mil/lz/level_05/{date}/{self.instrument}/"
            folder = self.folder_list[index]
            response = requests.head(url, allow_redirects=True)
            if response == 404:
                print(f"Date {date} not available")
            if response.status_code == 200:
                try:
                    command = ["wget", "-m", "-nH", "--cut-dirs=4", "-np", "-A", "fts", url, "-P", self.dir_descarga+str(folder)+"/"]
                    subprocess.run(command, check=True)
                    print(f"Date {date} downloaded")
                except subprocess.CalledProcessError:
                    print(f"Error downloading date {date}")
                    return

    def clean(self,):
        """
        limpieza de archivos descargados que pesen menos de 2Mb en cada folder.
        """
        for folder in list(set(self.folder_list)):
            for file in os.listdir(self.dir_descarga+str(folder)):
                if os.path.getsize(self.dir_descarga+str(folder)+"/"+file) < 2000000:
                    os.remove(self.dir_descarga+str(folder)+"/"+file)
        



