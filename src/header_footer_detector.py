import numpy as np
import pandas as pd
from sklearn.cluster import HDBSCAN

class HeaderFooterDetector:
    def __init__(self, page_count, hff=0.9, quantile=0.2):
        """
        Inicializa o detector de cabeçalhos e rodapés.

        :param page_count: Número total de páginas no documento PDF.
        :param hff: Fator de ajuste para determinar o tamanho mínimo dos clusters.
        :param quantile: Quantil utilizado para definir os limites superior e inferior.
        """
        self.page_count = page_count
        self.hff = hff
        self.quantile = quantile

    def detect(self, coordinates):
        """
        Detecta as posições de cabeçalho e rodapé usando clustering.

        :param coordinates: Dicionário contendo listas de coordenadas 'x0', 'y0', 'x1', 'y1'.
        :return: Tupla (header, footer) com as coordenadas dos limites do cabeçalho e rodapé.
        """
        df = pd.DataFrame(coordinates)

        # Calcular quantis para determinar os limites do cabeçalho e rodapé
        upper = np.floor(df['y0'].quantile(1 - self.quantile))
        lower = np.ceil(df['y1'].quantile(self.quantile))

        # Determinar o tamanho mínimo do cluster
        min_clust = max(int(np.floor(self.page_count * self.hff)), 2)
        #print("TAMANHO MINIMO DO CLUSTER: ", min_clust)
        if min_clust < 2:
            min_clust = 2

        #print("TAMANHO MINIMO DO CLUSTER: ", min_clust)
        # Aplicar HDBSCAN para clustering
        hdbscan = HDBSCAN(min_cluster_size=min_clust)
        df['clusters'] = hdbscan.fit_predict(df)

        # Agregar dados dos clusters
        df_group = df.groupby('clusters').agg(
            avg_y0=('y0', 'mean'),
            avg_y1=('y1', 'mean'),
            std_y0=('y0', 'std'),
            std_y1=('y1', 'std'),
            max_y0=('y0', 'max'),
            max_y1=('y1', 'max'),
            min_y0=('y0', 'min'),
            min_y1=('y1', 'min'),
            cluster_size=('clusters', 'count'),
            avg_x0=('x0', 'mean')
        ).reset_index()

        # Ordenar os clusters com base nas posições médias
        df_group = df_group.sort_values(['avg_y0', 'avg_y1'], ascending=[True, True])

        std = 0
        # Identificar candidatos a rodapé
        footer_candidates = df_group[
            (np.floor(df_group['std_y0']) == std) &
            (np.floor(df_group['std_y1']) == std) &
            (df_group['min_y0'] >= upper) &
            (df_group['cluster_size'] <= self.page_count)
        ]['min_y0']
        footer = np.floor(footer_candidates.min()) if not footer_candidates.empty else None

        # Identificar candidatos a cabeçalho
        header_candidates = df_group[
            (np.floor(df_group['std_y0']) == std) &
            (np.floor(df_group['std_y1']) == std) &
            (df_group['min_y1'] <= lower) &
            (df_group['cluster_size'] <= self.page_count)
        ]['min_y1']
        header = np.ceil(header_candidates.max()) if not header_candidates.empty else None

        return header, footer
