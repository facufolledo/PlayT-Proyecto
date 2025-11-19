"""
Configuración Elo V3 - Sistema Completamente Rediseñado
========================================================

FILOSOFÍA DEL SISTEMA:
- Caps dinámicos que escalan con el margen de victoria
- Multiplicadores progresivos y coherentes
- Diferenciación clara entre upset/esperado y ajustado/paliza
- Resultados predecibles y justos

FÓRMULA COMPLETA:
1. E = 1 / (1 + 10^(-(Ra - Rb) / 400))
2. S_ajustado = S_base + bonus_margen (más significativo que antes)
3. delta_base = K × (S_ajustado - E)
4. factor_margen = 0.70 a 1.30 según sets/games/tie-breaks
5. multiplicador_sorpresa = 1.0 a 2.5 según si es upset o no
6. delta_final = clamp(delta_base × factor_margen × mult_sorpresa, caps)
7. Los caps también se ajustan por margen

CAMBIOS CLAVE vs V2:
- K factors más conservadores (máx 80 para nuevos)
- Score ajustado más significativo (±0.25 en vez de ±0.1)
- Factor de margen más amplio (0.70-1.30)
- Multiplicador de sorpresa nuevo (amplifica upsets)
- Caps mejor calibrados
"""

from typing import Tuple
from enum import Enum
import math

class Desenlace(str, Enum):
    """Tipos de desenlace de partido"""
    NORMAL = "normal"
    WO_EQ1 = "wo_eq1"
    WO_EQ2 = "wo_eq2"
    RET_EQ1 = "ret_eq1"
    RET_EQ2 = "ret_eq2"


class EloConfigV2:
    """
    Configuración mejorada del algoritmo Elo V3
    
    CÓMO AJUSTAR EL SISTEMA:
    - Más agresivo: Aumentar K_FACTORS y BASE_CAPS (×1.2)
    - Más conservador: Reducir K_FACTORS y BASE_CAPS (×0.8)
    - Más impacto por margen: Aumentar MARGIN_FACTOR_RANGE
    - Más impacto por upset: Aumentar SURPRISE_MULTIPLIER_MAX
    """
    
    # ============================================================================
    # ESCALA ELO ESTÁNDAR
    # ============================================================================
    ELO_SCALE = 400  # Escala estándar de Elo (no tocar)
    
    # ============================================================================
    # FACTORES K POR EXPERIENCIA (RECALIBRADOS)
    # ============================================================================
    # Controlan la velocidad de cambio del rating
    # IMPORTANTE: Valores más bajos = sistema más estable
    K_FACTORS = {
        "nuevo": {
            "max_partidos": 5,
            "k_value": 100  # Nuevos: cambios grandes pero controlados
        },
        "intermedio": {
            "max_partidos": 15,
            "k_value": 80  # Intermedios: cambios moderados-altos
        },
        "estable": {
            "max_partidos": 40,
            "k_value": 50   # Estables: cambios moderados
        },
        "experto": {
            "max_partidos": float('inf'),
            "k_value": 40   # Expertos: cambios pequeños
        }
    }
    
    # ============================================================================
    # CAPS BASE POR TIPO DE PARTIDO Y ROL (RECALIBRADOS)
    # ============================================================================
    # Estos son los caps BASE que luego se ajustan por factor_margen
    # Los valores están calibrados para dar los rangos deseados
    
    # Caps para AMISTOSOS (siempre cambios pequeños)
    AMISTOSO_CAPS = {
        "underdog_win": 22,    # Underdog gana amistoso → ~15-30 con margen
        "underdog_loss": -18,  # Underdog pierde amistoso
        "favorite_win": 12,    # Favorito gana amistoso
        "favorite_loss": -22   # Favorito pierde amistoso
    }
    
    # Caps para TORNEOS (cambios moderados-altos)
    TORNEO_CAPS = {
        "underdog_win": 90,    # Underdog gana torneo → ~60-110 con margen
        "underdog_loss": -35,  # Underdog pierde torneo
        "favorite_win": 55,    # Favorito gana torneo → ~40-70 con margen
        "favorite_loss": -55   # Favorito pierde torneo
    }
    
    # Caps para FINALES (cambios muy altos)
    FINAL_CAPS = {
        "underdog_win": 170,   # Underdog gana final → ~120-220 con margen
        "underdog_loss": -70,  # Underdog pierde final
        "favorite_win": 65,    # Favorito gana final
        "favorite_loss": -85   # Favorito pierde final
    }
    
    # Caps para otros tipos
    CUARTOS_CAPS = {
        "underdog_win": 80,
        "underdog_loss": -32,
        "favorite_win": 40,
        "favorite_loss": -50
    }
    
    SEMI_CAPS = {
        "underdog_win": 100,
        "underdog_loss": -42,
        "favorite_win": 50,
        "favorite_loss": -65
    }
    
    # ============================================================================
    # FACTOR DE MARGEN (DINÁMICO) - RECALIBRADO
    # ============================================================================
    # Controla cuánto varían los resultados según el margen de victoria
    # Este es el CORAZÓN del sistema de caps dinámicos
    
    # Rango del multiplicador de margen (más amplio que antes)
    MARGIN_FACTOR_MIN = 0.70  # Victoria MUY ajustada (7-6/7-6 con tie-breaks)
    MARGIN_FACTOR_MAX = 1.30  # Victoria por paliza total (6-0/6-0)
    
    # Umbrales para calcular el margen
    DOMINANT_SET_THRESHOLD = 2     # 6-0, 6-1, 6-2 = set dominante
    TIEBREAK_THRESHOLD = 6         # 7-6 = tie-break
    CLOSE_SET_THRESHOLD = 4        # 6-4 o más ajustado = set reñido
    
    # Pesos para el cálculo del factor de margen
    MARGIN_WEIGHT_SETS = 0.30      # 30% por diferencia de sets
    MARGIN_WEIGHT_GAMES = 0.35     # 35% por diferencia de games
    MARGIN_WEIGHT_DOMINANT = 0.20  # 20% por sets dominantes
    MARGIN_WEIGHT_TIEBREAK = 0.15  # 15% por tie-breaks (negativo)
    
    # ============================================================================
    # MULTIPLICADOR DE SORPRESA (NUEVO)
    # ============================================================================
    # Amplifica los cambios cuando hay upset
    SURPRISE_MULTIPLIER_MIN = 1.0   # Sin sorpresa (equipos parejos)
    SURPRISE_MULTIPLIER_MAX = 2.5   # Máxima sorpresa (gran diferencia de rating)
    
    # Umbrales de diferencia de rating para sorpresa
    SURPRISE_THRESHOLD_MIN = 65     # A partir de aquí empieza a contar como upset
    SURPRISE_THRESHOLD_MAX = 400    # Máxima diferencia considerada
    
    # ============================================================================
    # UMBRAL PARA UNDERDOG/FAVORITO
    # ============================================================================
    UNDERDOG_THRESHOLD = 65        # Diferencia de rating para considerar underdog/favorito
                                   # Ej: 1400 vs 1360 (40 pts) = parejos
                                   # Ej: 1400 vs 1330 (70 pts) = favorito/underdog
    
    # ============================================================================
    # AJUSTE DE SCORE (S_ajustado)
    # ============================================================================
    # Controla cuánto se ajusta el score base (0 o 1) según el margen
    SCORE_ADJUSTMENT_MAX = 0.25    # Ajuste máximo al score (±0.25)
    
    # ============================================================================
    # VOLATILIDAD (Sistema de confiabilidad)
    # ============================================================================
    VOLATILIDAD_MIN = 0.7
    VOLATILIDAD_MAX = 1.3
    VOLATILIDAD_DOWN_FACTOR = 0.98
    VOLATILIDAD_UP_FACTOR = 1.02
    VOLATILIDAD_STABLE_THRESHOLD = 0.15
    VOLATILIDAD_VOLATILE_THRESHOLD = 0.35
    
    # ============================================================================
    # MÉTODOS AUXILIARES
    # ============================================================================
    
    @classmethod
    def get_k_factor(cls, partidos_jugados: int) -> int:
        """Obtiene el factor K según la experiencia del jugador"""
        for level, config in cls.K_FACTORS.items():
            if partidos_jugados <= config["max_partidos"]:
                return config["k_value"]
        return cls.K_FACTORS["experto"]["k_value"]
    
    @classmethod
    def get_caps_for_match_type(cls, match_type: str) -> dict:
        """Obtiene los caps base según el tipo de partido"""
        caps_map = {
            "amistoso": cls.AMISTOSO_CAPS,
            "torneo": cls.TORNEO_CAPS,
            "final": cls.FINAL_CAPS,
            "cuartos": cls.CUARTOS_CAPS,
            "semi": cls.SEMI_CAPS,
            "zona": cls.TORNEO_CAPS  # Zona usa caps de torneo
        }
        return caps_map.get(match_type, cls.TORNEO_CAPS)
    
    @classmethod
    def calculate_margin_factor(
        cls,
        sets_a: int,
        sets_b: int,
        games_a: int,
        games_b: int,
        sets_detail: list = None
    ) -> float:
        """
        Calcula el factor de margen basado en cómo fue la victoria
        
        ALGORITMO MEJORADO:
        - Combina múltiples factores con pesos específicos
        - Diferencia de sets (30%)
        - Diferencia de games (35%)
        - Sets dominantes (20%)
        - Tie-breaks (15%, negativo)
        
        Retorna un valor entre MARGIN_FACTOR_MIN (0.70) y MARGIN_FACTOR_MAX (1.30)
        
        EJEMPLOS:
        - 7-6 / 7-6 (doble tie-break) → ~0.70-0.75
        - 6-4 / 6-4 (normal) → ~0.95-1.05
        - 6-2 / 6-3 (clara) → ~1.10-1.15
        - 6-0 / 6-1 (paliza) → ~1.25-1.30
        """
        score = 0.0  # Score que luego convertiremos a factor
        
        # 1. COMPONENTE: Diferencia de sets (30%)
        sets_diff = abs(sets_a - sets_b)
        if sets_diff == 2:  # 2-0
            score += 0.30
        elif sets_diff == 1:  # 2-1
            score += 0.10
        else:  # Empate (no debería pasar)
            score += 0.0
        
        # 2. COMPONENTE: Diferencia de games (35%)
        total_games = games_a + games_b
        if total_games > 0:
            games_diff = abs(games_a - games_b)
            games_ratio = games_diff / total_games
            
            if games_ratio >= 0.50:  # 50%+ de diferencia (ej: 12-0)
                score += 0.35
            elif games_ratio >= 0.35:  # 35-50% (ej: 12-4)
                score += 0.28
            elif games_ratio >= 0.20:  # 20-35% (ej: 12-8)
                score += 0.18
            elif games_ratio >= 0.10:  # 10-20% (ej: 13-11)
                score += 0.08
            else:  # <10% muy ajustado
                score += 0.0
        
        # 3. COMPONENTE: Sets dominantes (20%)
        # 4. COMPONENTE: Tie-breaks (15%, negativo)
        if sets_detail:
            dominant_count = 0
            tiebreak_count = 0
            close_count = 0
            
            for set_info in sets_detail:
                ga = set_info.get("games_a", 0)
                gb = set_info.get("games_b", 0)
                winner_games = max(ga, gb)
                loser_games = min(ga, gb)
                
                # Set dominante (6-0, 6-1, 6-2)
                if winner_games == 6 and loser_games <= cls.DOMINANT_SET_THRESHOLD:
                    dominant_count += 1
                
                # Tie-break (7-6)
                elif (ga == 7 and gb == 6) or (gb == 7 and ga == 6):
                    tiebreak_count += 1
                
                # Set muy reñido (6-4, 6-5)
                elif winner_games == 6 and loser_games >= cls.CLOSE_SET_THRESHOLD:
                    close_count += 1
            
            # Aplicar bonus por sets dominantes
            if dominant_count == 2:  # Doble rosco
                score += 0.20
            elif dominant_count == 1:
                score += 0.12
            
            # Aplicar penalización por tie-breaks
            if tiebreak_count == 2:  # Doble tie-break
                score -= 0.15
            elif tiebreak_count == 1:
                score -= 0.08
        
        # 5. CONVERTIR SCORE A FACTOR
        # Score va de ~-0.15 (doble TB) a ~0.85 (paliza total)
        # Lo mapeamos a [MARGIN_FACTOR_MIN, MARGIN_FACTOR_MAX]
        
        # Normalizar: score esperado entre -0.15 y 0.85 (rango de 1.0)
        normalized = (score + 0.15) / 1.0  # Ahora entre 0 y 1
        
        # Mapear al rango deseado
        factor = cls.MARGIN_FACTOR_MIN + normalized * (cls.MARGIN_FACTOR_MAX - cls.MARGIN_FACTOR_MIN)
        
        # Clampear por seguridad
        factor = max(cls.MARGIN_FACTOR_MIN, min(cls.MARGIN_FACTOR_MAX, factor))
        
        return factor
    
    @classmethod
    def calculate_surprise_multiplier(
        cls,
        team_rating: float,
        opponent_rating: float,
        team_won: bool,
        match_type: str = "torneo"
    ) -> float:
        """
        Calcula el multiplicador de sorpresa para amplificar upsets
        
        LÓGICA MEJORADA:
        - Si el underdog gana → multiplicador alto
        - Si el favorito gana → multiplicador bajo (1.0)
        - Si son parejos → multiplicador neutro (1.0)
        - El multiplicador escala con el tipo de partido
        
        RANGOS POR TIPO:
        - Amistoso: 1.0 a 1.3 (poco impacto)
        - Torneo: 1.0 a 2.0 (impacto moderado)
        - Final: 1.0 a 3.0 (impacto alto)
        """
        rating_diff = abs(team_rating - opponent_rating)
        
        # Si la diferencia es pequeña, no hay sorpresa
        if rating_diff < cls.SURPRISE_THRESHOLD_MIN:
            return 1.0
        
        # Determinar si hubo upset
        is_underdog = team_rating < opponent_rating
        is_upset = is_underdog and team_won
        
        if not is_upset:
            # No hubo upset, multiplicador neutro
            return 1.0
        
        # Definir rango según tipo de partido
        if match_type == "amistoso":
            mult_max = 1.3
        elif match_type in ["final", "semi"]:
            mult_max = 3.0
        elif match_type == "cuartos":
            mult_max = 2.5
        else:  # torneo, zona
            mult_max = 2.0
        
        # Hubo upset: calcular multiplicador según magnitud
        # Normalizar la diferencia de rating
        normalized_diff = min(rating_diff, cls.SURPRISE_THRESHOLD_MAX) / cls.SURPRISE_THRESHOLD_MAX
        
        # Mapear a rango de multiplicador
        multiplier = 1.0 + normalized_diff * (mult_max - 1.0)
        
        return multiplier
    
    @classmethod
    def is_underdog(cls, team_rating: float, opponent_rating: float) -> bool:
        """Determina si un equipo es underdog"""
        return team_rating < (opponent_rating - cls.UNDERDOG_THRESHOLD)
    
    @classmethod
    def is_favorite(cls, team_rating: float, opponent_rating: float) -> bool:
        """Determina si un equipo es favorito"""
        return team_rating > (opponent_rating + cls.UNDERDOG_THRESHOLD)
    
    @classmethod
    def get_role_caps(
        cls,
        team_rating: float,
        opponent_rating: float,
        match_type: str,
        won: bool
    ) -> Tuple[float, float]:
        """
        Obtiene los caps según el rol del equipo y el resultado
        
        Returns:
            Tuple[cap_win, cap_loss]
        """
        caps = cls.get_caps_for_match_type(match_type)
        
        is_underdog = cls.is_underdog(team_rating, opponent_rating)
        is_favorite = cls.is_favorite(team_rating, opponent_rating)
        
        if is_underdog:
            if won:
                return caps["underdog_win"], caps["underdog_loss"]
            else:
                return caps["underdog_win"], caps["underdog_loss"]
        elif is_favorite:
            if won:
                return caps["favorite_win"], caps["favorite_loss"]
            else:
                return caps["favorite_win"], caps["favorite_loss"]
        else:
            # Equipos parejos: usar promedio
            avg_win = (caps["underdog_win"] + caps["favorite_win"]) / 2
            avg_loss = (caps["underdog_loss"] + caps["favorite_loss"]) / 2
            return avg_win, avg_loss
    
    @classmethod
    def k_with_volatility(cls, k_base: float, volatility: float) -> float:
        """Aplica volatilidad al factor K"""
        v = max(cls.VOLATILIDAD_MIN, min(cls.VOLATILIDAD_MAX, volatility))
        return k_base * v
    
    @classmethod
    def get_config_summary(cls) -> dict:
        """Obtiene un resumen de la configuración actual"""
        return {
            "elo_scale": cls.ELO_SCALE,
            "k_factors": cls.K_FACTORS,
            "amistoso_caps": cls.AMISTOSO_CAPS,
            "torneo_caps": cls.TORNEO_CAPS,
            "final_caps": cls.FINAL_CAPS,
            "margin_range": (cls.MARGIN_MULTIPLIER_MIN, cls.MARGIN_MULTIPLIER_MAX),
            "underdog_threshold": cls.UNDERDOG_THRESHOLD
        }


def clamp(x: float, lo: float, hi: float) -> float:
    """Limita un valor entre un mínimo y máximo"""
    return max(lo, min(hi, x))
