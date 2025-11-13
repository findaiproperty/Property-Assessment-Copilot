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
        try:
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    self.users = json.load(f)
            else:
                self.users = {}
                # Create initial file
                self.save_user_data()
        except Exception as e:
            print(f"Error loading user data: {e}")
            self.users = {}
    
    def save_user_data(self):
        """Save user data to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.users, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving user data: {e}")
            return False
    
    def hash_password(self, password):
        """Simple password hashing"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, password, email, plan='free'):
        """Create new user account"""
        # Input validation
        if not username or not password or not email:
            return False, "All fields are required"
        
        if username in self.users:
            return False, "Username already exists"
        
        if len(password) < 3:
            return False, "Password must be at least 3 characters"
        
        try:
            self.users[username] = {
                'password': self.hash_password(password),
                'email': email,
                'plan': plan,
                'created_at': datetime.now().isoformat(),
                'usage_count': 0,
                'max_uses': 5 if plan == 'free' else float('inf'),
                'last_reset': datetime.now().isoformat()
            }
            
            if self.save_user_data():
                return True, "User created successfully"
            else:
                return False, "Failed to save user data"
                
        except Exception as e:
            return False, f"Error creating user: {str(e)}"
    
    def verify_user(self, username, password):
        """Verify user credentials"""
        if not username or not password:
            return False, "Username and password required"
        
        if username not in self.users:
            return False, "User not found"
        
        stored_hash = self.users[username]['password']
        input_hash = self.hash_password(password)
        
        if stored_hash != input_hash:
            return False, "Invalid password"
        
        return True, "Login successful"
    
    def check_usage_limit(self, username):
        """Check if user has reached usage limit"""
        if username not in self.users:
            return False
        
        user = self.users[username]
        
        # Reset monthly usage for free users
        try:
            last_reset = datetime.fromisoformat(user['last_reset'])
            if datetime.now() - last_reset > timedelta(days=30):
                user['usage_count'] = 0
                user['last_reset'] = datetime.now().isoformat()
                self.save_user_data()
        except:
            # If there's an error with reset logic, continue anyway
            pass
        
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
            return self.save_user_data()
        return False
