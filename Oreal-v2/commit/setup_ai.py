"""
Setup script for AI Assistant with Gemini
"""
import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing AI Assistant requirements...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai>=0.3.0"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv>=1.0.0"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def create_env_file():
    """Create .env file template"""
    env_content = """# AI Assistant Configuration
# Get your free API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("📝 Created .env file template")
    else:
        print("📝 .env file already exists")

def main():
    print("🚀 Setting up AI Assistant with Google Gemini...")
    print()
    
    # Install requirements
    if install_requirements():
        print()
        
        # Create env file
        create_env_file()
        print()
        
        print("🎉 Setup complete!")
        print()
        print("📋 Next steps:")
        print("1. Get a free Gemini API key from: https://makersuite.google.com/app/apikey")
        print("2. Edit the .env file and replace 'your_gemini_api_key_here' with your actual API key")
        print("3. Restart your Streamlit app")
        print("4. The AI Assistant will now use Google Gemini for intelligent responses!")
        print()
        print("💡 Tip: You can also set the API key as an environment variable:")
        print("   Windows: set GEMINI_API_KEY=your_api_key")
        print("   Mac/Linux: export GEMINI_API_KEY=your_api_key")
    else:
        print("❌ Setup failed. Please install requirements manually:")
        print("   pip install google-generativeai python-dotenv")

if __name__ == "__main__":
    main()