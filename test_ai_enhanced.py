"""
Test script for enhanced AI analyzer error handling
"""

from ai_analyzer import AIAnalyzer

def test_ai_analyzer():
    print("🔍 Testing Enhanced AI Analyzer")
    print("=" * 40)
    
    analyzer = AIAnalyzer()
    
    # Test 1: Check availability
    print(f"✅ AI Available: {analyzer.is_available()}")
    
    # Test 2: Connection test
    print("\n🌐 Testing Connection...")
    connection_result = analyzer.test_connection()
    print(f"Connected: {connection_result['connected']}")
    if connection_result['connected']:
        print(f"Message: {connection_result['message']}")
    else:
        print(f"Error: {connection_result['error']}")
        print(f"Suggestion: {connection_result['suggestion']}")
    
    # Test 3: Quick investigation query
    print("\n🤖 Testing Investigation Query...")
    test_analysis = "This is a test forensic analysis with some suspicious content about drugs and weapons."
    test_query = "Any drug related info? Reply in very short."
    
    try:
        result = analyzer.investigate_analysis(test_query, test_analysis)
        print("✅ Investigation query successful")
        print(f"Response length: {len(result)} characters")
        print(f"First 100 characters: {result[:100]}...")
    except Exception as e:
        print(f"❌ Investigation query failed: {e}")
    
    print("\n" + "=" * 40)
    print("🎉 Test completed!")

if __name__ == "__main__":
    test_ai_analyzer()