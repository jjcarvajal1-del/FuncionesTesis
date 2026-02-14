"""
ALGORITMO DE INTERSECCIÓN DE CURVAS DISCRETAS CON ALTA PRECISIÓN
==================================================================

Requisitos: NumPy >= 1.20, SciPy >= 1.5
"""

import numpy as np
from scipy.optimize import brentq, fsolve
import warnings


class InterseccionCurvas:
    """
    Encuentra intersecciones precisas entre dos curvas discretas.
    
    Implementa:
    1. Búsqueda del intervalo de cruce (cambio de signo)
    2. Interpolación lineal en el intervalo
    3. Búsqueda de raíces de alta precisión (Brent, fsolve o analítica)
    """
    
    def __init__(self, X, Y1, Y2, verbose=True):
        """Inicializa con datos de las dos curvas."""
        self.X = np.asarray(X, dtype=np.float64)
        self.Y1 = np.asarray(Y1, dtype=np.float64)
        self.Y2 = np.asarray(Y2, dtype=np.float64)
        self.verbose = verbose
        
        # Validaciones
        if not (len(self.X) == len(self.Y1) == len(self.Y2)):
            raise ValueError("X, Y1 e Y2 deben tener la misma longitud")
        if len(self.X) < 2:
            raise ValueError("Se requieren al menos 2 puntos")
        if not np.all(np.diff(self.X) > 0):
            raise ValueError("X debe estar ordenado ascendentemente")
    
    def buscar_intervalo_cruce(self):
        """Paso 1: Encuentra intervalo donde hay cambio de signo."""
        D = self.Y1 - self.Y2
        signos = np.sign(D)
        cambios = np.where(np.diff(signos) != 0)[0]
        
        if len(cambios) == 0:
            raise ValueError("No hay intersección o hay múltiples cruces")
        
        return cambios[0], D
    
    def _diferencia_interpolada(self, x, x_points, y1_points, y2_points):
        """Calcula f(x) = Y1_interp(x) - Y2_interp(x)."""
        y1_interp = np.interp(x, x_points, y1_points)
        y2_interp = np.interp(x, x_points, y2_points)
        return y1_interp - y2_interp
    
    def encontrar_interseccion(self, metodo='brentq', tol=1e-12):
        """Encuentra el punto de intersección exacto."""
        
        # PASO 1: Localizar intervalo
        i, D = self.buscar_intervalo_cruce()
        x_inf = self.X[i]
        x_sup = self.X[i+1]
        
        if self.verbose:
            print(f"\nIntervalo de cruce: [{x_inf:.8f}, {x_sup:.8f}]")
            print(f"D[{i}] = {D[i]:+.6e}, D[{i+1}] = {D[i+1]:+.6e}")
        
        # PASO 2 & 3: Resolver
        if metodo == 'brentq':
            xint = brentq(
                self._diferencia_interpolada,
                x_inf, x_sup,
                args=(self.X, self.Y1, self.Y2),
                xtol=tol, rtol=tol
            )
        
        elif metodo == 'lineal':
            # Solución analítica exacta
            y1_i, y1_i1 = self.Y1[i], self.Y1[i+1]
            y2_i, y2_i1 = self.Y2[i], self.Y2[i+1]
            
            m1 = (y1_i1 - y1_i) / (x_sup - x_inf)
            m2 = (y2_i1 - y2_i) / (x_sup - x_inf)
            
            denom = m1 - m2
            if abs(denom) < 1e-14:
                xint = (x_inf + x_sup) / 2
            else:
                xint = (y2_i - y1_i) / denom + x_inf
        
        elif metodo == 'fsolve':
            x_inicial = (x_inf + x_sup) / 2
            xint, info, ier, msg = fsolve(
                self._diferencia_interpolada,
                x_inicial,
                args=(self.X, self.Y1, self.Y2),
                full_output=True, xtol=tol
            )
            xint = float(xint[0]) if hasattr(xint, '__len__') else float(xint)
            
            if ier != 1 and self.verbose:
                warnings.warn(f"fsolve no convergió: {msg}")
        
        else:
            raise ValueError(f"Método desconocido: {metodo}")
        
        # Calcular y
        yint = np.interp(xint, self.X, self.Y1)
        yint_check = np.interp(xint, self.X, self.Y2)
        error_y = abs(yint - yint_check)
        
        info_dict = {
            'metodo': metodo,
            'intervalo': (x_inf, x_sup),
            'indice_cruce': i,
            'error_consistencia': error_y,
            'valor_y1_en_xint': yint,
            'valor_y2_en_xint': yint_check
        }
        
        if self.verbose:
            print(f"Intersección: x={xint:.12f}, y={yint:.12f}")
            print(f"Error: {error_y:.2e}")
        
        return xint, yint, info_dict



