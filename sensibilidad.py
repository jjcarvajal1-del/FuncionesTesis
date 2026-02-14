
"""
ANÁLISIS DE SENSIBILIDAD OAT - ONE-AT-A-TIME SENSITIVITY ANALYSIS
Autor: Sistema Automático
Fecha: 2025-12-06
Versión: 3.1 (Percentiles Parametrizados)

Descripción:
    Implementación de algoritmo OAT (One-At-a-Time) para análisis de sensibilidad
    determinista local univariado.

    CARACTERÍSTICAS v3.1:
    - Completamente genérico: funciona con cualquier función
    - Percentiles 10-90 CALCULADOS AUTOMÁTICAMENTE desde media y desv.est
    - Distribuciones soportadas: Normal, Gumbel, Normal truncada
    - Sin lógica de pushover incluida

Uso:
    from analisis_oat import AnalisisSensibilidadOAT, variables_aleatorias

    # Tu función personalizada
    def pushover(x1, x2, x3, ..., x14):
        # Tu procedimiento completo de análisis
        return resultado

    # Ejecutar OAT
    valores_nominales = [var['media'] for var in variables_aleatorias.values()]
    analizador = AnalisisSensibilidadOAT(pushover, variables_aleatorias, valores_nominales)
    resultados = analizador.realizar_oat()
    print(analizador.generar_tabla_resultados())
"""

import numpy as np
import pandas as pd
from scipy.stats import norm, gumbel_r
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# FUNCIÓN PARA CALCULAR PERCENTILES AUTOMÁTICAMENTE
# ============================================================================

def calcular_percentiles(media, desv_est, distribucion='Normal'):
    """
    Calcula percentiles 10 y 90 según la distribución.

    Parámetros:
    -----------
    media : float
        Media (o parámetro central) de la distribución
    desv_est : float
        Desviación estándar
    distribucion : str
        Tipo: 'Normal', 'Gumbel', 'Normal truncada'

    Retorna:
    --------
    tuple : (P10, P90) - Percentil 10 y percentil 90
    """

    if distribucion == 'Normal' or distribucion == 'Normal truncada':
        # Distribución normal: N(media, desv_est)
        # Percentiles se calculan usando función cuantil ppf
        dist = norm(loc=media, scale=desv_est)
        P10 = dist.ppf(0.10)
        P90 = dist.ppf(0.90)

    elif distribucion == 'Gumbel':
        # Distribución Gumbel
        # Relaciones paramétricas:
        # media = loc + gamma * scale (donde gamma ≈ 0.5772, constante de Euler-Mascheroni)
        # desv_est = scale * pi / sqrt(6)
        # Despejando: scale = desv_est * sqrt(6) / pi
        scale = desv_est * np.sqrt(6) / np.pi
        loc = media - 0.5772 * scale
        dist = gumbel_r(loc=loc, scale=scale)
        P10 = dist.ppf(0.10)
        P90 = dist.ppf(0.90)

    else:
        raise ValueError(f"Distribución no soportada: {distribucion}")

    return P10, P90


# ============================================================================
# DEFINICIÓN DE VARIABLES ALEATORIAS (SIN PERCENTILES - SE CALCULAN AUTOMÁTICAMENTE)
# ============================================================================

variables_base = {
    1: {'nombre': 'Carga muerta de entrepiso', 'unidad': 'kN/m²', 'distribucion': 'Normal', 
        'media': 6.03, 'desviacion_estandar': 0.63},
    2: {'nombre': 'Carga muerta de cubierta', 'unidad': 'kN/m²', 'distribucion': 'Normal', 
        'media': 0.21, 'desviacion_estandar': 0.02},
    3: {'nombre': 'Carga viva', 'unidad': 'kN/m²', 'distribucion': 'Gumbel', 
        'media': 1.75, 'desviacion_estandar': 0.46},
    4: {'nombre': 'fc vigas', 'unidad': 'MPa', 'distribucion': 'Normal', 
        'media': 25.2, 'desviacion_estandar': 4.54},
    5: {'nombre': 'fc columnas', 'unidad': 'MPa', 'distribucion': 'Normal', 
        'media': 34.0, 'desviacion_estandar': 6.05},
    6: {'nombre': 'Fy acero', 'unidad': 'MPa', 'distribucion': 'Normal', 
        'media': 453.6, 'desviacion_estandar': 40.82},
    7: {'nombre': 'Fu acero', 'unidad': 'MPa', 'distribucion': 'Normal', 
        'media': 683.64, 'desviacion_estandar': 27.35},
    8: {'nombre': 'Ec concreto', 'unidad': 'GPa', 'distribucion': 'Normal', 
        'media': 23.59, 'desviacion_estandar': 4.25},
    9: {'nombre': 'Es acero', 'unidad': 'GPa', 'distribucion': 'Normal', 
        'media': 200.0, 'desviacion_estandar': 8.0},
    10: {'nombre': 'Ancho viga', 'unidad': 'm', 'distribucion': 'Normal truncada', 
        'media': 0.303, 'desviacion_estandar': 0.009},
    11: {'nombre': 'Alto viga', 'unidad': 'm', 'distribucion': 'Normal truncada', 
        'media': 0.396, 'desviacion_estandar': 0.012},
    12: {'nombre': 'Ancho columna', 'unidad': 'm', 'distribucion': 'Normal truncada', 
        'media': 0.404, 'desviacion_estandar': 0.016},
    13: {'nombre': 'Alto columna', 'unidad': 'm', 'distribucion': 'Normal truncada', 
        'media': 0.404, 'desviacion_estandar': 0.016},
    14: {'nombre': 'Recubrimiento', 'unidad': 'mm', 'distribucion': 'Normal', 
        'media': 34.67, 'desviacion_estandar': 1.65},
}

# Construir diccionario de variables con percentiles calculados automáticamente
variables_aleatorias = {}
for var_id, var_info in variables_base.items():
    P10, P90 = calcular_percentiles(var_info['media'], var_info['desviacion_estandar'], var_info['distribucion'])
    variables_aleatorias[var_id] = {
        'nombre': var_info['nombre'],
        'unidad': var_info['unidad'],
        'distribucion': var_info['distribucion'],
        'media': var_info['media'],
        'desviacion_estandar': var_info['desviacion_estandar'],
        'rango_min': P10,
        'rango_max': P90
    }


# ============================================================================
# CLASE ANALIZADOR OAT - GENÉRICO
# ============================================================================

class AnalisisSensibilidadOAT:
    """
    Análisis de sensibilidad determinista local univariado (OAT).
    Genérico: funciona con cualquier función y conjunto de variables.
    """

    def __init__(self, funcion, variables_dict, valores_nominales):
        """
        Inicializa el analizador.

        Parámetros:
        -----------
        funcion : callable
            Función de salida Y = f(X1, X2, ..., Xn)

        variables_dict : dict
            Diccionario con definición de variables
            Estructura: {id: {'nombre', 'unidad', 'media', 'desviacion_estandar', 
                              'distribucion', 'rango_min', 'rango_max'}}

        valores_nominales : list or array
            Valores nominales (medias) de cada variable en orden
        """
        self.funcion = funcion
        self.variables_dict = variables_dict
        self.valores_nominales = np.array(valores_nominales, dtype=float)
        self.n_variables = len(variables_dict)
        self.resultados = []
        self.resultados_ordenados = []

    def evaluar_en_punto(self, punto):
        """
        Evalúa la función en un punto específico.

        Parámetros:
        -----------
        punto : array-like
            Vector de valores para evaluar

        Retorna:
        --------
        float : Valor de salida de la función
        """
        try:
            return self.funcion(*punto)
        except Exception as e:
            print(f"Error al evaluar función: {e}")
            return None

    def realizar_oat(self, verbose=True):
        """
        Realiza el análisis OAT.

        Procedimiento:
        1. Calcula Y0 en el punto nominal
        2. Para cada variable:
           - Varía entre P10 (rango_min) y P90 (rango_max)
           - Calcula Y_min y Y_max
           - Calcula IR = |Y_max - Y_min|
        3. Ordena por IR descendente

        Parámetros:
        -----------
        verbose : bool
            Si es True, muestra progreso del análisis

        Retorna:
        --------
        list : Resultados ordenados por impacto (mayor a menor)
        """
        # Calcular valor nominal
        Y0 = self.evaluar_en_punto(self.valores_nominales)

        if verbose:
            print("\n" + "="*100)
            print("ANÁLISIS DE SENSIBILIDAD OAT (ONE-AT-A-TIME)")
            print("="*100)
            print(f"\nValor nominal Y₀ = {Y0:.6f}\n")
            print(f"{'Var':<4} {'Nombre':<30} {'P10':<12} {'P90':<12} {'Y_P10':<12} {'Y_P90':<12} {'IR':<12}")
            print("-" * 100)

        # Iterar sobre cada variable
        for i in range(self.n_variables):
            var_idx = i + 1
            var_info = self.variables_dict[var_idx]

            # Evaluar en percentil 10 (mínimo)
            punto_min = self.valores_nominales.copy()
            punto_min[i] = var_info['rango_min']
            Y_min = self.evaluar_en_punto(punto_min)

            # Evaluar en percentil 90 (máximo)
            punto_max = self.valores_nominales.copy()
            punto_max[i] = var_info['rango_max']
            Y_max = self.evaluar_en_punto(punto_max)

            # Calcular Rango de Impacto
            IR = abs(Y_max - Y_min)

            # Guardar resultado
            resultado = {
                'variable_id': var_idx,
                'nombre': var_info['nombre'],
                'unidad': var_info['unidad'],
                'rango_min': var_info['rango_min'],
                'rango_max': var_info['rango_max'],
                'Y_min': Y_min,
                'Y_max': Y_max,
                'IR': IR,
                'Y0': Y0
            }
            self.resultados.append(resultado)

            if verbose:
                print(f"{var_idx:<4} {var_info['nombre']:<30} {var_info['rango_min']:<12.4f} "
                      f"{var_info['rango_max']:<12.4f} {Y_min:<12.4f} {Y_max:<12.4f} {IR:<12.4f}")

        # Ordenar por IR descendente
        self.resultados_ordenados = sorted(self.resultados, key=lambda x: x['IR'], reverse=True)

        if verbose:
            print("-" * 100 + "\n")

        return self.resultados_ordenados

    def generar_tabla_resultados(self):
        """
        Genera tabla de resultados en formato DataFrame.

        Retorna:
        --------
        pandas.DataFrame : Tabla con resultados ordenados por impacto
        """
        datos = []
        for rank, resultado in enumerate(self.resultados_ordenados, 1):
            IR_max = max([r['IR'] for r in self.resultados_ordenados])
            Y0 = resultado['Y0']

            datos.append({
                'Ranking': rank,
                'Var': resultado['variable_id'],
                'Nombre': resultado['nombre'],
                'Unidad': resultado['unidad'],
                'P10': f"{resultado['rango_min']:.4f}",
                'P90': f"{resultado['rango_max']:.4f}",
                'Y_P10': f"{resultado['Y_min']:.4f}",
                'Y_P90': f"{resultado['Y_max']:.4f}",
                'IR': f"{resultado['IR']:.4f}",
                'IR_Normalizado(%)': f"{(resultado['IR']/IR_max*100):.2f}",
                'Sensibilidad_Relativa(%)': f"{(resultado['IR']/Y0*100):.2f}"
            })

        return pd.DataFrame(datos)

    def exportar_csv(self, filename='resultados_oat.csv'):
        """
        Exporta resultados a archivo CSV.

        Parámetros:
        -----------
        filename : str
            Nombre del archivo CSV a crear
        """
        datos = []
        IR_max = max([r['IR'] for r in self.resultados_ordenados])

        for rank, resultado in enumerate(self.resultados_ordenados, 1):
            Y0 = resultado['Y0']

            datos.append({
                'Ranking': rank,
                'Variable_ID': resultado['variable_id'],
                'Nombre': resultado['nombre'],
                'Unidad': resultado['unidad'],
                'P10': round(resultado['rango_min'], 6),
                'P90': round(resultado['rango_max'], 6),
                'Y_Nominal': round(Y0, 6),
                'Y_P10': round(resultado['Y_min'], 6),
                'Y_P90': round(resultado['Y_max'], 6),
                'IR': round(resultado['IR'], 6),
                'IR_Normalizado_%': round((resultado['IR']/IR_max)*100, 2),
                'Sensibilidad_Relativa_%': round((resultado['IR']/Y0)*100, 2),
                'Cambio_%_P10': round(((resultado['Y_min'] - Y0)/Y0)*100, 2),
                'Cambio_%_P90': round(((resultado['Y_max'] - Y0)/Y0)*100, 2),
            })

        df = pd.DataFrame(datos)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n✓ Resultados exportados a: {filename}")
        return df

    def obtener_resumen(self):
        """
        Obtiene resumen estadístico del análisis.

        Retorna:
        --------
        dict : Estadísticas principales
        """
        if not self.resultados_ordenados:
            print("Ejecuta realizar_oat() primero")
            return None

        IRs = np.array([r['IR'] for r in self.resultados_ordenados])
        Y0 = self.resultados_ordenados[0]['Y0']

        return {
            'Total_Variables': len(self.resultados_ordenados),
            'Valor_Nominal_Y0': Y0,
            'IR_Maximo': IRs.max(),
            'IR_Minimo': IRs.min(),
            'IR_Promedio': IRs.mean(),
            'IR_Desv_Est': IRs.std(),
            'IR_Mediana': np.median(IRs),
            'Top_3_Variables': [r['variable_id'] for r in self.resultados_ordenados[:3]],
        }


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":

    # DEFINE TU FUNCIÓN AQUÍ
    def mi_funcion_ejemplo(x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x13, x14):
        """Función de ejemplo genérica"""
        return x1*2 + x2*1.5 + x3*3 + x4*0.5 + x5*0.5 + x6*1 + x7*1.2 + x8*2.5 + x9*0.1 + x10*5 + x11*4 + x12*3 + x13*2 + x14*1

    # Crear analizador
    valores_nominales = [var['media'] for var in variables_aleatorias.values()]

    analizador = AnalisisSensibilidadOAT(
        funcion=mi_funcion_ejemplo,
        variables_dict=variables_aleatorias,
        valores_nominales=valores_nominales
    )

    # Ejecutar análisis
    resultados = analizador.realizar_oat(verbose=True)

    # Mostrar resultados
    print("\nTABLA DE RESULTADOS:")
    print(analizador.generar_tabla_resultados().to_string(index=False))

    # Mostrar resumen
    print("\nRESUMEN ESTADÍSTICO:")
    resumen = analizador.obtener_resumen()
    for clave, valor in resumen.items():
        print(f"  {clave}: {valor}")

    # Exportar a CSV
    analizador.exportar_csv('resultados_oat.csv')

    print("\n" + "="*100)
    print("✓ Análisis completado")
    print("="*100)