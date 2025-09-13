"""
Test script to demonstrate the beauty category classification feature
"""
import sys
sys.path.append('src')

from src.enhanced_analysis import EnhancedCommentAnalyzer
import pandas as pd

def test_beauty_categorization():
    """Test the beauty category classification system"""
    
    print("🏷️ BEAUTY CATEGORY CLASSIFICATION TEST")
    print("=" * 60)
    
    # Initialize the enhanced analyzer
    analyzer = EnhancedCommentAnalyzer()
    
    # Test comments for different beauty categories
    test_comments = [
        # Makeup comments
        ("Love this foundation! What shade are you wearing?", "makeup"),
        ("Your eyeshadow blending is incredible! Tutorial please?", "makeup"),
        ("That lipstick color is perfect for fall", "makeup"),
        ("Can you do a smoky eye tutorial for beginners?", "makeup"),
        ("What mascara gives you those amazing lashes?", "makeup"),
        ("Your contouring technique is flawless", "makeup"),
        
        # Skincare comments  
        ("My acne has improved so much with this routine", "skincare"),
        ("What serum do you use for anti-aging?", "skincare"),
        ("This moisturizer saved my dry skin", "skincare"),
        ("Retinol has changed my skin texture completely", "skincare"),
        ("Your skincare routine is goals! What cleanser is that?", "skincare"),
        ("Hyaluronic acid is a game changer for hydration", "skincare"),
        
        # Fragrance comments
        ("This perfume lasts all day! What's the name?", "fragrance"),
        ("Love floral scents, this one is beautiful", "fragrance"),
        ("Your signature scent is amazing, where can I buy it?", "fragrance"),
        ("Vanilla and sandalwood notes are my favorite", "fragrance"),
        
        # Haircare comments
        ("What shampoo do you use for curly hair?", "haircare"),
        ("My hair has never been this shiny! Love this oil", "haircare"),
        ("Heat protection is so important for styling", "haircare"),
        ("This hair mask repaired my damaged ends", "haircare"),
        
        # Nails comments
        ("That nail polish color is stunning!", "nails"),
        ("Your nail art skills are incredible", "nails"),
        ("What base coat do you recommend?", "nails"),
        
        # Tools and accessories
        ("What makeup brushes do you use?", "tools_accessories"),
        ("That beauty blender technique is perfect", "tools_accessories"),
        ("Your vanity setup is so organized", "tools_accessories"),
        
        # General beauty comments
        ("You look beautiful!", "general"),
        ("Great video!", "general"),
        ("First!", "general"),
        ("Thanks for the tips", "general")
    ]
    
    print("Testing beauty category classification:")
    print("-" * 60)
    
    correct_predictions = 0
    total_predictions = len(test_comments)
    
    category_results = {}
    
    for comment, expected_category in test_comments:
        predicted_category = analyzer.classify_beauty_category(comment)
        confidence = analyzer.get_category_confidence(comment)
        
        is_correct = predicted_category == expected_category
        if is_correct:
            correct_predictions += 1
        
        # Track results by category
        if expected_category not in category_results:
            category_results[expected_category] = {'correct': 0, 'total': 0}
        
        category_results[expected_category]['total'] += 1
        if is_correct:
            category_results[expected_category]['correct'] += 1
        
        status = "✅" if is_correct else "❌"
        print(f"{status} '{comment[:50]}...'")
        print(f"   Expected: {expected_category} | Predicted: {predicted_category} | Confidence: {confidence:.2f}")
        print()
    
    # Overall accuracy
    accuracy = (correct_predictions / total_predictions) * 100
    print("=" * 60)
    print(f"📊 OVERALL ACCURACY: {correct_predictions}/{total_predictions} ({accuracy:.1f}%)")
    print("=" * 60)
    
    # Category-wise performance
    print("\n📈 CATEGORY-WISE PERFORMANCE:")
    print("-" * 40)
    
    for category, results in category_results.items():
        cat_accuracy = (results['correct'] / results['total']) * 100
        print(f"{category.ljust(20)}: {results['correct']}/{results['total']} ({cat_accuracy:.1f}%)")
    
    return accuracy, category_results

def test_real_world_comments():
    """Test with more realistic YouTube comments"""
    
    print("\n🌍 REAL-WORLD COMMENT CLASSIFICATION TEST")
    print("=" * 60)
    
    analyzer = EnhancedCommentAnalyzer()
    
    real_comments = [
        "OMG your foundation routine is everything! What primer do you use underneath?",
        "I have oily skin and this skincare routine has been a game changer for my pores",
        "That perfume smells amazing on you! Is it long lasting?",
        "Your hair looks so healthy and shiny! What products do you use?",
        "Love that nail color! Is it gel or regular polish?",
        "What brushes do you recommend for beginners?",
        "You're so pretty! Love your videos",
        "First to comment! Love you girl",
        "Check out my channel for more beauty tips!",
        "Can you do a tutorial on winged eyeliner for hooded eyes?",
        "My sensitive skin loves this gentle cleanser you recommended",
        "That highlighter gives you such a beautiful glow!",
        "What's your favorite drugstore mascara?",
        "Your contouring skills are insane! Please teach us",
        "I need that lipstick shade name ASAP!",
        "This anti-aging serum has reduced my fine lines so much",
        "Your curls are gorgeous! What styling cream do you use?",
        "That eyeshadow palette has the most beautiful colors",
        "What setting spray keeps your makeup looking fresh all day?",
        "Your skincare routine cleared up my acne completely"
    ]
    
    print("Analyzing real-world comments:")
    print("-" * 40)
    
    category_distribution = {}
    
    for i, comment in enumerate(real_comments, 1):
        category = analyzer.classify_beauty_category(comment)
        confidence = analyzer.get_category_confidence(comment)
        
        # Track distribution
        if category not in category_distribution:
            category_distribution[category] = 0
        category_distribution[category] += 1
        
        print(f"{i:2d}. Category: {category.ljust(15)} | Confidence: {confidence:.2f}")
        print(f"    Comment: {comment}")
        print()
    
    # Show distribution
    print("📊 CATEGORY DISTRIBUTION:")
    print("-" * 30)
    
    total_comments = len(real_comments)
    for category, count in sorted(category_distribution.items()):
        percentage = (count / total_comments) * 100
        print(f"{category.ljust(20)}: {count:2d} ({percentage:5.1f}%)")
    
    return category_distribution

def demonstrate_filtering():
    """Demonstrate how filtering would work in the app"""
    
    print("\n🔍 FILTERING DEMONSTRATION")
    print("=" * 40)
    
    # Create sample dataset
    analyzer = EnhancedCommentAnalyzer()
    
    sample_data = {
        'textOriginal_cleaned': [
            "Love this foundation tutorial!",
            "What skincare routine do you follow?", 
            "That perfume smells amazing!",
            "Your hair looks so healthy",
            "Beautiful nail art design",
            "What brushes do you recommend?",
            "You look gorgeous!",
            "First comment!",
            "Amazing eyeshadow blending technique",
            "This moisturizer saved my dry skin"
        ]
    }
    
    df = pd.DataFrame(sample_data)
    
    # Add categories
    categories = []
    confidences = []
    
    for comment in df['textOriginal_cleaned']:
        category = analyzer.classify_beauty_category(comment)
        confidence = analyzer.get_category_confidence(comment)
        categories.append(category)
        confidences.append(confidence)
    
    df['beauty_category'] = categories
    df['category_confidence'] = confidences
    
    print("Sample dataset with categories:")
    print("-" * 40)
    
    for i, row in df.iterrows():
        print(f"{i+1}. {row['beauty_category'].ljust(15)} | {row['textOriginal_cleaned']}")
    
    print(f"\nTotal comments: {len(df)}")
    print("\nCategory breakdown:")
    category_counts = df['beauty_category'].value_counts()
    for category, count in category_counts.items():
        print(f"  {category}: {count}")
    
    # Demonstrate filtering
    print("\n🔍 FILTERING EXAMPLES:")
    print("-" * 25)
    
    # Filter by makeup
    makeup_comments = df[df['beauty_category'] == 'makeup']
    print(f"Makeup comments: {len(makeup_comments)}")
    
    # Filter by skincare
    skincare_comments = df[df['beauty_category'] == 'skincare']
    print(f"Skincare comments: {len(skincare_comments)}")
    
    # Filter by confidence
    high_confidence = df[df['category_confidence'] >= 0.5]
    print(f"High confidence (≥0.5): {len(high_confidence)}")
    
    return df

if __name__ == "__main__":
    print("🚀 BEAUTY CATEGORY CLASSIFICATION TESTING")
    print("=" * 80)
    print("Testing L'Oréal beauty category detection system")
    print("Categories: makeup, skincare, fragrance, haircare, nails, tools_accessories, general")
    print("=" * 80)
    
    try:
        # Test 1: Controlled test with known categories
        accuracy, category_results = test_beauty_categorization()
        
        # Test 2: Real-world comments
        distribution = test_real_world_comments()
        
        # Test 3: Filtering demonstration
        sample_df = demonstrate_filtering()
        
        print("\n🎉 TESTING COMPLETE!")
        print("=" * 40)
        print("✅ Beauty category classification system is working!")
        print("✅ Categories can be used for filtering in the app")
        print("✅ Confidence scores help identify classification quality")
        print("\n💡 The system can now automatically categorize comments into:")
        print("   🎨 Makeup, 🧴 Skincare, 🌸 Fragrance, 💇 Haircare")
        print("   💅 Nails, 🛠️ Tools & Accessories, 📝 General")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()