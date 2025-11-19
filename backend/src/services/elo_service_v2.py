"""
Servicio Elo V3 - Algoritmo Completamente Rediseñado
=====================================================

MEJORAS PRINCIPALES vs V2:
1. Factor de margen más robusto y predecible
2. Multiplicador de sorpresa para amplificar upsets
3. Score ajustado más significativo
4. K factors más conservadores
5. Caps mejor calibrados
6. Distribución equitativa entre jugadores

FÓRMULA COMPLETA (PASO A PASO):
1. E = 1 / (1 + 10^(-(Ra - Rb) / 400))
2. S_ajustado = S_base + bonus_margen (±0.25 máx)
3. K_efectivo = K_base × volatilidad
4. delta_base = K_efectivo × (S_ajustado - E)
5. factor_margen = 0.70 a 1.30 según sets/games/dominancia/TB
6. multiplicador_sorpresa = 1.0 a 2.5 si hay upset
7. delta_amplificado = delta_base × factor_margen × mult_sorpresa
8. caps_dinámicos = caps_base × factor_margen
9. delta_final = clamp(delta_amplificado, caps_dinámicos)
10. Distribuir equitativamente entre jugadores

DIFERENCIAS CLAVE:
- El multiplicador de sorpresa se aplica ANTES de los caps
- Los caps también se ajustan por margen
- El score ajustado es más significativo
- La distribución es 50/50 en vez de por peso inverso
"""

import math
from typing import Dict, Any, List, Tuple
from datetime import datetime
from .elo_config_v2 import EloConfigV2, Desenlace, clamp


class EloServiceV2:
    """Servicio mejorado para cálculo de Elo en pádel 2vs2 - Versión 3"""
    
    def __init__(self):
        self.config = EloConfigV2
    
    # ========================================================================
    # MÉTODOS PRINCIPALES
    # ========================================================================
    
    def calculate_team_rating(self, player1_rating: float, player2_rating: float) -> float:
        """Calcula el rating promedio del equipo"""
        return (player1_rating + player2_rating) / 2
    
    def calculate_expected_score(
        self,
        team_a_rating: float,
        team_b_rating: float
    ) -> Tuple[float, float]:
        """
        Calcula la expectativa de victoria usando el modelo logístico Elo
        
        E_a = 1 / (1 + 10^(-(Ra - Rb) / 400))
        """
        rating_diff = team_a_rating - team_b_rating
        expected_a = 1.0 / (1.0 + math.pow(10, -rating_diff / self.config.ELO_SCALE))
        expected_b = 1.0 - expected_a
        
        return expected_a, expected_b
    
    def calculate_adjusted_score(
        self,
        sets_won: int,
        sets_lost: int,
        games_won: int,
        games_lost: int,
        won_match: bool
    ) -> float:
        """
        Calcula el score ajustado (S_ajustado) - VERSIÓN MEJORADA
        
        S_base = 1.0 si ganó, 0.0 si perdió
        Luego se ajusta según el margen (±0.25 máximo)
        
        CAMBIO CLAVE: El ajuste ahora es más significativo para que
        el margen tenga impacto real en el delta base
        """
        # Score base
        s_base = 1.0 if won_match else 0.0
        
        # Ajuste por margen (±0.25 máximo)
        total_sets = sets_won + sets_lost
        total_games = games_won + games_lost
        
        if total_sets > 0 and total_games > 0:
            sets_ratio = sets_won / total_sets
            games_ratio = games_won / total_games
            
            # Ajuste combinado (más significativo que antes)
            # Promedio ponderado: 40% sets, 60% games
            margin_adjustment = (0.4 * sets_ratio + 0.6 * games_ratio) - 0.5
            margin_adjustment = clamp(margin_adjustment, -0.25, 0.25)
            
            s_adjusted = s_base + margin_adjustment
        else:
            s_adjusted = s_base
        
        return clamp(s_adjusted, 0.0, 1.0)
    
    def calculate_match_ratings(
        self,
        team_a_players: List[Dict[str, Any]],
        team_b_players: List[Dict[str, Any]],
        sets_a: int,
        sets_b: int,
        games_a: int = 0,
        games_b: int = 0,
        sets_detail: List[Dict] = None,
        desenlace: str = Desenlace.NORMAL.value,
        match_type: str = "torneo",
        match_date: datetime = None,
        recent_matches: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Calcula los nuevos ratings para un partido 2vs2
        
        ALGORITMO MEJORADO:
        1. Calcular ratings de equipo
        2. Calcular expectativas (E)
        3. Calcular score ajustado (S)
        4. Calcular factor de margen dinámico
        5. Calcular delta puro = K × (S - E)
        6. Aplicar caps dinámicos = caps_base × factor_margen
        7. Distribuir entre jugadores
        """
        
        # Validar equipos
        if len(team_a_players) != 2 or len(team_b_players) != 2:
            raise ValueError("Cada equipo debe tener exactamente 2 jugadores")
        
        # 1. CALCULAR RATINGS DE EQUIPO
        team_a_rating = self.calculate_team_rating(
            team_a_players[0]["rating"],
            team_a_players[1]["rating"]
        )
        team_b_rating = self.calculate_team_rating(
            team_b_players[0]["rating"],
            team_b_players[1]["rating"]
        )
        
        # 2. CALCULAR EXPECTATIVAS
        expected_a, expected_b = self.calculate_expected_score(team_a_rating, team_b_rating)
        
        # 3. DETERMINAR GANADOR Y CALCULAR SCORES AJUSTADOS
        team_a_won = sets_a > sets_b
        team_b_won = sets_b > sets_a
        
        # Manejar desenlaces especiales (WO)
        is_wo = desenlace in [Desenlace.WO_EQ1.value, Desenlace.WO_EQ2.value]
        
        if desenlace == Desenlace.WO_EQ1.value:
            # WO del equipo 1 (A no se presentó, B gana)
            # En WO, cambio fijo: +5 para ganador, -5 para perdedor
            team_a_won = False
            team_b_won = True
        elif desenlace == Desenlace.WO_EQ2.value:
            # WO del equipo 2 (B no se presentó, A gana)
            # En WO, cambio fijo: +5 para ganador, -5 para perdedor
            team_a_won = True
            team_b_won = False

        
        # CASO ESPECIAL: WO tiene cambio fijo
        if is_wo:
            # WO: +5 por jugador ganador, -10 por jugador perdedor (penalización por irresponsabilidad)
            # Equipo ganador: +10 total (+5 cada jugador)
            # Equipo perdedor: -20 total (-10 cada jugador)
            if team_a_won:
                delta_a1 = 5.0
                delta_a2 = 5.0
                delta_b1 = -10.0
                delta_b2 = -10.0
                delta_final_a = 10.0
                delta_final_b = -20.0
            else:
                delta_a1 = -10.0
                delta_a2 = -10.0
                delta_b1 = 5.0
                delta_b2 = 5.0
                delta_final_a = -20.0
                delta_final_b = 10.0
            
            # Calcular nuevos ratings
            new_rating_a1 = int(round(team_a_players[0]["rating"] + delta_a1))
            new_rating_a2 = int(round(team_a_players[1]["rating"] + delta_a2))
            new_rating_b1 = int(round(team_b_players[0]["rating"] + delta_b1))
            new_rating_b2 = int(round(team_b_players[1]["rating"] + delta_b2))
            
            # Volatilidad no cambia en WO
            new_vol_a1 = team_a_players[0].get("volatilidad", 1.0)
            new_vol_a2 = team_a_players[1].get("volatilidad", 1.0)
            new_vol_b1 = team_b_players[0].get("volatilidad", 1.0)
            new_vol_b2 = team_b_players[1].get("volatilidad", 1.0)
            
            # Construir respuesta simplificada para WO
            return {
                "team_a": {
                    "old_rating": team_a_rating,
                    "new_rating": (new_rating_a1 + new_rating_a2) / 2,
                    "rating_change": delta_final_a,
                    "players": [
                        {
                            "player_index": 0,
                            "old_rating": team_a_players[0]["rating"],
                            "new_rating": new_rating_a1,
                            "rating_change": delta_a1,
                            "old_volatility": team_a_players[0].get("volatilidad", 1.0),
                            "new_volatility": new_vol_a1
                        },
                        {
                            "player_index": 1,
                            "old_rating": team_a_players[1]["rating"],
                            "new_rating": new_rating_a2,
                            "rating_change": delta_a2,
                            "old_volatility": team_a_players[1].get("volatilidad", 1.0),
                            "new_volatility": new_vol_a2
                        }
                    ]
                },
                "team_b": {
                    "old_rating": team_b_rating,
                    "new_rating": (new_rating_b1 + new_rating_b2) / 2,
                    "rating_change": delta_final_b,
                    "players": [
                        {
                            "player_index": 0,
                            "old_rating": team_b_players[0]["rating"],
                            "new_rating": new_rating_b1,
                            "rating_change": delta_b1,
                            "old_volatility": team_b_players[0].get("volatilidad", 1.0),
                            "new_volatility": new_vol_b1
                        },
                        {
                            "player_index": 1,
                            "old_rating": team_b_players[1]["rating"],
                            "new_rating": new_rating_b2,
                            "rating_change": delta_b2,
                            "old_volatility": team_b_players[1].get("volatilidad", 1.0),
                            "new_volatility": new_vol_b2
                        }
                    ]
                },
                "match_details": {
                    "expected_a": 0.5,
                    "expected_b": 0.5,
                    "actual_score_a": 1.0 if team_a_won else 0.0,
                    "actual_score_b": 1.0 if team_b_won else 0.0,
                    "team_a_k": 0,
                    "team_b_k": 0,
                    "team_a_k_base": 0,
                    "team_b_k_base": 0,
                    "factor_margen": 1.0,
                    "surprise_mult_a": 1.0,
                    "surprise_mult_b": 1.0,
                    "caps_base_a": (5, -5),
                    "caps_base_b": (5, -5),
                    "caps_dynamic_a": (5, -5),
                    "caps_dynamic_b": (5, -5),
                    "delta_base_a": delta_final_a,
                    "delta_base_b": delta_final_b,
                    "delta_amplified_a": delta_final_a,
                    "delta_amplified_b": delta_final_b,
                    "match_type": match_type,
                    "desenlace": desenlace,
                    "is_underdog_a": False,
                    "is_favorite_a": False,
                    "is_wo": True
                }
            }
        
        # FLUJO NORMAL (no WO)
        # Calcular scores ajustados
        actual_score_a = self.calculate_adjusted_score(
            sets_a, sets_b, games_a, games_b, team_a_won
        )
        actual_score_b = self.calculate_adjusted_score(
            sets_b, sets_a, games_b, games_a, team_b_won
        )
        
        # 4. CALCULAR FACTOR DE MARGEN DINÁMICO
        factor_margen = self.config.calculate_margin_factor(
            sets_a, sets_b, games_a, games_b, sets_detail
        )
        
        # 5. CALCULAR FACTORES K CON VOLATILIDAD
        k_a1 = self.config.get_k_factor(team_a_players[0]["partidos"])
        k_a2 = self.config.get_k_factor(team_a_players[1]["partidos"])
        k_b1 = self.config.get_k_factor(team_b_players[0]["partidos"])
        k_b2 = self.config.get_k_factor(team_b_players[1]["partidos"])
        
        team_a_k_base = (k_a1 + k_a2) / 2
        team_b_k_base = (k_b1 + k_b2) / 2
        
        # Aplicar volatilidad
        vol_a = (team_a_players[0].get("volatilidad", 1.0) + team_a_players[1].get("volatilidad", 1.0)) / 2
        vol_b = (team_b_players[0].get("volatilidad", 1.0) + team_b_players[1].get("volatilidad", 1.0)) / 2
        
        team_a_k = self.config.k_with_volatility(team_a_k_base, vol_a)
        team_b_k = self.config.k_with_volatility(team_b_k_base, vol_b)
        
        # 6. CALCULAR DELTA BASE (sin multiplicadores todavía)
        delta_base_a = team_a_k * (actual_score_a - expected_a)
        delta_base_b = team_b_k * (actual_score_b - expected_b)
        
        # 7. CALCULAR MULTIPLICADOR DE SORPRESA (NUEVO)
        surprise_mult_a = self.config.calculate_surprise_multiplier(
            team_a_rating, team_b_rating, team_a_won, match_type
        )
        surprise_mult_b = self.config.calculate_surprise_multiplier(
            team_b_rating, team_a_rating, team_b_won, match_type
        )
        
        # 8. APLICAR MULTIPLICADORES (margen × sorpresa)
        # ESTE ES EL CORAZÓN DEL NUEVO SISTEMA
        delta_amplified_a = delta_base_a * factor_margen * surprise_mult_a
        delta_amplified_b = delta_base_b * factor_margen * surprise_mult_b
        
        # AJUSTE ESPECIAL: Asegurar mínimos razonables
        # Esto evita cambios ridículamente pequeños (+2, -1, etc.)
        # Solo se aplica cuando el delta es REALMENTE bajo (< 20)
        
        # Si el favorito gana, mínimo +25 (ajustado por margen)
        if self.config.is_favorite(team_a_rating, team_b_rating) and team_a_won:
            min_gain = 25 * factor_margen
            if 0 < delta_amplified_a < 20:  # Solo si es MUY bajo
                delta_amplified_a = min_gain
        
        if self.config.is_favorite(team_b_rating, team_a_rating) and team_b_won:
            min_gain = 25 * factor_margen
            if 0 < delta_amplified_b < 20:
                delta_amplified_b = min_gain
        
        # Si el underdog pierde, mínimo -15 (ajustado por margen)
        if self.config.is_underdog(team_a_rating, team_b_rating) and not team_a_won:
            min_loss = -15 * factor_margen
            if -20 < delta_amplified_a < 0:  # Solo si es MUY bajo
                delta_amplified_a = min_loss
        
        if self.config.is_underdog(team_b_rating, team_a_rating) and not team_b_won:
            min_loss = -15 * factor_margen
            if -20 < delta_amplified_b < 0:
                delta_amplified_b = min_loss
        
        # 9. OBTENER CAPS BASE Y APLICAR FACTOR DE MARGEN
        cap_win_a, cap_loss_a = self.config.get_role_caps(
            team_a_rating, team_b_rating, match_type, team_a_won
        )
        cap_win_b, cap_loss_b = self.config.get_role_caps(
            team_b_rating, team_a_rating, match_type, team_b_won
        )
        
        # APLICAR FACTOR DE MARGEN A LOS CAPS (caps también escalan)
        cap_win_a_dynamic = cap_win_a * factor_margen
        cap_loss_a_dynamic = cap_loss_a * factor_margen
        cap_win_b_dynamic = cap_win_b * factor_margen
        cap_loss_b_dynamic = cap_loss_b * factor_margen
        
        # 10. APLICAR CAPS DINÁMICOS
        delta_final_a = clamp(delta_amplified_a, cap_loss_a_dynamic, cap_win_a_dynamic)
        delta_final_b = clamp(delta_amplified_b, cap_loss_b_dynamic, cap_win_b_dynamic)
        
        # 11. DISTRIBUIR ENTRE JUGADORES (50/50 - más justo)
        # CAMBIO: Distribución equitativa en vez de por peso inverso
        delta_a1 = delta_final_a / 2
        delta_a2 = delta_final_a / 2
        delta_b1 = delta_final_b / 2
        delta_b2 = delta_final_b / 2
        
        # 12. CALCULAR NUEVOS RATINGS
        new_rating_a1 = int(round(team_a_players[0]["rating"] + delta_a1))
        new_rating_a2 = int(round(team_a_players[1]["rating"] + delta_a2))
        new_rating_b1 = int(round(team_b_players[0]["rating"] + delta_b1))
        new_rating_b2 = int(round(team_b_players[1]["rating"] + delta_b2))
        
        # 13. ACTUALIZAR VOLATILIDAD
        new_vol_a1 = self._update_volatility(
            team_a_players[0].get("volatilidad", 1.0),
            actual_score_a,
            expected_a
        )
        new_vol_a2 = self._update_volatility(
            team_a_players[1].get("volatilidad", 1.0),
            actual_score_a,
            expected_a
        )
        new_vol_b1 = self._update_volatility(
            team_b_players[0].get("volatilidad", 1.0),
            actual_score_b,
            expected_b
        )
        new_vol_b2 = self._update_volatility(
            team_b_players[1].get("volatilidad", 1.0),
            actual_score_b,
            expected_b
        )
        
        # 14. CONSTRUIR RESPUESTA
        return {
            "team_a": {
                "old_rating": team_a_rating,
                "new_rating": (new_rating_a1 + new_rating_a2) / 2,
                "rating_change": delta_final_a,
                "players": [
                    {
                        "player_index": 0,
                        "old_rating": team_a_players[0]["rating"],
                        "new_rating": new_rating_a1,
                        "rating_change": delta_a1,
                        "old_volatility": team_a_players[0].get("volatilidad", 1.0),
                        "new_volatility": new_vol_a1
                    },
                    {
                        "player_index": 1,
                        "old_rating": team_a_players[1]["rating"],
                        "new_rating": new_rating_a2,
                        "rating_change": delta_a2,
                        "old_volatility": team_a_players[1].get("volatilidad", 1.0),
                        "new_volatility": new_vol_a2
                    }
                ]
            },
            "team_b": {
                "old_rating": team_b_rating,
                "new_rating": (new_rating_b1 + new_rating_b2) / 2,
                "rating_change": delta_final_b,
                "players": [
                    {
                        "player_index": 0,
                        "old_rating": team_b_players[0]["rating"],
                        "new_rating": new_rating_b1,
                        "rating_change": delta_b1,
                        "old_volatility": team_b_players[0].get("volatilidad", 1.0),
                        "new_volatility": new_vol_b1
                    },
                    {
                        "player_index": 1,
                        "old_rating": team_b_players[1]["rating"],
                        "new_rating": new_rating_b2,
                        "rating_change": delta_b2,
                        "old_volatility": team_b_players[1].get("volatilidad", 1.0),
                        "new_volatility": new_vol_b2
                    }
                ]
            },
            "match_details": {
                "expected_a": expected_a,
                "expected_b": expected_b,
                "actual_score_a": actual_score_a,
                "actual_score_b": actual_score_b,
                "team_a_k": team_a_k,
                "team_b_k": team_b_k,
                "team_a_k_base": team_a_k_base,
                "team_b_k_base": team_b_k_base,
                "factor_margen": factor_margen,
                "surprise_mult_a": surprise_mult_a,
                "surprise_mult_b": surprise_mult_b,
                "caps_base_a": (cap_win_a, cap_loss_a),
                "caps_base_b": (cap_win_b, cap_loss_b),
                "caps_dynamic_a": (cap_win_a_dynamic, cap_loss_a_dynamic),
                "caps_dynamic_b": (cap_win_b_dynamic, cap_loss_b_dynamic),
                "delta_base_a": delta_base_a,
                "delta_base_b": delta_base_b,
                "delta_amplified_a": delta_amplified_a,
                "delta_amplified_b": delta_amplified_b,
                "match_type": match_type,
                "desenlace": desenlace,
                "is_underdog_a": self.config.is_underdog(team_a_rating, team_b_rating),
                "is_favorite_a": self.config.is_favorite(team_a_rating, team_b_rating)
            }
        }
    
    def _update_volatility(self, current_vol: float, actual: float, expected: float) -> float:
        """Actualiza la volatilidad del jugador"""
        gap = abs(actual - expected)
        
        if gap < self.config.VOLATILIDAD_STABLE_THRESHOLD:
            new_vol = current_vol * self.config.VOLATILIDAD_DOWN_FACTOR
        elif gap > self.config.VOLATILIDAD_VOLATILE_THRESHOLD:
            new_vol = current_vol * self.config.VOLATILIDAD_UP_FACTOR
        else:
            new_vol = current_vol
        
        return clamp(new_vol, self.config.VOLATILIDAD_MIN, self.config.VOLATILIDAD_MAX)
