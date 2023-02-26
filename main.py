import customtkinter
from tkintermapview import TkinterMapView
import pandas as pd
import geopandas as gpd
import requests
import json
import os
import openpyxl

customtkinter.set_default_color_theme("blue")


class App(customtkinter.CTk):

    APP_NAME = "Captação de Cliente Google Maps"
    WIDTH = 800
    HEIGHT = 500

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.bind("<Command-w>", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)

        self.marker_list = []
        self.current_position = ()

        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self, width=150, corner_radius=0, fg_color=None)
        self.frame_left.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.frame_right = customtkinter.CTkFrame(master=self, corner_radius=0)
        self.frame_right.grid(row=0, column=1, rowspan=1, pady=0, padx=0, sticky="nsew")

        # ============ frame_left ============

        self.frame_left.grid_rowconfigure(2, weight=1)

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Marcar Local",
                                                command=self.set_marker_event)
        self.button_1.grid(pady=(20, 0), padx=(20, 20), row=0, column=0)

        self.button_2 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Limpar",
                                                command=self.clear_marker_event)
        self.button_2.grid(pady=(20, 0), padx=(20, 20), row=1, column=0)

        self.entry_keywords = customtkinter.CTkEntry(master=self.frame_left,
                                            placeholder_text="Palavras-chave")
        self.entry_keywords.grid(row=2, column=0, sticky="we", padx=(20, 20), pady=0)

        self.button_search_clients = customtkinter.CTkButton(master=self.frame_left,
                                                text="Buscar Clientes",
                                                command=self.search_clients)
        self.button_search_clients.grid(pady=(0, 0), padx=(20, 20), row=3, column=0)

        self.map_label = customtkinter.CTkLabel(self.frame_left, text="Tipo de mapa:", anchor="w")
        self.map_label.grid(row=4, column=0, padx=(20, 20), pady=(20, 0))
        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left, values=["OpenStreetMap", "Google normal", "Google satellite"],
                                                                       command=self.change_map)
        self.map_option_menu.grid(row=5, column=0, padx=(20, 20), pady=(10, 0))

        self.appearance_mode_label = customtkinter.CTkLabel(self.frame_left, text="Tema:", anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=(20, 20), pady=(20, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.frame_left, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=(20, 20), pady=(10, 20))

        # ============ frame_right ============

        self.frame_right.grid_rowconfigure(1, weight=1)
        self.frame_right.grid_rowconfigure(0, weight=0)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(1, weight=0)
        self.frame_right.grid_columnconfigure(2, weight=1)

        self.map_widget = TkinterMapView(self.frame_right, corner_radius=0)
        self.map_widget.grid(row=1, rowspan=1, column=0, columnspan=3, sticky="nswe", padx=(0, 0), pady=(0, 0))

        self.entry = customtkinter.CTkEntry(master=self.frame_right,
                                            placeholder_text="Digite um local")
        self.entry.grid(row=0, column=0, sticky="we", padx=(12, 0), pady=12)
        self.entry.bind("<Return>", self.search_event)

        self.button_5 = customtkinter.CTkButton(master=self.frame_right,
                                                text="Buscar",
                                                width=90,
                                                command=self.search_event)
        self.button_5.grid(row=0, column=1, sticky="w", padx=(12, 0), pady=12)

        # Set default values
        self.map_widget.set_address("Rio de Janeiro")
        self.map_option_menu.set("OpenStreetMap")
        self.appearance_mode_optionemenu.set("Dark")

    def search_event(self, event=None):
        self.map_widget.set_address(self.entry.get())

    def set_marker_event(self):
        self.current_position = self.map_widget.get_position()
        self.marker_list.append(self.map_widget.set_marker(self.current_position[0], self.current_position[1]))

    def clear_marker_event(self):
        for marker in self.marker_list:
            marker.delete()

    def change_appearance_mode(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_map(self, new_map: str):
        if new_map == "OpenStreetMap":
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif new_map == "Google normal":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif new_map == "Google satellite":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()

    def find_locations(self, search_url, api_key):
                #lista de listas para todos os dados
                final_data = []

                #while loop para solicitar e analisar os arquivos JSON solicitados
                while True:
                    respon = requests.get(search_url)
                    jj = json.loads(respon.text)
                    results = jj['results']
                    #analise todas as informações necessárias
                    for result in results:
                        name = result['name']
                        place_id = result ['place_id']
                        lat = result['geometry']['location']['lat']
                        longi = result['geometry']['location']['lng']
                        rating = result['rating']
                        types = result['types']
                        data = [name, place_id, lat, longi, rating, types]
                        final_data.append(data)
                    
                    #se houver uma próxima página, o loop será reiniciado com uma url atualizada
                    #se não houver próxima página, o programa grava em um csv e salva em df    
                    if 'next_page_token' not in jj:
                        labels = ['Place Name','ID_Field', 'Latitude', 'Longitude', 'Rating', 'Tags']
                        location_df = pd.DataFrame.from_records(final_data, columns=labels)
                        #location_df.to_csv('location.csv')
                        break
                    else:
                        next_page_token = jj['next_page_token']
                        search_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?key='+str(api_key)+'&pagetoken='+str(next_page_token)

                return(final_data, location_df)
    
    def find_details(self, final_data, api_key):

                final_detailed_data =[]

                #Usa o ID exclusivo de cada local para usar outra solicitação de API para obter informações de telefone e site de cada empresa.
                for places in final_data:
                    id_field = places[1]
                    req_url = 'https://maps.googleapis.com/maps/api/place/details/json?place_id='+str(id_field)+'&fields=name,formatted_phone_number,website&key='+str(api_key)
                    respon = requests.get(req_url)
                    jj = json.loads(respon.text)
                    print(jj)
                    results = jj['result']
                    identification = id_field
                    try:
                        phone = results["formatted_phone_number"]
                    except KeyError:
                        continue
                    try:
                        website = results["website"]
                    except KeyError:
                        continue
                    title = results["name"]
                    detailed_data = [title, identification, phone, website]
                    final_detailed_data.append(detailed_data)

                columns = ["Business", "ID_Field","Phone", "Website"]
                details_df = pd.DataFrame.from_records(final_detailed_data, columns=columns)
                details_df.to_csv('further_details.csv')
                
                return details_df
    
    def join_data(self, details_df,location_df,keyword):

                final_sheet = location_df.join(details_df.set_index('ID_Field'), on='ID_Field')

                final_sheet.to_csv(str(keyword) + ".csv")

                print(final_sheet)

                return final_sheet
    
    def csv_to_point(self, non_spatial_data):
                #crie o geodataframe e exporte-o como um arquivo de ponto
                del non_spatial_data['Tags']
                spatial_df = gpd.GeoDataFrame(non_spatial_data, geometry=gpd.points_from_xy(non_spatial_data.Longitude, non_spatial_data.Latitude))
                #spatial_df.to_csv("point_data.csv")
                print(spatial_df)
                #spatial_df.to_file("point_data.shp")

                #create a projection file that corresponds to where data was taken from
                #prj = open("point_data.prj", "w")
                epsg = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]'
                #prj.write(epsg)
                #prj.close()

                return(spatial_df)
    
    def planilha(self):
        path = r"./"#COLOCAR O LOCAL ONDE ESTÁ OS EXCELS SALVOS
        # use compreensão de lista para criar uma lista de arquivos csv
        csv_files = [file for file in os.listdir(path) if file.endswith('.csv')]

        # cria uma lista vazia para armazenar os DataFrames
        df_list = []

        # iterar pelos arquivos csv
        for csv_file in csv_files:
            # lê o arquivo csv atual em um DataFrame
            df = pd.read_csv(os.path.join(path, csv_file))
            # adiciona uma nova coluna 'file_name' com o nome do arquivo csv atual
            df['name'] = os.path.basename(csv_file)
            # anexa o DataFrame atual à lista
            df_list.append(df)
        
        print(f'teste {df_list}')

        # concatenar todos os DataFrames em um único DataFrame
        merged_df = pd.concat(df_list)

        # grava o DataFrame mesclado em um novo arquivo csv
        merged_df.to_excel("all.xlsx", index=False)
    
    def search_clients(self):
        api_key = 'AIzaSyAQBPAC422_rwNTDvfM8tq2Opma5VCa12A'
        search_radius = '100000'
        
        coords = ','.join([str(value) for value in self.current_position])
        
        keywords = self.entry_keywords.get().split(",")

        for keyword in keywords:

            request_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+coords+'&radius='+str(search_radius)+'&keyword='+str(keyword)+'&key='+str(api_key)

            #encontre os locais dos estabelecimentos desejados no google maps
            final_data, location_df = self.find_locations(request_url, api_key)

            #encontre site, telefone e avaliações de estabelecimentos
            details_df = self.find_details(final_data, api_key)

            #junte os dois dataframes para ter um produto final
            non_spatial_data = self.join_data(details_df,location_df,keyword)

            #c
            spatial_df = self.csv_to_point(non_spatial_data)

            self.planilha()




if __name__ == "__main__":
    app = App()
    app.start()