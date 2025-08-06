"""ML-based recommendation system for QuickDeliver."""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
import json
from datetime import datetime, timedelta
from utils.data import MOCK_USERS, RESTAURANT_RECOMMENDATIONS
import streamlit as st


class RecommendationEngine:
    """ML-based recommendation engine using collaborative and content-based filtering."""
    
    def __init__(self):
        self.user_item_matrix = None
        self.restaurant_features = None
        self.user_profiles = None
        self.similarity_matrix = None
        self._initialize_data()
    
    def _initialize_data(self):
        """Initialize the recommendation system with existing data."""
        try:
            # Create user-restaurant interaction matrix
            self._build_user_item_matrix()
            
            # Build restaurant feature matrix
            self._build_restaurant_features()
            
            # Build user profiles
            self._build_user_profiles()
            
            # Calculate similarity matrices
            self._calculate_similarities()
            
        except Exception as e:
            print(f"Error initializing recommendation engine: {e}")
    
    def _build_user_item_matrix(self):
        """Build user-restaurant interaction matrix from order history."""
        user_restaurant_interactions = defaultdict(lambda: defaultdict(float))
        
        # Process all users' order history
        for username, user_data in MOCK_USERS.items():
            orders = user_data.get('orders', [])
            
            for order in orders:
                restaurant = order.get('restaurant', '')
                total = order.get('total', 0)
                status = order.get('status', '')
                
                # Weight interactions based on order value and status
                weight = self._calculate_interaction_weight(total, status)
                user_restaurant_interactions[username][restaurant] += weight
        
        # Convert to pandas DataFrame
        all_restaurants = set()
        for user_interactions in user_restaurant_interactions.values():
            all_restaurants.update(user_interactions.keys())
        
        all_users = list(user_restaurant_interactions.keys())
        all_restaurants = list(all_restaurants)
        
        # Create matrix
        matrix_data = []
        for user in all_users:
            row = []
            for restaurant in all_restaurants:
                row.append(user_restaurant_interactions[user].get(restaurant, 0))
            matrix_data.append(row)
        
        self.user_item_matrix = pd.DataFrame(
            matrix_data, 
            index=all_users, 
            columns=all_restaurants
        )
    
    def _calculate_interaction_weight(self, total: float, status: str) -> float:
        """Calculate interaction weight based on order value and status."""
        base_weight = 1.0
        
        # Weight by order value (normalized)
        value_weight = min(total / 500.0, 2.0)  # Cap at 2x for high-value orders
        
        # Weight by order status
        status_weights = {
            'Delivered': 1.0,
            'In Transit': 0.8,
            'Preparing': 0.6,
            'Cancelled': 0.1
        }
        status_weight = status_weights.get(status, 0.5)
        
        return base_weight * value_weight * status_weight
    
    def _build_restaurant_features(self):
        """Build restaurant feature matrix for content-based filtering."""
        restaurants = []
        features = []
        
        # Get all unique restaurants from orders and recommendations
        all_restaurants = set()
        for user_data in MOCK_USERS.values():
            for order in user_data.get('orders', []):
                all_restaurants.add(order.get('restaurant', ''))
        
        # Add restaurants from static data
        for restaurant in RESTAURANT_RECOMMENDATIONS:
            all_restaurants.add(restaurant['name'])
        
        # Build feature vectors for each restaurant
        cuisine_types = set()
        for restaurant_data in RESTAURANT_RECOMMENDATIONS:
            cuisine_types.add(restaurant_data['cuisine'])
        
        cuisine_types = list(cuisine_types)
        
        for restaurant_name in all_restaurants:
            if not restaurant_name:
                continue
                
            # Find restaurant data
            restaurant_info = None
            for r in RESTAURANT_RECOMMENDATIONS:
                if r['name'] == restaurant_name:
                    restaurant_info = r
                    break
            
            if restaurant_info:
                # Create feature vector: [rating, delivery_time_numeric, cuisine_one_hot...]
                feature_vector = [
                    restaurant_info['rating'],
                    self._parse_delivery_time(restaurant_info['delivery_time'])
                ]
                
                # One-hot encode cuisine
                for cuisine in cuisine_types:
                    feature_vector.append(1.0 if restaurant_info['cuisine'] == cuisine else 0.0)
                
                restaurants.append(restaurant_name)
                features.append(feature_vector)
            else:
                # Default features for restaurants not in static data
                feature_vector = [4.0, 30.0] + [0.0] * len(cuisine_types)
                restaurants.append(restaurant_name)
                features.append(feature_vector)
        
        self.restaurant_features = pd.DataFrame(
            features,
            index=restaurants,
            columns=['rating', 'delivery_time'] + [f'cuisine_{c}' for c in cuisine_types]
        )
    
    def _parse_delivery_time(self, delivery_time_str: str) -> float:
        """Parse delivery time string to numeric value."""
        try:
            # Extract numbers from "25-35 min" format
            numbers = [int(x) for x in delivery_time_str.split() if x.isdigit()]
            if len(numbers) >= 2:
                return (numbers[0] + numbers[1]) / 2.0
            elif len(numbers) == 1:
                return float(numbers[0])
            else:
                return 30.0  # Default
        except:
            return 30.0
    
    def _build_user_profiles(self):
        """Build user preference profiles based on order history."""
        user_profiles = {}
        
        for username in self.user_item_matrix.index:
            user_data = MOCK_USERS.get(username, {})
            orders = user_data.get('orders', [])
            
            if not orders:
                # Default profile
                user_profiles[username] = {
                    'avg_order_value': 500.0,
                    'preferred_cuisines': {},
                    'price_sensitivity': 0.5,
                    'rating_preference': 4.0,
                    'delivery_time_preference': 30.0,
                    'order_frequency': 0.1
                }
                continue
            
            # Calculate user preferences
            total_spent = sum(order.get('total', 0) for order in orders)
            avg_order_value = total_spent / len(orders)
            
            # Cuisine preferences
            cuisine_counts = Counter()
            total_ratings = 0
            total_delivery_times = 0
            valid_restaurants = 0
            
            for order in orders:
                restaurant_name = order.get('restaurant', '')
                
                # Find restaurant info
                for r in RESTAURANT_RECOMMENDATIONS:
                    if r['name'] == restaurant_name:
                        cuisine_counts[r['cuisine']] += 1
                        total_ratings += r['rating']
                        total_delivery_times += self._parse_delivery_time(r['delivery_time'])
                        valid_restaurants += 1
                        break
            
            # Normalize cuisine preferences
            total_cuisine_orders = sum(cuisine_counts.values())
            cuisine_prefs = {}
            if total_cuisine_orders > 0:
                for cuisine, count in cuisine_counts.items():
                    cuisine_prefs[cuisine] = count / total_cuisine_orders
            
            # Calculate preferences
            avg_rating_pref = total_ratings / valid_restaurants if valid_restaurants > 0 else 4.0
            avg_delivery_pref = total_delivery_times / valid_restaurants if valid_restaurants > 0 else 30.0
            
            # Price sensitivity (lower values = more price sensitive)
            price_sensitivity = min(avg_order_value / 1000.0, 1.0)
            
            user_profiles[username] = {
                'avg_order_value': avg_order_value,
                'preferred_cuisines': cuisine_prefs,
                'price_sensitivity': price_sensitivity,
                'rating_preference': avg_rating_pref,
                'delivery_time_preference': avg_delivery_pref,
                'order_frequency': len(orders) / 30.0  # Assuming 30-day period
            }
        
        self.user_profiles = user_profiles
    
    def _calculate_similarities(self):
        """Calculate user-user and item-item similarity matrices."""
        if self.user_item_matrix is None or self.user_item_matrix.empty:
            return
        
        # User-user similarity using cosine similarity
        user_matrix = self.user_item_matrix.values
        
        # Normalize rows
        norms = np.linalg.norm(user_matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        normalized_matrix = user_matrix / norms
        
        # Calculate cosine similarity
        self.similarity_matrix = np.dot(normalized_matrix, normalized_matrix.T)
    
    def get_collaborative_recommendations(self, username: str, n_recommendations: int = 5) -> List[Dict]:
        """Get recommendations using collaborative filtering."""
        if (self.user_item_matrix is None or 
            username not in self.user_item_matrix.index or
            self.similarity_matrix is None):
            return []
        
        try:
            user_idx = self.user_item_matrix.index.get_loc(username)
            user_similarities = self.similarity_matrix[user_idx]
            
            # Get most similar users (excluding self)
            similar_users_idx = np.argsort(user_similarities)[::-1][1:6]  # Top 5 similar users
            
            # Get restaurants that similar users liked but current user hasn't tried
            user_restaurants = set(self.user_item_matrix.columns[
                self.user_item_matrix.loc[username] > 0
            ])
            
            restaurant_scores = defaultdict(float)
            
            for similar_user_idx in similar_users_idx:
                similarity_score = user_similarities[similar_user_idx]
                if similarity_score <= 0:
                    continue
                
                similar_user = self.user_item_matrix.index[similar_user_idx]
                similar_user_restaurants = self.user_item_matrix.loc[similar_user]
                
                for restaurant, rating in similar_user_restaurants.items():
                    if rating > 0 and restaurant not in user_restaurants:
                        restaurant_scores[restaurant] += similarity_score * rating
            
            # Sort and return top recommendations
            sorted_restaurants = sorted(
                restaurant_scores.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:n_recommendations]
            
            recommendations = []
            for restaurant, score in sorted_restaurants:
                # Get restaurant info
                restaurant_info = self._get_restaurant_info(restaurant)
                if restaurant_info:
                    restaurant_info['recommendation_score'] = float(score)
                    restaurant_info['recommendation_type'] = 'collaborative'
                    recommendations.append(restaurant_info)
            
            return recommendations
            
        except Exception as e:
            print(f"Error in collaborative filtering: {e}")
            return []
    
    def get_content_based_recommendations(self, username: str, n_recommendations: int = 5) -> List[Dict]:
        """Get recommendations using content-based filtering."""
        if username not in self.user_profiles:
            return []
        
        user_profile = self.user_profiles[username]
        restaurant_scores = {}
        
        # Score each restaurant based on user preferences
        for restaurant in self.restaurant_features.index:
            if not restaurant:
                continue
                
            score = 0.0
            restaurant_features = self.restaurant_features.loc[restaurant]
            
            # Rating preference (higher weight for better ratings)
            rating_score = restaurant_features['rating'] / 5.0
            score += rating_score * 0.3
            
            # Delivery time preference (prefer shorter times, but consider user's historical preference)
            delivery_time = restaurant_features['delivery_time']
            user_delivery_pref = user_profile['delivery_time_preference']
            delivery_score = max(0, 1 - abs(delivery_time - user_delivery_pref) / 30.0)
            score += delivery_score * 0.2
            
            # Cuisine preference
            cuisine_score = 0.0
            for cuisine, preference in user_profile['preferred_cuisines'].items():
                cuisine_col = f'cuisine_{cuisine}'
                if cuisine_col in restaurant_features.index:
                    if restaurant_features[cuisine_col] > 0:
                        cuisine_score += preference
            
            score += cuisine_score * 0.5
            
            restaurant_scores[restaurant] = score
        
        # Get user's already tried restaurants
        user_data = MOCK_USERS.get(username, {})
        tried_restaurants = set(order.get('restaurant', '') for order in user_data.get('orders', []))
        
        # Filter out already tried restaurants and sort
        filtered_scores = {
            restaurant: score for restaurant, score in restaurant_scores.items()
            if restaurant not in tried_restaurants
        }
        
        sorted_restaurants = sorted(
            filtered_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:n_recommendations]
        
        recommendations = []
        for restaurant, score in sorted_restaurants:
            restaurant_info = self._get_restaurant_info(restaurant)
            if restaurant_info:
                restaurant_info['recommendation_score'] = float(score)
                restaurant_info['recommendation_type'] = 'content_based'
                recommendations.append(restaurant_info)
        
        return recommendations
    
    def get_hybrid_recommendations(self, username: str, n_recommendations: int = 8) -> List[Dict]:
        """Get hybrid recommendations combining collaborative and content-based filtering."""
        # Get recommendations from both methods
        collaborative_recs = self.get_collaborative_recommendations(username, n_recommendations)
        content_recs = self.get_content_based_recommendations(username, n_recommendations)
        
        # Combine and weight the recommendations
        all_recommendations = {}
        
        # Add collaborative recommendations with higher weight
        for rec in collaborative_recs:
            restaurant_name = rec['name']
            all_recommendations[restaurant_name] = {
                **rec,
                'final_score': rec['recommendation_score'] * 0.6,
                'recommendation_type': 'hybrid'
            }
        
        # Add content-based recommendations
        for rec in content_recs:
            restaurant_name = rec['name']
            if restaurant_name in all_recommendations:
                # Combine scores if restaurant appears in both
                all_recommendations[restaurant_name]['final_score'] += rec['recommendation_score'] * 0.4
            else:
                all_recommendations[restaurant_name] = {
                    **rec,
                    'final_score': rec['recommendation_score'] * 0.4,
                    'recommendation_type': 'hybrid'
                }
        
        # Sort by final score and return top N
        sorted_recommendations = sorted(
            all_recommendations.values(),
            key=lambda x: x['final_score'],
            reverse=True
        )[:n_recommendations]
        
        return sorted_recommendations
    
    def get_trending_recommendations(self, n_recommendations: int = 6) -> List[Dict]:
        """Get trending restaurants based on recent order patterns."""
        # Calculate restaurant popularity from all users' recent orders
        restaurant_popularity = defaultdict(float)
        current_time = datetime.now()
        
        for user_data in MOCK_USERS.values():
            orders = user_data.get('orders', [])
            
            for order in orders:
                restaurant = order.get('restaurant', '')
                order_date_str = order.get('date', '')
                
                try:
                    order_date = datetime.strptime(order_date_str, '%Y-%m-%d')
                    days_ago = (current_time - order_date).days
                    
                    # Weight recent orders more heavily
                    if days_ago <= 7:
                        weight = 1.0
                    elif days_ago <= 30:
                        weight = 0.5
                    else:
                        weight = 0.1
                    
                    restaurant_popularity[restaurant] += weight
                    
                except:
                    # If date parsing fails, give minimal weight
                    restaurant_popularity[restaurant] += 0.1
        
        # Sort by popularity
        sorted_restaurants = sorted(
            restaurant_popularity.items(),
            key=lambda x: x[1],
            reverse=True
        )[:n_recommendations]
        
        recommendations = []
        for restaurant, popularity_score in sorted_restaurants:
            restaurant_info = self._get_restaurant_info(restaurant)
            if restaurant_info:
                restaurant_info['recommendation_score'] = float(popularity_score)
                restaurant_info['recommendation_type'] = 'trending'
                recommendations.append(restaurant_info)
        
        return recommendations
    
    def _get_restaurant_info(self, restaurant_name: str) -> Optional[Dict]:
        """Get restaurant information from static data."""
        for restaurant in RESTAURANT_RECOMMENDATIONS:
            if restaurant['name'] == restaurant_name:
                return restaurant.copy()
        
        # If not found in static data, create basic info
        return {
            'name': restaurant_name,
            'cuisine': 'Mixed',
            'rating': 4.0,
            'delivery_time': '30-40 min'
        }
    
    def get_personalized_recommendations(self, username: str) -> Dict[str, List[Dict]]:
        """Get all types of personalized recommendations for a user."""
        try:
            return {
                'hybrid': self.get_hybrid_recommendations(username, 6),
                'collaborative': self.get_collaborative_recommendations(username, 4),
                'content_based': self.get_content_based_recommendations(username, 4),
                'trending': self.get_trending_recommendations(4)
            }
        except Exception as e:
            print(f"Error getting personalized recommendations: {e}")
            # Fallback to static recommendations
            return {
                'hybrid': RESTAURANT_RECOMMENDATIONS[:6],
                'collaborative': [],
                'content_based': [],
                'trending': RESTAURANT_RECOMMENDATIONS[:4]
            }


# Global recommendation engine instance
recommendation_engine = RecommendationEngine()


def get_ml_recommendations(username: str) -> Dict[str, List[Dict]]:
    """Get ML-based recommendations for a user."""
    return recommendation_engine.get_personalized_recommendations(username)


def update_recommendation_model():
    """Update the recommendation model with new data."""
    global recommendation_engine
    recommendation_engine = RecommendationEngine()
    return True