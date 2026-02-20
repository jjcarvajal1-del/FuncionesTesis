"""
=============================================================================
LATIN HYPERCUBE SAMPLING (LHS) PARA ANÁLISIS DE CONFIABILIDAD ESTRUCTURAL
=============================================================================

Script que implementa el Muestreo por Hipercubo Latino (LHS) para generar
muestras correlacionadas de 14 variables aleatorias con diferentes 
distribuciones de probabilidad.

=============================================================================
"""

import numpy as np
from scipy import stats
import pandas as pd

def generar_lhs_muestreo(n_samples=1000, seed=2025):
    """
    Genera muestras usando Latin Hypercube Sampling (LHS) para 14 variables 
    aleatorias con diferentes distribuciones de probabilidad.
    
    El LHS es una técnica de muestreo estratificado que produce muestras 
    más uniformemente distribuidas que el muestreo de Monte Carlo simple,
    reduciendo la varianza de estimadores con menos muestras.
    
    Parámetros:
    -----------
    n_samples : int, default=500
        Número de muestras a generar
    seed : int, default=2025
        Semilla para reproducibilidad de los resultados
    
    Regresa:
    --------
    samples : np.ndarray
        Matriz de forma (n_samples, 14) con las muestras transformadas
        a las distribuciones especificadas. Cada columna corresponde a
        una variable aleatoria diferente.
    
    Notas:
    ------
    Distribuciones implementadas:
    - Normal (norm): 9 variables
    - Gumbel derecha (gumbel_r): 1 variable
    - Normal truncada (truncnorm): 4 variables
    
    Proceso:
    1. Generación de matriz uniforme estratificada en [0, 1] usando LHS
    2. Permutación aleatoria para romper correlaciones sistemáticas
    3. Transformación a distribuciones específicas usando PPF (Inverse CDF)
    """
    
    # Establecer semilla para reproducibilidad
    np.random.seed(seed)
    
    n_variables = 14
    
    # ========================================================================
    # PASO 1: Generar matriz uniforme estratificada en [0, 1] usando LHS
    # ========================================================================
    
    print("[1/3] Generando matriz uniforme estratificada (LHS)...")
    
    uniform_matrix = np.zeros((n_samples, n_variables))
    
    for j in range(n_variables):
        # Crear n_samples intervalos de igual tamaño en [0, 1]
        intervals = np.linspace(0, 1, n_samples + 1)
        
        # Para cada intervalo, muestrear un valor uniforme
        uniform_samples = np.array([
            np.random.uniform(intervals[i], intervals[i + 1])
            for i in range(n_samples)
        ])
        
        # Permutar aleatoriamente para romper la correlación sistemática
        permutation = np.random.permutation(n_samples)
        uniform_matrix[:, j] = uniform_samples[permutation]
    
    print(f"   ✓ Matriz uniforme LHS generada: {uniform_matrix.shape}")
    
    # ========================================================================
    # PASO 2: Transformar muestras uniformes a distribuciones específicas
    # ========================================================================
    
    print("[2/3] Transformando a distribuciones de probabilidad...")
    
    # Inicializar matriz de salida
    samples = np.zeros((n_samples, n_variables))
    # [0] Carga muerta entrepiso - Normal
    samples[:, 0] = stats.norm.ppf(uniform_matrix[:, 0], loc=6.03, scale=0.63)
    # [1] Carga muerta cubierta - Normal
    samples[:, 1] = stats.norm.ppf(uniform_matrix[:, 1], loc=0.21, scale=0.02)
    # [2] Carga viva - Gumbel derecha
    samples[:, 2] = stats.gumbel_r.ppf(uniform_matrix[:, 2], loc=1.75, scale=0.36)
    # [3] Resistencia f'c vigas - Normal
    samples[:, 3] = stats.norm.ppf(uniform_matrix[:, 3], loc=25.2, scale=4.54)
    # [4] Resistencia f'c columnas - Normal
    samples[:, 4] = stats.norm.ppf(uniform_matrix[:, 4], loc=34.0, scale=6.05)
    # [5] Límite fluencia acero fy - Normal
    samples[:, 5] = stats.norm.ppf(uniform_matrix[:, 5], loc=453.6, scale=40.82)
    # [6] Resistencia última fu acero - Normal
    samples[:, 6] = stats.norm.ppf(uniform_matrix[:, 6], loc=683.6, scale=27.35)
    # [7] Módulo Ec concreto - Normal
    samples[:, 7] = stats.norm.ppf(uniform_matrix[:, 7], loc=23.59, scale=4.25)
    # [8] Módulo Es acero - Normal
    samples[:, 8] = stats.norm.ppf(uniform_matrix[:, 8], loc=200, scale=8)
    # [9] Ancho vigas bw - Normal Truncada
    mu_bw, sigma_bw = 0.303, 0.009
    a_bw = (0.29 - mu_bw) / sigma_bw
    b_bw = (0.315 - mu_bw) / sigma_bw
    samples[:, 9] = stats.truncnorm.ppf(uniform_matrix[:, 9], 
                                         a=a_bw, b=b_bw, 
                                         loc=mu_bw, scale=sigma_bw)
    # [10] Altura vigas h - Normal Truncada
    mu_h, sigma_h = 0.396, 0.012
    a_h = (0.39 - mu_h) / sigma_h
    b_h = (0.415 - mu_h) / sigma_h
    samples[:, 10] = stats.truncnorm.ppf(uniform_matrix[:, 10], 
                                          a=a_h, b=b_h, 
                                          loc=mu_h, scale=sigma_h)
    # [11] Ancho columnas bc - Normal Truncada
    mu_bc, sigma_bc = 0.404, 0.016
    a_bc = (0.39 - mu_bc) / sigma_bc
    b_bc = (0.415 - mu_bc) / sigma_bc
    samples[:, 11] = stats.truncnorm.ppf(uniform_matrix[:, 11], 
                                          a=a_bc, b=b_bc, 
                                          loc=mu_bc, scale=sigma_bc)    
    # [12] Altura columnas hc - Normal Truncada
    mu_hc, sigma_hc = 0.404, 0.016
    a_hc = (0.39 - mu_hc) / sigma_hc
    b_hc = (0.415 - mu_hc) / sigma_hc
    samples[:, 12] = stats.truncnorm.ppf(uniform_matrix[:, 12], 
                                          a=a_hc, b=b_hc, 
                                          loc=mu_hc, scale=sigma_hc)  
    # [13] Recubrimiento - Normal
    samples[:, 13] = stats.norm.ppf(uniform_matrix[:, 13], loc=34.67, scale=1.65)
    print(f"   ✓ Transformación completada: {samples.shape}")
    return samples


def crear_dataframe_muestras(samples):
    """
    Convierte la matriz de muestras NumPy a un DataFrame de pandas
    con nombres descriptivos de variables.
    
    Parameters:
    -----------
    samples : np.ndarray
        Matriz de muestras de forma (n_samples, 14)
    
    Returns:
    --------
    df : pd.DataFrame
        DataFrame con las muestras y nombres de columnas descriptivos
    """
    
    var_names = [
        "Carga_muerta_entrepiso",
        "Carga_muerta_cubierta",
        "Carga_viva",
        "fc_vigas",
        "fc_columnas",
        "fy_acero",
        "fu_acero",
        "Ec_concreto",
        "Es_acero",
        "bv_vigas",
        "hv_vigas",
        "bc_columnas",
        "hc_columnas",
        "recubrimiento"
    ]
    
    return pd.DataFrame(samples, columns=var_names)


def imprimir_resumen_estadistico(samples, var_names=None):
    """
    Imprime un resumen estadístico completo de las muestras.
    
    Parameters:
    -----------
    samples : np.ndarray
        Matriz de muestras de forma (n_samples, 14)
    var_names : list, optional
        Lista de nombres de variables. Si es None, usa nombres por defecto.
    """
    
    if var_names is None:
        var_names = [
            "Carga muerta entrepiso",
            "Carga muerta cubierta",
            "Carga viva",
            "Resistencia f'c vigas",
            "Resistencia f'c columnas",
            "Límite fluencia acero fy",
            "Resistencia última fu acero",
            "Módulo Ec concreto",
            "Módulo Es acero",
            "Ancho vigas bv",
            "Altura vigas hv",
            "Ancho columnas bc",
            "Altura columnas hc",
            "Recubrimiento"
        ]
    
    print()
    print("=" * 90)
    print("ESTADÍSTICAS DESCRIPTIVAS DE LAS MUESTRAS LHS")
    print("=" * 90)
    print()
    print(f"{'Variable':<30} {'Media':<12} {'Desv. Est':<12} {'Min':<12} {'Max':<12} {'CV(%)':<10}")
    print("-" * 90)
    
    for j, name in enumerate(var_names):
        media = np.mean(samples[:, j])
        desv = np.std(samples[:, j])
        minimo = np.min(samples[:, j])
        maximo = np.max(samples[:, j])
        cv = (desv / media) * 100 if media != 0 else 0
        
        print(f"{name:<30} {media:<12.4f} {desv:<12.4f} {minimo:<12.4f} {maximo:<12.4f} {cv:<10.2f}")
    
    print()


# =============================================================================
# EJECUCIÓN PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    
    print()
    print("=" * 90)
    print("LATIN HYPERCUBE SAMPLING (LHS)")
    print("Análisis de Confiabilidad Estructural - 14 Variables Aleatorias")
    print("=" * 90)
    print()
    
    # Generar muestras LHS
    lhs_samples = generar_lhs_muestreo(n_samples=1000, seed=2025)
    
    print()
    print("[3/3] Verificando resultados...")
    print(f"   ✓ Matriz generada: {lhs_samples.shape[0]} muestras × {lhs_samples.shape[1]} variables")
    print()
    
    # Nombres de variables
    var_names = [
        "Carga muerta entrepiso",
        "Carga muerta cubierta",
        "Carga viva",
        "Resistencia f'c vigas",
        "Resistencia f'c columnas",
        "Límite fluencia acero fy",
        "Resistencia última fu acero",
        "Módulo Ec concreto",
        "Módulo Es acero",
        "Ancho vigas bv",
        "Altura vigas hv",
        "Ancho columnas bc",
        "Altura columnas hc",
        "Recubrimiento"
    ]
    
    # =========================================================================
    # MOSTRAR PRIMERAS 5 FILAS
    # =========================================================================
    
    print("PRIMERAS 5 FILAS DE LA MATRIZ DE MUESTRAS:")
    print("-" * 90)
    
    df_preview = pd.DataFrame(lhs_samples[:5], columns=var_names)
    print(df_preview.to_string())
    
    # =========================================================================
    # MOSTRAR ESTADÍSTICAS DESCRIPTIVAS
    # =========================================================================
    
    imprimir_resumen_estadistico(lhs_samples, var_names)
    
    # =========================================================================
    # CREAR DATAFRAME Y GUARDAR (OPCIONAL)
    # =========================================================================
    
    # Descomentar las siguientes líneas para guardar los datos en CSV
    df_samples = crear_dataframe_muestras(lhs_samples)
    df_samples.to_csv('lhs_muestras_500.csv', index=False)
    print("Muestras guardadas en: lhs_muestras_500.csv")
    
    print("=" * 90)
    print("Script completado exitosamente ✓")
    print("=" * 90)
    print()
print(df_samples)
