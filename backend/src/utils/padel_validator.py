"""
Validador de reglas de pádel
Valida resultados de partidos según las reglas oficiales
"""
from typing import Dict, List, Tuple


class PadelValidator:
    """Validador de reglas de pádel"""
    
    @staticmethod
    def validar_set(juegos_eq1: int, juegos_eq2: int) -> Tuple[bool, str]:
        """
        Valida si un set es válido según las reglas de pádel
        
        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        # Validaciones básicas
        if juegos_eq1 < 0 or juegos_eq2 < 0:
            return False, "Los juegos no pueden ser negativos"
        
        if juegos_eq1 > 7 or juegos_eq2 > 7:
            return False, "Un set no puede tener más de 7 juegos"
        
        max_juegos = max(juegos_eq1, juegos_eq2)
        min_juegos = min(juegos_eq1, juegos_eq2)
        diferencia = abs(juegos_eq1 - juegos_eq2)
        
        # Set a 6 juegos
        if max_juegos == 6:
            if diferencia < 2:
                return False, "Para ganar 6 juegos debe haber ventaja de 2 o más"
            if min_juegos > 4:
                return False, "Set inválido: 6-5 o 6-6 no son resultados finales válidos"
            return True, ""
        
        # Set a 7 juegos (7-5 o 7-6 con tiebreak)
        if max_juegos == 7:
            if min_juegos not in [5, 6]:
                return False, "Un set a 7 juegos solo puede ser 7-5 o 7-6"
            return True, ""
        
        # Set incompleto
        if max_juegos < 6:
            return False, "Set incompleto: debe llegar a 6 o 7 juegos"
        
        return False, "Resultado de set inválido"
    
    @staticmethod
    def validar_tiebreak(puntos_eq1: int, puntos_eq2: int) -> Tuple[bool, str]:
        """
        Valida si un tiebreak es válido (a 7 puntos)
        
        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        if puntos_eq1 < 0 or puntos_eq2 < 0:
            return False, "Los puntos no pueden ser negativos"
        
        max_puntos = max(puntos_eq1, puntos_eq2)
        min_puntos = min(puntos_eq1, puntos_eq2)
        diferencia = abs(puntos_eq1 - puntos_eq2)
        
        # Debe llegar a 7 como mínimo
        if max_puntos < 7:
            return False, "Tiebreak incompleto: debe llegar a 7 puntos"
        
        # Si es 7, debe haber ventaja de 2+
        if max_puntos == 7:
            if diferencia < 2:
                return False, "Tiebreak a 7 puntos requiere ventaja de 2 o más"
            return True, ""
        
        # Si es más de 7, debe haber ventaja de exactamente 2
        if max_puntos > 7:
            if diferencia != 2:
                return False, "Tiebreak extendido requiere ventaja de exactamente 2 puntos"
            return True, ""
        
        return False, "Tiebreak inválido"
    
    @staticmethod
    def validar_supertiebreak(puntos_eq1: int, puntos_eq2: int) -> Tuple[bool, str]:
        """
        Valida si un supertiebreak es válido (a 10 puntos)
        
        Reglas:
        - Gana el primero en llegar a 10 puntos
        - Si ambos llegan a 9 o más, se requiere diferencia de 2 puntos
        - Ejemplos válidos: 10-0, 10-5, 10-8, 11-9, 13-11, 15-13
        
        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        if puntos_eq1 < 0 or puntos_eq2 < 0:
            return False, "Los puntos no pueden ser negativos"
        
        max_puntos = max(puntos_eq1, puntos_eq2)
        min_puntos = min(puntos_eq1, puntos_eq2)
        diferencia = abs(puntos_eq1 - puntos_eq2)
        
        # Debe llegar a 10 como mínimo
        if max_puntos < 10:
            return False, "Supertiebreak incompleto: debe llegar a 10 puntos"
        
        # Si el ganador tiene 10 puntos
        if max_puntos == 10:
            # Puede ser cualquier resultado: 10-0, 10-1, ..., 10-8
            # Solo si el perdedor tiene 9, necesita diferencia de 2 (pero eso sería 11-9)
            if min_puntos >= 9:
                return False, "Con 10-9 el supertiebreak continúa (debe haber diferencia de 2)"
            return True, ""
        
        # Si el ganador tiene más de 10 puntos (11, 12, 13, etc.)
        if max_puntos > 10:
            # Debe haber diferencia de exactamente 2
            if diferencia != 2:
                return False, f"Supertiebreak extendido requiere diferencia de exactamente 2 puntos (ej: 11-9, 13-11)"
            return True, ""
        
        return False, "Supertiebreak inválido"
    
    @staticmethod
    def validar_resultado_completo(sets: List[Dict], supertiebreak: Dict = None) -> Tuple[bool, List[str]]:
        """
        Valida un resultado completo de partido
        
        Args:
            sets: Lista de sets con formato {'juegos_eq1': int, 'juegos_eq2': int, 'esSuperTiebreak': bool}
            supertiebreak: Dict opcional con formato {'puntos_eq1': int, 'puntos_eq2': int}
            
        Returns:
            Tuple[bool, List[str]]: (es_valido, lista_de_errores)
        """
        errores = []
        
        # Validar que haya al menos 2 sets
        if len(sets) < 2:
            errores.append("Debe haber al menos 2 sets jugados")
            return False, errores
        
        # Validar que no haya más de 3 sets
        if len(sets) > 3:
            errores.append("No puede haber más de 3 sets")
            return False, errores
        
        # Validar cada set
        sets_ganados_eq1 = 0
        sets_ganados_eq2 = 0
        
        for i, set_data in enumerate(sets, 1):
            juegos_eq1 = set_data.get('juegos_eq1', 0)
            juegos_eq2 = set_data.get('juegos_eq2', 0)
            es_supertiebreak = set_data.get('esSuperTiebreak', False)
            
            # Si es supertiebreak, validar como supertiebreak
            if es_supertiebreak:
                es_valido, mensaje = PadelValidator.validar_supertiebreak(juegos_eq1, juegos_eq2)
                if not es_valido:
                    errores.append(f"Super Tiebreak: {mensaje}")
                else:
                    if juegos_eq1 > juegos_eq2:
                        sets_ganados_eq1 += 1
                    else:
                        sets_ganados_eq2 += 1
            else:
                # Validar como set normal
                es_valido, mensaje = PadelValidator.validar_set(juegos_eq1, juegos_eq2)
                if not es_valido:
                    errores.append(f"Set {i}: {mensaje}")
                else:
                    if juegos_eq1 > juegos_eq2:
                        sets_ganados_eq1 += 1
                    else:
                        sets_ganados_eq2 += 1
        
        # Validar que el partido esté completo (alguien ganó 2 sets)
        if sets_ganados_eq1 < 2 and sets_ganados_eq2 < 2:
            errores.append("Partido incompleto: debe haber un ganador con 2 sets")
        
        return len(errores) == 0, errores
    
    @staticmethod
    def validar_resultado_razonable(sets: List[Dict]) -> Tuple[bool, List[str]]:
        """
        Valida que el resultado sea razonable (detecta posibles trampas)
        
        Returns:
            Tuple[bool, List[str]]: (es_razonable, lista_de_advertencias)
        """
        advertencias = []
        
        for i, set_data in enumerate(sets, 1):
            juegos_eq1 = set_data.get('juegos_eq1', 0)
            juegos_eq2 = set_data.get('juegos_eq2', 0)
            es_supertiebreak = set_data.get('esSuperTiebreak', False)
            
            # Detectar resultados muy desbalanceados (posible trampa)
            if not es_supertiebreak:
                if juegos_eq1 == 6 and juegos_eq2 == 0:
                    advertencias.append(f"Set {i}: Resultado 6-0 (muy desbalanceado)")
                elif juegos_eq2 == 6 and juegos_eq1 == 0:
                    advertencias.append(f"Set {i}: Resultado 0-6 (muy desbalanceado)")
                
                # Detectar resultados imposibles (solo para sets normales)
                if juegos_eq1 > 7 or juegos_eq2 > 7:
                    advertencias.append(f"Set {i}: Resultado imposible (más de 7 juegos)")
            # Para supertiebreak, no hay límite de 7
        
        return len(advertencias) == 0, advertencias
