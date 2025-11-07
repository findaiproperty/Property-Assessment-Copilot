import streamlit as st
import json
import os
from datetime import datetime, timedelta
import hashlib

class AuthSystem:
    def __init__(self, data_file='data/user_data.json'):
        self.data_file = data_file
        self.load_user_data()
    
    def load_user_data(self):
        """Load user data from JSON file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.users = json.load(f)
        else:
            self.users = {}
            os.makedirs('data', exist_ok=True)
    
    def save_user_data(self):
        """Save user data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def hash_password(self, password):
        """Simple password hashing"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, password, email, plan='free'):
        """Create new user account"""
        if username in self.users:
            return False, "Username already exists"
        
        self.users[username] = {
            'password': self.hash_password(password),
            'email': email,
            'plan': plan,
            'created_at': datetime.now().isoformat(),
            'usage_count': 0,
            'max_uses': 5 if plan == 'free' else float('inf'),
            'last_reset': datetime.now().isoformat()
        }
        self.save_user_data()
        return True, "User created successfully"
    
    def verify_user(self, username, password):
        """Verify user credentials"""
        if username not in self.users:
            return False, "User not found"
        
        if self.users[username]['password'] != self.hash_password(password):
            return False, "Invalid password"
        
        return True, "Login successful"
    
    def check_usage_limit(self, username):
        """Check if user has reached usage limit"""
        user = self.users.get(username)
        if not user:
            return False
        
        # Reset monthly usage for free users
        last_reset = datetime.fromisoformat(user['last_reset'])
        if datetime.now() - last_reset > timedelta(days=30):
            user['usage_count'] = 0
            user['last_reset'] = datetime.now().isoformat()
            self.save_user_data()
        
        return user['usage_count'] < user['max_uses']
    
    def increment_usage(self, username):
        """Increment user usage count"""
        if username in self.users:
            self.users[username]['usage_count'] += 1
            self.save_user_data()
    
    def get_user_plan(self, username):
        """Get user's subscription plan"""
        return self.users.get(username, {}).get('plan', 'free')
    
    def upgrade_user(self, username, new_plan):
        """Upgrade user subscription"""
        if username in self.users:
            self.users[username]['plan'] = new_plan
            self.users[username]['max_uses'] = float('inf')
            self.save_user_data()
            return True
        return False
