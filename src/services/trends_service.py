# -*- coding: utf-8 -*-
"""
Trends analysis service for transaction data
"""
import logging
from typing import Dict, Any, List
from decimal import Decimal
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)

class TrendsService:
    """Service for analyzing transaction trends"""
    
    def analyze_trends(self, transactions: List[Dict[str, Any]], query_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze trends in transaction data
        
        Returns comprehensive trend analysis including:
        - Weekly aggregations
        - Growth rates
        - Trend direction
        - Top performers
        - AI-generated insights
        """
        try:
            if not transactions:
                return {
                    'has_data': False,
                    'message': 'No hay suficientes datos para análisis de tendencias'
                }
            
            # Group transactions by product and week
            weekly_data = self._aggregate_by_week(transactions)
            
            # Calculate trends for each product
            product_trends = {}
            for product, weeks in weekly_data.items():
                product_trends[product] = self._calculate_product_trend(product, weeks)
            
            # Generate overall insights
            insights = self._generate_insights(product_trends, query_params)
            
            # Identify top performers
            top_growing = self._get_top_growing(product_trends, limit=5)
            top_declining = self._get_top_declining(product_trends, limit=5)
            
            return {
                'has_data': True,
                'period_days': self._calculate_period_days(transactions),
                'total_products': len(product_trends),
                'product_trends': product_trends,
                'top_growing': top_growing,
                'top_declining': top_declining,
                'insights': insights,
                'weekly_data': weekly_data
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trends: {str(e)}")
            return {
                'has_data': False,
                'error': str(e)
            }
    
    def _aggregate_by_week(self, transactions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Aggregate transactions by product and week"""
        weekly_data = defaultdict(lambda: defaultdict(lambda: {'quantity': Decimal('0'), 'cost': Decimal('0'), 'count': 0}))
        
        for transaction in transactions:
            try:
                # Parse date
                date_str = transaction.get('date_registry', '')
                if not date_str:
                    continue
                
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                
                # Get week start (Monday)
                week_start = date - timedelta(days=date.weekday())
                week_key = week_start.strftime('%Y-%m-%d')
                
                # Aggregate data
                product = transaction.get('product', 'Desconocido').lower()
                quantity = Decimal(str(transaction.get('quantity', 0)))
                cost = Decimal(str(transaction.get('cost', 0)))
                
                weekly_data[product][week_key]['quantity'] += quantity
                weekly_data[product][week_key]['cost'] += cost
                weekly_data[product][week_key]['count'] += 1
                weekly_data[product][week_key]['week_start'] = week_key
                
            except Exception as e:
                logger.warning(f"Error processing transaction for trends: {str(e)}")
                continue
        
        # Convert to sorted lists
        result = {}
        for product, weeks in weekly_data.items():
            sorted_weeks = sorted(weeks.items(), key=lambda x: x[0])
            result[product] = [
                {
                    'week_start': week_key,
                    'quantity': float(data['quantity']),
                    'cost': float(data['cost']),
                    'count': data['count']
                }
                for week_key, data in sorted_weeks
            ]
        
        return result
    
    def _calculate_product_trend(self, product: str, weeks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate trend metrics for a single product"""
        try:
            if len(weeks) < 2:
                return {
                    'product': product,
                    'trend': 'insufficient_data',
                    'weeks_count': len(weeks),
                    'message': 'Datos insuficientes para calcular tendencia'
                }
            
            # Extract time series
            costs = [week['cost'] for week in weeks]
            quantities = [week['quantity'] for week in weeks]
            
            # Calculate growth rates
            cost_growth = self._calculate_growth_rate(costs)
            quantity_growth = self._calculate_growth_rate(quantities)
            
            # Determine trend direction
            trend_direction = self._determine_trend_direction(costs)
            
            # Calculate volatility (standard deviation)
            cost_volatility = statistics.stdev(costs) if len(costs) > 1 else 0
            
            # Calculate averages
            avg_weekly_cost = statistics.mean(costs)
            avg_weekly_quantity = statistics.mean(quantities)
            
            # Recent vs historical comparison
            recent_avg = statistics.mean(costs[-4:]) if len(costs) >= 4 else costs[-1]
            historical_avg = statistics.mean(costs[:-4]) if len(costs) > 4 else costs[0]
            recent_change = ((recent_avg - historical_avg) / historical_avg * 100) if historical_avg > 0 else 0
            
            return {
                'product': product,
                'trend': trend_direction,
                'weeks_count': len(weeks),
                'cost_growth_rate': round(cost_growth, 2),
                'quantity_growth_rate': round(quantity_growth, 2),
                'cost_volatility': round(cost_volatility, 2),
                'avg_weekly_cost': round(avg_weekly_cost, 2),
                'avg_weekly_quantity': round(avg_weekly_quantity, 2),
                'recent_change_percent': round(recent_change, 2),
                'first_week_cost': round(costs[0], 2),
                'last_week_cost': round(costs[-1], 2),
                'total_cost': round(sum(costs), 2),
                'total_quantity': round(sum(quantities), 2),
                'weekly_data': weeks
            }
            
        except Exception as e:
            logger.error(f"Error calculating trend for {product}: {str(e)}")
            return {
                'product': product,
                'trend': 'error',
                'error': str(e)
            }
    
    def _calculate_growth_rate(self, values: List[float]) -> float:
        """Calculate average growth rate across periods"""
        if len(values) < 2:
            return 0.0
        
        growth_rates = []
        for i in range(1, len(values)):
            if values[i-1] > 0:
                growth = ((values[i] - values[i-1]) / values[i-1]) * 100
                growth_rates.append(growth)
        
        return statistics.mean(growth_rates) if growth_rates else 0.0
    
    def _determine_trend_direction(self, values: List[float]) -> str:
        """Determine overall trend direction"""
        if len(values) < 2:
            return 'stable'
        
        # Calculate linear regression slope
        n = len(values)
        x = list(range(n))
        
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 'stable'
        
        slope = numerator / denominator
        
        # Classify based on slope
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'
    
    def _get_top_growing(self, product_trends: Dict[str, Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
        """Get top growing products"""
        valid_trends = [
            trend for trend in product_trends.values()
            if trend.get('trend') != 'error' and trend.get('trend') != 'insufficient_data'
        ]
        
        sorted_trends = sorted(
            valid_trends,
            key=lambda x: x.get('cost_growth_rate', 0),
            reverse=True
        )
        
        return sorted_trends[:limit]
    
    def _get_top_declining(self, product_trends: Dict[str, Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
        """Get top declining products"""
        valid_trends = [
            trend for trend in product_trends.values()
            if trend.get('trend') != 'error' and trend.get('trend') != 'insufficient_data'
        ]
        
        sorted_trends = sorted(
            valid_trends,
            key=lambda x: x.get('cost_growth_rate', 0)
        )
        
        return sorted_trends[:limit]
    
    def _generate_insights(self, product_trends: Dict[str, Dict[str, Any]], query_params: Dict[str, Any]) -> List[str]:
        """Generate actionable insights from trend data"""
        insights = []
        
        try:
            valid_trends = [
                trend for trend in product_trends.values()
                if trend.get('trend') not in ['error', 'insufficient_data']
            ]
            
            if not valid_trends:
                return ["No hay suficientes datos para generar insights"]
            
            # Count trends
            increasing = sum(1 for t in valid_trends if t['trend'] == 'increasing')
            decreasing = sum(1 for t in valid_trends if t['trend'] == 'decreasing')
            stable = sum(1 for t in valid_trends if t['trend'] == 'stable')
            
            total = len(valid_trends)
            
            # Overall trend insight
            if increasing > total * 0.6:
                insights.append(f"📈 Tendencia general positiva: {increasing} de {total} productos en crecimiento")
            elif decreasing > total * 0.6:
                insights.append(f"📉 Tendencia general negativa: {decreasing} de {total} productos en declive")
            else:
                insights.append(f"📊 Tendencia mixta: {increasing} creciendo, {decreasing} declinando, {stable} estables")
            
            # Top performer insight
            top_product = max(valid_trends, key=lambda x: x.get('cost_growth_rate', 0))
            if top_product['cost_growth_rate'] > 5:
                insights.append(
                    f"🌟 Mejor desempeño: {top_product['product'].title()} "
                    f"con {top_product['cost_growth_rate']:.1f}% de crecimiento semanal"
                )
            
            # Volatility insight
            high_volatility = [t for t in valid_trends if t.get('cost_volatility', 0) > 50]
            if high_volatility:
                products = ", ".join([t['product'].title() for t in high_volatility[:3]])
                insights.append(f"⚠️ Alta volatilidad detectada en: {products}")
            
            # Recent changes insight
            significant_changes = [
                t for t in valid_trends 
                if abs(t.get('recent_change_percent', 0)) > 20
            ]
            if significant_changes:
                insights.append(
                    f"🔔 {len(significant_changes)} producto(s) con cambios significativos "
                    f"en las últimas 4 semanas"
                )
            
            # Transaction type specific insights
            transaction_type = query_params.get('transaction_type')
            if transaction_type == 1:  # Sales
                insights.append("💡 Considera aumentar inventario de productos en crecimiento")
            elif transaction_type == 0:  # Purchases
                insights.append("💡 Revisa proveedores de productos con costos crecientes")
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            insights.append("Error al generar insights")
        
        return insights
    
    def _calculate_period_days(self, transactions: List[Dict[str, Any]]) -> int:
        """Calculate the number of days in the analysis period"""
        try:
            dates = []
            for transaction in transactions:
                date_str = transaction.get('date_registry', '')
                if date_str:
                    date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    dates.append(date)
            
            if len(dates) < 2:
                return 0
            
            min_date = min(dates)
            max_date = max(dates)
            
            return (max_date - min_date).days
            
        except Exception as e:
            logger.error(f"Error calculating period days: {str(e)}")
            return 0
